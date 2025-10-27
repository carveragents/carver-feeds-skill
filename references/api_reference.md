# Carver Feeds SDK - API Quick Reference

Complete technical reference for the Carver Feeds SDK.

**When to load this reference**: When you need detailed API specifications, method signatures, or data schemas beyond the core workflows in SKILL.md.

---

## Installation

```bash
pip install carver-feeds-sdk
```

## Configuration

Set environment variables in `.env`:

```bash
CARVER_API_KEY=your_api_key_here          # Required
CARVER_BASE_URL=https://app.carveragents.ai  # Optional
```

---

## Three-Layer Architecture

### 1. CarverFeedsAPIClient (Low-level)
- Direct HTTP client for raw API access
- Returns Python dicts
- Use when: Need specific control over requests

### 2. FeedsDataManager (Mid-level)
- Converts API responses to pandas DataFrames
- Hierarchical data views
- Use when: Simple DataFrame operations without complex filtering

### 3. EntryQueryEngine (High-level)
- Fluent interface with method chaining
- Advanced filtering and search
- Use when: Complex queries with multiple filters (RECOMMENDED)

---

## Quick Start Patterns

### Factory Functions (Recommended)

```python
from carver_feeds import get_client, create_data_manager, create_query_engine

# Auto-loads from .env
client = get_client()
dm = create_data_manager()
qe = create_query_engine()
```

### Direct Instantiation

```python
from carver_feeds import CarverFeedsAPIClient, FeedsDataManager, EntryQueryEngine

client = CarverFeedsAPIClient(api_key="your_key")
dm = FeedsDataManager(client)
qe = EntryQueryEngine(dm)
```

---

## Data Model Hierarchy

```
Topic (e.g., "Banking Regulation")
  ↓ 1:N
Feed (e.g., "SEC News Feed")
  ↓ 1:N
Entry (individual article/post)
```

**Key Relationships**:
- `feed.topic_id` → `topic.id`
- `entry.feed_id` → `feed.id` (only when fetched via feed-specific endpoints)

---

## Core API Methods

### FeedsDataManager

#### `get_topics_df() -> pd.DataFrame`
Fetch all topics as DataFrame.

**Returns**: DataFrame with columns: `id`, `name`, `description`, `created_at`, `updated_at`, `is_active`

```python
topics_df = dm.get_topics_df()
```

---

#### `get_feeds_df(topic_id: Optional[str] = None) -> pd.DataFrame`
Fetch feeds as DataFrame, optionally filtered by topic.

**Parameters**:
- `topic_id`: Filter by topic ID (optional, client-side filtering)

**Returns**: DataFrame with columns: `id`, `name`, `url`, `topic_id`, `topic_name`, `description`, `created_at`, `is_active`

```python
# All feeds
feeds_df = dm.get_feeds_df()

# Feeds for specific topic
topic_feeds = dm.get_feeds_df(topic_id="topic-123")
```

---

#### `get_entries_df(feed_id: Optional[str] = None, topic_id: Optional[str] = None, is_active: Optional[bool] = None, fetch_all: bool = True) -> pd.DataFrame`
Fetch entries as DataFrame with flexible filtering.

**Parameters**:
- `feed_id`: Filter by feed ID (uses optimized endpoint)
- `topic_id`: Filter by topic ID (uses optimized endpoint)
- `is_active`: Filter by active status
- `fetch_all`: Fetch all pages vs first page only

**Returns**: DataFrame with columns: `id`, `title`, `link`, `content_markdown`, `description`, `published_at`, `created_at`, `is_active`, `feed_id` (when available)

**Performance**:
- With `feed_id` or `topic_id`: Fast (~2-20s)
- Without filters + `fetch_all=True`: Slow (~30-60s, ~10,000 entries)

```python
# All entries (slow)
all_entries = dm.get_entries_df()

# Entries for specific feed (fast)
feed_entries = dm.get_entries_df(feed_id="feed-456")

# Entries for topic (medium speed)
topic_entries = dm.get_entries_df(topic_id="topic-123")
```

---

#### `get_hierarchical_view(include_entries: bool = True, feed_id: Optional[str] = None, topic_id: Optional[str] = None) -> pd.DataFrame`
Build denormalized hierarchical view combining topic, feed, and entry data.

**Parameters**:
- `include_entries`: Include entry data (default: True)
- `feed_id`: Filter to specific feed (fastest)
- `topic_id`: Filter to specific topic

**Returns**: DataFrame with prefixed columns: `topic_*`, `feed_*`, `entry_*`

