"""
Quick Start Guide - Swing Trading System
=========================================

This script helps you get started with the trading system.
"""

import os
import sys
from pathlib import Path

def print_banner():
    print("🎯 Swing Trading System for Indian Stocks")
    print("="*60)
    print("Enterprise-grade trading system with AI analysis")
    print("="*60)

def check_environment():
    """Check if environment is properly set up."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Check for Gemini API key
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_gemini_api_key_here' in content:
            print("⚠️  Please set your Gemini API key in .env file")
            print("   Edit .env and replace 'your_gemini_api_key_here' with your actual API key")
            return False
    
    print("✅ Environment configured")
    return True

def show_options():
    """Show available options."""
    print("\n📋 Available Commands:")
    print("-" * 30)
    print("1. 🧪 Run Demo           - python demo.py")
    print("2. 📊 Daily Analysis     - python main.py analyze")
    print("3. 🎯 Analyze Stock      - python main.py stock RELIANCE.NS")
    print("4. 💼 Monitor Portfolio  - python main.py monitor")
    print("5. 🌐 Launch Dashboard   - python main.py dashboard")
    print("6. 🌐 Direct Dashboard   - streamlit run dashboard.py")

def get_api_key_instructions():
    """Show instructions for getting Gemini API key."""
    print("\n🔑 How to get Gemini API Key:")
    print("-" * 30)
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Click 'Create API key'")
    print("3. Copy the generated key")
    print("4. Open .env file and replace 'your_gemini_api_key_here' with your key")
    print("5. Save the file and restart the system")

def main():
    print_banner()
    
    # Check environment
    if not check_environment():
        get_api_key_instructions()
        return
    
    # Show options
    show_options()
    
    print("\n🚀 Quick Start:")
    print("-" * 15)
    print("For beginners: python demo.py")
    print("For analysis:  python main.py analyze")
    print("For dashboard: python main.py dashboard")
    
    print("\n📚 Documentation:")
    print("-" * 17)
    print("Full guide: README.md")
    print("Configuration: .env file")
    
    print("\n⚠️  Important Notes:")
    print("-" * 17)
    print("• This is for educational purposes only")
    print("• Not financial advice")
    print("• Always do your own research")
    print("• Start with paper trading")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
