import os, datetime
from xml.sax.saxutils import escape
from email.utils import format_datetime
from firecrawl import Firecrawl

app = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])

TOPIC = "artificial intelligence"
FEED_TITLE = "AI News Feed"
# Public URL where this feed will live (used in the <atom:link> self-reference)
FEED_SELF_URL = "https://raw.githubusercontent.com/dimitryvolos/news-feed/master/feed.xml"

# sources=["news"] returns individual articles, not archive/landing pages
result = app.search(query=TOPIC, sources=["news"], limit=20)

news_results = getattr(result, "news", None)
if news_results is None and isinstance(result, dict):
    news_results = result.get("news", [])
news_results = news_results or []

def field(r, key):
    return getattr(r, key, None) or (r.get(key) if isinstance(r, dict) else None) or ""

def to_rfc822(value):
    """Convert whatever date the API gives into RFC-822 (RSS standard)."""
    if not value:
        return None
    try:
        # handles ISO strings like 2026-05-28T15:46:42Z
        dt = datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return format_datetime(dt)
    except Exception:
        return None

now = format_datetime(datetime.datetime.now(datetime.timezone.utc))

items_xml = []
for r in news_results:
    title = escape(field(r, "title") or "Untitled")
    link = escape(field(r, "url"))
    desc = escape(field(r, "description") or field(r, "snippet") or "")
    if not link:
        continue
    pub = to_rfc822(field(r, "date") or field(r, "publishedDate"))
    pubdate_tag = f"      <pubDate>{pub}</pubDate>\n" if pub else ""
    items_xml.append(
        "    <item>\n"
        f"      <title>{title}</title>\n"
        f"      <link>{link}</link>\n"
        f"      <guid isPermaLink=\"true\">{link}</guid>\n"
        f"      <description>{desc}</description>\n"
        f"{pubdate_tag}"
        "    </item>"
    )

rss = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
    "  <channel>\n"
    f"    <title>{escape(FEED_TITLE)}</title>\n"
    f"    <link>https://github.com/dimitryvolos/news-feed</link>\n"
    f"    <description>Latest news on {escape(TOPIC)}</description>\n"
    f"    <language>en</language>\n"
    f"    <lastBuildDate>{now}</lastBuildDate>\n"
    f'    <atom:link href="{escape(FEED_SELF_URL)}" rel="self" type="application/rss+xml" />\n'
    + "\n".join(items_xml) + "\n"
    "  </channel>\n"
    "</rss>\n"
)

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)

print(f"Wrote {len(items_xml)} items to feed.xml")