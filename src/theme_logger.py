"""
Hesion Theme Logger
Extracts themes from saved stories and logs them to a JSON file.
Runs daily after story discovery. Accumulates data over time.
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

STORIES_DIR = Path("reports")
THEMES_DIR = Path("reports")
THEME_LOG_PATH = THEMES_DIR / f"THEMES_{datetime.now().strftime('%Y-%m-%d')}.json"

def load_theme_log():
    """Load all existing theme logs and merge them."""
    combined = {"entries": []}
    for f in THEMES_DIR.glob("THEMES_*.json"):
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            combined["entries"].extend(data.get("entries", []))
    return combined

def save_theme_log(log):
    """Save theme log to disk."""
    with open(THEME_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def get_already_logged_files(log):
    """Return set of filenames already in the log."""
    logged = set()
    for entry in log["entries"]:
        logged.add(entry.get("filename", ""))
    return logged

def extract_themes_from_stories(story_files):
    """Send batch of story titles/summaries to Claude for theme extraction."""
    
    stories_text = ""
    filenames = []
    for filepath in story_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Unknown"
        
        summary_match = re.search(r'## Summary\n(.+?)(?=\n##)', content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        lesson_match = re.search(r'## Leadership Lesson\n(.+?)(?=\n##)', content, re.DOTALL)
        lesson = lesson_match.group(1).strip() if lesson_match else ""
        
        stories_text += f"Title: {title}\nSummary: {summary}\nLesson: {lesson}\n---\n"
        filenames.append(filepath.name)
    
    prompt = f"""Analyze these leadership/org psych stories and extract the key themes from each one.

{stories_text}

For EACH story, respond with ONLY a JSON array (no other text, no markdown, no backticks). Each element should be:
{{
  "title": "Story title",
  "themes": ["theme1", "theme2", "theme3"]
}}

Use standardized theme labels from this list when they fit (but add new ones if needed):
- Change Management
- Psychological Safety
- Trust
- AI in the Workplace
- Leadership Modeling
- Organizational Culture
- Employee Engagement
- Decision Making
- Communication
- Conflict Resolution
- Talent Management
- Performance Management
- Remote/Hybrid Work
- Burnout/Wellbeing
- DEI/Inclusion
- Innovation
- Accountability
- Power Dynamics
- Team Dynamics
- Restructuring/Layoffs

Each story should have 2-4 themes. Be specific and consistent.
"""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        results = json.loads(response_text)
        return results, filenames
    except Exception as e:
        print(f"  ⚠️ Claude API error: {e}")
        return None, filenames

def main():
    print("=" * 70)
    print("HESION THEME LOGGER")
    print("=" * 70)
    
    # Load existing log
    log = load_theme_log()
    already_logged = get_already_logged_files(log)
    
    print(f"\n📊 Existing log has {len(log['entries'])} entries")
    
    # Find new stories not yet logged
    story_files = list(STORIES_DIR.glob("*.md"))
    new_files = [f for f in story_files if f.name not in already_logged]
    
    if not new_files:
        print("No new stories to log. Done.")
        return
    
    print(f"📂 Found {len(new_files)} new stories to log")
    
    # Process in batches of 10
    batch_size = 10
    for i in range(0, len(new_files), batch_size):
        batch = new_files[i:i + batch_size]
        print(f"\n🧠 Extracting themes from batch {i // batch_size + 1} ({len(batch)} stories)...")
        
        results, filenames = extract_themes_from_stories(batch)
        
        if results is None:
            print("  ⚠️ Failed to extract themes for this batch")
            continue
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for j, result in enumerate(results):
            entry = {
                "date": today,
                "filename": filenames[j] if j < len(filenames) else "unknown",
                "title": result.get("title", "Unknown"),
                "themes": result.get("themes", []),
            }
            log["entries"].append(entry)
            print(f"  ✓ Logged: {entry['title'][:50]} → {entry['themes']}")
    
    # Save updated log
    save_theme_log(log)
    
    # Print theme summary
    all_themes = {}
    for entry in log["entries"]:
        for theme in entry.get("themes", []):
            all_themes[theme] = all_themes.get(theme, 0) + 1
    
    print("\n" + "=" * 70)
    print("THEME FREQUENCY (All Time)")
    print("=" * 70)
    for theme, count in sorted(all_themes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {theme}: {count}")
    
    print(f"\n✓ Theme log saved: {THEME_LOG_PATH}")
    print(f"  Total entries: {len(log['entries'])}")

if __name__ == "__main__":
    main()
