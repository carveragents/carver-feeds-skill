---
name: carver-feeds-skill
description: Access and query regulatory feed data from the Carver API. Use when searching, filtering, or analyzing regulatory updates across topics like Banking, Healthcare, Energy, etc. Enables keyword searches, date-based filtering, topic/feed comparisons, and multi-format exports (CSV, JSON, DataFrame).
---

# Carver Regulatory Feeds

## Overview

This skill provides access to the Carver Feeds API, a regulatory intelligence platform with a number of topics, feeds, and regulatory entries. Query and filter regulatory data across multiple jurisdictions, export results, and build monitoring workflows.

**Key capabilities:**
- Search regulatory entries by keyword across multiple topics/feeds
- Filter by topic, feed, date range, and active status
- Export results to CSV, JSON, or pandas DataFrame
- Compare regulatory activity across topics
- Generate daily/periodic regulatory briefs

## When to Use This Skill

Use when the user requests:
- "Find recent banking regulations about cryptocurrency"
- "Search for healthcare compliance updates"
- "Export SEC news feed entries to CSV"
- "Compare regulatory activity across banking and healthcare"
- "What regulatory topics are available?"
- "Show me all entries from a specific feed"

## MANDATORY INITIALIZATION (DO THIS FIRST!)

**CRITICAL:** Before running ANY queries, you MUST initialize the environment by running the auto-initialization script.

### Architecture

The skill uses a dual-location approach:

**Skill Directory** (`~/.claude/skills/carver-feeds-skill`):
- `.venv/` - Python 3.10 virtual environment (shared across projects)
- `scripts/` - Helper scripts
- `references/` - Documentation

**User's CWD** (where they run queries):
- `.env` - API key configuration (REQUIRED, no fallback)
- Output files (CSVs, JSONs) - All outputs saved here

### Requirements

- **Python 3.10 is REQUIRED** - The carver-feeds-sdk only works with Python 3.10
- The script will automatically find and use Python 3.10 to create the venv
- If Python 3.10 is not found, the script will exit with installation instructions
- **`.env` file MUST be in your current working directory** (not in the skill directory)

### Initialization Process

Run this command FIRST every time the skill is invoked, passing the current working directory:

```bash
python /path/to/skill/scripts/auto_init.py /path/to/your/working/directory
```

Or if running from the working directory:

```bash
python /path/to/skill/scripts/auto_init.py $(pwd)
```

The script will:
1. Find Python 3.10 on the system (exits if not found)
2. Create or use existing venv with Python 3.10 in skill directory
3. Upgrade pip to latest version
4. Install carver-feeds-sdk if not present
5. Check for .env file with CARVER_API_KEY in CWD (not skill directory!)
6. Verify SDK connection using the .env from CWD

### Handling the Output

**Exit Code 0 (Success):**
- Output will contain:
  - `VENV_PYTHON=/path/to/skill/.venv/bin/python`
  - `CWD=/path/to/user/working/directory`
- Extract the VENV_PYTHON path and CWD
- Use VENV_PYTHON for ALL subsequent Python commands
- Ensure queries load .env from CWD and save outputs to CWD

**Exit Code 2 (API Key Needed):**
- The script will output:
  - `API_KEY_REQUIRED`
  - `CWD=/path/to/user/working/directory`
- You MUST use the AskUserQuestion tool to prompt the user for their API key
- Question: "Please provide your Carver API key (get it from https://app.carveragents.ai)"
- Once received, save it to .env file **in the CWD**:
  ```bash
  echo "CARVER_API_KEY=user_provided_key" > /path/to/cwd/.env
  echo "CARVER_BASE_URL=https://app.carveragents.ai" >> /path/to/cwd/.env
  ```
- Then re-run auto_init.py with the same CWD

**Exit Code 1 (Error):**
- An error occurred during initialization
- Show the error message to the user and stop

### Example Initialization Workflow

