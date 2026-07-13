"""
Hesion Morning Briefing Generator
Reads pending stories from the stories/ folder, ranks them, and generates
a daily briefing with top picks for LinkedIn, newsletter, and workshop use.
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

STORIES_DIR = Path("reports")
BRIEFINGS_DIR = Path("reports")

def parse_story_markdown(filepath):
    """Extract key fields from a story markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    story = {"filename": filepath.name, "raw": content}
    
    # Extract title
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    story["title"] = title_match.group(1) if title_match else "Unknown"
    
    # Extract source
    source_match = re.search(r'\*\*Source:\*\* (.+)', content)
    story["source"] = source_match.group(1).strip() if source_match else "Unknown"
    
    # Extract strength score
    score_match = re.search(r'\*\*(\d+)/10\*\*', content)
    story["score"] = int(score_match.group(1)) if score_match else 0
    
    # Extract summary
    summary_match = re.search(r'## Summary\n(.+?)(?=\n##)', content, re.DOTALL)
    story["summary"] = summary_match.group(1).strip() if summary_match else ""
    
    # Extract org psych angle
    angle_match = re.search(r'## Organizational Psychology Angle\n(.+?)(?=\n##)', content, re.DOTALL)
    story["org_psych_angle"] = angle_match.group(1).strip() if angle_match else ""
    
    # Extract leadership lesson
    lesson_match = re.search(r'## Leadership Lesson\n(.+?)(?=\n##)', content, re.DOTALL)
    story["leadership_lesson"] = lesson_match.group(1).strip() if lesson_match else ""
    
    # Extract discovered date
    date_match = re.search(r'\*\*Discovered:\*\* (.+)', content)
    story["discovered"] = date_match.group(1).strip() if date_match else ""
    
    # Extract URL
    url_match = re.search(r'\*\*URL:\*\* \[.+?\]\((.+?)\)', content)
    story["url"] = url_match.group(1).strip() if url_match else ""
    
    # Check if still pending
    story["pending"] = "Pending review" in content
    
    return story

def get_briefing_from_claude(stories):
    """Send top stories to Claude for briefing generation."""
    
    stories_text = ""
    for i, s in enumerate(stories, 1):
        stories_text += f"""
---
Story {i}: {s['title']}
Source: {s['source']}
Score: {s['score']}/10
Summary: {s['summary']}
Org Psych Angle: {s['org_psych_angle']}
Leadership Lesson: {s['leadership_lesson']}
URL: {s['url']}
---
"""
    
    prompt = f"""You are generating a morning briefing for Pete Dusché, founder of Hesion Leadership Consulting. Pete is an organizational psychologist targeting CHROs and COOs.

Here are today's top stories (already scored for org psych relevance):

{stories_text}

Generate a morning briefing in this exact format. Be direct, conversational, and specific. No filler.

Respond with ONLY the briefing text (no JSON, no backticks). Use this structure:

# Morning Briefing — {datetime.now().strftime('%B %d, %Y')}

## Top Story
[Pick the single most compelling story for Hesion's audience. 2-3 sentences on why it matters for leadership.]

## Best LinkedIn Post Candidate
[Pick the story that would make the strongest LinkedIn post. Explain in 1-2 sentences why, and suggest a hook (opening line).]

## Best Newsletter Candidate
[Pick the story with the deepest org psych angle — something worth 500+ words of analysis. Explain why.]

## Best Workshop/Keynote Example
[Pick a story that would work as a real-world illustration in a presentation. What concept does it illustrate?]

## Stories Worth Watching
[List any remaining stories that are interesting but not top picks. One line each.]

## Skip These
[List any stories that made it through the filter but aren't worth Pete's time. One line each explaining why.]
"""
    
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"⚠️ Claude API error: {e}")
        return None

def main():
    print("=" * 70)
    print("HESION MORNING BRIEFING GENERATOR")
    print("=" * 70)
    
    # Read all pending stories
    story_files = list(STORIES_DIR.glob("*.md"))
    
    if not story_files:
        print("No stories found in stories/ folder.")
        return
    
    print(f"\n📂 Found {len(story_files)} story files")
    
    # Parse all stories
    stories = []
    for filepath in story_files:
        try:
            story = parse_story_markdown(filepath)
            if story["pending"]:
                stories.append(story)
        except Exception as e:
            print(f"  ⚠️ Error parsing {filepath.name}: {e}")
    
    print(f"📋 {len(stories)} pending stories to review")
    
    if not stories:
        print("No pending stories. Nothing to brief.")
        return
    
    # Sort by score (highest first)
    stories.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top 10 for briefing
    top_stories = stories[:10]
    
    print(f"\n🧠 Generating briefing from top {len(top_stories)} stories...")
    
    # Generate briefing
    briefing = get_briefing_from_claude(top_stories)
    
    if briefing is None:
        print("Failed to generate briefing.")
        return
    
    # Save briefing
    today = datetime.now().strftime("%Y-%m-%d")
    briefing_path = BRIEFINGS_DIR / f"{today}.md"
    
    with open(briefing_path, "w", encoding="utf-8") as f:
        f.write(briefing)
    
    print(f"\n✓ Briefing saved: {briefing_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"✓ BRIEFING COMPLETE")
    print(f"  Top stories analyzed: {len(top_stories)}")
    print(f"  Briefing location: {briefing_path.absolute()}")
    print("=" * 70)

if __name__ == "__main__":
    main()
