# Carver Feeds Skill for Claude Code

A [Claude Code skill](https://www.anthropic.com/news/skills) that enables natural language querying of regulatory feed data from the Carver API. Search, filter, and analyze regulatory updates across topics like Banking, Healthcare, Energy, and more—directly within Claude Code.

## 📖 What is This?

This skill integrates the [carver-feeds-sdk](https://github.com/carveragents/carver-feeds-sdk) into Claude Code, allowing you to query regulatory intelligence data using natural language instead of writing Python scripts.

**Without this skill:**
```python
# You'd need to write Python code like this
from carver_feeds import create_query_engine
from datetime import datetime, timedelta

qe = create_query_engine()
results = qe \
    .filter_by_topic(topic_name="Banking") \
    .filter_by_date(start_date=datetime.now() - timedelta(days=7)) \
    .search_entries(["regulation", "compliance"]) \
    .to_csv("results.csv")
```

**With this skill:**
```
You: "Show me banking regulations from the last 7 days mentioning compliance"
Claude: [Automatically runs the query and saves results.csv to your directory]
```

## ✨ Why Use This Skill?

The Carver Feeds API provides real-time regulatory monitoring across global jurisdictions. This skill makes that data accessible without:
- Writing Python code manually
- Managing virtual environments
- Learning the SDK API
- Handling API authentication

Perfect for:
- **Compliance teams** tracking regulatory changes
- **Risk analysts** monitoring trends across jurisdictions
- **Legal teams** researching historical regulatory updates
- **Developers** prototyping compliance monitoring tools

## ✅ Prerequisites

1. **Python 3.10** (required by carver-feeds-sdk)
   ```bash
   # Check your version
   python3.10 --version

   # macOS installation
   brew install python@3.10

   # Ubuntu/Debian
   sudo apt-get install python3.10
   ```

2. **Carver API Key**
   - Get your free API key at [https://app.carveragents.ai](https://app.carveragents.ai)
   - The skill will prompt you to add it on first use

## 📦 Installation

```bash
# Clone to your Claude Code skills directory
cd ~/.claude/skills
git clone https://github.com/carveragents/carver-feeds-skill.git
```

That's it! The skill will be available the next time you start Claude Code.

## 🚀 Quick Start

1. **Navigate to your working directory**
   ```bash
   cd /path/to/your/project
   ```

2. **Query regulatory data with natural language**
   ```
   "Show me all healthcare regulations from the last 30 days"
   "Search for banking regulations mentioning 'capital requirements'"
   "List all available regulatory topics"
   "Export energy sector updates to CSV"
   ```

3. **Results are saved to your current directory**
   - CSV files for data exports
   - JSON files for structured output
   - All outputs in your project folder, not the skill directory

## 💼 Common Use Cases

### Monitor Specific Topics
```
"Show me recent updates for Banking and FinTech topics"
```

### Keyword Search
```
"Find regulations mentioning 'climate risk' across all energy feeds"
```

### Date Range Queries
```
"Show banking regulations from January 2025"
```

### Export Data
```
"Export all SEC feed entries to CSV"
```

### Compare Activity
```
"Compare regulatory activity across Banking, Insurance, and Consumer Protection over the last quarter"
```

### Daily Briefing
```
"Generate a weekly regulatory brief for Banking and Insurance topics and include sources for all updates"
```

## ⚙️ How It Works

1. **Auto-initialization**: On first use, the skill:
   - Finds/creates a Python 3.10 virtual environment
   - Installs carver-feeds-sdk
   - Prompts you for your API key to add it to `.env`

2. **Query execution**: Claude translates your natural language requests into SDK queries

3. **Output**: Results saved to your current directory (CSV, JSON, or DataFrame)

## 🗂️ Data Hierarchy

```
Topic (e.g., "Banking Regulation")
  ├── Feed (e.g., "SEC News Feed")
  │     └── Entry (individual article/post)
  └── Feed (e.g., "Federal Reserve Updates")
        └── Entry (individual article/post)
```

## 📚 Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation and workflows
- **[API Reference](references/api_reference.md)** - Detailed SDK method signatures
- **[Usage Examples](references/usage_examples.md)** - Practical code examples

## 🔧 Troubleshooting

### Python 3.10 Not Found
The skill requires Python 3.10+. Install it:
```bash
# macOS
brew install python@3.10

# Ubuntu/Debian
sudo apt-get install python3.10
```

### API Key Issues
- Ensure `.env` file is in your **current working directory**, not the skill directory
- Get a new key at [https://app.carveragents.ai](https://app.carveragents.ai)
- Check for typos in the key

### Slow Queries
- Try asking Claude to filter by topic/feed before loading all entries
- Use date ranges to limit results

## 🔗 Related Projects

- **[carver-feeds-sdk](https://github.com/carveragents/carver-feeds-sdk)** - The underlying Python SDK
- **[Carver Agents Platform](https://app.carveragents.ai)** - Web interface for regulatory monitoring

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/carveragents/carver-feeds-skill/issues)
- **API Docs**: [https://app.carveragents.ai/api-docs/](https://app.carveragents.ai/api-docs/)
- **SDK Docs**: [https://github.com/carveragents/carver-feeds-sdk](https://github.com/carveragents/carver-feeds-sdk)

---

**Note**: This is a Claude Code skill, not a standalone application. It requires [Claude Code](https://claude.ai/code) to function.
