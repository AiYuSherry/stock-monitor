# 📦 Download & Install / 下载与安装

**English** | **中文**

---

## 🚀 Quick Start / 快速开始

No Python installation required! Just download and run.

无需安装 Python！下载即可运行。

---

## macOS

### Download / 下载

Download `StockMonitor-mac.zip` from [Releases](../../releases)

从 [Releases](../../releases) 下载 `StockMonitor-mac.zip`

### Install / 安装

1. **Unzip** / 解压
   ```bash
   unzip StockMonitor-mac.zip
   ```

2. **Run** / 运行
   - Double-click `StockMonitor.app`
   - 双击 `StockMonitor.app`

3. **First Time Setup** / 首次配置
   - Enter your Bark Key
   - 输入你的 Bark Key
   - Select stocks to monitor
   - 选择要监测的股票

4. **Done!** / 完成！
   - The program will start monitoring automatically
   - 程序将自动开始监测

### Note / 注意事项

If you see "Cannot open because it's from an unidentified developer":

如果提示"无法打开，因为来自未识别的开发者"：

1. Right-click (or Control+click) the app
2. Select "Open"
3. Click "Open" in the dialog

---

## Windows

### Download / 下载

Download `StockMonitor-windows.zip` from [Releases](../../releases)

从 [Releases](../../releases) 下载 `StockMonitor-windows.zip`

### Install / 安装

1. **Unzip** / 解压
   - Right-click the zip file → "Extract All"
   - 右键 zip 文件 → "解压全部"

2. **Run** / 运行
   - Double-click `StockMonitor.exe`
   - 双击 `StockMonitor.exe`

3. **First Time Setup** / 首次配置
   - A black window will appear for configuration
   - 会弹出黑色窗口进行配置
   - Enter your Bark Key and stock list
   - 输入 Bark Key 和自选股列表

4. **Done!** / 完成！
   - The program will run in the background
   - 程序将在后台运行
   - You'll receive push notifications on your iPhone
   - 你将在 iPhone 上收到推送通知

### Note / 注意事项

- Windows may show a security warning. Click "More info" → "Run anyway"
- Windows 可能会显示安全警告，点击"更多信息" → "仍要运行"

---

## 🛠️ Build from Source / 从源码构建

If you prefer to build from source:

如果你更喜欢从源码构建：

### Prerequisites / 前置要求

```bash
pip3 install pyinstaller
```

### macOS Build / macOS 构建

```bash
python3 build_mac.py
```

Output: `dist/StockMonitor.app`

### Windows Build / Windows 构建

```bash
python3 build_windows.py
```

Output: `dist/StockMonitor.exe`

---

## 📱 After Installation / 安装后

Once configured, the program will:

配置完成后，程序将：

1. **Monitor your stocks** 24/7
   全天候监测你的股票

2. **Send push notifications** at:
   在以下时间发送推送：
   - 09:30 - Market Open / 开盘
   - 11:25 - Morning Close / 上午收盘
   - 13:00 - Afternoon Open / 下午开盘
   - 14:55 - Pre-close / 收盘前
   - 15:00 - Daily Summary / 全日总结

3. **Track profit/loss** based on your cost price
   根据成本价追踪盈亏

---

## 🔧 Troubleshooting / 故障排除

### macOS: "App is damaged" / 应用已损坏

Run in Terminal / 在终端运行：
```bash
xattr -cr /Applications/StockMonitor.app
```

### Windows: Antivirus blocks the app / 杀毒软件拦截

Add the app to your antivirus whitelist:
将应用添加到杀毒软件白名单

### Cannot receive notifications / 无法收到通知

1. Check your Bark Key is correct
   检查 Bark Key 是否正确
2. Ensure Bark App is installed on your iPhone
   确保 iPhone 上安装了 Bark App
3. Check your internet connection
   检查网络连接

---

## 💡 Tips / 提示

- The configuration file is saved as `config.json` in the same folder
  配置文件保存在同一文件夹的 `config.json`
- You can edit it anytime to change stocks or settings
  可以随时编辑修改股票或设置
- The database is saved as `stock_data.db`
  数据库保存在 `stock_data.db`

---

**Enjoy your stock monitoring!** / **祝你投资顺利！** 📈