**Column Examples**: `topic_id`, `topic_name`, `feed_id`, `feed_name`, `entry_id`, `entry_title`, `entry_content_markdown`

**Performance**:
- `feed_id` specified: 1 API call (fastest)
- `topic_id` specified: N API calls (N = number of feeds in topic)
- Neither specified: ~800+ API calls (very slow, not recommended)

```python
# Topic + Feed only (fast)
hierarchy = dm.get_hierarchical_view(include_entries=False)

# Full hierarchy for specific feed (fast)
full = dm.get_hierarchical_view(include_entries=True, feed_id="feed-456")

# Full hierarchy for topic (moderate)
topic_full = dm.get_hierarchical_view(include_entries=True, topic_id="topic-123")
```

---

### EntryQueryEngine (Recommended for Complex Queries)

#### `chain() -> EntryQueryEngine`
Reset query to start fresh with cached data.

```python
results1 = qe.filter_by_topic(topic_name="Banking").to_dataframe()
results2 = qe.chain().filter_by_topic(topic_name="Healthcare").to_dataframe()
```

---

#### `search_entries(keywords, search_fields=['entry_content_markdown'], case_sensitive=False, match_all=False) -> EntryQueryEngine`
Search entries by keywords across specified fields.

**Parameters**:
- `keywords`: Single keyword (str) or list of keywords
- `search_fields`: Fields to search in (default: `['entry_content_markdown']`)
  - Available: `entry_content_markdown`, `entry_title`, `entry_description`, `entry_link`
- `case_sensitive`: Case-sensitive search (default: False)
- `match_all`: ALL keywords must match (AND) vs ANY keyword (OR) (default: False)

```python
# Single keyword
results = qe.search_entries("regulation").to_dataframe()

# Multiple keywords (OR logic)
results = qe.search_entries(["banking", "finance"], match_all=False).to_dataframe()

# Multiple keywords (AND logic)
results = qe.search_entries(["banking", "regulation"], match_all=True).to_dataframe()

# Case-sensitive
results = qe.search_entries("SEC", case_sensitive=True).to_dataframe()

# Search specific fields
results = qe.search_entries("fintech", search_fields=['entry_title', 'entry_description']).to_dataframe()
```

---

#### `filter_by_topic(topic_id: Optional[str] = None, topic_name: Optional[str] = None) -> EntryQueryEngine`
Filter entries by topic.

**Parameters**:
- `topic_id`: Exact topic ID match
- `topic_name`: Partial topic name match, case-insensitive

```python
# By name (partial match)
results = qe.filter_by_topic(topic_name="Banking").to_dataframe()

# By ID (exact match)
results = qe.filter_by_topic(topic_id="topic-123").to_dataframe()
```

---

#### `filter_by_feed(feed_id: Optional[str] = None, feed_name: Optional[str] = None) -> EntryQueryEngine`
Filter entries by feed.

**Parameters**:
- `feed_id`: Exact feed ID match
- `feed_name`: Partial feed name match, case-insensitive

```python
# By name (partial match)
results = qe.filter_by_feed(feed_name="SEC News").to_dataframe()

# By ID (exact match)
results = qe.filter_by_feed(feed_id="feed-456").to_dataframe()
```

---

#### `filter_by_date(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> EntryQueryEngine`
Filter entries by publication date range.

**Parameters**:
- `start_date`: Start of date range, inclusive (optional)
- `end_date`: End of date range, inclusive (optional)

```python
from datetime import datetime

# Entries from 2024 onwards
results = qe.filter_by_date(start_date=datetime(2024, 1, 1)).to_dataframe()

# Entries in date range
results = qe.filter_by_date(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
).to_dataframe()
```

---

#### `filter_by_active(is_active: bool) -> EntryQueryEngine`
Filter entries by active status.

```python
results = qe.filter_by_active(is_active=True).to_dataframe()
```

---

### Export Methods

#### `to_dataframe() -> pd.DataFrame`
Export results as pandas DataFrame.

```python
df = qe.filter_by_topic(topic_name="Banking").to_dataframe()
```

#### `to_dict() -> List[Dict]`
Export results as list of dictionaries.

```python
entries = qe.filter_by_topic(topic_name="Banking").to_dict()
```

#### `to_json(indent: Optional[int] = None) -> str`
Export results as JSON string.

```python
json_str = qe.filter_by_topic(topic_name="Banking").to_json(indent=2)
```

#### `to_csv(filepath: str) -> str`
Export results to CSV file.

```python
csv_path = qe.filter_by_topic(topic_name="Banking").to_csv("banking.csv")
```

