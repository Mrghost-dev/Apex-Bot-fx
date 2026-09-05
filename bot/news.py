
import os
import urllib.parse
import requests
import feedparser
from datetime import datetime
from .config import load_config

def _google_news(query):
    q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    out = []
    for e in feed.entries[:8]:
        out.append({
            "title": e.get("title",""),
            "source": e.get("source",{}).get("title","Google News") if isinstance(e.get("source"), dict) else "Google News",
            "published": e.get("published",""),
            "url": e.get("link",""),
            "impact": "Potentially relevant macro/market headline; verify economic calendar importance before trading."
        })
    return out

def _newsapi(query, key):
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "apiKey": key, "language":"en", "pageSize": 8, "sortBy":"publishedAt"}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return [{
        "title": a.get("title",""),
        "source": a.get("source",{}).get("name","NewsAPI"),
        "published": a.get("publishedAt",""),
        "url": a.get("url",""),
        "impact": "Headline context from NewsAPI; assess whether it is high-impact before execution."
    } for a in data.get("articles",[])]

def _finnhub(query, key):
    url = "https://finnhub.io/api/v1/news"
    params = {"category":"general","token":key}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    return [{
        "title": a.get("headline",""),
        "source": a.get("source","Finnhub"),
        "published": datetime.fromtimestamp(a.get("datetime",0)).isoformat() if a.get("datetime") else "",
        "url": a.get("url",""),
        "impact": "Market headline from Finnhub; map it to the instrument before acting."
    } for a in data[:8]]

def collect_news(symbol):
    cfg = load_config()
    query = f"{symbol} forex gold markets USD Federal Reserve CPI NFP"
    results = []
    if cfg["NEWSAPI_KEY"]:
        try: results.extend(_newsapi(query, cfg["NEWSAPI_KEY"]))
        except Exception: pass
    if cfg["FINNHUB_API_KEY"]:
        try: results.extend(_finnhub(query, cfg["FINNHUB_API_KEY"]))
        except Exception: pass
    try: results.extend(_google_news(query))
    except Exception: pass

    seen = set()
    unique = []
    for item in results:
        key = item["title"].strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:16]
