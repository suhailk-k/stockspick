"""
System Health Check
===================

Check if all dependencies and configurations are properly set up.
"""

import sys
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.9+")
        return False

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        'pandas', 'numpy', 'yfinance', 'ta', 'plotly', 
        'requests', 'dotenv', 'google.generativeai', 
        'schedule', 'fastapi', 'uvicorn', 'pydantic', 
        'streamlit', 'sqlalchemy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'dotenv':
                importlib.import_module('dotenv')
            elif package == 'google.generativeai':
                importlib.import_module('google.generativeai')
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_project_structure():
    """Check if project structure is correct."""
    required_files = [
        'src/trading_system/__init__.py',
        'src/trading_system/config.py',
        'src/trading_system/data_manager.py',
        'src/trading_system/technical_analysis.py',
        'src/trading_system/risk_manager.py',
        'src/trading_system/ai_analyzer.py',
        'src/trading_system/portfolio_manager.py',
        'src/trading_system/trading_engine.py',
        'main.py',
        'dashboard.py',
        '.env',
        'requirements.txt',
        'README.md'
    ]
    
    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing.append(file_path)
    
    return len(missing) == 0, missing

def check_configuration():
    """Check configuration files."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file missing")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        
        if 'GEMINI_API_KEY=' in content:
            if 'your_gemini_api_key_here' in content:
                print("⚠️  Gemini API key not set")
                return False
            else:
                print("✅ Gemini API key configured")
        
        if 'CAPITAL=' in content:
            print("✅ Trading capital configured")
        
        return True

def test_basic_functionality():
    """Test basic system functionality."""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from trading_system.config import TradingConfig
        from trading_system.data_manager import DataManager
        
        print("Testing configuration...")
        config = TradingConfig()
        print("✅ Configuration loaded")
        
        print("Testing data manager...")
        data_manager = DataManager(config)
        print("✅ Data manager initialized")
        
        print("Testing market status...")
        status = data_manager.get_market_status()
        print(f"✅ Market status: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Run all health checks."""
    print("🔍 System Health Check")
    print("="*50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", lambda: check_dependencies()[0]),
        ("Project Structure", lambda: check_project_structure()[0]),
        ("Configuration", check_configuration),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        print("-" * 30)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 HEALTH CHECK SUMMARY")
    print("="*50)
    
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:<20} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 System is ready!")
        print("You can now run the trading system.")
    else:
        print("\n⚠️  Please fix the issues above before proceeding.")
        
        # Show fix suggestions
        print("\n🔧 Suggested fixes:")
        for check_name, passed in results:
            if not passed:
                if check_name == "Dependencies":
                    print("• Run: pip install -r requirements.txt")
                elif check_name == "Configuration":
                    print("• Set your Gemini API key in .env file")
                elif check_name == "Project Structure":
                    print("• Ensure all project files are present")

if __name__ == "__main__":
    main()
