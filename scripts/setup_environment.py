#!/usr/bin/env python3
"""
Environment setup script for Carver Feeds SDK.

This script:
1. Creates a virtual environment (if not already in one)
2. Installs the carver-feeds-sdk package from PyPI
3. Verifies the API key is configured
4. Tests the SDK connection
5. Provides setup guidance if issues are found
"""

import subprocess
import sys
import os
from pathlib import Path
import venv


def is_venv():
    """Check if currently running in a virtual environment."""
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))


def create_venv(venv_path):
    """Create a virtual environment."""
    print(f"📁 Creating virtual environment at {venv_path}...")
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_venv_python(venv_path):
    """Get the path to the Python executable in the venv."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def setup_venv():
    """Set up virtual environment if not already in one."""
    if is_venv():
        print("✅ Already running in a virtual environment")
        return sys.executable, True

    print("⚠️  Not in a virtual environment")
    venv_path = Path.cwd() / ".venv"

    if venv_path.exists():
        print(f"✅ Found existing virtual environment at {venv_path}")
    else:
        if not create_venv(venv_path):
            return None, False

    venv_python = get_venv_python(venv_path)

    if not venv_python.exists():
        print(f"❌ Virtual environment Python not found at {venv_python}")
        return None, False

    # Provide activation instructions
    print("\n📝 To activate the virtual environment:")
    if sys.platform == "win32":
        print(f"   {venv_path}\\Scripts\\activate")
    else:
        print(f"   source {venv_path}/bin/activate")

    print("\n⚠️  Please activate the virtual environment and run this script again.")
    return str(venv_python), False


def install_sdk():
    """Install carver-feeds-sdk from PyPI."""
    print("📦 Installing carver-feeds-sdk from PyPI...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "carver-feeds-sdk"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ SDK installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install SDK: {e}")
        return False


def check_api_key():
    """Check if CARVER_API_KEY is configured."""
    # Check environment variable
    api_key = os.getenv("CARVER_API_KEY")
    if api_key:
        print("✅ CARVER_API_KEY found in environment")
        return True

    # Check .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip().startswith("CARVER_API_KEY="):
                    print("✅ CARVER_API_KEY found in .env file")
                    return True

    print("❌ CARVER_API_KEY not found")
    print("\n📝 To set up your API key:")
    print("1. Create a .env file in your working directory")
    print("2. Add this line: CARVER_API_KEY=your_api_key_here")
    print("3. Get your API key from: https://app.carveragents.ai")
    return False


def test_connection():
    """Test SDK connection to Carver API."""
    try:
        from carver_feeds import get_client
        client = get_client()
        topics = client.list_topics()
        print(f"✅ Connected successfully! Found {len(topics)} topics available")
        return True
    except ImportError:
        print("❌ SDK not installed. Run this script again to install.")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n📝 Troubleshooting:")
        print("- Verify your API key is correct")
        print("- Check your internet connection")
        print("- Visit https://app.carveragents.ai/api-docs/ for API status")
        return False


def main():
    """Run environment setup and verification."""
    print("🚀 Carver Feeds SDK - Environment Setup\n")
    print("=" * 60)

    # Step 0: Set up virtual environment
    print("\n🔍 Step 1: Checking virtual environment...")
    python_exe, in_venv = setup_venv()
    if not in_venv:
        # Venv exists but not activated - exit and ask user to activate
        sys.exit(1)

    # Step 1: Install SDK
    print("\n📦 Step 2: Installing SDK...")
    sdk_installed = install_sdk()
    if not sdk_installed:
        print("\n❌ Setup failed: Could not install SDK")
        sys.exit(1)

    # Step 2: Check API key
    print("\n🔑 Step 3: Checking API key...")
    has_api_key = check_api_key()
    if not has_api_key:
        print("\n⚠️  Setup incomplete: API key not configured")
        sys.exit(1)

    # Step 3: Test connection
    print("\n🔌 Step 4: Testing API connection...")
    connected = test_connection()
    if not connected:
        print("\n❌ Setup failed: Could not connect to API")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ Environment setup complete!")
    print("\n📚 Next steps:")
    print("- Use 'from carver_feeds import create_query_engine' to start querying")
    print("- See reference docs for API details and examples")
    print("- Run query templates for common use cases")

    if is_venv():
        venv_path = Path(sys.prefix)
        print(f"\n💡 Your virtual environment is at: {venv_path}")
        print("   Remember to activate it in future sessions!")


if __name__ == "__main__":
    main()
