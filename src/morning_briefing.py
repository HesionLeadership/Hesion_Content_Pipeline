"""
Hesion Morning Briefing Generator
- Daily picks: stories not yet featured in any briefing, discovered in the last 3 days.
- This Week's Themes: everything discovered in the last 7 days (including already-briefed stories).
- Once a story appears in a briefing, it is retired and never picked again.
"""

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
BRIEFED_FILE = Path("data/briefed_stories.json")
BRIEFED_FILE.parent.mkdir(exist_ok=True)

DAILY_WINDOW_DAYS = 3      # how far back to look for today's picks
THEME_WINDOW_DAYS = 7      # how far back to look for weekly themes
MAX_DAILY_STORIES = 10
MAX_THEME_STORIES = 40

# Non-Latin scripts (Greek, Cyrillic, Hebrew, Arabic, Indic, Thai, Japanese, Chinese, Korean).
# Accented Latin letters like é are NOT matched.
NON_LATIN = re.compile(
    r"[\u0370-\u03FF\u0400-\u052F\u0590-\u06FF\u0900-\u0E7F"
    r"\u3040-\u30FF\u3400-\u9FFF\uAC00-\uD7AF\uF900-\uFAFF]"
)

# ============================================================================
# READING REPORTS
# ============================================================================

def parse_story_markdown(filepath):
    """Extract key fields from a story markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    story = {"filename": filepath.name}

    def grab(pattern, flags=0, default=""):
        m = re.search(pattern, content, flags)
        return m.group(1).strip() if m else default

    story["title"] = grab(r'^# (.+)$', re.MULTILINE, "Unknown")
    story["source"] = grab(r'\*\*Source:\*\* (.+)', 0, "Unknown")
    story["url"] = grab(r'\*\*URL:\*\* \[.+?\]\((.+?)\)')
    story["content_basis"] = grab(r'\*\*Content basis:\*\* (.+)', 0, "Unknown (older report)")
    story["summary"] = grab(r'## Summary\n(.+?)(?=\n##)', re.DOTALL)
    story["org_psych_angle"] = grab(r'## Organizational Psychology Angle\n(.+?)(?=\n##)', re.DOTALL)
    story["leadership_lesson"] = grab(r'## Leadership Lesson\n(.+?)(?=\n##)', re.DOTALL)
    story["discovered"] = grab(r'\*\*Discovered:\*\* (.+)')

    score = grab(r'\*\*(\d+)/10\*\*', 0, "0")
    story["score"] = int(score) if score.isdigit() else 0

    try:
        story["discovered_dt"] = datetime.strptime(story["discovered"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        story["discovered_dt"] = None

    story["pending"] = "Pending review" in content
    return story

def load_briefed():
    """Stories already featured in a briefing: {filename: date briefed}."""
    if BRIEFED_FILE.exists():
        try:
            return json.loads(BRIEFED_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

def save_briefed(briefed):
    """Save briefed list, keeping 60 days so the file never bloats."""
    cutoff = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    recent = {k: v for k, v in briefed.items() if v >= cutoff}
    BRIEFED_FILE.write_text(json.dumps(recent, indent=1), encoding="utf-8")

# ============================================================================
# CLAUDE
# ============================================================================

def call_claude(prompt):
    """Send prompt to Claude and return only the answer text (skips thinking blocks)."""
    try:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = "".join(
            block.text for block in response.content
            if getattr(block, "type", "") == "text"
        ).strip()
        if not text:
            print(f"⚠️ Empty response from Claude. stop_reason={response.stop_reason}", flush=True)
            return None
        return text
    except Exception as e:
        import traceback
        print(f"⚠️ Claude API error: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        return None

def build_prompt(daily, weekly):
    today_text = ""
    for s in daily:
        today_text += f"""
---
TITLE: {s['title']}
Source: {s['source']} | Score: {s['score']}/10 | Content basis: {s['content_basis']}
Summary: {s['summary']}
Org Psych Angle: {s['org_psych_angle']}
Leadership Lesson: {s['leadership_lesson']}
---
"""

    week_text = ""
    for s in weekly:
        angle = s['org_psych_angle'][:300]
        week_text += f"- {s['title']} ({s['source']}): {angle}\n"

    return f"""You are generating a morning briefing for Pete Dusché, founder of Hesion Leadership Consulting. Pete is an organizational psychologist targeting CHROs and COOs.

TODAY'S STORIES (new since the last briefing; use ONLY these for the picks):
{today_text}

THIS WEEK'S STORIES (last 7 days; use ONLY for the themes section):
{week_text}

