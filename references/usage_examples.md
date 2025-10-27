# Carver Feeds SDK - Usage Examples

Practical examples for common regulatory monitoring workflows.

**When to load this reference**: When you need concrete code examples for specific use cases beyond the basic workflows in SKILL.md.

---

## Example 1: Search for Recent Regulatory Updates

**Scenario**: Find recent banking regulations about cryptocurrency.

```python
from carver_feeds import create_query_engine
from datetime import datetime, timedelta

qe = create_query_engine()

# Last 30 days of banking crypto regulations
results = qe \
    .filter_by_topic(topic_name="Banking") \
    .filter_by_date(start_date=datetime.now() - timedelta(days=30)) \
    .search_entries("cryptocurrency") \
    .to_dataframe()

print(f"Found {len(results)} entries")
results[['entry_title', 'entry_published_at', 'feed_name']].head()
```

---

## Example 2: Monitor Multiple Keywords Across Topics

**Scenario**: Track "compliance" AND "enforcement" mentions across Banking and Healthcare.

```python
from carver_feeds import create_query_engine

qe = create_query_engine()

# Banking compliance
banking = qe \
    .filter_by_topic(topic_name="Banking") \
    .search_entries(["compliance", "enforcement"], match_all=True) \
    .to_dataframe()

# Healthcare compliance
healthcare = qe.chain() \
    .filter_by_topic(topic_name="Healthcare") \
    .search_entries(["compliance", "enforcement"], match_all=True) \
    .to_dataframe()

import pandas as pd
combined = pd.concat([banking, healthcare])

print(f"Total matches: {len(combined)}")
print(combined.groupby('topic_name').size())
```

---

## Example 3: Export Feed Entries to CSV

**Scenario**: Export all SEC News Feed entries to CSV for analysis.

```python
from carver_feeds import create_query_engine

qe = create_query_engine()

# Get all SEC News entries
results = qe.filter_by_feed(feed_name="SEC News")

# Export to CSV
csv_path = results.to_csv("sec_news_entries.csv")
print(f"Exported to: {csv_path}")

# Also available: to_json(), to_dict(), to_dataframe()
```

---

## Example 4: Compare Activity Across Topics

**Scenario**: Compare regulatory activity in Banking vs Healthcare over last 90 days.

```python
from carver_feeds import create_query_engine
from datetime import datetime, timedelta
import pandas as pd

qe = create_query_engine()
start = datetime.now() - timedelta(days=90)

topics = ["Banking", "Healthcare", "Energy"]
comparison = []

for topic in topics:
    results = qe.chain() \
        .filter_by_topic(topic_name=topic) \
        .filter_by_date(start_date=start) \
        .to_dataframe()

    comparison.append({
        'Topic': topic,
        'Entries': len(results),
        'Feeds': results['feed_name'].nunique(),
        'Avg/Day': round(len(results) / 90, 2)
    })

df = pd.DataFrame(comparison)
print(df.to_string(index=False))
```

---

## Example 5: Daily Regulatory Brief

**Scenario**: Generate a daily summary of yesterday's regulatory updates.

```python
from carver_feeds import create_query_engine
from datetime import datetime, timedelta

qe = create_query_engine()
yesterday = datetime.now() - timedelta(days=1)

results = qe \
    .filter_by_date(start_date=yesterday, end_date=datetime.now()) \
    .filter_by_active(is_active=True) \
    .to_dataframe()

if len(results) > 0:
    print(f"Yesterday's Regulatory Updates: {len(results)} entries\n")

    # Group by topic
    topic_summary = results.groupby('topic_name').size().sort_values(ascending=False)
    print("By Topic:")
    for topic, count in topic_summary.items():
        print(f"  {topic}: {count}")

    # Top feeds
    print("\nTop Feeds:")
    feed_summary = results.groupby('feed_name').size().sort_values(ascending=False)
    print(feed_summary.head())
```

---

## Example 6: Find Entries from Specific Feed

**Scenario**: Get all entries from a specific feed.

```python
from carver_feeds import create_data_manager

dm = create_data_manager()

# List all feeds first (to find the feed_id)
feeds = dm.get_feeds_df()
sec_feeds = feeds[feeds['name'].str.contains('SEC', case=False)]
print(sec_feeds[['id', 'name']])

# Get entries for specific feed
feed_id = sec_feeds.iloc[0]['id']
entries = dm.get_entries_df(feed_id=feed_id)

print(f"Found {len(entries)} entries from {sec_feeds.iloc[0]['name']}")
```

---

## Example 7: Case-Sensitive Keyword Search

**Scenario**: Search for "SEC" (Securities and Exchange Commission) vs "sec" (second).

```python
from carver_feeds import create_query_engine

qe = create_query_engine()

# Case-sensitive search for "SEC"
results = qe \
    .filter_by_topic(topic_name="Banking") \
    .search_entries("SEC", case_sensitive=True) \
    .to_dataframe()

print(f"Found {len(results)} entries mentioning 'SEC'")
```

---

## Example 8: Search Specific Fields

**Scenario**: Search for "fintech" in titles only (not full content).

