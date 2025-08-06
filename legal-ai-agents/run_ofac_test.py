#!/usr/bin/env python3
"""
Quick OFAC Integration Test Runner

This script sets up and runs the OFAC integration test to verify
the Compliance Checker Agent works with real OFAC sanctions data.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'requests',
        'aiohttp', 
        'xml.etree.ElementTree',  # Built-in
        'sqlite3',  # Built-in
        'asyncio'   # Built-in
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package in ['xml.etree.ElementTree', 'sqlite3', 'asyncio']:
                # These are built-in modules
                __import__(package.split('.')[0])
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print(f"📦 Please install them with: pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required dependencies are installed")
    return True

def run_ofac_test():
    """Run the OFAC integration test"""
    print("🚀 Starting OFAC Integration Test...")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before running the test.")
        print("💡 You can install all dependencies with: pip install -r requirements.txt")
        return False
    
    # Set up environment
    project_root = Path(__file__).parent
    test_script = project_root / "examples" / "test_ofac_integration.py"
    
    if not test_script.exists():
        print(f"❌ Test script not found: {test_script}")
        return False
    
    # Run the test
    try:
        print(f"🔧 Running test script: {test_script}")
        result = subprocess.run([
            sys.executable, str(test_script)
        ], cwd=project_root, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n🎉 OFAC Integration Test completed successfully!")
            return True
        else:
            print(f"\n❌ Test failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main function"""
    print("🏛️ OFAC Integration Test Runner")
    print("Testing Compliance Checker Agent with Real OFAC Sanctions Data")
    print("=" * 70)
    
    print("\n📋 What this test will do:")
    print("   1. Download real OFAC SDN list (XML format)")
    print("   2. Download OFAC crypto addresses (JSON format)")
    print("   3. Parse and store sanctions data in local database")
    print("   4. Test sanctions screening with known entities")
    print("   5. Test crypto address screening")
    print("   6. Run a complete compliance workflow")
    print("   7. Generate a comprehensive test report")
    
    print("\n⚠️ Important notes:")
    print("   - This test uses real OFAC data from treasury.gov")
    print("   - Internet connection required for data download")
    print("   - Test may take 30-60 seconds to complete")
    print("   - No API keys required for this test")
    
    # Ask for confirmation
    try:
        response = input("\n🔄 Do you want to proceed? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Test cancelled.")
            return
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return
    
    # Run the test
    success = run_ofac_test()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Review the test results above")
        print("   2. Check if sanctions screening worked as expected")
        print("   3. Verify database was populated with OFAC data")
        print("   4. Test with your own entities using the agent")
    else:
        print("\n❌ Test failed!")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Verify all dependencies are installed")
        print("   3. Check the error messages above")
        print("   4. Try running: pip install -r requirements.txt")

if __name__ == "__main__":
    main()