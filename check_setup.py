#!/usr/bin/env python3
"""
Setup Check - Verify your trading system is ready
=================================================

This script checks if all requirements are met for analyzing today's trades.
"""

import sys
import os
from pathlib import Path

def check_setup():
    """Check if the trading system is properly set up."""
    print("🔧 TRADING SYSTEM SETUP CHECK")
    print("="*50)
    
    issues = []
    
    # Check Python version
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        issues.append("❌ Python 3.8+ required")
    else:
        print("✅ Python version OK")
    
    # Check required files
    required_files = [
        'requirements.txt',
        'src/trading_system/__init__.py',
        'src/trading_system/config.py',
        'src/trading_system/data_manager.py',
        'src/trading_system/technical_analysis.py',
        'src/trading_system/risk_manager.py',
        'src/trading_system/ai_analyzer.py',
        'main.py',
        'analyze_today.py',
        'quick_screen.py'
    ]
    
    print(f"\n📁 Checking required files...")
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            issues.append(f"Missing file: {file}")
    
    # Check environment file
    print(f"\n🔐 Environment Configuration...")
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'GEMINI_API_KEY=' in env_content:
                if 'your_gemini_api_key_here' in env_content:
                    print("⚠️  Gemini API key needs to be configured")
                    issues.append("Configure GEMINI_API_KEY in .env file")
                else:
                    print("✅ Gemini API key configured")
            else:
                print("⚠️  GEMINI_API_KEY not found in .env")
                issues.append("Add GEMINI_API_KEY to .env file")
    else:
        print("❌ .env file missing")
        issues.append("Create .env file with GEMINI_API_KEY")
    
    # Try importing key modules
    print(f"\n📦 Checking Python packages...")
    try:
        import pandas
        print(f"✅ pandas {pandas.__version__}")
    except ImportError:
        print("❌ pandas not installed")
        issues.append("Install packages: pip install -r requirements.txt")
    
    try:
        import yfinance
        print(f"✅ yfinance {yfinance.__version__}")
    except ImportError:
        print("❌ yfinance not installed")
        issues.append("Install packages: pip install -r requirements.txt")
    
    try:
        import ta
        print(f"✅ ta (technical analysis)")
    except ImportError:
        print("❌ ta not installed")
        issues.append("Install packages: pip install -r requirements.txt")
    
    # Test internet connection
    print(f"\n🌐 Testing internet connection...")
    try:
        import requests
        response = requests.get('https://finance.yahoo.com', timeout=5)
        if response.status_code == 200:
            print("✅ Internet connection OK")
        else:
            print("⚠️  Yahoo Finance may be blocked")
            issues.append("Check internet connection to Yahoo Finance")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        issues.append("Check internet connection")
    
    # Summary
    print(f"\n📊 SETUP SUMMARY")
    print("="*50)
    
    if not issues:
        print("🎉 All checks passed! Your system is ready.")
        print("\n🚀 To start analyzing today's trades:")
        print("   python analyze_today.py")
        print("   python quick_screen.py")
        print("   python main.py analyze")
    else:
        print(f"❌ Found {len(issues)} issues to fix:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 QUICK FIX COMMANDS:")
        if any("Install packages" in issue for issue in issues):
            print("   pip install -r requirements.txt")
        
        if any("GEMINI_API_KEY" in issue for issue in issues):
            print("   Edit .env file and add your Gemini API key:")
            print("   GEMINI_API_KEY=your_actual_api_key_here")
            print("\n   Get free API key: https://makersuite.google.com/app/apikey")
    
    print(f"\n💡 Need help? Check README.md for detailed setup instructions.")


if __name__ == "__main__":
    check_setup()
