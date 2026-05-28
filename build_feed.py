import json, os, datetime
from firecrawl import Firecrawl

app = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
TOPIC = "artificial intelligence"

result = app.search(query=f"{TOPIC} news", limit=20)

# v2 SDK returns an object; web results are under .web
web_results = result.web if hasattr(result, "web") else result.get("web", [])

articles = []
for r in web_results:
    title = getattr(r, "title", None) or (r.get("title") if isinstance(r, dict) else "")
    url = getattr(r, "url", None) or (r.get("url") if isinstance(r, dict) else "")
    articles.append({"title": title, "link": url})

feed = {
    "topic": TOPIC,
    "updated": datetime.datetime.utcnow().isoformat() + "Z",
    "articles": articles,
}

with open("feed.json", "w") as f:
    json.dump(feed, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(articles)} articles")