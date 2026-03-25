# 📦 Download & Install / 下载与安装

**English** | **中文**

---

## 🚀 Quick Start / 快速开始

No Python installation required! Just download and run.

无需安装 Python！下载即可运行。

---

## 📥 Download Links / 下载链接

| Version | macOS | Windows | Date |
|---------|-------|---------|------|
| **v1.0.0** | [StockMonitor-mac.zip](https://github.com/AiYuSherry/stock-monitor/releases/download/v1.0.0/StockMonitor-mac.zip) (17MB) | Build from source | 2026-03-25 |

📋 [View All Releases](../../releases)

---

## macOS

### System Requirements / 系统要求

- macOS 10.15 (Catalina) or later
- Intel or Apple Silicon (M1/M2/M3)

### Install & Run / 安装与运行

1. **Download** / 下载
   ```bash
   curl -L -o StockMonitor-mac.zip https://github.com/AiYuSherry/stock-monitor/releases/download/v1.0.0/StockMonitor-mac.zip
   ```
   Or click the link above / 或直接点击上方链接

2. **Unzip** / 解压
   ```bash
   unzip StockMonitor-mac.zip
   ```
   Or double-click the zip file / 或双击 zip 文件

3. **Run** / 运行
   - Double-click `StockMonitor.app`
   - 双击 `StockMonitor.app`

4. **First Time Setup** / 首次配置
   - A terminal window will appear
   - 会弹出终端窗口
   - Enter your Bark Key (get from Bark App on iPhone)
   - 输入 Bark Key（从 iPhone 上的 Bark App 获取）
   - Select stocks to monitor or use defaults
   - 选择要监测的股票或使用默认列表

5. **Done!** / 完成！
   - The program runs in the background
   - 程序在后台运行
   - You'll receive push notifications on your iPhone
   - 你将在 iPhone 上收到推送通知

### Troubleshooting / 故障排除

#### "Cannot open because it's from an unidentified developer"
**"无法打开，因为来自未识别的开发者"**

1. Right-click (or Control+click) the app / 右键（或 Control+点击）应用
2. Select "Open" / 选择"打开"
3. Click "Open" in the dialog / 在对话框中点击"打开"

Or run in Terminal / 或在终端运行：
```bash
xattr -cr StockMonitor.app
```

#### "App is damaged"
**"应用已损坏"**

```bash
xattr -cr /Applications/StockMonitor.app
```

---

## Windows

### Status / 状态

✅ **Auto-build via GitHub Actions**

Windows version is automatically built by GitHub Actions for every release.

Windows 版本由 GitHub Actions 自动构建。

### Download / 下载

Download directly from the [Releases](../../releases) page:
- `StockMonitor-windows.zip` (~12MB)

直接从 [Releases](../../releases) 页面下载：
- `StockMonitor-windows.zip` (~12MB)

### Install & Run / 安装与运行

1. **Download** / 下载
   ```bash
   curl -L -o StockMonitor-windows.zip https://github.com/AiYuSherry/stock-monitor/releases/latest/download/StockMonitor-windows.zip
   ```
   Or click the link on the releases page / 或直接点击发布页面链接

2. **Extract** / 解压
   - Right-click the zip file → "Extract All"
   - 右键 zip 文件 → "解压全部"

3. **Run** / 运行
   - Double-click `StockMonitor.exe`
   - 双击 `StockMonitor.exe`

4. **First Time Setup** / 首次配置
   - A terminal window will appear for configuration
   - 会弹出终端窗口进行配置
   - Enter your Bark Key and select stocks
   - 输入 Bark Key 和选择股票

5. **Done!** / 完成！
   - The program runs in the background
   - 程序在后台运行

---

## 🛠️ Advanced: Build from Source / 高级：从源码构建

### Prerequisites / 前置要求

```bash
pip3 install pyinstaller
```

### macOS Build / macOS 构建

```bash
python3 build_mac.py
```

Output: `dist/StockMonitor.app`

Package for distribution / 打包分发：
```bash
cd dist && zip -r StockMonitor-mac.zip StockMonitor.app
```

### Windows Build / Windows 构建

```bash
python build_windows.py
```

Output: `dist/StockMonitor.exe`

---

## 📱 After Installation / 安装后

Once configured, the program will:

配置完成后，程序将：

### Automatic Monitoring / 自动监测

1. **Monitor your stocks** 24/7 / 全天候监测你的股票

2. **Send push notifications** at: / 在以下时间发送推送：
   | Time | Event |
   |------|-------|
   | 09:30 | 🌅 Market Open / 开盘 |
   | 11:25 | 📢 Morning Close / 上午收盘 |
   | 13:00 | 📢 Afternoon Open / 下午开盘 |
   | 14:55 | 📢 Pre-close / 收盘前 |
   | 15:00 | 📊 Daily Summary / 全日总结 |

3. **Track profit/loss** based on your cost price / 根据成本价追踪盈亏

### Data Files / 数据文件

The program creates these files in the same folder:

程序会在同一文件夹创建以下文件：

| File | Description |
|------|-------------|
| `config.json` | Your configuration / 你的配置 |
| `stock_data.db` | Historical price database / 历史价格数据库 |
| `stock_monitor.log` | Program logs / 程序日志 |

### Modifying Configuration / 修改配置

Simply edit `config.json` to:
- Change stocks / 更改股票
- Update Bark Key / 更新 Bark Key
- Adjust alert thresholds / 调整告警阈值

No restart needed - changes take effect immediately!

无需重启 - 更改立即生效！

---

## 🔧 Troubleshooting / 故障排除

### Cannot receive notifications / 无法收到通知

1. Check your Bark Key is correct in `config.json`
   检查 `config.json` 中的 Bark Key 是否正确

2. Ensure Bark App is installed on your iPhone
   确保 iPhone 上安装了 Bark App

3. Check your internet connection
   检查网络连接

4. Check the log file `stock_monitor.log`
   检查日志文件 `stock_monitor.log`

### Program crashes / 程序崩溃

1. Check `stock_monitor.log` for error messages
   检查 `stock_monitor.log` 中的错误信息

2. Ensure `config.json` is valid JSON
   确保 `config.json` 是有效的 JSON 格式

3. Try deleting `config.json` and reconfiguring
   尝试删除 `config.json` 并重新配置

---

## 💡 Tips / 提示

- **Silent mode**: Default is silent push (no sound). Change `bark_sound` in config to enable sound.
  - 默认静音推送（无声音）。在配置中更改 `bark_sound` 可启用声音。

- **Trading days only**: Set `trading_days_only: false` to run every day
  - 设置 `trading_days_only: false` 可每天运行（不仅交易日）

- **Multiple stocks**: You can monitor unlimited stocks
  - 可以监测无限数量的股票

- **Cost tracking**: Set `cost_price` to track your profit/loss
  - 设置 `cost_price` 可追踪你的盈亏

---

**Enjoy your stock monitoring!** / **祝你投资顺利！** 📈
