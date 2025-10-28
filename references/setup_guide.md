# Carver Feeds Skill - Setup Guide

This guide provides detailed setup instructions for the Carver Feeds Skill, including manual setup alternatives, troubleshooting, and environment configuration.

## Table of Contents

- [Automatic Setup (Recommended)](#automatic-setup-recommended)
- [Manual Setup (Alternative)](#manual-setup-alternative)
- [Python Version Requirements](#python-version-requirements)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Automatic Setup (Recommended)

The `auto_init.py` script handles all setup automatically. See SKILL.md for usage instructions.

**What it does:**
1. Searches for compatible Python version (3.10, 3.11, or 3.12)
2. Creates virtual environment in skill directory
3. Installs carver-feeds-sdk and dependencies
4. Checks for .env file in your working directory
5. Verifies API connectivity

**Exit Codes:**
- `0` - Success: Returns VENV_PYTHON path and CWD
- `1` - Error: Shows error message
- `2` - API Key Required: Prompts for API key setup

## Manual Setup (Alternative)

If you need to set up manually without using auto_init.py:

### Step 1: Check Python Version

```bash
python3 --version
```

**Requirements:** Python 3.10, 3.11, or 3.12 is REQUIRED for carver-feeds-sdk.

### Step 2: Create Virtual Environment

```bash
# Using Python 3.12 (recommended)
python3.12 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# OR
.venv\Scripts\activate     # On Windows
```

### Step 3: Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install carver-feeds-sdk
pip install carver-feeds-sdk
```

### Step 4: Configure Environment Variables

Create a `.env` file in your working directory:

```bash
# Required
CARVER_API_KEY=your_api_key_here

# Optional - defaults to production API
CARVER_BASE_URL=https://app.carveragents.ai
```

**Get your API key:** https://app.carveragents.ai

### Step 5: Verify Installation

```python
from carver_feeds import create_query_engine

# Test connection
qe = create_query_engine()
topics = qe.to_dataframe()
print(f"✓ Connected! Found {len(topics)} topics")
```

## Python Version Requirements

### Why Python 3.10+ is Required

The carver-feeds-sdk has dependencies that require Python 3.10 or newer. Older Python versions are not supported.

### Installing Compatible Python

#### macOS (via Homebrew)

```bash
# Install Python 3.12 (recommended)
brew install python@3.12

# Verify installation
python3.12 --version
```

#### Ubuntu/Debian

```bash
# Install Python 3.12
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

# Verify installation
python3.12 --version
```

#### Windows

1. Download Python 3.12 from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify installation: `python --version`

#### Using pyenv (All Platforms)

```bash
# Install pyenv (if not already installed)
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12.0

# Set as global version
pyenv global 3.12.0
```

## Environment Variables

### Required Variables

**CARVER_API_KEY**
- Your personal API key for accessing the Carver Feeds API
- Get it from: https://app.carveragents.ai
- **Security:** Never commit this to version control

### Optional Variables

**CARVER_BASE_URL**
- Default: `https://app.carveragents.ai`
- Use this to override the API endpoint (e.g., for testing)

### .env File Location

**CRITICAL:** The `.env` file MUST be in your **current working directory**, NOT in the skill directory.

**Why?**
- Security: Keeps API keys in your project, not shared skill location
- Multi-project: Different projects can use different API keys
- Isolation: Each user maintains their own credentials

**Example structure:**
```
/Users/you/my-project/           # Your working directory
├── .env                          # ✓ API key goes here
├── queries/
└── results/

~/.claude/skills/carver-feeds-skill/  # Skill directory
├── .venv/                        # ✓ Virtual environment here
├── scripts/
└── SKILL.md                      # ✗ NO .env file here
```

## Troubleshooting

### Python Version Not Found

**Problem:** `ERROR: Python 3.10, 3.11, or 3.12 is required but not found`

**Solutions:**
1. Install a compatible Python version (see above)
2. Ensure Python is in your PATH:
   ```bash
   which python3.12
   # Should return a path like /usr/local/bin/python3.12
   ```
3. Try specifying full path in auto_init.py call

### Virtual Environment Creation Failed

**Problem:** `ERROR: Failed to create virtual environment`

**Solutions:**
1. Ensure you have write permissions to skill directory
2. Check disk space: `df -h`
3. Try manual venv creation:
   ```bash
   python3.12 -m venv ~/.claude/skills/carver-feeds-skill/.venv
   ```

### SDK Installation Failed

**Problem:** `ERROR: Could not install carver-feeds-sdk`

**Solutions:**
1. Check internet connectivity
2. Try manual installation:
   ```bash
   source ~/.claude/skills/carver-feeds-skill/.venv/bin/activate
   pip install --upgrade pip
   pip install carver-feeds-sdk
   ```
3. Check for proxy/firewall issues

### API Key Not Found

**Problem:** `API_KEY_REQUIRED` exit code

**Solutions:**
1. Verify `.env` file exists in your **working directory**:
   ```bash
   ls -la .env
   cat .env
   ```
2. Check .env format (no quotes, no spaces around `=`):
   ```
   CARVER_API_KEY=abc123def456
   ```
3. Verify API key is valid at https://app.carveragents.ai

### Authentication Failed

**Problem:** `AuthenticationError: Invalid API key`

**Solutions:**
1. Verify API key is correct (no typos, complete string)
2. Check for extra spaces or newlines in .env file
3. Get a new API key from https://app.carveragents.ai
4. Test key directly:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print(f"API Key: {os.getenv('CARVER_API_KEY')[:10]}...")
   ```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'carver_feeds'`

**Solutions:**
1. Ensure you're using VENV_PYTHON from auto_init output
2. Verify SDK is installed:
   ```bash
   ~/.claude/skills/carver-feeds-skill/.venv/bin/python -m pip list | grep carver
   ```
3. Reinstall SDK:
   ```bash
   ~/.claude/skills/carver-feeds-skill/.venv/bin/python -m pip install --force-reinstall carver-feeds-sdk
   ```

### Slow Query Performance

**Problem:** Queries taking 30+ seconds

**Solutions:**
1. Always filter by topic or feed FIRST
2. Use date ranges to limit results
3. Avoid loading all entries without filters
4. See Performance Considerations in SKILL.md

## Advanced Configuration

### Custom Virtual Environment Location

By default, the venv is created in `~/.claude/skills/carver-feeds-skill/.venv`.

To use a different location:
1. Skip auto_init.py
2. Create venv manually at desired location
3. Install carver-feeds-sdk
4. Use that Python path for all queries

### Multiple API Keys

To use different API keys for different projects:

```bash
# Project 1
cd ~/projects/banking-analysis
echo "CARVER_API_KEY=key1" > .env

# Project 2
cd ~/projects/healthcare-monitoring
echo "CARVER_API_KEY=key2" > .env
```

Each project's .env is loaded when you run queries from that directory.

### Proxy Configuration

If behind a corporate proxy:

```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Then run auto_init.py
python scripts/auto_init.py $(pwd)
```

### Offline Usage

The SDK requires internet access to query the API. For offline development:

1. Cache query results:
   ```python
   results = qe.filter_by_topic(topic_name="Banking").to_dataframe()
   results.to_pickle("banking_cache.pkl")
   ```
2. Load cached results:
   ```python
   import pandas as pd
   results = pd.read_pickle("banking_cache.pkl")
   ```

## Getting Help

- **Skill Issues:** Check SKILL.md Common Pitfalls section
- **SDK Documentation:** https://github.com/carveragents/carver-feeds-sdk
- **API Documentation:** https://app.carveragents.ai/api-docs/
- **Support:** https://app.carveragents.ai

## Next Steps

After successful setup:
1. Review SKILL.md for core workflows
2. Explore `usage_examples.md` for practical examples
3. Check `api_reference.md` for detailed API documentation
4. Try the pre-built query templates in `scripts/query_templates.py`
