#!/usr/bin/env python3
"""
Stock Monitor - macOS Launcher
macOS 启动器：自动配置并运行
"""

import os
import sys
import json

def setup_config():
    """首次运行自动配置"""
    config_file = "config.json"
    example_file = "config.example.json"
    
    if os.path.exists(config_file):
        return True
    
    print("=" * 60)
    print("  📈 Stock Monitor - First Time Setup / 首次配置")
    print("=" * 60)
    print("\nWelcome! Let's configure the program. / 欢迎！让我们配置程序。\n")
    
    if not os.path.exists(example_file):
        print("❌ Error: config.example.json not found! / 错误：示例配置不存在！")
        input("Press Enter to exit...")
        return False
    
    with open(example_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Bark Key
    print("Step 1: Bark Key / 步骤1：Bark Key")
    print("1. Download Bark App / 下载 Bark App")
    print("2. Copy your Bark Key / 复制你的 Bark Key")
    print()
    bark_key = input("Enter Bark Key / 输入 Bark Key: ").strip()
    if not bark_key:
        print("❌ Bark Key is required! / Bark Key 不能为空！")
        input("Press Enter to exit...")
        return False
    
    config['bark_key'] = bark_key
    
    # Stocks
    print("\nStep 2: Stock List / 步骤2：自选股")
    print("Format: CODE,NAME,COST / 格式：代码,名称,成本价")
    print("Type 'done' when finished / 输入 'done' 完成\n")
    
    stocks = []
    default_stocks = [
        ("sh518880", "Gold ETF / 黄金ETF"),
        ("sz161226", "Silver Fund / 国投白银LOF"),
        ("sh512400", "Non-ferrous Metals ETF / 有色金属ETF"),
        ("sz399006", "ChiNext Index / 创业板指")
    ]
    
    use_default = input("Use defaults? / 使用默认? (y/n): ").strip().lower()
    
    if use_default == 'y':
        stocks = [{"code": code, "name": name.split(" / ")[0], "cost_price": 0} 
                  for code, name in default_stocks]
    else:
        while True:
            user_input = input("Stock / 股票 (or 'done'): ").strip()
            if user_input.lower() == 'done':
                break
            parts = user_input.split(',')
            if len(parts) < 2:
                print("❌ Invalid format! / 格式错误！")
                continue
            stocks.append({
                "code": parts[0].strip(),
                "name": parts[1].strip(),
                "cost_price": float(parts[2]) if len(parts) > 2 and parts[2].strip() else 0
            })
    
    if not stocks:
        stocks = [{"code": code, "name": name.split(" / ")[0], "cost_price": 0} 
                  for code, name in default_stocks]
    
    config['stocks'] = stocks
    
    # Save
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    print("\n✅ Configuration saved! / 配置已保存！")
    print("Starting program... / 启动程序...\n")
    return True

def main():
    """Main entry point"""
    if setup_config():
        # Import and run main program
        import stock_monitor
        stock_monitor.main()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
