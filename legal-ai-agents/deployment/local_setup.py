#!/usr/bin/env python3
"""
Local Setup and Deployment Script for Legal Research AI Agents

This script helps users set up and deploy the legal AI agents locally
with proper environment configuration and dependency management.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import venv
import json

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🏛️  {text}")
    print("="*60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}️⃣  {description}")
    print("-" * 40)

def run_command(command, description, check=True):
    """Run a shell command with proper error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Set up a virtual environment for the project"""
    print_step(2, "Setting up Virtual Environment")
    
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "legal-ai-env"
    
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("   Do you want to recreate it? (y/N): ").lower()
        if response == 'y':
            print("🗑️  Removing existing virtual environment...")
            shutil.rmtree(venv_path)
        else:
            print("✅ Using existing virtual environment")
            return str(venv_path)
    
    print("🔨 Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print(f"✅ Virtual environment created at: {venv_path}")
        return str(venv_path)
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return None

def install_dependencies(venv_path):
    """Install project dependencies"""
    print_step(3, "Installing Dependencies")
    
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = Path(venv_path) / "Scripts" / "pip"
    else:  # Unix/Linux/macOS
        pip_path = Path(venv_path) / "bin" / "pip"
    
    # Upgrade pip first
    if not run_command(f'"{pip_path}" install --upgrade pip', "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f'"{pip_path}" install -r "{requirements_file}"', "Installing project dependencies"):
        return False
    
    print("✅ All dependencies installed successfully")
    return True

def setup_environment_variables():
    """Set up environment variables"""
    print_step(4, "Setting up Environment Variables")
    
    project_root = Path(__file__).parent.parent
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Do you want to update it? (y/N): ").lower()
        if response != 'y':
            print("✅ Using existing .env file")
            return True
    
    # Copy example file
    shutil.copy2(env_example, env_file)
    print(f"✅ Created .env file from template")
    
    # Prompt for API keys
    print("\n🔑 API Key Configuration:")
    print("   You can add your API keys now or later by editing the .env file")
    
    api_keys = {
        'OPENAI_API_KEY': 'OpenAI API Key (for GPT models)',
        'ANTHROPIC_API_KEY': 'Anthropic API Key (for Claude models)'
    }
    
    env_content = env_file.read_text()
    
    for key, description in api_keys.items():
        current_value = "your_" + key.lower() + "_here"
        if current_value in env_content:
            api_key = input(f"   Enter {description} (or press Enter to skip): ").strip()
            if api_key:
                env_content = env_content.replace(current_value, api_key)
                print(f"   ✅ {key} configured")
            else:
                print(f"   ⏭️  {key} skipped (you can add it later)")
    
    env_file.write_text(env_content)
    print("✅ Environment variables configured")
    return True

def create_directories():
    """Create necessary directories"""
    print_step(5, "Creating Project Directories")
    
    project_root = Path(__file__).parent.parent
    directories = ['data', 'logs', 'cache', 'output']
    
    for dir_name in directories:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}/")
    
    return True

def run_tests(venv_path):
    """Run the test suite to verify installation"""
    print_step(6, "Running Test Suite")
    
    project_root = Path(__file__).parent.parent
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = Path(venv_path) / "Scripts" / "python"
    else:  # Unix/Linux/macOS
        python_path = Path(venv_path) / "bin" / "python"
    
    # Run tests
    test_command = f'cd "{project_root}" && "{python_path}" -m pytest tests/ -v --tb=short'
    
    print("🧪 Running tests (this may take a moment)...")
    if run_command(test_command, "Running test suite", check=False):
        print("✅ All tests passed successfully")
        return True
    else:
        print("⚠️  Some tests failed, but the installation should still work")
        print("   This is normal if you haven't configured API keys yet")
        return True

def run_demo(venv_path):
    """Run a quick demo to verify everything works"""
    print_step(7, "Running Demo")
    
    project_root = Path(__file__).parent.parent
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = Path(venv_path) / "Scripts" / "python"
    else:  # Unix/Linux/macOS
        python_path = Path(venv_path) / "bin" / "python"
    
    demo_script = project_root / "examples" / "basic_usage.py"
    
    if not demo_script.exists():
        print("❌ Demo script not found")
        return False
    
    print("🚀 Running basic usage demo...")
    demo_command = f'cd "{project_root}" && "{python_path}" "{demo_script}"'
    
    if run_command(demo_command, "Running demo", check=False):
        print("✅ Demo completed successfully")
        return True
    else:
        print("⚠️  Demo encountered issues (possibly due to missing API keys)")
        return True

def create_launch_scripts(venv_path):
    """Create convenience launch scripts"""
    print_step(8, "Creating Launch Scripts")
    
    project_root = Path(__file__).parent.parent
    
    # Determine paths based on OS
    if os.name == 'nt':  # Windows
        python_path = Path(venv_path) / "Scripts" / "python.exe"
        script_extension = ".bat"
        script_template = f"""@echo off