```bash
# Assume user is in /home/user/my-project

# Step 1: Run initialization with CWD
python ~/.claude/skills/carver-feeds-skill/scripts/auto_init.py /home/user/my-project

# Step 2: If successful, output will be:
# VENV_PYTHON=/home/user/.claude/skills/carver-feeds-skill/.venv/bin/python
# CWD=/home/user/my-project

# Step 3: Use that Python path for queries, with .env loaded from CWD
/home/user/.claude/skills/carver-feeds-skill/.venv/bin/python -c "
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from CWD
load_dotenv('/home/user/my-project/.env')

# Run query
from carver_feeds import create_query_engine
qe = create_query_engine()
results = qe.filter_by_topic(topic_name='Banking').to_dataframe()

# Save to CWD
results.to_csv('/home/user/my-project/banking_results.csv')
print(f'Saved {len(results)} results to banking_results.csv')
"
```

**IMPORTANT:**
- NEVER skip initialization
- NEVER run queries without first getting the VENV_PYTHON path
- ALWAYS pass the CWD to auto_init.py
- ALWAYS load .env from CWD (not skill directory)
- ALWAYS save outputs to CWD (not skill directory)
- If initialization fails, DO NOT proceed with queries

## Setup

**NOTE:** The auto_init.py script (described above) handles all setup automatically. The information below is for reference only.

### Manual Setup (Alternative)

If you need to set up manually without using auto_init.py:

**Requirements:**
- Python 3.10 is REQUIRED for carver-feeds-sdk

1. Create and activate a virtual environment with Python 3.10:
```bash
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Upgrade pip and install the SDK:
```bash
pip install --upgrade pip
pip install carver-feeds-sdk
```

3. Create a `.env` file with your API key:
```bash
CARVER_API_KEY=your_api_key_here
CARVER_BASE_URL=https://app.carveragents.ai  # optional
```

4. Get API key from: https://app.carveragents.ai

### Old Setup Script (Deprecated)

The `scripts/setup_environment.py` script is deprecated. Use `scripts/auto_init.py` instead, which handles Python 3.10 requirement automatically.

## Core Workflows

**IMPORTANT:** All queries MUST:
1. Use the VENV_PYTHON from initialization
2. Load .env from CWD using `load_dotenv(Path(cwd) / ".env")`
3. Save all outputs to CWD

### Query Template Structure

Every query should follow this pattern:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from CWD (provided by auto_init.py)
cwd = Path('/path/to/cwd')  # From auto_init output
load_dotenv(cwd / ".env")

# Now import and use the SDK
from carver_feeds import create_query_engine

# Run your query
qe = create_query_engine()
results = qe.filter_by_topic(topic_name="Banking").to_dataframe()

# Save output to CWD
output_file = cwd / "output.csv"
results.to_csv(output_file, index=False)
print(f"Saved {len(results)} results to {output_file}")
```

### 1. Search for Recent Regulatory Updates

Use the query engine for complex searches with filtering:

```python
from carver_feeds import create_query_engine
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load .env from CWD
cwd = Path('/path/to/cwd')
load_dotenv(cwd / ".env")

qe = create_query_engine()

results = qe \
    .filter_by_topic(topic_name="Banking") \
    .filter_by_date(start_date=datetime.now() - timedelta(days=30)) \
    .search_entries("cryptocurrency") \
    .to_dataframe()

print(f"Found {len(results)} entries")
# Save to CWD if needed
# results.to_csv(cwd / "banking_crypto.csv", index=False)
```

**Key points:**
- Use `filter_by_topic()` or `filter_by_feed()` FIRST for performance (uses optimized endpoints)
- Then apply date filters and searches
- Topic/feed names are case-insensitive partial matches

### 2. List Available Topics and Feeds

Use the data manager for simple data access:

