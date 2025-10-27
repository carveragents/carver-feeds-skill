#!/usr/bin/env python3
"""
Common query templates for Carver Feeds SDK.

This module provides pre-built query patterns for common regulatory monitoring tasks.
Each function demonstrates a specific workflow and can be customized for your needs.
"""

from carver_feeds import create_query_engine, create_data_manager
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd


def list_available_topics() -> pd.DataFrame:
    """
    List all available regulatory topics.

    Returns:
        DataFrame with topic information (id, name, description, is_active)
    """
    dm = create_data_manager()
    topics_df = dm.get_topics_df()

    print(f"📋 Found {len(topics_df)} topics")
    print(f"   Active: {topics_df['is_active'].sum()}")
    print(f"   Inactive: {(~topics_df['is_active']).sum()}\n")

    return topics_df[['id', 'name', 'description', 'is_active']]


def search_by_keyword(
    keyword: str,
    topic_name: Optional[str] = None,
    days_back: int = 30
) -> pd.DataFrame:
    """
    Search for entries containing a specific keyword.

    Args:
        keyword: Keyword to search for
        topic_name: Optional topic filter (partial name match)
        days_back: Number of days to search back (default: 30)

    Returns:
        DataFrame with matching entries
    """
    qe = create_query_engine()
    start_date = datetime.now() - timedelta(days=days_back)

    query = qe.filter_by_date(start_date=start_date)

    if topic_name:
        query = query.filter_by_topic(topic_name=topic_name)

    results = query.search_entries(keyword).to_dataframe()

    print(f"🔍 Found {len(results)} entries for '{keyword}'")
    if topic_name:
        print(f"   Topic filter: {topic_name}")
    print(f"   Date range: Last {days_back} days\n")

    return results


def get_recent_updates_by_topic(
    topic_name: str,
    days_back: int = 7
) -> pd.DataFrame:
    """
    Get recent regulatory updates for a specific topic.

    Args:
        topic_name: Topic to search (partial name match)
        days_back: Number of days to look back (default: 7)

    Returns:
        DataFrame with recent entries for the topic
    """
    qe = create_query_engine()
    start_date = datetime.now() - timedelta(days=days_back)

    results = qe \
        .filter_by_topic(topic_name=topic_name) \
        .filter_by_date(start_date=start_date) \
        .filter_by_active(is_active=True) \
        .to_dataframe()

    print(f"📰 Recent {topic_name} updates (last {days_back} days):")
    print(f"   Total entries: {len(results)}")

    if len(results) > 0:
        print(f"   Date range: {results['entry_published_at'].min().date()} to {results['entry_published_at'].max().date()}")
        print(f"   Unique feeds: {results['feed_name'].nunique()}\n")

    return results


def monitor_keywords_across_topics(
    keywords: List[str],
    topics: List[str],
    match_all: bool = False,
    days_back: int = 30
) -> pd.DataFrame:
    """
    Monitor multiple keywords across multiple topics.

    Args:
        keywords: List of keywords to search for
        topics: List of topic names (partial matches)
        match_all: If True, entries must match ALL keywords (AND logic)
                  If False, entries match ANY keyword (OR logic)
        days_back: Number of days to search back

    Returns:
        DataFrame with matching entries
    """
    qe = create_query_engine()
    start_date = datetime.now() - timedelta(days=days_back)

    all_results = []

    for topic in topics:
        results = qe.chain() \
            .filter_by_topic(topic_name=topic) \
            .filter_by_date(start_date=start_date) \
            .search_entries(keywords, match_all=match_all) \
            .to_dataframe()

        if len(results) > 0:
            all_results.append(results)

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        logic = "ALL" if match_all else "ANY"
        print(f"🎯 Keyword monitoring results ({logic} of {keywords}):")
        print(f"   Total matches: {len(combined)}")
        print(f"   Topics searched: {len(topics)}")
        print(f"   Date range: Last {days_back} days\n")
        return combined
    else:
        print(f"No matches found for keywords: {keywords}")
        return pd.DataFrame()


def compare_topic_activity(
    topics: List[str],
    days_back: int = 30
) -> pd.DataFrame:
    """
    Compare regulatory activity across multiple topics.

    Args:
        topics: List of topic names to compare
        days_back: Number of days to analyze

    Returns:
        DataFrame with comparison metrics
    """
    qe = create_query_engine()
    start_date = datetime.now() - timedelta(days=days_back)

    comparison_data = []

    for topic in topics:
        results = qe.chain() \
            .filter_by_topic(topic_name=topic) \
            .filter_by_date(start_date=start_date) \
            .filter_by_active(is_active=True) \
            .to_dataframe()

        if len(results) > 0:
            comparison_data.append({
                'Topic': topic,
                'Total Entries': len(results),
                'Active Feeds': results['feed_name'].nunique(),
                'Avg Entries/Day': round(len(results) / days_back, 2),
                'Date Range': f"{results['entry_published_at'].min().date()} to {results['entry_published_at'].max().date()}"
            })

    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('Total Entries', ascending=False)

        print(f"📊 Topic activity comparison (last {days_back} days):\n")
        print(comparison_df.to_string(index=False))
        print()

        return comparison_df
    else:
        print("No data found for the specified topics")
        return pd.DataFrame()