---

## Method Chaining Pattern

All query engine filter methods return `self`, enabling fluent method chaining:

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

**Best practice**: Apply filters in order of specificity (narrowest first) for optimal performance.

---

## Performance Optimization

### 1. Filter Before Loading

The query engine automatically uses optimized endpoints when you filter by topic or feed:

```python
# Optimal: Uses /topics/{id}/entries endpoint
results = qe.filter_by_topic(topic_name="Banking").to_dataframe()

# Optimal: Uses /feeds/{id}/entries endpoint
results = qe.filter_by_feed(feed_name="SEC News").to_dataframe()

# Less optimal: Loads all ~10,000 entries first
results = qe.to_dataframe()
```

### 2. Data Loading Times

| Operation | Volume | Time |
|-----------|--------|------|
| List topics | ~114 | < 1s |
| List feeds | ~827 | ~3-5s |
| List all entries | ~10,000 | ~30-60s |
| Entries for feed | Varies | ~2-10s |
| Entries for topic | Varies | ~5-20s |

### 3. Caching

Data is cached after first load. Use `chain()` to reset and reuse cached data:

```python
qe = create_query_engine()

# First query: loads data
results1 = qe.filter_by_topic(topic_name="Banking").to_dataframe()

# Subsequent queries: use cached data (instant)
results2 = qe.chain().filter_by_topic(topic_name="Healthcare").to_dataframe()
```

---

## Error Handling

### Exception Types

- `CarverAPIError`: Base exception for all API errors
- `AuthenticationError`: Invalid or missing API key (401/403)
- `RateLimitError`: Rate limit exceeded (429)

### Retry Logic

- Automatic exponential backoff for 429 (rate limit) and 500 (server error)
- Default: 3 retries with 2x backoff factor
- Configurable via `max_retries` and `initial_retry_delay` parameters

### Example

```python
from carver_feeds import get_client, CarverAPIError, AuthenticationError

try:
    client = get_client()
    topics = client.list_topics()
except AuthenticationError:
    print("Invalid API key. Check your .env file.")
except CarverAPIError as e:
    print(f"API error: {e}")
```

---

## Data Schemas

### Topic Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Unique topic identifier |
| `name` | str | Topic name |
| `description` | str | Topic description |
| `created_at` | datetime64 | Creation timestamp |
| `updated_at` | datetime64 | Last update timestamp |
| `is_active` | bool | Active status |

### Feed Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Unique feed identifier |
| `name` | str | Feed name |
| `url` | str | RSS feed URL |
| `topic_id` | str | Associated topic ID (foreign key) |
| `topic_name` | str | Associated topic name (denormalized) |
| `description` | str | Feed description |
| `created_at` | datetime64 | Creation timestamp |
| `is_active` | bool | Active status |

### Entry Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | str | Unique entry identifier |
| `title` | str | Entry headline |
| `link` | str | URL to original article |
| `content_markdown` | str | Full article content in markdown |
| `description` | str | Brief summary |
| `published_at` | datetime64 | Publication date |
| `created_at` | datetime64 | Creation timestamp in Carver system |
| `is_active` | bool | Active status |
| `feed_id` | str | Associated feed ID (only when fetched via feed endpoint) |

**Important**: `feed_id` is only present when entries are fetched via:
- `get_feed_entries(feed_id)`
- `get_hierarchical_view(feed_id=...)`

It is NOT present when fetched via:
- `list_entries()` (general entry list)
- `get_topic_entries(topic_id)` (topic-specific entries)

### Hierarchical View Schema

**Without entries** (`include_entries=False`):
- `topic_*`: id, name, description, created_at, updated_at, is_active
- `feed_*`: id, name, url, description, created_at, is_active

**With entries** (`include_entries=True`):
- `topic_*`: id, name, description, created_at, updated_at, is_active
- `feed_*`: id, name, url, description, created_at, is_active
- `entry_*`: id, title, link, content_markdown, description, published_at, created_at, is_active

---

## API Rate Limits

- **Standard**: 10 requests/second
- **Admin**: 5 requests/second

The SDK automatically handles rate limiting with exponential backoff retry logic.

---

## Additional Resources

- **PyPI Package**: https://pypi.org/project/carver-feeds-sdk/
- **GitHub Repository**: https://github.com/carveragents/carver-feeds-sdk
- **API Documentation**: https://app.carveragents.ai/api-docs/
- **Get API Key**: https://app.carveragents.ai

---

**Document Version**: 1.0
**SDK Version**: 0.1.0+
