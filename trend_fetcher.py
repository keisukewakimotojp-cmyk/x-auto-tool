"""
trend_fetcher.py - トレンド・ネタを外部から取得する

現在サポートしているソース:
    - rss: RSSフィードからニュースを取得

将来的に追加予定:
    - google_trends: pytrends で急上昇ワードを取得
    - custom: 独自エンドポイントから取得
"""

import os
import feedparser


MAX_ITEMS = 10  # デフォルトの取得件数


def fetch_trends(
    source: str = None,
    source_url: str = None,
    topics: list[str] = None,
    max_items: int = None,
) -> list[dict]:
    """
    トレンドを取得する。

    Args:
        source:     ソース種別（現在は "rss" のみ）。未指定時は環境変数 TREND_SOURCE を参照。
        source_url: RSSフィードのURL。未指定時は環境変数 TREND_RSS_URL を参照。
        topics:     キーワードリスト（いずれかにマッチする記事のみ取得 / OR 条件）。
        max_items:  取得件数上限。未指定時は MAX_ITEMS。

    Returns:
        [{"title": str, "url": str, "summary": str}, ...]
    """
    source = source or os.getenv("TREND_SOURCE", "rss")

    if source == "rss" or source_url:
        return _fetch_from_rss(url=source_url, topics=topics, max_items=max_items)

    raise NotImplementedError(f"TREND_SOURCE='{source}' is not supported yet.")


def _fetch_from_rss(
    url: str = None,
    topics: list[str] = None,
    max_items: int = None,
) -> list[dict]:
    """RSSフィードからニュース記事を取得する。"""
    url = url or os.getenv(
        "TREND_RSS_URL",
        "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",
    )
    max_items = max_items or MAX_ITEMS

    feed = feedparser.parse(url)

    if not feed.entries:
        raise RuntimeError(f"RSSフィードからデータを取得できませんでした: {url}")

    entries = feed.entries

    if topics:
        keywords = [kw.lower() for kw in topics]
        entries = [
            e for e in entries
            if any(
                kw in (e.get("title", "") + " " + e.get("summary", "")).lower()
                for kw in keywords
            )
        ]

    trends = []
    for entry in entries[:max_items]:
        trends.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
        })

    return trends
