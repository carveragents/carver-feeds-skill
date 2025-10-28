#!/usr/bin/env python3
"""
Auto-initialization script for Carver Feeds Skill.

This script MUST be run before any queries. It automatically:
1. Creates/uses existing venv in skill directory without requiring activation
2. Installs carver-feeds-sdk if not present
3. Checks for .env file in CWD and prompts for API key if missing
4. Returns the venv Python path for subsequent commands

Architecture:
- Skill infrastructure (venv, scripts) stays in ~/.claude/skills/carver-feeds-skill
- .env file MUST be in the user's current working directory (CWD)
- All outputs are saved to CWD

Requirements:
- Python 3.10, 3.11, or 3.12 (required by carver-feeds-sdk)

Usage:
    python /path/to/skill/scripts/auto_init.py [cwd_path]

Arguments:
    cwd_path: Optional. The current working directory where .env should be.
              If not provided, uses the directory from which script was called.
"""

import subprocess
import sys
import os
from pathlib import Path
import venv


def get_skill_dir():
    """Get the skill directory (parent of scripts/)."""
    return Path(__file__).parent.parent


def get_user_cwd():
    """Get the user's current working directory from args or environment."""
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    return Path.cwd()


def get_venv_path():
    """Get the venv path for this skill."""
    return get_skill_dir() / ".venv"


def get_venv_python(venv_path):
    """Get the path to the Python executable in the venv."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def find_compatible_python():
    """Find Python 3.10, 3.11, or 3.12 executable.

    Returns:
        Tuple of (python_path, version_string) or (None, None) if not found
    """
    # Try common Python locations, preferring newer versions
    candidates = [
        "python3.12",
        "python3.11",
        "python3.10",
        "python3",
        "/usr/bin/python3.12",
        "/usr/bin/python3.11",
        "/usr/bin/python3.10",
        "/usr/local/bin/python3.12",
        "/usr/local/bin/python3.11",
        "/usr/local/bin/python3.10",
        "/opt/homebrew/bin/python3.12",
        "/opt/homebrew/bin/python3.11",
        "/opt/homebrew/bin/python3.10",
    ]

    for candidate in candidates:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_output = result.stdout.strip()
                # Check for Python 3.10, 3.11, or 3.12
                if any(f"Python 3.{minor}" in version_output for minor in [10, 11, 12]):
                    return candidate, version_output
        except Exception:
            continue

    return None, None


def ensure_venv():
    """Ensure venv exists, create if it doesn't using compatible Python version."""
    venv_path = get_venv_path()

    if venv_path.exists():
        return get_venv_python(venv_path)

    print("Creating virtual environment...")

    # Find compatible Python version
    python_exe, version = find_compatible_python()
    if not python_exe:
        print("\nERROR: Python 3.10, 3.11, or 3.12 is required but not found.")
        print("\nThe carver-feeds-sdk requires Python 3.10+.")
        print("\nPlease install a compatible Python version:")
        print("  - macOS: brew install python@3.12")
        print("  - Ubuntu: sudo apt install python3.12")
        print("  - Windows: Download from python.org")
        sys.exit(1)

    print(f"✓ Found compatible Python: {version}")

    try:
        # Create venv using compatible Python
        subprocess.check_call(
            [python_exe, "-m", "venv", str(venv_path)],
            timeout=60
        )
        print("✓ Virtual environment created")
        return get_venv_python(venv_path)
    except Exception as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        sys.exit(1)


