#!/usr/bin/env python3
"""
Stock Monitor - Windows Build Script
股票监测程序 - Windows 打包脚本
"""

import os
import sys
import shutil
import subprocess

def main():
    print("=" * 60)
    print("  📦 Stock Monitor - Windows Build")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}")
    
    # Create launcher script for Windows
    print("\n📝 Creating Windows launcher...")
    launcher_content = '''#!/usr/bin/env python3
"""
Stock Monitor - Windows Launcher
启动器：自动配置并运行程序
"""

import os
import sys
import json

def setup_config():
    """Setup configuration on first run"""
    config_file = "config.json"
    example_file = "config.example.json"
    
    if os.path.exists(config_file):
        return True
    
    print("=" * 60)
    print("  📈 Stock Monitor - First Time Setup")
    print("=" * 60)
    print("\\nWelcome! Let's configure the program.")
    print("欢迎！让我们配置程序。\\n")
    
    if not os.path.exists(example_file):
        print("❌ Error: config.example.json not found!")
        input("Press Enter to exit...")
        return False
    
    with open(example_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Get Bark Key
    print("Step 1: Bark Key")
    print("1. Download Bark App on your iPhone")
    print("2. Open app and copy your Bark Key")
    print()
    bark_key = input("Enter Bark Key: ").strip()
    if not bark_key:
        print("❌ Bark Key is required!")
        input("Press Enter to exit...")
        return False
    
    config['bark_key'] = bark_key
    
    # Get stocks
    print("\\nStep 2: Stock List")
    print("Format: CODE,NAME,COST_PRICE (cost optional)")
    print("Example: sh518880,Gold ETF,9.125")
    print("Type 'done' when finished\\n")
    
    stocks = []
    default_stocks = [
        ("sh518880", "Gold ETF"),
        ("sz161226", "Silver Fund"),
        ("sh512400", "Non-ferrous Metals ETF"),
        ("sz399006", "ChiNext Index")
    ]
    
    use_default = input("Use default stock list? (y/n): ").strip().lower()
    
    if use_default == 'y':
        stocks = [{"code": code, "name": name, "cost_price": 0} 
                  for code, name in default_stocks]
    else:
        while True:
            user_input = input("Stock (or 'done'): ").strip()
            if user_input.lower() == 'done':
                break
            parts = user_input.split(',')
            if len(parts) < 2:
                print("❌ Invalid format!")
                continue
            stocks.append({
                "code": parts[0].strip(),
                "name": parts[1].strip(),
                "cost_price": float(parts[2]) if len(parts) > 2 and parts[2].strip() else 0
            })
    
    if not stocks:
        stocks = [{"code": code, "name": name, "cost_price": 0} 
                  for code, name in default_stocks]
    
    config['stocks'] = stocks
    
    # Save config
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    print("\\n✅ Configuration saved!")
    print("Starting program...\\n")
    return True

if __name__ == "__main__":
    if setup_config():
        # Import and run main program
        import stock_monitor
        stock_monitor.main()
    else:
        sys.exit(1)
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # Build
    print("\n🔨 Building Windows executable...")
    print("This may take a few minutes...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",           # Single executable file
            "--windowed",          # No console window
            "--name", "StockMonitor",
            "--add-data", "config.example.json;.",
            "--hidden-import", "schedule",
            "--hidden-import", "requests",
            "--hidden-import", "sqlite3",
            "--clean",
            "--noconfirm",
            "launcher.py"
        ], check=True)
        
        print("\n" + "=" * 60)
        print("  ✅ Build Successful!")
        print("=" * 60)
        print("\n📦 Output: dist/StockMonitor.exe")
        print("\nPackage contents:")
        print("  - StockMonitor.exe (main program)")
        print("  - config.json (will be created on first run)")
        print("  - stock_data.db (database)")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
