"""
trend_fetcher.py - トレンド・ネタを外部から取得する

現在サポートしているソース:
    - rss: RSSフィードからニュースを取得（デフォルト: Google News Japan）

将来的に追加予定:
    - google_trends: pytrends で急上昇ワードを取得
    - custom: 独自エンドポイントから取得
"""

import os
import feedparser


MAX_ITEMS = 5  # 取得するトレンド件数


def fetch_trends() -> list[dict]:
    """
    環境変数 TREND_SOURCE に応じてトレンドを取得する。

    Returns:
        [{"title": str, "url": str, "summary": str}, ...]
    """
    source = os.getenv("TREND_SOURCE", "rss")

    if source == "rss":
        return _fetch_from_rss()

    # Future: google_trends / custom
    raise NotImplementedError(f"TREND_SOURCE='{source}' is not supported yet.")


def _fetch_from_rss() -> list[dict]:
    """RSSフィードからニュース記事を取得する。"""
    url = os.getenv("TREND_RSS_URL", "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja")
    feed = feedparser.parse(url)

    if not feed.entries:
        raise RuntimeError(f"RSSフィードからデータを取得できませんでした: {url}")

    trends = []
    for entry in feed.entries[:MAX_ITEMS]:
        trends.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
        })

    return trends