```python
from carver_feeds import create_data_manager

dm = create_data_manager()

# List all topics
topics = dm.get_topics_df()
print(topics[['id', 'name', 'is_active']].head())

# List feeds for a topic
feeds = dm.get_feeds_df(topic_id="topic-123")
print(feeds[['id', 'name', 'url']].head())
```

### 3. Export Results to Multiple Formats

```python
from carver_feeds import create_query_engine

qe = create_query_engine()

results = qe.filter_by_topic(topic_name="Banking")

# Export to CSV
csv_path = results.to_csv("banking_entries.csv")

# Or JSON
json_str = results.to_json(indent=2)

# Or DataFrame
df = results.to_dataframe()

# Or dict list
entries = results.to_dict()
```

### 4. Compare Activity Across Topics

```python
from carver_feeds import create_query_engine

qe = create_query_engine()

banking = qe.filter_by_topic(topic_name="Banking").to_dataframe()
healthcare = qe.chain().filter_by_topic(topic_name="Healthcare").to_dataframe()

print(f"Banking: {len(banking)} entries")
print(f"Healthcare: {len(healthcare)} entries")
```

**Important:** Use `chain()` to reset the query engine between different filters.

## Query Templates

For common use cases, use the pre-built query templates in `scripts/query_templates.py`:

```python
from scripts.query_templates import (
    list_available_topics,
    search_by_keyword,
    get_recent_updates_by_topic,
    monitor_keywords_across_topics,
    compare_topic_activity,
    export_feed_entries,
    daily_regulatory_brief
)

# Example: List all topics
topics = list_available_topics()

# Example: Search for keyword in topic
results = search_by_keyword("regulation", topic_name="Banking", days_back=30)

# Example: Daily brief
brief = daily_regulatory_brief(topics=["Banking", "Healthcare"])
```

Available templates:
- `list_available_topics()` - List all available regulatory topics
- `search_by_keyword(keyword, topic_name, days_back)` - Search by keyword with optional topic filter
- `get_recent_updates_by_topic(topic_name, days_back)` - Get recent updates for a topic
- `monitor_keywords_across_topics(keywords, topics, match_all, days_back)` - Track keywords across multiple topics
- `compare_topic_activity(topics, days_back)` - Compare regulatory activity across topics
- `export_feed_entries(feed_name, output_format, output_path)` - Export feed entries
- `daily_regulatory_brief(topics)` - Generate daily regulatory brief

## Method Chaining Pattern

The query engine supports fluent method chaining for complex queries:

```python
from carver_feeds import create_query_engine
from datetime import datetime, timedelta

qe = create_query_engine()

results = qe \
    .filter_by_topic(topic_name="Banking") \
    .filter_by_date(start_date=datetime.now() - timedelta(days=30)) \
    .filter_by_active(is_active=True) \
    .search_entries(["regulation", "compliance"], match_all=True) \
    .to_dataframe()
```

**Filter order (for performance):**
1. `filter_by_topic()` or `filter_by_feed()` - Narrow dataset first (uses optimized endpoint)
2. `filter_by_date()` - Apply date range
3. `filter_by_active()` - Filter by status
4. `search_entries()` - Search by keywords

## Keyword Search Options

```python
# Single keyword (case-insensitive by default)
qe.search_entries("regulation")

# Multiple keywords with OR logic (matches ANY)
qe.search_entries(["regulation", "compliance", "enforcement"], match_all=False)

# Multiple keywords with AND logic (matches ALL)
qe.search_entries(["banking", "regulation"], match_all=True)

# Case-sensitive search
qe.search_entries("SEC", case_sensitive=True)

# Search specific fields
qe.search_entries("fintech", search_fields=['entry_title', 'entry_description'])
```

**Available search fields:**
- `entry_content_markdown` (default, full article content)
- `entry_title` (headline)
- `entry_description` (brief summary)
- `entry_link` (URL)

## Performance Considerations

**Data loading times:**
- List topics: < 1s
- List feeds: ~3-5s
- List all entries: ~30-60s
- Entries for feed: ~2-10s
- Entries for topic: ~5-20s

