#!/usr/bin/env python3
"""
Stock Monitor - Installation Test Script
股票监测程序 - 安装测试脚本
"""

import sys
import json

def test_imports():
    """Test if required packages are installed / 测试依赖是否安装"""
    print("Testing dependencies / 测试依赖安装...")
    try:
        import requests
        import schedule
        print("✅ requests installed / 已安装")
        print("✅ schedule installed / 已安装")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency / 缺少依赖: {e}")
        print("\nPlease run / 请运行: pip3 install -r requirements.txt")
        return False

def test_config():
    """Test configuration file / 测试配置文件"""
    print("\nTesting configuration / 测试配置文件...")
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check required fields / 检查必要字段
        required = ['bark_key', 'stocks', 'schedule']
        for field in required:
            if field not in config:
                print(f"❌ Missing field / 缺少字段: {field}")
                return False
        
        # Check bark_key / 检查 bark_key
        if config['bark_key'] == 'YOUR_BARK_KEY_HERE / 在此处填写你的Bark Key':
            print("⚠️  Bark Key not configured / Bark Key 未配置")
            return False
        
        print(f"✅ Bark Key: {config['bark_key'][:10]}...")
        print(f"✅ Stocks count / 自选股数量: {len(config['stocks'])}")
        
        for stock in config['stocks']:
            print(f"   - {stock['name']} ({stock['code']})")
        
        return True
        
    except FileNotFoundError:
        print("❌ Config file not found / 配置文件不存在")
        print("   Please run / 请运行: python3 setup.py")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format / JSON格式错误: {e}")
        return False

def test_bark():
    """Test Bark push notification / 测试 Bark 推送"""
    print("\nTesting Bark push / 测试 Bark 推送...")
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        bark_key = config.get('bark_key', '')
        if bark_key == 'YOUR_BARK_KEY_HERE / 在此处填写你的Bark Key':
            print("⚠️  Bark Key not configured, skipping test / Bark Key 未配置，跳过测试")
            return True
        
        import requests
        
        title = "📱 Stock Monitor Test / 股票监测测试"
        body = "If you receive this, setup is successful!\n如果收到这条消息，说明配置成功！"
        
        url = f'https://api.day.app/{bark_key}/{title}/{body}?sound=none'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Test push sent, check your phone / 测试推送已发送，请检查手机")
            return True
        else:
            print(f"⚠️  Push failed / 推送失败 (status: {response.status_code})")
            print("   Please check your Bark Key / 请检查 Bark Key 是否正确")
            return False
            
    except Exception as e:
        print(f"⚠️  Test push failed / 测试推送失败: {e}")
        return True  # Don't block installation / 不阻断安装流程

def main():
    print("=" * 60)
    print("  📈 Stock Monitor - Installation Test")
    print("  📈 股票监测程序 - 安装测试")
    print("=" * 60)
    
    all_pass = True
    
    all_pass &= test_imports()
    all_pass &= test_config()
    test_bark()  # Non-blocking / 不阻断流程
    
    print("\n" + "=" * 60)
    if all_pass:
        print("  ✅ All tests passed! You can now run the program.")
        print("  ✅ 测试通过！可以运行程序了。")
        print("=" * 60)
        print("\nRun command / 运行命令:")
        print("  python3 stock_monitor.py")
        return 0
    else:
        print("  ❌ Tests failed. Please check the errors above.")
        print("  ❌ 测试未通过，请检查上述错误。")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