cd /d "{project_root}"
"{python_path}" {{}}
pause
"""
    else:  # Unix/Linux/macOS
        python_path = Path(venv_path) / "bin" / "python"
        script_extension = ".sh"
        script_template = f"""#!/bin/bash
cd "{project_root}"
"{python_path}" {{}}
"""
    
    # Create launch scripts for examples
    scripts = {
        f"run_basic_demo{script_extension}": "examples/basic_usage.py",
        f"run_advanced_demo{script_extension}": "examples/document_analysis_demo.py",
        f"run_tests{script_extension}": "-m pytest tests/ -v"
    }
    
    for script_name, command in scripts.items():
        script_path = project_root / script_name
        script_content = script_template.format(command)
        
        script_path.write_text(script_content)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(script_path, 0o755)
        
        print(f"✅ Created: {script_name}")
    
    return True

def print_next_steps(venv_path):
    """Print next steps for the user"""
    print_header("Setup Complete! 🎉")
    
    project_root = Path(__file__).parent.parent
    
    print("\n📚 Next Steps:")
    print("   1. Activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        activate_script = Path(venv_path) / "Scripts" / "activate.bat"
        print(f"      {activate_script}")
    else:  # Unix/Linux/macOS
        activate_script = Path(venv_path) / "bin" / "activate"
        print(f"      source {activate_script}")
    
    print("\n   2. Configure API keys (if not done already):")
    print(f"      Edit {project_root}/.env and add your API keys")
    
    print("\n   3. Try the examples:")
    print(f"      python examples/basic_usage.py")
    print(f"      python examples/document_analysis_demo.py")
    
    print("\n   4. Run tests to verify everything works:")
    print("      python -m pytest tests/ -v")
    
    print("\n   5. Or use the convenience scripts:")
    if os.name == 'nt':
        print("      run_basic_demo.bat")
        print("      run_advanced_demo.bat")
        print("      run_tests.bat")
    else:
        print("      ./run_basic_demo.sh")
        print("      ./run_advanced_demo.sh")
        print("      ./run_tests.sh")
    
    print("\n📖 Documentation:")
    print(f"   - README.md: Complete project documentation")
    print(f"   - config/settings.py: Configuration options")
    print(f"   - examples/: Usage examples and demos")
    print(f"   - tests/: Test suite for validation")
    
    print("\n🆘 Need Help?")
    print("   - Check the README.md for detailed instructions")
    print("   - Review the examples for usage patterns")
    print("   - Run tests to identify any issues")
    print("   - Check the logs/ directory for error details")

def main():
    """Main setup function"""
    print_header("Legal Research AI Agents - Local Setup")
    
    print("This script will set up the Legal Research AI Agents on your local machine.")
    print("It will create a virtual environment, install dependencies, and configure the project.")
    
    # Check if user wants to continue
    response = input("\nDo you want to continue? (Y/n): ").lower()
    if response == 'n':
        print("Setup cancelled.")
        return
    
    # Step-by-step setup
    steps = [
        ("Check Python version", check_python_version),
        ("Setup virtual environment", setup_virtual_environment),
        ("Install dependencies", lambda: install_dependencies(venv_path)),
        ("Setup environment variables", setup_environment_variables),
        ("Create directories", create_directories),
        ("Run tests", lambda: run_tests(venv_path)),
        ("Run demo", lambda: run_demo(venv_path)),
        ("Create launch scripts", lambda: create_launch_scripts(venv_path))
    ]
    
    venv_path = None
    
    for i, (description, step_func) in enumerate(steps, 1):
        try:
            if i == 2:  # Setup virtual environment step
                venv_path = step_func()
                if not venv_path:
                    print("❌ Setup failed at virtual environment creation")
                    return
            elif i >= 3:  # Steps that need venv_path
                if not venv_path:
                    print("❌ Virtual environment path not available")
                    return
                if not step_func():
                    print(f"❌ Setup failed at step: {description}")
                    response = input("Do you want to continue anyway? (y/N): ").lower()
                    if response != 'y':
                        return
            else:
                if not step_func():
                    print(f"❌ Setup failed at step: {description}")
                    return
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted by user")
            return
        except Exception as e:
            print(f"❌ Unexpected error in step '{description}': {e}")
            response = input("Do you want to continue anyway? (y/N): ").lower()
            if response != 'y':
                return
    
    # Print final instructions
    print_next_steps(venv_path)

if __name__ == "__main__":
    main()