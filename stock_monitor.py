#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票监测程序 - 新浪财经API版
功能：
1. 定时获取自选股价格
2. 单日跌幅分级提醒：3%(轻)/5%(中)/8%(重)
3. 累计跌幅提醒：3日超5%、5日超10%、10日超20%、15日超30%
4. 单日涨幅提醒：超5%止盈
5. 累计涨幅提醒：10日超25%、15日超50%
6. 基于成本价的盈亏提醒（盈利15%/30%/50%，亏损-10%止损）
7. 上午收盘和下午收盘前5分钟推送价格信息
8. Bark 推送（静音模式）

刷新逻辑：每5分钟轮询一次（非实时流式监控）
"""

import requests
import json
import sqlite3
import schedule
import time
import os
import sys
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re

# ============ 配置 ============

def get_config_path():
    """获取配置文件路径（程序所在目录）"""
    # 获取程序所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的程序
        app_path = sys.executable
        # 如果是 .app/Contents/MacOS/xxx，向上找到 .app 同级目录
        if '.app/Contents/MacOS' in app_path:
            app_dir = app_path.split('.app/Contents/MacOS')[0] + '.app'
            program_dir = os.path.dirname(app_dir)
        else:
            program_dir = os.path.dirname(app_path)
    else:
        # 开发环境，使用当前工作目录
        program_dir = os.getcwd()
    
    return os.path.join(program_dir, "config.json")

def get_db_path():
    """获取数据库文件路径（与配置文件同目录）"""
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)
    if config_dir:
        return os.path.join(config_dir, "stock_data.db")
    return "stock_data.db"

CONFIG_FILE = get_config_path()
DB_FILE = get_db_path()

# ============ 数据库操作 ============
class StockDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                prev_close REAL,
                volume INTEGER,
                UNIQUE(code, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                alert_date TEXT NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_price(self, code: str, date: str, open_price: float, high: float, 
                   low: float, close: float, prev_close: float, volume: int):
        """保存价格数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO stock_prices 
            (code, date, open, high, low, close, prev_close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (code, date, open_price, high, low, close, prev_close, volume))
        conn.commit()
        conn.close()
    
    def get_price_history(self, code: str, days: int = 5) -> List[Dict]:
        """获取最近N天的价格历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, close, prev_close FROM stock_prices 
            WHERE code = ? 
            ORDER BY date DESC 
            LIMIT ?
        ''', (code, days))
        rows = cursor.fetchall()
        conn.close()
        
        return [{"date": r[0], "close": r[1], "prev_close": r[2]} for r in rows]
    
    def has_alert_today(self, code: str, alert_type: str, date: str) -> bool:
        """检查今天是否已经发送过此类告警"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM alerts 
            WHERE code = ? AND alert_type = ? AND alert_date = ?
            LIMIT 1
        ''', (code, alert_type, date))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def record_alert(self, code: str, alert_type: str, date: str, message: str):
        """记录告警"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (code, alert_type, alert_date, message)
            VALUES (?, ?, ?, ?)
        ''', (code, alert_type, date, message))
        conn.commit()
        conn.close()


