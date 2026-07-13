"""
Hesion Content Pipeline - Story Discovery & Enrichment
Fetches leadership-relevant news, analyzes org psych angle via Claude, scores quality.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
import feedparser
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
client = Anthropic()

# ============================================================================
# CONFIGURATION
# ============================================================================

# RSS Feed URLs - business & leadership focused (no political news)
RSS_FEEDS = {
    # Business & Leadership (verified working)
    "HBR": "http://feeds.hbr.org/harvardbusiness",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CNBC Business": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "CNBC CEO": "https://www.cnbc.com/id/19206666/device/rss/rss.html",
    "NYT Business RSS": "https://feeds.nytimes.com/services/xml/rss/nyt/Business.xml",
    "BBC Business": "https://www.bbc.com/news/business/rss.xml",
    "MIT Sloan": "https://mitsloan.mit.edu/feed",
    "Fast Company": "https://www.fastcompany.com/latest/rss",
    "Inc": "https://www.inc.com/rss",
    "SHRM": "https://www.shrm.org/rss",
    
    # Google News workarounds (for sources that killed their RSS)
    "Reuters via Google": "https://news.google.com/rss/search?q=site:reuters.com+when:3d&hl=en-US&gl=US&ceid=US:en",
    "WSJ via Google": "https://news.google.com/rss/search?q=site:wsj.com+when:3d&hl=en-US&gl=US&ceid=US:en",
    "Reuters CEO via Google": "https://news.google.com/rss/search?q=CEO+site:reuters.com+when:7d&hl=en-US&gl=US&ceid=US:en",
    "Reuters Mgmt via Google": "https://news.google.com/rss/search?q=management+site:reuters.com+when:7d&hl=en-US&gl=US&ceid=US:en",
    "Reuters Leadership via Google": "https://news.google.com/rss/search?q=leadership+site:reuters.com+when:7d&hl=en-US&gl=US&ceid=US:en",
    
    # Tech & Culture
    "TechCrunch": "https://techcrunch.com/feed/",
    "Hacker News": "https://news.ycombinator.com/rss",
    
    # Leadership & Management
    "Fortune": "https://fortune.com/feed/fortune-feeds/?id=3230629",
}

# API Keys from .env
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NYT_API_KEY = os.getenv("NYT_API_KEY")
CROSSREF_EMAIL = os.getenv("CROSSREF_EMAIL")

# Paths
STORIES_DIR = Path("stories")
STORIES_DIR.mkdir(exist_ok=True)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def sanitize_filename(title):
    """Convert story title to safe filename."""
    # Remove special characters, keep alphanumeric and hyphens
    safe_name = re.sub(r'[^\w\s-]', '', title)
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    return safe_name[:50].lower()  # Limit to 50 chars

def story_exists(filename_base):
    """Check if story markdown already exists (avoid duplicates)."""
    filepath = STORIES_DIR / f"{filename_base}.md"
    return filepath.exists()

def prefilter(story):
    keywords = [
        "leadership",
        "manager",
        "CEO",
        "culture",
        "employee",
        "team",
        "workplace",
        "organization",
        "psychology",
        "AI",
    ]

    text = (
        story["title"] + " " + story["summary"]
    ).lower()

    return any(k in text for k in keywords)

def get_claude_enrichment(story_text, source):
    """
    Send story to Claude for enrichment.
    Returns: dict with summary, angle, and strength_score (1-10)
    """
    prompt = f"""You are analyzing a news story for leadership and organizational psychology insights.

IMPORTANT: Skip stories that are primarily about electoral politics, politicians' personal actions, or political opinion/commentary (e.g., Trump's latest statement, congressional voting, partisan disputes). 

Exception: If a story is about *organizational dynamics* within a political or corporate entity (e.g., internal conflict, decision-making, leadership challenges), that's fair game—evaluate it on org psych merit, not political affiliation.

Otherwise, focus on business, tech, corporate culture, and organizational behavior stories.

Story Title & Summary:
{story_text}

Source: {source}

Please provide ONLY a JSON response (no other text, no markdown, no backticks) with these exact fields:
{{
  "summary": "1-2 sentence summary of the story",
  "org_psych_angle": "The organizational psychology or leadership insight (1-2 sentences). If no clear angle exists, say 'No clear angle.'",
  "strength_score": <number 1-10 where 10 = perfect org psych fit, 1 = no relevance>,
  "reasoning": "Brief explanation of why this score"
}}

