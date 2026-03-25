# 📈 Stock Monitor / 股票监测程序

**English** | [中文](#中文文档)

A Python-based stock monitoring program that tracks stock/ETF prices in real-time and pushes notifications to your phone via Bark.

基于 Python 的股票监测程序，支持实时监控股票/ETF价格，并通过 Bark 推送到手机。

---

## 📥 Download / 下载

**No installation required!** Download and run directly.

**无需安装！**下载直接运行。

| Platform | Download | Size |
|----------|----------|------|
| **macOS** | [StockMonitor-mac.zip](../../releases) | ~15MB |
| **Windows** | [StockMonitor-windows.zip](../../releases) | ~12MB |

📖 [Installation Guide / 安装指南](RELEASES.md)

---

## English Documentation

### ✨ Features

- 📱 **Real-time Push Notifications**: Push to iPhone via Bark (supports silent mode)
- 📊 **Multi-dimensional Monitoring**: Intraday, 3/5/10/15 day changes, cost-based P/L
- ⏰ **Scheduled Alerts**: 5 push notifications throughout the trading day
- 💾 **Data Persistence**: SQLite database for historical prices
- ☁️ **Cloud Server Support**: 24/7 operation on cloud servers

### 🚀 Quick Start

#### 1. Clone & Install

```bash
git clone https://github.com/yourusername/stock-monitor.git
cd stock-monitor
pip3 install -r requirements.txt
```

#### 2. Configure

```bash
python3 setup.py
```

Enter your Bark Key and stock list when prompted.

#### 3. Run

```bash
python3 stock_monitor.py
```

### 📱 Push Schedule

| Time | Type |
|------|------|
| 09:30 | 🌅 Market Open |
| 11:25 | 📢 Morning Close |
| 13:00 | 📢 Afternoon Open |
| 14:55 | 📢 Pre-close |
| 15:00 | 📊 Daily Summary |

### ☁️ Cloud Deployment

```bash
# Upload to server
scp stock-monitor-deploy.tar.gz root@server:/opt/

# Setup systemd auto-start
systemctl enable stock-monitor
systemctl start stock-monitor
```

---

<h2 id="中文文档">中文文档</h2>

### ✨ 功能特点

- 📱 **实时推送**：通过 Bark 推送到 iPhone（支持静音模式）
- 📊 **多维度监控**：日内涨跌、3/5/10/15日累计涨跌、成本盈亏
- ⏰ **定时提醒**：交易日内 5 次定时推送
- 💾 **数据持久化**：SQLite 数据库存储历史价格
- ☁️ **云服务器支持**：24小时不间断运行

### 🚀 快速开始

#### 1. 克隆并安装

```bash
git clone https://github.com/yourusername/stock-monitor.git
cd stock-monitor
pip3 install -r requirements.txt
```

#### 2. 配置

```bash
python3 setup.py
```

按提示输入 Bark Key 和自选股列表。

#### 3. 运行

```bash
python3 stock_monitor.py
```

### 📱 推送时间表

| 时间 | 类型 |
|------|------|
| 09:30 | 🌅 开盘提醒 |
| 11:25 | 📢 上午收盘 |
| 13:00 | 📢 下午开盘 |
| 14:55 | 📢 收盘前提醒 |
| 15:00 | 📊 全日总结 |

### ☁️ 云服务器部署

```bash
# 上传到服务器
scp stock-monitor-deploy.tar.gz root@server:/opt/

# 设置开机自启
systemctl enable stock-monitor
systemctl start stock-monitor
```

---

## Configuration / 配置说明

### Stock Code Format / 股票代码格式

| Exchange | Format | Example |
|----------|--------|---------|
| Shanghai (SSE) | `sh` + code | `sh518880` |
| Shenzhen (SZSE) | `sz` + code | `sz399006` |

### Example Config / 配置示例

```json
{
    "bark_key": "YOUR_BARK_KEY_HERE",
    "stocks": [
        {"code": "sh518880", "name": "Gold ETF / 黄金ETF", "cost_price": 9.125}
    ],
    "schedule": {
        "market_open": "09:30",
        "morning_end": "11:25",
        "afternoon_open": "13:00",
        "afternoon_remind": "14:55",
        "market_close": "15:00"
    }
}
```

---

## File Structure / 文件结构

```
stock-monitor/
├── stock_monitor.py      # Main program / 主程序
├── setup.py              # Setup wizard / 配置向导
├── config.example.json   # Example config / 示例配置
├── start.sh              # Start script / 启动脚本
├── test_install.py       # Test script / 测试脚本
└── README.md             # This file / 本文件
```

---

## License / 许可证

MIT License - See [LICENSE](LICENSE)

## Contributing / 贡献

Issues and Pull Requests are welcome! / 欢迎提交 Issue 和 Pull Request！

## Acknowledgments / 致谢

- [Bark](https://github.com/Finb/Bark) - iOS Push Service
- Sina Finance API / 新浪财经 API
- East Money API / 东方财富 API
