#!/usr/bin/env python3
"""
Stock Monitor - macOS Build Script
股票监测程序 - macOS 打包脚本
"""

import os
import sys
import shutil
import subprocess

def main():
    print("=" * 60)
    print("  📦 Stock Monitor - macOS Build")
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
    for folder in ['build', 'dist', 'StockMonitor.app']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Removed {folder}")
    
    # Create spec file
    print("\n📝 Creating build configuration...")
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['stock_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[('config.example.json', '.')],
    hiddenimports=['schedule', 'requests', 'sqlite3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StockMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

app = BUNDLE(
    exe,
    name='StockMonitor.app',
    icon=None,
    bundle_identifier='com.aiyusherry.stockmonitor',
)
'''
    
    with open('StockMonitor.spec', 'w') as f:
        f.write(spec_content)
    
    # Build
    print("\n🔨 Building macOS app...")
    print("This may take a few minutes...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "StockMonitor.spec",
            "--clean",
            "--noconfirm"
        ], check=True)
        
        print("\n" + "=" * 60)
        print("  ✅ Build Successful!")
        print("=" * 60)
        print("\n📦 Output: dist/StockMonitor.app")
        print("\nTo package for distribution:")
        print("  cd dist && zip -r StockMonitor-mac.zip StockMonitor.app")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