**Optimization tips:**
1. **Always filter by topic or feed first** - Uses optimized API endpoints
2. **Use `chain()` to reset queries** - Reuses cached data efficiently
3. **Avoid loading all entries without filters** - Very slow (~30-60s)

**Example:**
```python
# Good: Fast, uses optimized endpoint
results = qe.filter_by_topic(topic_name="Banking").to_dataframe()

# Less optimal: Slow, loads all ~10,000 entries first
results = qe.to_dataframe()
```

## Error Handling

Handle common errors gracefully:

```python
from carver_feeds import create_query_engine, CarverAPIError, AuthenticationError

try:
    qe = create_query_engine()
    results = qe.filter_by_topic(topic_name="Banking").to_dataframe()

    if len(results) == 0:
        print("No results found. Try broadening search criteria.")
except AuthenticationError:
    print("Invalid API key. Check .env file and CARVER_API_KEY.")
except CarverAPIError as e:
    print(f"API error: {e}")
    print("Check network connection and API status.")
```

## Data Model

**Hierarchy:**
```
Topic (e.g., "Banking Regulation")
  ↓ 1:N
Feed (e.g., "SEC News Feed")
  ↓ 1:N
Entry (individual article/post)
```

**Key relationships:**
- Each Feed belongs to one Topic (`feed.topic_id`)
- Each Entry belongs to one Feed (`entry.feed_id`, when available)

## Additional Resources

### Bundled Scripts

- `scripts/setup_environment.py` - Environment setup and verification
- `scripts/query_templates.py` - Pre-built query patterns for common use cases

### Reference Documentation

For detailed API specifications and examples, load reference files as needed:

- `references/api_reference.md` - Complete API method signatures, parameters, and data schemas
- `references/usage_examples.md` - 10+ practical examples for common workflows

**When to load references:**
- Need detailed method signatures or parameters
- Want to see more code examples
- Need data schema specifications
- Troubleshooting specific API behaviors

### External Resources

- **PyPI Package**: https://pypi.org/project/carver-feeds-sdk/
- **GitHub Repository**: https://github.com/carveragents/carver-feeds-sdk
- **API Documentation**: https://app.carveragents.ai/api-docs/
- **Get API Key**: https://app.carveragents.ai

## Common Pitfalls

1. **Not filtering before loading data** - Always use `filter_by_topic()` or `filter_by_feed()` first
2. **Forgetting to use `chain()`** - Reset query engine between different filters
3. **Case-sensitive searches** - Default is case-insensitive; set `case_sensitive=True` if needed
4. **Expecting `feed_id` in all entries** - Only present when fetched via feed-specific endpoints
5. **Not handling empty results** - Always check `len(results)` before processing

## Quick Reference

### Three-Layer Architecture

1. **CarverFeedsAPIClient** - Low-level HTTP client, returns dicts
2. **FeedsDataManager** - Converts to DataFrames, simple filtering
3. **EntryQueryEngine** - High-level fluent interface (RECOMMENDED)

### Factory Functions

```python
from carver_feeds import get_client, create_data_manager, create_query_engine

client = get_client()              # Low-level API client
dm = create_data_manager()         # Mid-level data manager
qe = create_query_engine()         # High-level query engine (recommended)
```

### Common Filters

```python
qe.filter_by_topic(topic_name="Banking")           # Partial match
qe.filter_by_feed(feed_name="SEC News")            # Partial match
qe.filter_by_date(start_date=datetime(2024, 1, 1)) # Date range
qe.filter_by_active(is_active=True)                # Active status
qe.search_entries("keyword")                       # Keyword search
```

### Export Methods

```python
df = qe.to_dataframe()              # pandas DataFrame
dict_list = qe.to_dict()            # List of dicts
json_str = qe.to_json(indent=2)     # JSON string
csv_path = qe.to_csv("output.csv")  # CSV file
```
