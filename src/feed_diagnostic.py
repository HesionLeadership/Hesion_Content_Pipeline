"""
Feed Diagnostic - Tests each RSS feed to see which are alive and how many stories they return.
Run this standalone to check feed health. Does NOT touch your stories folder or use any API keys.
"""

import feedparser

# Same feeds as the main pipeline - keep this list in sync with story_discovery.py
RSS_FEEDS = {
    # Business & Leadership
    "HBR": "https://feeds.hbr.org/harvardbusinessreview",
    "Reuters Finance": "https://feeds.reuters.com/finance",
    "Reuters Technology": "https://feeds.reuters.com/technology",
    "Reuters Business": "https://feeds.reuters.com/business",
    "WSJ Business": "https://feeds.wsj.com/xml/rss/3_7085.xml",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CNBC": "https://feeds.cnbc.com/id/100003114/device/rss/rss.html",
    "USA Today": "https://www.usatoday.com/money/usaedition.xml",
    "BBC Business": "https://www.bbc.com/news/business/rss.xml",
    "NYT Business RSS": "https://feeds.nytimes.com/services/xml/rss/nyt/Business.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Hacker News": "https://news.ycombinator.com/rss",
}

print("=" * 70)
print("FEED DIAGNOSTIC - Checking each RSS feed")
print("=" * 70)

alive = []
dead = []

for source_name, feed_url in RSS_FEEDS.items():
    print(f"\n{source_name}")
    print(f"  URL: {feed_url}")
    try:
        feed = feedparser.parse(feed_url)
        count = len(feed.entries)

        # feedparser sets .bozo = 1 when the feed is malformed or failed to parse
        if feed.bozo:
            bozo_msg = str(feed.get("bozo_exception", "unknown parse issue"))
            print(f"  ⚠️ WARNING: parse issue - {bozo_msg}")

        # HTTP status if available
        status = feed.get("status", "N/A")
        print(f"  HTTP status: {status}")
        print(f"  Stories returned: {count}")

        if count > 0:
            # Show the newest headline + its date so you can eyeball freshness
            newest = feed.entries[0]
            title = newest.get("title", "No title")
            published = newest.get("published", "No date")
            print(f"  Newest: \"{title[:60]}\"")
            print(f"  Dated:  {published}")
            alive.append((source_name, count))
        else:
            dead.append(source_name)

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        dead.append(source_name)

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\n✓ WORKING FEEDS ({len(alive)}):")
for name, count in sorted(alive, key=lambda x: x[1], reverse=True):
    print(f"    {name}: {count} stories")

print(f"\n✗ DEAD / EMPTY FEEDS ({len(dead)}):")
if dead:
    for name in dead:
        print(f"    {name}")
else:
    print("    None - all feeds are alive!")

print("\n" + "=" * 70)
