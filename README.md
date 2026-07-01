# Hesion Content Pipeline

**Making our work transparent.** This pipeline is publicly documented to reflect Hesion's commitment to showing how we think and operate.

**Automated discovery pipeline for leadership-relevant news and research.**

**Automated discovery pipeline for leadership-relevant news and research.**

An AI-powered system that discovers fresh stories from business, tech, and organizational psychology sources, analyzes them for leadership insights, and outputs draft posts for Hesion's LinkedIn content strategy.

---

## Overview

Hesion Content Pipeline automates three core workflows:

1. **Discovery** — Fetches latest stories from curated RSS feeds and news APIs
2. **Enrichment** — Claude analyzes each story for organizational psychology angles
3. **Scoring** — Auto-rejects stories below a quality threshold (6/10)

**Output:** Markdown files in the `stories/` folder, ready for manual review and LinkedIn posting.

---

## How It Works

### Daily Workflow (Automated via GitHub Actions)

```
8:00 AM UTC (daily)
    ↓
Fetch stories from all sources
    ↓
Send each to Claude for analysis
    ↓
Claude scores organizational psychology angle (1-10)
    ↓
Save stories scoring 6+ as markdown files
    ↓
Commit new stories to GitHub
```

### Manual Review (Monday & Thursday)

Pete reviews markdown files in the `stories/` folder, selects 1-2 highest-quality stories, and posts to LinkedIn.

---

## Data Sources

### Business & Leadership News (RSS)

- **Harvard Business Review** — hbr.org/feed
- **Reuters Business** — feeds.reuters.com/business
- **Reuters Technology** — feeds.reuters.com/technology
- **WSJ Business** — feeds.wsj.com/xml/rss/3_7085.xml
- **Bloomberg News** — feeds.bloomberg.com/news.rss
- **CNBC** — feeds.cnbc.com/id/100003114/device/rss/rss.html
- **NYT Business** — feeds.nytimes.com/services/xml/rss/nyt/Business.xml
- **USA Today Money** — usatoday.com/money/usaedition.xml

### Tech & Culture (RSS)

- **TechCrunch** — techcrunch.com/feed/
- **Hacker News** — news.ycombinator.com/rss

### News APIs

- **NYT Top Stories API** — Curated top business stories (real-time)
- **NYT Most Popular API** — Trending articles in past 7 days

### Organizational Psychology Research

- **CrossRef API** — Peer-reviewed journals on psychological safety, organizational culture, leadership effectiveness, team dynamics

---

## Scoring System

Claude evaluates each story on organizational psychology relevance (1-10):

### 8-10: Excellent
Clear, research-backed organizational psychology or leadership insight. Example: *"Company restructures to flatten hierarchy, improving decision-making speed and psychological safety."*

### 6-7: Good
Solid angle, but not exceptional. Example: *"New CEO implements different communication style; team adapts to change management."*

### Below 6: Rejected
Weak or forced connection. Example: *"Company raises funding" (no org psych angle)* or *"Political news story" (filtered out).*

**Threshold:** Only stories scoring 6+ are saved to `stories/`.

---

## Filtering & Quality Control

### Political Stories
Stories about electoral politics, politicians' personal actions, or partisan disputes are **automatically rejected**, unless they involve organizational dynamics within a political or corporate entity.

### Duplicate Prevention
If the same story appears across multiple sources, the system saves it only once.

### Conversational Tone
All organizational psychology angles are framed conversationally for LinkedIn, not academic. Positive lessons are preferred over finger-pointing.

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- Git
- API keys:
  - Anthropic (Claude API)
  - NYT Developer API (free tier)
  - CrossRef (email for API access)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HesionLeadership/Hesion_Content_Pipeline.git
   cd Hesion_Content_Pipeline
   ```

2. **Create `.env` file in the root directory:**
   ```
   ANTHROPIC_API_KEY=your_anthropic_key
   NYT_API_KEY=your_nyt_key
   CROSSREF_EMAIL=your_email@example.com
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the pipeline locally:**
   ```bash
   python src/story_discovery.py
   ```

   Output appears in `stories/` folder as markdown files.

---

## GitHub Actions Automation

