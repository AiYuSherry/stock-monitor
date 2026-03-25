# 📈 Stock Monitor / 股票监测程序

**English** | [中文](#中文文档)

A Python-based stock monitoring program that tracks stock/ETF prices in real-time and pushes notifications to your phone via Bark.

基于 Python 的股票监测程序，支持实时监控股票/ETF价格，并通过 Bark 推送到手机。

---

## 📥 Download / 下载

**No installation required!** Download and run directly.

**无需安装 Python！**下载直接运行。

| Platform | Download | Size | Status |
|----------|----------|------|--------|
| **macOS** | [StockMonitor-mac.zip](https://github.com/AiYuSherry/stock-monitor/releases/latest/download/StockMonitor-mac.zip) | ~17MB | ✅ Available |
| **Windows** | [StockMonitor-windows.zip](https://github.com/AiYuSherry/stock-monitor/releases/latest/download/StockMonitor-windows.zip) | ~12MB | ✅ Auto-build |

📖 [Installation Guide / 安装指南](RELEASES.md)

> **Auto-build:** Windows version is automatically built by GitHub Actions. Download directly from the link above.
>
> **自动构建：** Windows 版本由 GitHub Actions 自动构建。直接点击上方链接下载即可。

---

## 🚀 Quick Start / 快速开始

### For End Users / 对于最终用户

1. **Download** / 下载
   - Click the download link above for your platform
   - 点击上方对应平台的下载链接

2. **Unzip** / 解压
   - macOS: Double-click the zip file
   - macOS: 双击 zip 文件解压

3. **Run** / 运行
   - macOS: Double-click `StockMonitor.app`
   - macOS: 双击 `StockMonitor.app`

4. **Configure** / 配置
   - First run will prompt for Bark Key and stock list
   - 首次运行会提示输入 Bark Key 和自选股列表

5. **Done!** / 完成！
   - The program will start monitoring automatically
   - 程序将自动开始监测，推送通知到手机

### For Developers / 对于开发者

```bash
git clone https://github.com/AiYuSherry/stock-monitor.git
cd stock-monitor
pip3 install -r requirements.txt
python3 stock_monitor.py
```

---

## English Documentation

### ✨ Features

- 📱 **Real-time Push Notifications**: Push to iPhone via Bark (supports silent mode)
- 📊 **Multi-dimensional Monitoring**: Intraday, 3/5/10/15 day changes, cost-based P/L
- ⏰ **Scheduled Alerts**: 5 push notifications throughout the trading day
- 💾 **Data Persistence**: SQLite database for historical prices
- ☁️ **Cloud Server Support**: 24/7 operation on cloud servers
- 🔧 **Easy Configuration**: First-run setup wizard

### 📱 Push Schedule

| Time | Type | Description |
|------|------|-------------|
| 09:30 | 🌅 Market Open | Opening prices and initial status |
| 11:25 | 📢 Morning Close | Morning session summary |
| 13:00 | 📢 Afternoon Open | Afternoon session start |
| 14:55 | 📢 Pre-close | Pre-market close reminder |
| 15:00 | 📊 Daily Summary | Full day summary with historical data |

---

<h2 id="中文文档">中文文档</h2>

### ✨ 功能特点

- 📱 **实时推送**：通过 Bark 推送到 iPhone（支持静音模式）
- 📊 **多维度监控**：日内涨跌、3/5/10/15日累计涨跌、成本盈亏
- ⏰ **定时提醒**：交易日内 5 次定时推送
- 💾 **数据持久化**：SQLite 数据库存储历史价格
- ☁️ **云服务器支持**：24小时不间断运行
- 🔧 **轻松配置**：首次运行配置向导

### 📱 推送时间表

| 时间 | 类型 | 说明 |
|------|------|------|
| 09:30 | 🌅 开盘提醒 | 开盘价和初始状态 |
| 11:25 | 📢 上午收盘 | 上午盘总结 |
| 13:00 | 📢 下午开盘 | 下午盘开始 |
| 14:55 | 📢 收盘前提醒 | 收盘前提醒 |
| 15:00 | 📊 全日总结 | 包含历史数据的全日总结 |

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
├── launcher_mac.py       # macOS launcher / macOS 启动器
├── build_mac.py          # macOS build script / macOS 构建脚本
├── build_windows.py      # Windows build script / Windows 构建脚本
├── config.example.json   # Example config / 示例配置
├── start.sh              # Start script / 启动脚本
├── test_install.py       # Test script / 测试脚本
├── README.md             # This file / 本文件
└── RELEASES.md           # Release notes / 发布说明
```

---

## Building from Source / 从源码构建

### macOS

```bash
pip3 install pyinstaller
python3 build_mac.py
# Output: dist/StockMonitor.app
```

### Windows

```bash
pip3 install pyinstaller
python3 build_windows.py
# Output: dist/StockMonitor.exe
```

---

## License / 许可证

MIT License - See [LICENSE](LICENSE)

## Contributing / 贡献

Issues and Pull Requests are welcome! / 欢迎提交 Issue 和 Pull Request！

Contributions especially welcome for:
- Windows pre-built binary
- Additional stock market support
- UI improvements

特别欢迎以下贡献：
- Windows 预构建版本
- 支持更多股市
- 界面改进

## Acknowledgments / 致谢

- [Bark](https://github.com/Finb/Bark) - iOS Push Service
- Sina Finance API / 新浪财经 API
- East Money API / 东方财富 API