def is_sdk_installed(python_exe):
    """Check if carver-feeds-sdk is installed in the venv."""
    try:
        result = subprocess.run(
            [str(python_exe), "-c", "import carver_feeds"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def upgrade_pip(python_exe):
    """Upgrade pip to latest version."""
    print("Upgrading pip...")
    try:
        subprocess.check_call(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            timeout=60
        )
        print("✓ pip upgraded")
        return True
    except Exception as e:
        print(f"WARNING: Could not upgrade pip: {e}")
        return False


def install_sdk(python_exe):
    """Install carver-feeds-sdk using the venv Python."""
    print("Installing carver-feeds-sdk...")
    try:
        subprocess.check_call(
            [str(python_exe), "-m", "pip", "install", "carver-feeds-sdk"],
            timeout=120
        )
        print("✓ SDK installed")
        return True
    except Exception as e:
        print(f"ERROR: Failed to install SDK: {e}")
        sys.exit(1)


def check_env_file(cwd):
    """Check if .env file exists with CARVER_API_KEY in the user's CWD.

    Args:
        cwd: Path to the user's current working directory

    Returns:
        Tuple of (has_valid_key, api_key)
    """
    env_file = cwd / ".env"

    # Check if file exists
    if not env_file.exists():
        return False, None

    # Check if CARVER_API_KEY is present
    with open(env_file) as f:
        for line in f:
            if line.strip().startswith("CARVER_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and key != "your_api_key_here":
                    return True, key

    return False, None


def prompt_for_api_key(cwd):
    """Prompt user for API key if not configured.

    Args:
        cwd: Path to the user's current working directory
    """
    print("\n" + "="*60)
    print("CARVER API KEY REQUIRED")
    print("="*60)
    print("\nThe Carver Feeds SDK requires an API key to function.")
    print("\nTo get your API key:")
    print("1. Visit: https://app.carveragents.ai")
    print("2. Sign in or create an account")
    print("3. Copy your API key")
    print("\nPlease provide your Carver API key to continue.")
    print(f"\n(The key will be saved to {cwd}/.env)")
    print("="*60)

    # Signal to Claude that user input is needed
    print(f"\nAPI_KEY_REQUIRED")
    print(f"CWD={cwd}")
    sys.exit(2)  # Special exit code to indicate API key is needed


def test_sdk_connection(python_exe, cwd):
    """Test that SDK can connect with the API key from CWD.

    Args:
        python_exe: Path to venv Python executable
        cwd: Path to the user's current working directory where .env is located
    """
    test_script = f"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from CWD
env_file = Path(r"{cwd}") / ".env"
if not env_file.exists():
    print("ERROR: .env file not found in CWD")
    sys.exit(1)

load_dotenv(env_file)

# Test connection
from carver_feeds import get_client
client = get_client()
topics = client.list_topics()
print(f"SUCCESS: Connected! Found {{len(topics)}} topics")
"""

    try:
        result = subprocess.run(
            [str(python_exe), "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and "SUCCESS" in result.stdout:
            print("✓ SDK connection verified")
            return True
        else:
            print(f"ERROR: SDK connection failed")
            if result.stderr:
                print(f"  {result.stderr}")
            if result.stdout and "ERROR" in result.stdout:
                print(f"  {result.stdout}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to test SDK connection: {e}")
        return False


def ensure_python_dotenv(python_exe):
    """Ensure python-dotenv is installed for .env file support."""
    try:
        result = subprocess.run(
            [str(python_exe), "-c", "import dotenv"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return True

        # Install python-dotenv
        subprocess.check_call(
            [str(python_exe), "-m", "pip", "install", "-q", "python-dotenv"],
            timeout=60
        )
        return True
    except Exception:
        return False


def main():
    """Main initialization routine."""
    # Get user's CWD (where they're running queries from)
    user_cwd = get_user_cwd()
    skill_dir = get_skill_dir()

    print(f"Skill directory: {skill_dir}")
    print(f"Working directory: {user_cwd}")
    print()

    # Step 1: Ensure venv exists in skill directory
    python_exe = ensure_venv()

    # Step 2: Upgrade pip to avoid compatibility issues
    upgrade_pip(python_exe)

    # Step 3: Ensure SDK is installed
    if not is_sdk_installed(python_exe):
        install_sdk(python_exe)

    # Step 4: Ensure python-dotenv is installed
    ensure_python_dotenv(python_exe)

    # Step 5: Check for .env file and API key in CWD
    has_key, api_key = check_env_file(user_cwd)

    if not has_key:
        # API key not configured - prompt user
        prompt_for_api_key(user_cwd)
        # This exits with code 2

    # Step 6: Test connection using .env from CWD
    if not test_sdk_connection(python_exe, user_cwd):
        print("\nERROR: SDK is installed but cannot connect to API.")
        print("Please check your API key and network connection.")
        print(f"Looking for .env in: {user_cwd}")
        sys.exit(1)

    # Success! Print the venv Python path and CWD for subsequent commands
    print(f"\nVENV_PYTHON={python_exe}")
    print(f"CWD={user_cwd}")
    sys.exit(0)


if __name__ == "__main__":
    main()