# ============ 新浪财经API ============
class SinaStockAPI:
    """新浪财经股票数据接口"""
    
    BASE_URL = "https://hq.sinajs.cn/list={}"
    
    @staticmethod
    def normalize_code(code: str) -> str:
        """标准化股票代码"""
        code = code.strip().lower()
        
        if code.startswith(('sh', 'sz', 'bj')):
            return code
        
        if len(code) == 6:
            if code.startswith(('600', '601', '603', '605', '688', '689')):
                return f"sh{code}"
            elif code.startswith(('000', '001', '002', '003', '300', '301')):
                return f"sz{code}"
            elif code.startswith(('430', '83', '87', '88')):
                return f"bj{code}"
        
        return code
    
    def fetch_quotes(self, codes: List[str]) -> Dict[str, Dict]:
        """获取股票行情数据（支持股票和指数）"""
        normalized_codes = []
        for c in codes:
            if c.startswith(('nf_', 'hk_')):
                # 期货和港股指数特殊处理
                normalized_codes.append(c)
            else:
                normalized_codes.append(self.normalize_code(c))
        
        codes_str = ','.join(normalized_codes)
        
        url = self.BASE_URL.format(codes_str)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gb2312'
            return self._parse_response(response.text, normalized_codes)
        except Exception as e:
            print(f"[错误] 获取股票数据失败: {e}")
            return {}
    
    def _parse_response(self, response_text: str, codes: List[str]) -> Dict[str, Dict]:
        """解析新浪返回的数据"""
        result = {}
        
        for code in codes:
            var_name = f"hq_str_{code}"
            pattern = rf'{var_name}="([^"]*)"'
            match = re.search(pattern, response_text)
            
            if match and match.group(1):
                data = match.group(1).split(',')
                
                if code.startswith(('sh', 'sz', 'bj')):
                    name = data[0]
                    open_price = float(data[1])
                    prev_close = float(data[2])
                    current = float(data[3])
                    high = float(data[4])
                    low = float(data[5])
                    volume = int(data[8])
                    
                    change_pct = ((current - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                    
                    result[code] = {
                        'code': code,
                        'name': name,
                        'price': current,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'prev_close': prev_close,
                        'volume': volume,
                        'change_pct': round(change_pct, 2),
                        'change': round(current - prev_close, 3)
                    }
        
        return result


# ============ Bark 推送（静音模式） ============
class BarkNotifier:
    """Bark消息推送 - 静音模式（无声音无震动）"""
    
    BASE_URL = "https://api.day.app/{key}/{title}/{body}"
    
    def __init__(self, key: str, sound: str = "none"):
        self.key = key
        self.sound = sound
    
    def send(self, title: str, body: str) -> bool:
        """发送推送（静音模式）"""
        try:
            encoded_title = urllib.parse.quote(title, safe='')
            encoded_body = urllib.parse.quote(body, safe='')
            
            url = f"https://api.day.app/{self.key}/{encoded_title}/{encoded_body}"
            
            params = {
                "sound": self.sound,
                "group": "股票监测"
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get('code') == 200:
                print(f"[推送成功] {title}")
                return True
            else:
                print(f"[推送失败] {result.get('message')}")
                return False
        except Exception as e:
            print(f"[推送错误] {e}")
            return False


# ============ 主程序 ============
class StockMonitor:
    def __init__(self):
        self.config = self._load_config()
        self.db = StockDatabase(DB_FILE)
        self.api = SinaStockAPI()
        self.notifier = BarkNotifier(
            self.config['bark_key'],
            self.config.get('bark_sound', 'none')
        )
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if not os.path.exists(CONFIG_FILE):
            example_file = CONFIG_FILE.replace('.json', '.example.json')
            error_msg = f"""
❌ 配置文件不存在: {CONFIG_FILE}

请复制示例配置文件并修改：
    cp {example_file} {CONFIG_FILE}

然后编辑 {CONFIG_FILE}，填入你的 Bark Key 和自选股信息。
            """
            raise FileNotFoundError(error_msg)
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_stock_config(self, code: str) -> dict:
        """获取股票配置信息"""
        for stock in self.config['stocks']:
            if stock['code'] == code:
                return stock
        return {}
    
    def is_trading_day(self) -> bool:
        """判断今天是否为交易日"""
        today = datetime.now()
        if today.weekday() >= 5:
            return False
        return True
    
    def is_trading_time(self) -> bool:
        """判断当前是否为交易时间"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        morning_start = "09:30"
        morning_end = "11:30"
        afternoon_start = "13:00"
        afternoon_end = "15:00"
        
        return ((morning_start <= current_time <= morning_end) or 
                (afternoon_start <= current_time <= afternoon_end))
    
    def check_single_day_alerts(self, stock_data: Dict, today: str) -> List[Tuple]:
        """检查单日涨跌幅告警（补仓+止盈）"""
        code = stock_data['code']
        name = stock_data['name']
        change_pct = stock_data['change_pct']
        price = stock_data['price']
        prev_close = stock_data['prev_close']
        
        thresholds = self.config['alert_threshold']['single_day']
        alerts = []
        
        # 涨幅告警（止盈）
        if change_pct >= thresholds.get('rise_level1', 5.0):
            alert_type = 'single_day_rise'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"💰 单日涨幅止盈提醒 - {name}"
                body = f"""单日涨幅超5%（止盈信号）

🔸 {name} ({code})

📈 当前涨幅：+{change_pct:.2f}%

💰 价格信息：
  • 当前价格：{price:.3f}
  • 昨收价格：{prev_close:.3f}
  • 上涨金额：+{price - prev_close:.3f}

💡 建议操作（止盈）：
  💰 单日大涨，考虑部分止盈
    - 可卖出部分持仓（20-30%）锁定利润
    - 或设置移动止盈保护收益
    - 关注是否冲高回落

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        # 跌幅告警（补仓）
        elif change_pct <= thresholds.get('drop_level3', -8.0):
            alert_type = 'single_day_l3'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"🔴 重度补仓提醒 - {name}"
                body = f"""单日跌幅超8%（重度）

🔸 {name} ({code})

📉 当前跌幅：{change_pct:.2f}%

💰 价格信息：
  • 当前价格：{price:.3f}
  • 昨收价格：{prev_close:.3f}
  • 下跌金额：{price - prev_close:.3f}

📊 阈值对比：
  • 3%轻度：已触发 ⚠️
  • 5%中度：已触发 🟠
  • 8%重度：已触发 🔴

💡 建议操作：
  🔴 强烈建议补仓或止损
    - 可考虑大幅补仓（40-50%）
    - 或评估是否需要止损离场

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        elif change_pct <= thresholds.get('drop_level2', -5.0):
            alert_type = 'single_day_l2'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"🟠 中度补仓提醒 - {name}"
                body = f"""单日跌幅超5%（中度）

🔸 {name} ({code})

📉 当前跌幅：{change_pct:.2f}%

💰 价格信息：
  • 当前价格：{price:.3f}
  • 昨收价格：{prev_close:.3f}
  • 下跌金额：{price - prev_close:.3f}

📊 阈值对比：
  • 3%轻度：已触发 ⚠️
  • 5%中度：已触发 🟠
  • 8%重度：未触发

💡 建议操作：
  🟠 建议关注，考虑适当补仓
    - 可补仓当前持仓的 20-30%
    - 或分批补仓降低成本

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        elif change_pct <= thresholds.get('drop_level1', -3.0):
            alert_type = 'single_day_l1'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"🟡 轻度补仓提醒 - {name}"
                body = f"""单日跌幅超3%（轻度）

🔸 {name} ({code})

📉 当前跌幅：{change_pct:.2f}%

💰 价格信息：
  • 当前价格：{price:.3f}
  • 昨收价格：{prev_close:.3f}
  • 下跌金额：{price - prev_close:.3f}

📊 阈值对比：
  • 3%轻度：已触发 🟡
  • 5%中度：未触发
  • 8%重度：未触发

💡 建议操作：
  🟡 可适度关注，考虑小幅补仓
    - 可小幅试探性补仓（10-15%）
    - 观察后续走势再决定

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        return alerts
    
    def check_cumulative_alerts(self, stock_data: Dict, today: str) -> List[Tuple]:
        """检查累计涨跌幅告警（补仓+止盈）"""
        code = stock_data['code']
        name = stock_data['name']
        current_price = stock_data['price']
        
        thresholds = self.config['alert_threshold']['cumulative']
        alerts = []
        
        history = self.db.get_price_history(code, days=20)
        
        if len(history) >= 2:
            sorted_history = sorted(history, key=lambda x: x['date'])
            
            # 累计涨幅告警（止盈）
            if len(sorted_history) >= 15 and thresholds.get('rise_15day'):
                price_15days_ago = sorted_history[-15]['close']
                fifteen_day_change_pct = ((current_price - price_15days_ago) / price_15days_ago) * 100
                
                if fifteen_day_change_pct >= thresholds['rise_15day']:
                    alert_type = 'cumulative_rise_15day'
                    if not self.db.has_alert_today(code, alert_type, today):
                        title = f"💰💰 15日累计涨幅高度止盈 - {name}"
                        body = f"""15个交易日累计涨幅超50%（高度止盈）

🔸 {name} ({code})

📈 累计涨幅：+{fifteen_day_change_pct:.2f}%

💰 价格对比：
  • 15日前收盘价：{price_15days_ago:.3f}
  • 当前价格：{current_price:.3f}
  • 累计上涨：+{current_price - price_15days_ago:.3f}

📊 日均涨幅：约 +{fifteen_day_change_pct / 15:.2f}%/天

💡 建议操作（强烈止盈）：
  💰💰 累计涨幅巨大，强烈建议止盈！
    - 建议卖出40-60%锁定大部分利润
    - 保留底仓观察，设置移动止盈
    - 或分批卖出，避免踏空
    - 关注是否出现见顶信号

⚠️ 温馨提示：15日涨50%属于强势上涨，注意回调风险！

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                        alerts.append((alert_type, title, body))
            
            if len(sorted_history) >= 10 and thresholds.get('rise_10day'):
                price_10days_ago = sorted_history[-10]['close']
                ten_day_change_pct = ((current_price - price_10days_ago) / price_10days_ago) * 100
                
                if ten_day_change_pct >= thresholds['rise_10day']:
                    alert_type = 'cumulative_rise_10day'
                    if not self.db.has_alert_today(code, alert_type, today):
                        title = f"💰 10日累计涨幅止盈提醒 - {name}"
                        body = f"""10个交易日累计涨幅超25%（止盈信号）

🔸 {name} ({code})

📈 累计涨幅：+{ten_day_change_pct:.2f}%

💰 价格对比：
  • 10日前收盘价：{price_10days_ago:.3f}
  • 当前价格：{current_price:.3f}
  • 累计上涨：+{current_price - price_10days_ago:.3f}

📊 日均涨幅：约 +{ten_day_change_pct / 10:.2f}%/天

💡 建议操作（止盈）：
  💰 累计涨幅可观，建议部分止盈
    - 可卖出20-30%锁定部分利润
    - 或设置止盈线保护收益
    - 关注后续动能是否持续
    - 剩余仓位可继续持有观察

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                        alerts.append((alert_type, title, body))
            
            # 累计跌幅告警（补仓）
            if len(sorted_history) >= 15 and thresholds.get('drop_15day'):
                price_15days_ago = sorted_history[-15]['close']
                fifteen_day_change_pct = ((current_price - price_15days_ago) / price_15days_ago) * 100
                
                if fifteen_day_change_pct <= thresholds['drop_15day']:
                    alert_type = 'cumulative_15day'
                    if not self.db.has_alert_today(code, alert_type, today):
                        title = f"🔴🔴 15日累计跌幅严重告警 - {name}"
                        body = f"""15个交易日累计跌幅超30%（严重）

🔸 {name} ({code})

📉 累计跌幅：{fifteen_day_change_pct:.2f}%

💰 价格对比：
  • 15日前收盘价：{price_15days_ago:.3f}
  • 当前价格：{current_price:.3f}
  • 累计下跌：{current_price - price_15days_ago:.3f}

📊 日均跌幅：约 {fifteen_day_change_pct / 15:.2f}%/天

💡 建议操作：
  🔴🔴 累计跌幅严重，必须立即评估！
    - 深度套牢，谨慎补仓（建议不超过10%）
    - 重新评估投资逻辑是否变化
    - 考虑止损或转换投资标的
    - 避免情绪化操作，制定明确计划

⚠️ 风险提示：连续15日大幅下跌，注意风险！

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                        alerts.append((alert_type, title, body))
            
            if len(sorted_history) >= 10 and thresholds.get('drop_10day'):
                price_10days_ago = sorted_history[-10]['close']
                ten_day_change_pct = ((current_price - price_10days_ago) / price_10days_ago) * 100
                
                if ten_day_change_pct <= thresholds['drop_10day']:
                    alert_type = 'cumulative_10day'
                    if not self.db.has_alert_today(code, alert_type, today):
                        title = f"🔴 10日累计跌幅深度告警 - {name}"
                        body = f"""10个交易日累计跌幅超20%（深度）

🔸 {name} ({code})

📉 累计跌幅：{ten_day_change_pct:.2f}%

💰 价格对比：
  • 10日前收盘价：{price_10days_ago:.3f}
  • 当前价格：{current_price:.3f}
  • 累计下跌：{current_price - price_10days_ago:.3f}

📊 日均跌幅：约 {ten_day_change_pct / 10:.2f}%/天

💡 建议操作：
  🔴 深度调整，谨慎应对
    - 可分批补仓但控制仓位（建议15-20%）
    - 关注是否有企稳迹象
    - 评估是否进入价值投资区间
    - 设置止损线防止进一步下跌

⚠️ 风险提示：连续10日下跌，注意风险！

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                        alerts.append((alert_type, title, body))
            
            if len(sorted_history) >= 5 and thresholds.get('drop_5day'):
                price_5days_ago = sorted_history[-5]['close']
                five_day_change_pct = ((current_price - price_5days_ago) / price_5days_ago) * 100
                
                if five_day_change_pct <= thresholds['drop_5day']:
                    alert_type = 'cumulative_5day'
                    if not self.db.has_alert_today(code, alert_type, today):
                        title = f"📉 5日累计跌幅告警 - {name}"
                        body = f"""5个交易日累计跌幅超10%

🔸 {name} ({code})

📉 累计跌幅：{five_day_change_pct:.2f}%

💰 价格对比：
  • 5日前收盘价：{price_5days_ago:.3f}
  • 当前价格：{current_price:.3f}
  • 累计下跌：{current_price - price_5days_ago:.3f}

📊 日均跌幅：约 {five_day_change_pct / 5:.2f}%/天

💡 建议操作：
  📉 累计跌幅较大，建议评估仓位
    - 可考虑分批补仓摊低成本
    - 评估基本面是否发生变化
    - 或设置止损线控制风险

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                        alerts.append((alert_type, title, body))
            
            if len(sorted_history) >= 3 and thresholds.get('drop_3day'):
                price_3days_ago = sorted_history[-3]['close']
                three_day_change_pct = ((current_price - price_3days_ago) / price_3days_ago) * 100
                
                if three_day_change_pct <= thresholds['drop_3day']:
                    alert_type = 'cumulative_3day'
                    if not self.db.has_alert_today(code, alert_type, today):
                        title = f"📉 3日累计跌幅告警 - {name}"
                        body = f"""3个交易日累计跌幅超5%

🔸 {name} ({code})

📉 累计跌幅：{three_day_change_pct:.2f}%

💰 价格对比：
  • 3日前收盘价：{price_3days_ago:.3f}
  • 当前价格：{current_price:.3f}
  • 累计下跌：{current_price - price_3days_ago:.3f}

📊 日均跌幅：约 {three_day_change_pct / 3:.2f}%/天

💡 建议操作：
  📉 短期跌幅明显，可关注补仓机会
    - 可考虑小幅试探性补仓
    - 观察明日走势再做决定
    - 或等待企稳信号

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                        alerts.append((alert_type, title, body))
        
        return alerts
    
    def check_cost_based_alerts(self, stock_data: Dict, today: str) -> List[Tuple]:
        """检查基于成本价的盈亏告警"""
        code = stock_data['code']
        name = stock_data['name']
        current_price = stock_data['price']
        
        stock_config = self.get_stock_config(code)
        if not stock_config or 'cost_price' not in stock_config:
            return []
        
        cost_price = stock_config['cost_price']
        profit_pct = ((current_price - cost_price) / cost_price) * 100
        
        thresholds = self.config['alert_threshold']['based_on_cost']
        alerts = []
        
        # 止盈提醒（基于成本价）
        if profit_pct >= thresholds.get('stop_profit_3', 50.0):
            alert_type = 'cost_profit_l3'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"💰💰💰 成本止盈提醒（高度）- {name}"
                body = f"""基于成本价的盈利超50%（高度止盈）

🔸 {name} ({code})

💰 成本盈亏信息：
  • 成本价格：{cost_price:.3f}
  • 当前价格：{current_price:.3f}
  • 盈利幅度：+{profit_pct:.2f}% 🎉

💡 建议操作（强烈止盈）：
  💰💰💰 盈利丰厚，强烈建议止盈！
    - 建议卖出50-70%锁定大部分利润
    - 保留少量底仓博取更高收益
    - 或设置移动止盈保护剩余利润
    - 关注是否出现见顶回调信号

⚠️ 温馨提示：盈利50%已超预期，注意回调风险！

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        elif profit_pct >= thresholds.get('stop_profit_2', 30.0):
            alert_type = 'cost_profit_l2'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"💰💰 成本止盈提醒（中度）- {name}"
                body = f"""基于成本价的盈利超30%（中度止盈）

🔸 {name} ({code})

💰 成本盈亏信息：
  • 成本价格：{cost_price:.3f}
  • 当前价格：{current_price:.3f}
  • 盈利幅度：+{profit_pct:.2f}% 🎉

💡 建议操作（中度止盈）：
  💰💰 盈利可观，建议部分止盈
    - 可卖出30-40%锁定部分利润
    - 剩余仓位继续持有观察
    - 设置移动止盈保护收益
    - 关注趋势是否持续

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        elif profit_pct >= thresholds.get('stop_profit_1', 15.0):
            alert_type = 'cost_profit_l1'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"💰 成本止盈提醒（轻度）- {name}"
                body = f"""基于成本价的盈利超15%（轻度止盈）

🔸 {name} ({code})

💰 成本盈亏信息：
  • 成本价格：{cost_price:.3f}
  • 当前价格：{current_price:.3f}
  • 盈利幅度：+{profit_pct:.2f}% 👍

💡 建议操作（轻度止盈）：
  💰 已有盈利，可考虑部分止盈
    - 可卖出20%左右锁定部分利润
    - 或继续持有等待更高涨幅
    - 设置止损线保护本金

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        # 止损提醒（基于成本价）
        elif profit_pct <= thresholds.get('stop_loss', -10.0):
            alert_type = 'cost_stop_loss'
            if not self.db.has_alert_today(code, alert_type, today):
                title = f"⛔ 成本止损提醒 - {name}"
                body = f"""基于成本价的亏损超10%（止损提醒）

🔸 {name} ({code})

💰 成本盈亏信息：
  • 成本价格：{cost_price:.3f}
  • 当前价格：{current_price:.3f}
  • 亏损幅度：{profit_pct:.2f}% ⚠️

💡 建议操作（止损决策）：
  ⛔ 亏损已达10%，请评估是否止损
    - 重新评估投资逻辑是否仍然成立
    - 如趋势恶化，考虑止损离场
    - 如基本面未变，可继续持有或补仓
    - 设置止损线防止进一步亏损

⚠️ 风险提示：亏损扩大，注意风险控制！

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                alerts.append((alert_type, title, body))
        
        return alerts
    
    def check_alerts(self, stock_data: Dict):
        """检查所有告警条件"""
        code = stock_data['code']
        today = datetime.now().strftime("%Y-%m-%d")
        
        single_day_alerts = self.check_single_day_alerts(stock_data, today)
        cumulative_alerts = self.check_cumulative_alerts(stock_data, today)
        cost_based_alerts = self.check_cost_based_alerts(stock_data, today)
        
        all_alerts = single_day_alerts + cumulative_alerts + cost_based_alerts
        
        for alert_type, title, body in all_alerts:
            if self.notifier.send(title, body):
                self.db.record_alert(code, alert_type, today, body)
    
    def save_daily_data(self, stock_data: Dict):
        """保存每日收盘数据到数据库"""
        today = datetime.now().strftime("%Y-%m-%d")
        code = stock_data['code']
        
        self.db.save_price(
            code=code,
            date=today,
            open_price=stock_data['open'],
            high=stock_data['high'],
            low=stock_data['low'],
            close=stock_data['price'],
            prev_close=stock_data['prev_close'],
            volume=stock_data['volume']
        )
    
    def fetch_and_check(self):
        """获取数据并检查告警"""
        if self.config.get('trading_days_only', True) and not self.is_trading_day():
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 今天不是交易日，跳过")
            return
        
        if not self.is_trading_time():
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 当前不是交易时间")
            return
        
        stock_codes = [s['code'] for s in self.config['stocks']]
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 正在获取股票数据...")
        
        quotes = self.api.fetch_quotes(stock_codes)
        
        for code, data in quotes.items():
            emoji = "📈" if data['change'] >= 0 else "📉"
            print(f"  {data['name']}({code}): 价格={data['price']:.3f}, 涨跌={data['change_pct']:+.2f}% {emoji}")
            
            self.save_daily_data(data)
            self.check_alerts(data)
    
    def get_multi_day_change(self, code: str, days: int) -> float:
        """获取N日涨跌幅（基于历史收盘价，与成本无关）"""
        history = self.db.get_price_history(code, days + 5)  # 多取一些避免节假日影响
        if len(history) < days + 1:
            return 0.0
        
        # 按日期排序（从早到晚）
        sorted_history = sorted(history, key=lambda x: x['date'])
        
        # 获取N个交易日前的收盘价
        old_price = sorted_history[-(days + 1)]['close'] if len(sorted_history) > days else sorted_history[0]['close']
        current_price = sorted_history[-1]['close']
        
        if old_price <= 0:
            return 0.0
        
        return ((current_price - old_price) / old_price) * 100
    
    def get_cost_based_change(self, code: str, current_price: float) -> float:
        """获取基于持仓成本的涨跌幅"""
        stock_config = self.get_stock_config(code)
        if not stock_config or 'cost_price' not in stock_config:
            return 0.0
        
        cost_price = stock_config['cost_price']
        if cost_price <= 0:
            return 0.0
        
        return ((current_price - cost_price) / cost_price) * 100
    

    def send_market_open_reminder(self):
        """开盘提醒 - 9:30"""
        if self.config.get('trading_days_only', True) and not self.is_trading_day():
            return
        
        stock_codes = [s['code'] for s in self.config['stocks']]
        quotes = self.api.fetch_quotes(stock_codes)
        
        if not quotes:
            return
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        title = f"🌅 开盘提醒 ({now})"
        header = f"🌅 开盘提醒 ({now})\n"
        
        body_lines = [header, "━━━━━━━━━━━━━━━"]
        
        for code, data in quotes.items():
            # 开盘价和当前价
            open_price = data['open']
            current_price = data['price']
            prev_close = data['prev_close']
            
            # 计算开盘涨跌幅
            open_change_pct = ((open_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
            open_emoji = "📈" if open_change_pct >= 0 else "📉"
            
            # 基于成本的盈亏
            cost_change = self.get_cost_based_change(code, current_price)
            if cost_change != 0:
                cost_emoji = "🟢" if cost_change >= 0 else "🔴"
                cost_line = f"  • 成本盈亏: {cost_emoji} {cost_change:+.2f}%"
            else:
                cost_line = "  • 成本盈亏: 未设置"
            
            body_lines.append(f"""
🔸 {data['name']} ({code})
  • 开盘价: {open_price:.3f} {open_emoji} {open_change_pct:+.2f}%
  • 当前价: {current_price:.3f}
{cost_line}
""")
            body_lines.append("━━━━━━━━━━━━━━━")
        
        # 收盘总结在收盘时发送
        
        body = "\n".join(body_lines)
        self.notifier.send(title, body)

    def send_afternoon_open_reminder(self):
        """下午开盘提醒 - 13:00"""
        if self.config.get('trading_days_only', True) and not self.is_trading_day():
            return
        
        stock_codes = [s['code'] for s in self.config['stocks']]
        quotes = self.api.fetch_quotes(stock_codes)
        
        if not quotes:
            return
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"🌅 下午开盘提醒 ({now})"
        
        body_lines = [f"🌅 下午开盘提醒 ({now})\n", "━━━━━━━━━━━━━━━"]
        
        for code, data in quotes.items():
            # 下午开盘价（当前价）
            current_price = data['price']
            
            # 日内涨跌幅
            day_change = data['change_pct']
            day_emoji = "📈" if day_change >= 0 else "📉"
            
            # 基于成本的盈亏
            cost_change = self.get_cost_based_change(code, current_price)
            if cost_change != 0:
                cost_emoji = "🟢" if cost_change >= 0 else "🔴"
                cost_line = f"  • 成本盈亏: {cost_emoji} {cost_change:+.2f}%"
            else:
                cost_line = "  • 成本盈亏: 未设置"
            
            body_lines.append(f"""
🔸 {data['name']} ({code})
  • 下午开盘价: {current_price:.3f}
  • 日内涨跌: {day_emoji} {day_change:+.2f}%
{cost_line}
""")
            body_lines.append("━━━━━━━━━━━━━━━")
        
        body_lines.append("\n💡 下午交易开始，祝投资顺利！")
        
        body = "\n".join(body_lines)
        self.notifier.send(title, body)
    def send_afternoon_reminder(self):
        """14:55 收盘前提醒 - 显示成本盈亏和日内/3日/5日/10日涨跌幅"""
        if self.config.get('trading_days_only', True) and not self.is_trading_day():
            return
        
        stock_codes = [s['code'] for s in self.config['stocks']]
        quotes = self.api.fetch_quotes(stock_codes)
        
        if not quotes:
            return
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"🌙 收盘前提醒 ({now})"
        
        body_lines = [f"🌙 收盘前提醒 ({now})\n", "━━━━━━━━━━━━━━━"]
        
        for code, data in quotes.items():
            stock_config = self.get_stock_config(code)
            cost_price = stock_config.get('cost_price', 0)
            
            day_change = data['change_pct']
            day_emoji = "📈" if day_change >= 0 else "📉"
            
            if cost_price > 0:
                cost_profit = ((data['price'] - cost_price) / cost_price) * 100
                cost_emoji = "🟢" if cost_profit >= 0 else "🔴"
                cost_str = f"{cost_emoji} 成本盈亏: {cost_profit:+.2f}%"
            else:
                cost_str = "成本价未设置"
            
            change_3d = self.get_multi_day_change(code, 3)
            change_5d = self.get_multi_day_change(code, 5)
            change_10d = self.get_multi_day_change(code, 10)
            
            body_lines.append(f"""
🔸 {data['name']} ({code})
  • 现价: {data['price']:.3f} {day_emoji} 日内{day_change:+.2f}%
  • {cost_str}
  • 3日: {change_3d:+.2f}% | 5日: {change_5d:+.2f}% | 10日: {change_10d:+.2f}%
""")
            body_lines.append("━━━━━━━━━━━━━━━")
        
        body_lines.append("\n⏰ 收盘后立即推送全日总结")
        
        body = "\n".join(body_lines)
        self.notifier.send(title, body)
    
    def send_daily_summary(self):
        """15:01 全日总结推送"""
        if self.config.get('trading_days_only', True) and not self.is_trading_day():
            return
        
        stock_codes = [s['code'] for s in self.config['stocks']]
        quotes = self.api.fetch_quotes(stock_codes)
        
        if not quotes:
            return
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"📊 全日总结 ({now})"
        
        body_lines = [f"📊 全日总结 ({now})\n", "━━━━━━━━━━━━━━━"]
        
        # 自选ETF部分
        for code, data in quotes.items():
            day_change = data['change_pct']
            day_emoji = "📈" if day_change >= 0 else "📉"
            
            # 基于成本的盈亏
            cost_change = self.get_cost_based_change(code, data['price'])
            if cost_change != 0:
                cost_emoji = "🟢" if cost_change >= 0 else "🔴"
                cost_line = f"  • 成本盈亏: {cost_emoji} {cost_change:+.2f}%"
            else:
                cost_line = "  • 成本盈亏: 未设置成本价"
            
            # 基于历史收盘价的多日涨跌幅
            change_3d = self.get_multi_day_change(code, 3)
            change_5d = self.get_multi_day_change(code, 5)
            change_10d = self.get_multi_day_change(code, 10)
            
            # 显示格式：数据不足时显示0
            change_3d_str = f"{change_3d:+.2f}%" if change_3d != 0 else "0.00%"
            change_5d_str = f"{change_5d:+.2f}%" if change_5d != 0 else "0.00%"
            change_10d_str = f"{change_10d:+.2f}%" if change_10d != 0 else "0.00%"
            
            body_lines.append(f"""
🔸 {data['name']} ({code})
  • 现价: {data['price']:.3f}
  • 日内涨跌: {day_emoji} {day_change:+.2f}%
{cost_line}
  • 历史涨跌: 3日{change_3d_str} | 5日{change_5d_str} | 10日{change_10d_str}
""")
            body_lines.append("━━━━━━━━━━━━━━━")
        
        # 市场指数部分
        index_codes = [idx['code'] for idx in self.config.get('market_indices', [])]
        if index_codes:
            body_lines.append("\n📊 市场指数\n")
            index_quotes = self.api.fetch_quotes(index_codes)
            for code, data in index_quotes.items():
                day_change = data['change_pct']
                day_emoji = "📈" if day_change >= 0 else "📉"
                body_lines.append(f"🔸 {data['name']}: {data['price']:.2f} {day_emoji} {day_change:+.2f}%")
            body_lines.append("━━━━━━━━━━━━━━━")
        
        body = "\n".join(body_lines)
        self.notifier.send(title, body)

    def run_once(self):
        """运行一次（用于测试）"""
        print("="*60)
        print("股票监测程序 - 单次运行模式")
        print("="*60)
        
        self.fetch_and_check()
        
        current_time = datetime.now().strftime("%H:%M")
        if current_time >= "11:25" and current_time < "12:00":
            self.send_afternoon_reminder()
        elif current_time >= "14:55":
            self.send_afternoon_reminder()
        
        print("\n运行完成！")
    
    def run_scheduler(self):
        """启动定时调度"""
        print("="*60)
        print("股票监测程序 - 定时调度模式")
        print("="*60)
        print(f"推送方式：Bark（静音模式）")
        print(f"刷新频率：每 {self.config.get('refresh_interval_minutes', 5)} 分钟")
        print("-"*60)
        print(f"自选股数量: {len(self.config['stocks'])}")
        schedule_config = self.config.get('schedule', {})
        print(f"上午开盘: {schedule_config.get('market_open', '09:30')}")
        print(f"下午开盘: {schedule_config.get('afternoon_open', '13:00')}")
        print(f"上午收盘: {schedule_config.get('morning_end', '11:25')}")
        print(f"下午收盘前: {schedule_config.get('afternoon_remind', '14:55')}")
        print(f"全日总结: {schedule_config.get('market_close', '15:00')}")
        print("="*60)
        print("按 Ctrl+C 停止程序")
        print("="*60)
        
        interval = self.config.get('refresh_interval_minutes', 5)
        schedule.every(interval).minutes.do(self.fetch_and_check)
        
        schedule_config = self.config.get('schedule', {})
        
        # 上午开盘提醒 9:30
        schedule.every().day.at(schedule_config.get('market_open', '09:30')).do(
            lambda: self.send_market_open_reminder()
        )
        
        # 上午收盘提醒
        schedule.every().day.at(schedule_config.get('morning_end', '11:25')).do(
            lambda: self.send_afternoon_reminder()
        )
        
        # 下午开盘提醒 13:00
        schedule.every().day.at(schedule_config.get('afternoon_open', '13:00')).do(
            lambda: self.send_afternoon_open_reminder()
        )
        
        # 下午收盘前提醒
        schedule.every().day.at(schedule_config.get('afternoon_remind', '14:55')).do(
            lambda: self.send_afternoon_reminder()
        )
        
        # 盘后总结 15:00
        schedule.every().day.at(schedule_config.get('market_close', '15:00')).do(
            lambda: self.send_daily_summary()
        )
        
        self.fetch_and_check()
        
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    """主函数"""
    import sys
    
    monitor = StockMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        monitor.run_once()
    else:
        try:
            monitor.run_scheduler()
        except KeyboardInterrupt:
            print("\n\n程序已停止")


if __name__ == "__main__":
    main()
