"""
app.py - X Auto Tool Web アプリ

起動方法:
    uvicorn app:app --reload

エンドポイント:
    GET  /             メインページ
    POST /api/trends   トレンド取得
    POST /api/generate ツイート生成（content_generator.py が必要）
    POST /api/post     X に投稿（x_poster.py が必要）
"""

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

load_dotenv()

# オプションモジュールの動的インポート
try:
    from content_generator import generate_tweet as _generate_tweet
    HAS_CONTENT_GENERATOR = True
except ImportError:
    HAS_CONTENT_GENERATOR = False

try:
    from x_poster import post_tweet as _post_tweet
    HAS_X_POSTER = True
except ImportError:
    HAS_X_POSTER = False

from trend_fetcher import fetch_trends

app = FastAPI(title="X Auto Tool")
templates = Jinja2Templates(directory="templates")

PRESET_SOURCES = [
    # --- Google News ---
    {
        "id": "google_news_japan",
        "label": "Google News — 日本 総合",
        "url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",
        "group": "Google News",
    },
    {
        "id": "google_news_tech",
        "label": "Google News — テクノロジー",
        "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja",
        "group": "Google News",
    },
    {
        "id": "google_news_business",
        "label": "Google News — ビジネス",
        "url": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja",
        "group": "Google News",
    },
    {
        "id": "google_news_entertainment",
        "label": "Google News — エンタメ",
        "url": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=ja&gl=JP&ceid=JP:ja",
        "group": "Google News",
    },
    {
        "id": "google_news_sports",
        "label": "Google News — スポーツ",
        "url": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=ja&gl=JP&ceid=JP:ja",
        "group": "Google News",
    },
    # --- 日本語メディア（公式 RSS あり）---
    {
        "id": "gigazine",
        "label": "Gigazine",
        "url": "https://gigazine.net/news/rss_2.0/",
        "group": "日本語メディア",
    },
    # --- 英語メディア（公式 RSS あり）---
    {
        "id": "reuters",
        "label": "Reuters — Top News",
        "url": "https://feeds.reuters.com/reuters/topNews",
        "group": "英語メディア",
    },
    {
        "id": "techcrunch",
        "label": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "group": "英語メディア",
    },
    {
        "id": "theverge",
        "label": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "group": "英語メディア",
    },
    {
        "id": "producthunt",
        "label": "Product Hunt",
        "url": "https://www.producthunt.com/feed",
        "group": "英語メディア",
    },
    # --- カスタム ---
    {
        "id": "custom",
        "label": "カスタム RSS URL",
        "url": "",
        "group": "カスタム",
    },
]


# ---------- Routes ----------


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "preset_sources": PRESET_SOURCES,
            "has_content_generator": HAS_CONTENT_GENERATOR,
            "has_x_poster": HAS_X_POSTER,
        },
    )


# ---------- API ----------


class FetchTrendsRequest(BaseModel):
    source_url: str
    topics: Optional[list[str]] = None  # 複数キーワード（OR マッチ）
    max_items: int = 10


class GenerateTweetRequest(BaseModel):
    trends: list[dict]


class PostTweetRequest(BaseModel):
    tweet: str


@app.post("/api/trends")
async def api_fetch_trends(req: FetchTrendsRequest):
    try:
        trends = fetch_trends(
            source_url=req.source_url,
            topics=req.topics or None,
            max_items=req.max_items,
        )
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def api_generate_tweet(req: GenerateTweetRequest):
    if not HAS_CONTENT_GENERATOR:
        raise HTTPException(
            status_code=501,
            detail="content_generator.py が見つかりません。先に実装してください。",
        )
    try:
        tweet = _generate_tweet(req.trends)
        return {"tweet": tweet}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/post")
async def api_post_tweet(req: PostTweetRequest):
    if not HAS_X_POSTER:
        raise HTTPException(
            status_code=501,
            detail="x_poster.py が見つかりません。先に実装してください。",
        )
    try:
        result = _post_tweet(req.tweet)
        return {"success": True, "result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
