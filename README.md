# Agent 3 â€” Remote Job Hunter

![CI](https://github.com/MuhammadOmerAbid/agent-jobs/actions/workflows/ci.yml/badge.svg) ![License](https://img.shields.io/github/license/MuhammadOmerAbid/agent-jobs) ![Python](https://img.shields.io/badge/python-3.11+-blue)


Finds remote jobs that match your profile, scores them with AI, and drafts tailored cover notes. You review and apply manually â€” no auto-apply ever.

**Part of:** [AI Outreach System](../ai-outreach-system/)

---

## What It Does

1. You provide your CV/profile once (PDF or text) and set your preferences (roles, tech stack, salary range, timezone)
2. On a schedule, it pulls new postings from RemoteOK, WeWorkRemotely, Wellfound, and the other sources listed below
3. Claude scores each job: fit %, reasons it fits, any red flags
4. Top matches are sent to you as a daily Telegram digest
5. For jobs you pick, Claude drafts a short tailored cover note + suggested CV bullet tweaks
6. You review everything and apply yourself

**No auto-apply. You always apply manually.**

---

## Job Sources

| Source | Method | Auth Needed |
|--------|--------|-------------|
| RemoteOK | Official API | None |
| WeWorkRemotely | RSS Feed | None |
| Wellfound (AngelList) | Official listings | None |
| Remotive | Official API | None (rate-limited, max 4 pulls/day) |
| Arbeitnow | Official API | None |
| Himalayas | Official API | None |
| Jobicy | Official API/RSS | None |
| Adzuna | Official API | Free `app_id` + `app_key` (register at [developer.adzuna.com](https://developer.adzuna.com), 1,000 calls/month) |
| Hacker News "Who is Hiring" | Official Firebase API | None |
| NoDesk | RSS Feed | None |
| The Muse | Official API | None (500 req/hr) — free `api_key` bumps to 3,600 req/hr |
| Findwork.dev | Official API | Free token (register at [findwork.dev](https://findwork.dev)), 60 req/min |
| Jooble | Official API | Free key (instant signup form at [jooble.org/api/about](https://jooble.org/api/about)) |
| Working Nomads | Official API | None |
| Jobspresso | RSS Feed | None |
| 4dayweek.io | RSS Feed | None |

No scraping. Official APIs and public RSS only. All sources above are free — no paid API plans are used.

### Known data-quality limitation: 4dayweek.io

Its RSS feed's `<description>` field only repeats the job title — it does not include the actual job description. Getting the real JD text would require fetching and scraping the individual job page, which conflicts with this project's no-scraping policy, so postings from this source have thin `jd_text` (title-only). Fit scores and the resume/interview hand-off will be low-value for this source's jobs until/unless 4dayweek.io ships a richer feed. NoDesk has a related but milder issue: its feed is a digest newsletter (each entry is one weekly "Issue #NNN" post, not one job per entry), so titles read as `NoDesk: Issue #419` rather than an actual role — read the full text before acting on jobs from this source.

### Sources evaluated but not added (no free API/RSS, or dead)

Requested but confirmed unusable without scraping (verified by direct HTTP checks, not just docs search):

| Source | Why not added |
|--------|---------------|
| Remote.co | No public API or RSS found |
| Dynamite Jobs | No public API or RSS found |
| Skip The Drive | No public API or RSS found |
| DailyRemote | Confirmed no RSS; email/Twitter alerts only |
| Remoters.net | No public API or RSS found |
| Otta | Rebranded to Welcome to the Jungle; no public feed |
| Arc.dev | `/feed` returns 404; no public API found |
| NoHQ.co | `/feed` exists but is the *blog* feed, not jobs |
| PowerToFly | `/feed/` and `/jobs/feed/` both 404 |
| Crossover | Recruiting platform, no public job data feed |
| EuropeRemotely | `/feed/` returns 403 |
| AsiaRemoteJobs | Domain unreachable |
| RemotePython | `/jobs/feed/` returns 404 |
| Work at a Startup (YC) | No public API; scraping-only |
| Product Hunt Jobs | No public jobs feed (product API only) |
| Support Driven Jobs | `/jobs/feed/` returns 404 |
| Citizen Remote | `/feed/` returns 404 |
| Remote Tribe | Domain does not resolve |
| I ❤ Remote.io | RSS endpoint works but the remote-filtered feed returns 0 items — unreliable, revisit later |
| RemoteWoman | RSS works but hasn't published since 2019 — dead |

If any of these later ship a real API, they can be added following the same `RawJobPosting` fetcher pattern as the sources above.

### Note on Adzuna

Unlike most other sources, Adzuna has no dedicated "remote jobs" feed — its `/v1/api/jobs/{country}/search` endpoint is per-country. To get useful coverage, the agent queries it across all 19 supported countries and keeps only listings that look remote-friendly (keyword match on "remote"/"work from home" in the title or description):

`us, gb, ca, au, de, fr, in, nl, es, it, pl, br, mx, sg, za, nz, at, be, ch`

This costs one API call per country per run (19 calls), so budget accordingly against the 1,000 calls/month free tier — roughly one full run every ~1.5 days at daily-schedule granularity, or run it less frequently than the other sources (e.g. weekly) if using the daily digest schedule for everything else.

### Note on Hacker News "Who is Hiring"

This isn't a continuous feed — a new thread is posted by the `@whoishiring` account on the first business day of each month. The agent should fetch the latest thread ID (searchable via the Algolia HN Search API, `https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring`), then pull its top-level comments via the official Firebase API (`https://hacker-news.firebaseio.com/v0/item/{id}.json`). Each top-level comment is one job post — parse company/stack/remote-or-not from free text since there's no structured schema. Cache the thread ID and only re-fetch new comments on subsequent runs within the same month.

### Note on The Muse and Jooble

Neither is remote-first — The Muse lists jobs across all work arrangements, and Jooble aggregates general listings from across the web. Both need the same remote/work-from-home keyword filtering approach used for Adzuna to stay useful for this agent's purpose.

---

## Setup

```bash
# Inside ai-outreach-system/
pip install -r requirements.txt
cp .env.example .env
# Fill in ANTHROPIC_API_KEY and TELEGRAM_BOT_TOKEN in .env
```

---

## Usage

```bash
# Set up your profile (run once â€” parses your CV)
python agent_jobs/main.py setup --cv path/to/your-cv.pdf

# Run job search manually
python agent_jobs/main.py run

# Start the scheduler (daily digest)
python agent_jobs/main.py schedule

# Request cover note for a saved job
python agent_jobs/main.py cover --job-id 42
```

---

## Profile Setup

After running `setup`, edit `agent_jobs/config/profile.json`:

```json
{
  "roles": ["Full Stack Developer", "Frontend Developer", "Web Developer"],
  "tech_stack": ["React", "Next.js", "Node.js", "Python", "Tailwind CSS"],
  "salary_min_usd": 3000,
  "salary_max_usd": 8000,
  "timezone": "UTC+5",
  "preferred_company_size": "startup",
  "remote_preference": "fully_remote",
  "no_go": ["PHP only", "no equity", "non-technical founder only"]
}
```

---

## Environment Variables Needed

```
ANTHROPIC_API_KEY=       # https://console.anthropic.com
TELEGRAM_BOT_TOKEN=      # Create bot via @BotFather on Telegram
TELEGRAM_CHAT_ID=        # Your personal Telegram chat ID
ADZUNA_APP_ID=           # Free — register at https://developer.adzuna.com
ADZUNA_APP_KEY=          # Free — same registration as above
FINDWORK_API_TOKEN=      # Free — register at https://findwork.dev
JOOBLE_API_KEY=          # Free — instant signup at https://jooble.org/api/about
THEMUSE_API_KEY=         # Optional, free — only needed to raise the 500 req/hr cap to 3,600
```

Only Adzuna, Findwork.dev, and Jooble require credentials (all free). RemoteOK, WeWorkRemotely, Wellfound, Remotive, Arbeitnow, Himalayas, Jobicy, Hacker News, and NoDesk all work with zero signup. The Muse works without a key too — `THEMUSE_API_KEY` is optional.

---

## Daily Digest Format (Telegram)

```
ðŸ” Daily Job Digest â€” 3 June 2026

1. Senior Frontend Dev @ Acme Inc
   Fit: 87% âœ…
   Pros: Next.js stack, UTCÂ±3, $5kâ€“$7k
   Red flags: None
   [Get Cover Note] [Skip]

2. Full Stack Engineer @ Beta Corp
   Fit: 72% âš ï¸
   Pros: Remote, React
   Red flags: Requires US timezone overlap
   [Get Cover Note] [Skip]
```

---

## Schedule

Default: daily at 8:00 AM (your local time).
Configurable in `agent_jobs/config/schedule.py`.

---

## Database

SQLite file: `data/jobs.db`

Tables:
- `jobs` â€” all fetched job postings
- `scored` â€” AI-scored jobs with fit %
- `selected` â€” jobs you picked for cover note generation
- `applied` â€” your application history

---

## Safety

- No auto-apply â€” against most job sites' terms and produces low quality
- Official APIs and RSS only â€” no scraping
- You control every application