def export_feed_entries(
    feed_name: str,
    output_format: str = 'csv',
    output_path: Optional[str] = None
) -> str:
    """
    Export all entries from a specific feed.

    Args:
        feed_name: Name of the feed (partial match)
        output_format: Format for export ('csv', 'json', or 'dataframe')
        output_path: Custom output path (optional)

    Returns:
        Path to exported file or 'dataframe' string
    """
    qe = create_query_engine()

    results = qe.filter_by_feed(feed_name=feed_name)

    if output_format == 'csv':
        path = output_path or f"{feed_name.lower().replace(' ', '_')}_entries.csv"
        results.to_csv(path)
        print(f"📄 Exported to CSV: {path}")
        return path

    elif output_format == 'json':
        path = output_path or f"{feed_name.lower().replace(' ', '_')}_entries.json"
        with open(path, 'w') as f:
            f.write(results.to_json(indent=2))
        print(f"📄 Exported to JSON: {path}")
        return path

    elif output_format == 'dataframe':
        df = results.to_dataframe()
        print(f"📊 Returned DataFrame: {len(df)} rows × {len(df.columns)} columns")
        return 'dataframe'

    else:
        raise ValueError(f"Unsupported format: {output_format}. Use 'csv', 'json', or 'dataframe'")


def daily_regulatory_brief(
    topics: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Generate a daily brief of regulatory updates.

    Args:
        topics: Optional list of topics to include (if None, includes all)

    Returns:
        DataFrame with yesterday's regulatory updates
    """
    qe = create_query_engine()
    yesterday = datetime.now() - timedelta(days=1)
    today = datetime.now()

    query = qe.filter_by_date(start_date=yesterday, end_date=today).filter_by_active(is_active=True)

    if topics:
        all_results = []
        for topic in topics:
            results = qe.chain() \
                .filter_by_topic(topic_name=topic) \
                .filter_by_date(start_date=yesterday, end_date=today) \
                .filter_by_active(is_active=True) \
                .to_dataframe()
            if len(results) > 0:
                all_results.append(results)

        if all_results:
            results = pd.concat(all_results, ignore_index=True)
        else:
            results = pd.DataFrame()
    else:
        results = query.to_dataframe()

    if len(results) > 0:
        print(f"📅 Daily regulatory brief for {yesterday.strftime('%Y-%m-%d')}:")
        print(f"   Total updates: {len(results)}")
        print(f"   Topics covered: {results['topic_name'].nunique()}")
        print(f"   Active feeds: {results['feed_name'].nunique()}\n")

        topic_summary = results.groupby('topic_name').size().sort_values(ascending=False)
        print("   Updates by topic:")
        for topic, count in topic_summary.items():
            print(f"     - {topic}: {count}")
        print()
    else:
        print(f"No regulatory updates found for {yesterday.strftime('%Y-%m-%d')}")

    return results


# Example usage
if __name__ == "__main__":
    print("🚀 Carver Feeds SDK - Query Templates\n")
    print("=" * 60)

    # Example 1: List topics
    print("\n1️⃣  Listing available topics...")
    topics = list_available_topics()
    print(topics.head(10))

    # Example 2: Search by keyword
    print("\n2️⃣  Searching for 'regulation' in Banking...")
    results = search_by_keyword("regulation", topic_name="Banking", days_back=30)
    if len(results) > 0:
        print(results[['entry_title', 'feed_name', 'entry_published_at']].head())

    # Example 3: Recent updates
    print("\n3️⃣  Getting recent Banking updates...")
    recent = get_recent_updates_by_topic("Banking", days_back=7)
    if len(recent) > 0:
        print(recent[['entry_title', 'entry_published_at']].head())

    print("\n" + "=" * 60)
    print("✅ Template examples complete!")
    print("\n📚 Available templates:")
    print("   - list_available_topics()")
    print("   - search_by_keyword(keyword, topic_name, days_back)")
    print("   - get_recent_updates_by_topic(topic_name, days_back)")
    print("   - monitor_keywords_across_topics(keywords, topics, match_all, days_back)")
    print("   - compare_topic_activity(topics, days_back)")
    print("   - export_feed_entries(feed_name, output_format, output_path)")
    print("   - daily_regulatory_brief(topics)")