```python
from carver_feeds import create_query_engine

qe = create_query_engine()

# Search only in title and description
results = qe \
    .search_entries(
        "fintech",
        search_fields=['entry_title', 'entry_description']
    ) \
    .to_dataframe()

print(f"Found {len(results)} entries with 'fintech' in title/description")
print(results[['entry_title', 'feed_name']].head())
```

---

## Example 9: Quarterly Analysis

**Scenario**: Analyze regulatory activity by quarter for 2024.

```python
from carver_feeds import create_query_engine
from datetime import datetime
import pandas as pd

qe = create_query_engine()

quarters = [
    ("Q1", datetime(2024, 1, 1), datetime(2024, 3, 31)),
    ("Q2", datetime(2024, 4, 1), datetime(2024, 6, 30)),
    ("Q3", datetime(2024, 7, 1), datetime(2024, 9, 30)),
    ("Q4", datetime(2024, 10, 1), datetime(2024, 12, 31)),
]

quarterly_data = []

for quarter, start, end in quarters:
    results = qe.chain() \
        .filter_by_topic(topic_name="Banking") \
        .filter_by_date(start_date=start, end_date=end) \
        .to_dataframe()

    quarterly_data.append({
        'Quarter': quarter,
        'Entries': len(results),
        'Feeds': results['feed_name'].nunique() if len(results) > 0 else 0
    })

df = pd.DataFrame(quarterly_data)
print("Banking Regulation Activity by Quarter (2024):")
print(df.to_string(index=False))
```

---

## Example 10: Hierarchical View for Topic

**Scenario**: Get complete topic/feed/entry hierarchy for Banking.

```python
from carver_feeds import create_data_manager

dm = create_data_manager()

# First get topic ID
topics = dm.get_topics_df()
banking = topics[topics['name'].str.contains('Banking', case=False)]
topic_id = banking.iloc[0]['id']

# Get hierarchical view
hierarchy = dm.get_hierarchical_view(
    include_entries=True,
    topic_id=topic_id
)

print(f"Hierarchical view: {len(hierarchy)} rows")
print(f"Columns: {', '.join(hierarchy.columns[:10])}...")

# Access nested data
print(f"\nUnique topics: {hierarchy['topic_name'].nunique()}")
print(f"Unique feeds: {hierarchy['feed_name'].nunique()}")
print(f"Total entries: {len(hierarchy)}")
```

---

## Common Patterns

### Pattern: OR vs AND Logic

```python
# OR logic: Match ANY keyword
results = qe.search_entries(["crypto", "blockchain", "digital assets"], match_all=False)

# AND logic: Match ALL keywords
results = qe.search_entries(["banking", "regulation"], match_all=True)
```

### Pattern: Chaining Queries

```python
qe = create_query_engine()

# First query
banking = qe.filter_by_topic(topic_name="Banking").to_dataframe()

# Reset and new query
healthcare = qe.chain().filter_by_topic(topic_name="Healthcare").to_dataframe()
```

### Pattern: Filter Order (Performance)

```python
# Good: Narrow first (topic filter), then refine
results = qe \
    .filter_by_topic(topic_name="Banking") \      # Narrow dataset first
    .filter_by_date(start_date=recent) \          # Then filter by date
    .search_entries("keyword")                    # Then search

# Less optimal: Search all data first
results = qe.search_entries("keyword").filter_by_topic(topic_name="Banking")
```

### Pattern: Partial Name Matching

```python
# Topic name is case-insensitive partial match
qe.filter_by_topic(topic_name="bank")    # Matches "Banking", "Bank Regulation", etc.

# Feed name is case-insensitive partial match
qe.filter_by_feed(feed_name="sec")       # Matches "SEC News", "SEC Updates", etc.
```

---

## Error Handling Examples

### Handle Authentication Errors

```python
from carver_feeds import get_client, AuthenticationError

try:
    client = get_client()
    topics = client.list_topics()
except AuthenticationError:
    print("Error: Invalid API key")
    print("1. Check .env file exists")
    print("2. Verify CARVER_API_KEY is set correctly")
```

### Handle Empty Results

```python
from carver_feeds import create_query_engine

qe = create_query_engine()

results = qe.filter_by_topic(topic_name="Banking").search_entries("rare_keyword").to_dataframe()

if len(results) == 0:
    print("No results found. Try:")
    print("- Broadening search terms")
    print("- Using OR logic (match_all=False)")
    print("- Expanding date range")
else:
    print(f"Found {len(results)} results")
```

### Handle API Errors

```python
from carver_feeds import create_query_engine, CarverAPIError
import logging

logging.basicConfig(level=logging.INFO)

try:
    qe = create_query_engine()
    results = qe.filter_by_topic(topic_name="Banking").to_dataframe()
except CarverAPIError as e:
    print(f"API error: {e}")
    print("Check network connection and API status")
except Exception as e:
    logging.exception("Unexpected error:")
```

---

## Tips

1. **Always filter by topic or feed when possible** - This uses optimized API endpoints
2. **Use chain() to reset queries** - Reuses cached data efficiently
3. **Check result lengths before processing** - Handle empty results gracefully
4. **Export large datasets to CSV** - Rather than keeping in memory
5. **Use partial name matching** - Topic and feed names are case-insensitive partial matches

---

**Document Version**: 1.0
**SDK Version**: 0.1.0+
