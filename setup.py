#!/usr/bin/env python3
"""
Stock Monitor - Configuration Wizard
股票监测程序 - 配置向导
"""

import os
import json
import sys

def main():
    print("=" * 60)
    print("  📈 Stock Monitor - Setup Wizard")
    print("  📈 股票监测程序 - 配置向导")
    print("=" * 60)
    
    # Check if config file exists / 检查配置文件是否存在
    config_file = "config.json"
    example_file = "config.example.json"
    
    if os.path.exists(config_file):
        print(f"\n✅ Config file exists / 配置文件已存在: {config_file}")
        overwrite = input("Reconfigure? / 重新配置? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Exiting / 退出")
            return
    
    # Read example config / 读取示例配置
    if not os.path.exists(example_file):
        print(f"\n❌ Example config not found / 示例配置不存在: {example_file}")
        sys.exit(1)
    
    with open(example_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("\n" + "-" * 60)
    print("Step 1: Bark Key / 步骤1：Bark Key")
    print("-" * 60)
    print("1. Download Bark App from App Store / 从 App Store 下载 Bark App")
    print("2. Open app, tap + to add server / 打开 App，点击 + 添加服务器")
    print("3. Copy Bark Key from URL / 从 URL 中复制 Bark Key")
    print()
    
    bark_key = input("Enter Bark Key / 输入 Bark Key: ").strip()
    if not bark_key:
        print("❌ Bark Key is required / Bark Key 不能为空")
        sys.exit(1)
    
    config['bark_key'] = bark_key
    
    print("\n" + "-" * 60)
    print("Step 2: Stock List / 步骤2：自选股列表")
    print("-" * 60)
    print("Format: CODE,NAME,COST_PRICE (cost optional)")
    print("格式：代码,名称,成本价（成本价可选）")
    print("Type 'done' when finished / 输入 'done' 完成")
    print()
    
    stocks = []
    default_stocks = [
        ("sh518880", "Gold ETF / 黄金ETF"),
        ("sh512400", "Non-ferrous Metals ETF / 有色金属ETF"),
        ("sz161226", "Silver Fund / 国投白银LOF"),
        ("sz399006", "ChiNext Index / 创业板指")
    ]
    
    print("Default stocks / 默认股票列表:")
    for i, (code, name) in enumerate(default_stocks, 1):
        print(f"  {i}. {code} - {name}")
    
    use_default = input("\nUse defaults / 使用默认? (y/n): ").strip().lower()
    
    if use_default == 'y':
        stocks = [{"code": code, "name": name.split(" / ")[0], "cost_price": 0} 
                  for code, name in default_stocks]
    else:
        while True:
            user_input = input("\nStock / 股票 (CODE,NAME,COST): ").strip()
            if user_input.lower() == 'done':
                break
            
            parts = user_input.split(',')
            if len(parts) < 2:
                print("❌ Invalid format / 格式错误。Use: CODE,NAME,COST")
                continue
            
            code = parts[0].strip()
            name = parts[1].strip()
            cost_price = float(parts[2].strip()) if len(parts) > 2 and parts[2].strip() else 0
            
            stocks.append({
                "code": code,
                "name": name,
                "cost_price": cost_price
            })
            print(f"✅ Added / 已添加: {name} ({code})")
    
    if not stocks:
        print("⚠️ No stocks added, using defaults / 未添加股票，使用默认")
        stocks = [{"code": code, "name": name.split(" / ")[0], "cost_price": 0} 
                  for code, name in default_stocks]
    
    config['stocks'] = stocks
    
    # Save config / 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    print("\n" + "=" * 60)
    print("  ✅ Setup Complete / 配置完成!")
    print("=" * 60)
    print(f"\nConfig saved to / 配置已保存: {config_file}")
    print("\nYou can now / 你现在可以:")
    print(f"  1. Run / 运行: python3 stock_monitor.py")
    print(f"  2. Edit config / 修改配置: {config_file}")
    print("\nHappy investing! / 祝你投资顺利！📈")

if __name__ == "__main__":
    main()