RULES, follow all of them:
1. Refer to every story by its exact TITLE in bold, copied character for character, followed by the source in parentheses. Example: **3 Uncommon Traits of Strong Leaders People Never Forget** (Inc). Never refer to a story by number, never shorten or reword a title.
2. Write entirely in English. Every word must be English. No words or characters from any other language.
3. Top Story, Best LinkedIn Post Candidate, Best Newsletter Candidate, and Best Workshop/Keynote Example must each come from TODAY'S STORIES.
4. If a story's content basis says "Headline + teaser only," add "(article not read)" after its title wherever you mention it, and prefer stories built on full article text for the top picks.
5. Use only facts stated in the story material above. Do not add details.
6. Be direct, conversational, and specific. No filler. If a section has nothing to list, write "None."

Respond with ONLY the briefing text (no JSON, no backticks), in this structure:

# Morning Briefing — {datetime.now().strftime('%B %d, %Y')}

## This Week's Themes
[Using THIS WEEK'S STORIES, write 3-5 sentences on recurring and emerging themes across sources. Name the themes. Name the specific stories (exact titles) that support each theme.]

## Top Story
[The single most compelling story from TODAY'S STORIES. 2-3 sentences on why it matters for leadership.]

## Best LinkedIn Post Candidate
[1-2 sentences on why, plus a suggested hook (opening line).]

## Best Newsletter Candidate
[The story with the deepest org psych angle, worth 500+ words. Explain why.]

## Best Workshop/Keynote Example
[A story that works as a real-world illustration. What concept does it illustrate?]

## Stories Worth Watching
[Remaining stories from TODAY'S STORIES that are interesting but not top picks. One line each.]

## Skip These
[Stories from TODAY'S STORIES not worth Pete's time. One line each explaining why.]
"""

def generate_briefing(prompt):
    """Generate briefing; regenerate once if non-English characters appear."""
    text = None
    for attempt in range(2):
        text = call_claude(prompt)
        if text is None:
            return None
        if not NON_LATIN.search(text):
            return text
        print(f"⚠️ Non-English characters found (attempt {attempt + 1}), regenerating...", flush=True)
    cleaned = NON_LATIN.sub("", text)
    return cleaned + "\n\n*Note: non-English characters were detected and removed from this briefing.*"

def build_index(daily):
    """Exact titles, files, and links, generated by code (not by Claude)."""
    lines = ["", "---", "", "## Stories in Today's Briefing", ""]
    for s in daily:
        link = f" · [Read article]({s['url']})" if s['url'] else ""
        flag = " · ⚠️ article not read" if "teaser only" in s['content_basis'].lower() else ""
        lines.append(f"- **{s['title']}** ({s['source']}, {s['score']}/10) · File: `{s['filename']}`{link}{flag}")
    return "\n".join(lines) + "\n"

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("HESION MORNING BRIEFING GENERATOR")
    print("=" * 70)

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    story_files = list(STORIES_DIR.glob("*.md"))
    print(f"\n📂 Found {len(story_files)} files in reports/")

    stories = []
    for filepath in story_files:
        if filepath.name.startswith("BRIEFING_"):
            continue
        try:
            stories.append(parse_story_markdown(filepath))
        except Exception as e:
            print(f"  ⚠️ Error parsing {filepath.name}: {e}")

    briefed = load_briefed()

    def is_recent(s, days):
        return s["discovered_dt"] is not None and s["discovered_dt"] >= now - timedelta(days=days)

    def not_yet_briefed(s):
        # Stories briefed earlier TODAY stay eligible, so a same-day rerun gives the same picks
        return briefed.get(s["filename"]) in (None, today)

    daily = [s for s in stories if s["pending"] and is_recent(s, DAILY_WINDOW_DAYS) and not_yet_briefed(s)]
    daily.sort(key=lambda s: (s["score"], s["discovered_dt"]), reverse=True)
    daily = daily[:MAX_DAILY_STORIES]

    weekly = [s for s in stories if is_recent(s, THEME_WINDOW_DAYS)]
    weekly.sort(key=lambda s: s["discovered_dt"], reverse=True)
    weekly = weekly[:MAX_THEME_STORIES]

    print(f"📋 {len(daily)} new stories for today's picks")
    print(f"🗓️ {len(weekly)} stories from the last {THEME_WINDOW_DAYS} days for themes")

    briefing_path = BRIEFINGS_DIR / f"BRIEFING_{today}.md"

    if not daily:
        briefing = (
            f"# Morning Briefing — {now.strftime('%B %d, %Y')}\n\n"
            "No new stories since the last briefing.\n"
        )
        briefing_path.write_text(briefing, encoding="utf-8")
        print(f"\n✓ No new stories. Short briefing saved: {briefing_path}")
        return

    print(f"\n🧠 Generating briefing...")
    briefing = generate_briefing(build_prompt(daily, weekly))

    if briefing is None:
        print("Failed to generate briefing.")
        return

    briefing += build_index(daily)
    briefing_path.write_text(briefing, encoding="utf-8")

    for s in daily:
        briefed[s["filename"]] = today
    save_briefed(briefed)

    print(f"\n✓ Briefing saved: {briefing_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