Be critical. Only score 6+ if there's a genuine, non-forced organizational psychology connection.
"""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse JSON from response
        response_text = response.content[0].text
        
        # Strip markdown backticks if Claude wrapped it
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        
        response_text = response_text.strip()
        
        enrichment = json.loads(response_text)
        return enrichment
    
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"  ⚠️ Claude API error: {e}")
        return None

# ============================================================================
# STORY FETCHERS
# ============================================================================

def fetch_rss_stories():
    """Fetch stories from all RSS feeds."""
    all_stories = []
    
    print("\n📰 Fetching from RSS feeds...")
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            print(f"  Fetching {source_name}...", end=" ")
            feed = feedparser.parse(feed_url)
            
            # Get top 5 most recent entries from each feed
            for entry in feed.entries[:10]:
                story = {
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "source": source_name,
                    "published": entry.get("published", ""),
                }
                all_stories.append(story)
            
            print(f"✓ Got {len(feed.entries[:10])} stories")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return all_stories

def fetch_nyt_top_stories():
    """Fetch from NYT Top Stories API (Business section)."""
    all_stories = []
    
    print("\n📰 Fetching from NYT Top Stories API...")
    try:
        url = f"https://api.nytimes.com/svc/topstories/v2/business.json?api-key={NYT_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Get top 5 results
        for article in data.get("results", [])[:5]:
            story = {
                "title": article.get("title", "No title"),
                "link": article.get("url", ""),
                "summary": article.get("abstract", ""),
                "source": "NYT Top Stories",
                "published": article.get("published_date", ""),
            }
            all_stories.append(story)
        
        print(f"  ✓ Got {len(data.get('results', [])[:5])} stories")
    except Exception as e:
        print(f"  ✗ Error fetching NYT Top Stories: {e}")
    
    return all_stories

def fetch_nyt_most_popular():
    """Fetch from NYT Most Popular API (most viewed articles in past 7 days)."""
    all_stories = []
    
    print("\n📰 Fetching from NYT Most Popular API...")
    try:
        url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json?api-key={NYT_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Get top 5 results
        for article in data.get("results", [])[:5]:
            story = {
                "title": article.get("title", "No title"),
                "link": article.get("url", ""),
                "summary": article.get("abstract", ""),
                "source": "NYT Most Popular",
                "published": article.get("published_date", ""),
            }
            all_stories.append(story)
        
        print(f"  ✓ Got {len(data.get('results', [])[:5])} stories")
    except Exception as e:
        print(f"  ✗ Error fetching NYT Most Popular: {e}")
    
    return all_stories

def fetch_crossref_journals():
    """Fetch org psych research from CrossRef API."""
    from datetime import timedelta
    
    all_stories = []
    
    print("\n📚 Fetching from CrossRef (org psych journals)...")
    
    # Calculate date from 7 days ago
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Search terms for org psych research
    search_terms = [
        "psychological safety",
        "organizational culture",
        "leadership effectiveness",
        "team dynamics",
    ]
    
    for term in search_terms:
        try:
            # CrossRef API - get recent articles matching search term
            url = "https://api.crossref.org/v1/works"
            params = {
                "query": term,
                "order": "desc",
                "sort": "published",
                "rows": 2,
                "mailto": CROSSREF_EMAIL,
                "from-pub-date": one_week_ago,  # Always pulls past 7 days
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("message", {}).get("items", []):
                story = {
                    "title": item.get("title", ["No title"])[0] if isinstance(item.get("title"), list) else item.get("title", "No title"),
                    "link": item.get("URL", ""),
                    "summary": f"Published in {item.get('container-title', ['Unknown Journal'])[0]}. DOI: {item.get('DOI', 'N/A')}",
                    "source": "CrossRef Journal",
                    "published": item.get("published-online", {}).get("date-parts", [[]])[0],
                }
                all_stories.append(story)
            
            print(f"  ✓ Got {len(data.get('message', {}).get('items', [])[:2])} articles for '{term}'")
        except Exception as e:
            print(f"  ✗ Error fetching CrossRef for '{term}': {e}")
    
    return all_stories

# ============================================================================
# SAVE STORY AS MARKDOWN
# ============================================================================

def save_story_markdown(story, enrichment, filepath):
    """Save story + enrichment as markdown file."""
    
    markdown_content = f"""# {story['title']}

**Source:** {story['source']}  
**Published:** {story['published']}  
**URL:** [{story['link']}]({story['link']})

## Summary
{enrichment['summary']}

## Organizational Psychology Angle
{enrichment['org_psych_angle']}

## Strength Score
**{enrichment['strength_score']}/10** — {enrichment['reasoning']}

## Original Story Summary
{story['summary']}

---

**Status:** Pending review  
**Discovered:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"  ✓ Saved: {filepath.name}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("HESION CONTENT PIPELINE - Story Discovery & Enrichment")
    print("=" * 70)
    
    # Fetch all stories from all sources
    stories = []
    stories.extend(fetch_rss_stories())
    stories.extend(fetch_nyt_top_stories())
    stories.extend(fetch_nyt_most_popular())
    stories.extend(fetch_crossref_journals())
    
    print(f"\n📊 Total stories fetched: {len(stories)}")
    
    stories = [s for s in stories if prefilter(s)]

    print(f"🎯 After keyword filtering: {len(stories)}")
    
    # Enrich each story with Claude
    print("\n🧠 Enriching stories with Claude...")
    saved_count = 0
    skipped_count = 0
    
    for i, story in enumerate(stories, 1):
        print(f"\n  [{i}/{len(stories)}] Processing: {story['title'][:60]}...")
        
        # Check if already exists
        filename_base = sanitize_filename(story['title'])
        if story_exists(filename_base):
            print(f"    ⊘ Already exists, skipping")
            skipped_count += 1
            continue
        
        # Get Claude enrichment
        story_text = f"{story['title']}\n\n{story['summary']}"
        enrichment = get_claude_enrichment(story_text, story['source'])
        
        if enrichment is None:
            print(f"    ✗ Failed to enrich")
            skipped_count += 1
            continue
        
        # Check strength score
        strength = enrichment.get('strength_score', 0)
        if strength < 6:
            print(f"    ⊘ Score {strength}/10 - Below threshold, skipping")
            skipped_count += 1
            continue
        
        # Save markdown file
        filepath = STORIES_DIR / f"{filename_base}.md"
        save_story_markdown(story, enrichment, filepath)
        saved_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✓ COMPLETE")
    print(f"  Saved: {saved_count} stories")
    print(f"  Skipped: {skipped_count} stories")
    print(f"  Stories location: {STORIES_DIR.absolute()}")
    print("=" * 70)

if __name__ == "__main__":
    main()
