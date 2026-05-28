import json, os, datetime
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
TOPIC = "artificial intelligence"

result = app.search(query=f"{TOPIC} news", params={"limit": 20})

articles = [
    {"title": r.get("title", ""), "link": r.get("url", "")}
    for r in result.get("data", [])
]

feed = {
    "topic": TOPIC,
    "updated": datetime.datetime.utcnow().isoformat() + "Z",
    "articles": articles,
}

with open("feed.json", "w") as f:
    json.dump(feed, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(articles)} articles")