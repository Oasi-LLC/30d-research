# last30days – What It Is, How It Works, How to Use It

## What This Tool Does (In One Sentence)

**last30days** researches any topic across **Reddit** and **X (Twitter)** from the **last 30 days**, then returns a ranked list of threads and posts with summaries and links so you see what people are actually discussing and sharing right now.

---

## What It Does (Detailed)

1. **Takes a topic** – e.g. “Meta ads for short-term rentals”, “best AI tools 2026”, “ClawdBot setup”.
2. **Searches Reddit** – Uses the OpenAI API (with web search) to find recent Reddit threads about that topic.
3. **Searches X (Twitter)** – Uses the xAI API to find recent X posts about that topic.
4. **Filters by date** – Keeps only content from the last 30 days.
5. **Scores and ranks** – Combines relevance, recency, and engagement (upvotes, likes, reposts).
6. **Removes duplicates** – Deduplicates similar items.
7. **Returns a report** – A structured result (compact markdown, full markdown, or JSON) with:
   - Reddit threads (title, subreddit, URL, score, comments, date)
   - X posts (text, author, URL, likes, reposts, date)
   - Date range and source mode

**Optional:** With no API keys it can run in “web-only” mode and tell you to use Claude’s WebSearch for the actual search (it doesn’t do the web search itself).

---

## How It Works (Technical Flow)

```
You enter a topic
       ↓
Script loads config (~/.config/last30days/.env)
  - OPENAI_API_KEY → for Reddit search
  - XAI_API_KEY → for X search
       ↓
Gets “last 30 days” date range (e.g. 2026-01-02 to 2026-02-01)
       ↓
Calls OpenAI API → gets Reddit thread URLs/snippets
Calls xAI API → gets X post snippets
(Can run in parallel)
       ↓
Optionally enriches Reddit threads (real upvotes/comments via Reddit)
       ↓
Normalizes all items (title, url, date, engagement)
       ↓
Filters out items outside the 30-day window
       ↓
Scores each item (relevance + recency + engagement)
       ↓
Sorts by score, dedupes
       ↓
Builds a Report (topic, date range, Reddit list, X list)
       ↓
Renders output in chosen format (compact | json | md | context | path)
       ↓
Prints result to stdout (or writes to file for some modes)
```

So: **input = topic + options**, **output = text report (or JSON)**.

---

## How to Use It (Command Line)

### Basic usage

```bash
# From project root, with venv activated
source venv/bin/activate   # or: venv\Scripts\activate on Windows

python scripts/last30days.py "your topic here"
```

Example:

```bash
python scripts/last30days.py "best Meta ads creatives for hotels"
```

### Options

| Option | Meaning | Example |
|--------|--------|--------|
| (no option) | Default: Reddit + X, normal depth, compact output | `python scripts/last30days.py "AI tools"` |
| `--quick` | Fewer sources (8–12 per platform), faster (~30–50 s) | `... "AI tools" --quick` |
| `--deep` | More sources (50–70 Reddit, 40–60 X), slower (~90+ s) | `... "AI tools" --deep` |
| `--emit=compact` | Short markdown summary (default) | `... --emit=compact` |
| `--emit=md` | Full markdown report | `... --emit=md` |
| `--emit=json` | Full result as JSON | `... --emit=json` |
| `--emit=context` | Context snippet for Claude | `... --emit=context` |
| `--sources=reddit` | Only Reddit | `... --sources=reddit` |
| `--sources=x` | Only X | `... --sources=x` |
| `--sources=both` | Reddit + X (explicit) | `... --sources=both` |
| `--mock` | Use sample data (no API calls) | `... "test" --mock` |
| `--include-web` | Include web search in logic (Claude WebSearch instructions) | `... --include-web` |

### Examples

```bash
# Quick research, compact output
python scripts/last30days.py "AI tools 2026" --quick

# Full report as markdown
python scripts/last30days.py "Meta ads for short term rentals" --emit=md

# JSON for integration
python scripts/last30days.py "ClawdBot errors" --emit=json

# Test without API (fixtures only)
python scripts/last30days.py "test topic" --mock
```

---

## What You Need to Run It

1. **Python 3** – Script uses standard library + no extra pip packages.
2. **Config file** – `~/.config/last30days/.env` with:
   - `OPENAI_API_KEY=sk-...` (for Reddit)
   - `XAI_API_KEY=xai-...` (for X)  
   At least one key is required for real Reddit/X results; without keys it runs in web-only mode.
3. **Working directory** – Run from the **project root** so `scripts/last30days.py` and `scripts/lib/` are found.

---

## Output Formats

- **compact** – Best for humans: header, date range, then Reddit threads and X posts with score, link, and a short summary.
- **md** – Full markdown report (same data, more structure).
- **json** – Full report as JSON (good for APIs or other tools).
- **context** – Text snippet suitable for pasting into Claude as context.
- **path** – Prints the path where the report file was written (used internally).

---

## Summary for Your Team

- **What it is:** A research tool that searches Reddit and X for the last 30 days on any topic and returns a ranked, summarized report.
- **How you use it:** Enter a topic (and optionally `--quick`, `--deep`, `--emit=...`, `--sources=...`), run the script, read the output (or use JSON).
- **Next step:** The Streamlit UI wraps this same behavior in a simple web form so the team can enter a topic, click “Research”, and see the same report in the browser. Deployment (e.g. Streamlit Community Cloud) is the step to put that UI online.