The pipeline runs automatically via GitHub Actions every day at **8:00 AM UTC**.

### Workflow Details

- **Trigger:** Scheduled daily (cron: `0 8 * * *`)
- **Runtime:** ~3-5 minutes depending on API response times
- **Output:** New story markdown files committed to `stories/` folder
- **Commit message:** `Daily story discovery - YYYY-MM-DD HH:MM UTC`

### Manual Trigger

To run the workflow immediately (without waiting for 8am UTC):

1. Go to **Actions** tab on GitHub
2. Select **Daily Story Discovery**
3. Click **Run workflow** → **Run workflow**

### View Logs

After each run, check the **Actions** tab to see:
- Number of stories fetched
- Number of stories saved (6+/10)
- Any API errors or warnings
- Full execution logs

---

## File Structure

```
Hesion_Content_Pipeline/
├── src/
│   └── story_discovery.py          # Main pipeline script
├── stories/                         # Output folder (markdown files)
├── .github/workflows/
│   └── daily_story_discovery.yml   # GitHub Actions workflow
├── requirements.txt                 # Python dependencies
├── .env                            # API keys (local only, not in Git)
├── .gitignore                      # Excludes .env and other sensitive files
├── README.md                       # This file
└── LICENSE                         # MIT license
```

---

## Story Markdown Format

Each saved story is a markdown file with this structure:

```markdown
# Story Title

**Source:** Publication Name  
**Published:** Date  
**URL:** [Link](url)

## Summary
1-2 sentence summary of the story

## Organizational Psychology Angle
The leadership insight or org psych connection

## Strength Score
**7/10** — Why this score was given

## Original Story Summary
Full original story text

---

**Status:** Pending review  
**Discovered:** YYYY-MM-DD HH:MM:SS
```

---

## Review & Posting Workflow

### Monday & Thursday Review

1. Check `stories/` folder on GitHub
2. Open markdown files and read summaries
3. Pick 1-2 stories with strongest angles
4. (Optional) Refine Claude's organizational psychology angle for tone/clarity
5. Draft LinkedIn post using Claude's suggested copy
6. Post to LinkedIn with proper attribution to source

### Content Guidelines

- **Cite sources:** Always link back to original story
- **Tone:** Conversational, not academic
- **Length:** 150-300 words for LinkedIn
- **CTA:** End with reflection question or call to action
- **Brand:** Emphasize Hesion's expertise in organizational psychology and leadership culture

---

## API Rate Limits & Costs

- **Anthropic Claude API:** Pay-per-use. ~$0.10-0.50 per day depending on token usage
- **NYT APIs:** Free tier includes 4,000 requests/month (sufficient for daily pipeline)
- **CrossRef:** Free, no API key required (just email)
- **RSS feeds:** Free, no limits

---

## Contributing

This is Hesion Leadership's proprietary tool, but the architecture is open source and documented here for transparency.

To suggest improvements or report issues:
1. Open an issue on GitHub
2. Include error logs and steps to reproduce
3. Describe the expected behavior

---

## License

MIT License — See LICENSE file for details.

---

## Contact

**Hesion Leadership Consulting**  
Website: [hesionleadership.com](https://hesionleadership.com)  
Email: [contact info]

---

## FAQ

**Q: Why does the pipeline reject so many stories?**  
A: Quality > quantity. We only save stories with genuine organizational psychology angles (6+/10). This keeps Hesion's brand strong: "If we speak, it's important, and we're helping."

**Q: Can I add my own RSS feed sources?**  
A: Yes. Edit the `RSS_FEEDS` dictionary in `src/story_discovery.py` and add a new line with the feed URL.

**Q: What if Claude's angle is weak for a story I like?**  
A: You can manually override the score. Edit the markdown file before posting, or add the story manually to the review queue.

**Q: How do I run the pipeline on my local machine?**  
A: See "Local Setup" section above. Follow steps 1-4 to install and run.

**Q: Can I schedule the pipeline to run at a different time?**  
A: Yes. Edit `.github/workflows/daily_story_discovery.yml` and change the cron expression in the `schedule` section.

---

**Last updated:** June 2026  
**Maintained by:** Hesion Leadership Consulting
