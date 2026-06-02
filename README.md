# Agent 3 — Remote Job Hunter

Finds remote jobs that match your profile, scores them with AI, and drafts tailored cover notes. You review and apply manually — no auto-apply ever.

**Part of:** [AI Outreach System](../ai-outreach-system/)

---

## What It Does

1. You provide your CV/profile once (PDF or text) and set your preferences (roles, tech stack, salary range, timezone)
2. On a schedule, it pulls new postings from RemoteOK, WeWorkRemotely, and Wellfound
3. Claude scores each job: fit %, reasons it fits, any red flags
4. Top matches are sent to you as a daily Telegram digest
5. For jobs you pick, Claude drafts a short tailored cover note + suggested CV bullet tweaks
6. You review everything and apply yourself

**No auto-apply. You always apply manually.**

---

## Job Sources

| Source | Method |
|--------|--------|
| RemoteOK | Official API |
| WeWorkRemotely | RSS Feed |
| Wellfound (AngelList) | Official listings |

No scraping. Official APIs and public RSS only.

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
# Set up your profile (run once — parses your CV)
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
```

---

## Daily Digest Format (Telegram)

```
🔍 Daily Job Digest — 3 June 2026

1. Senior Frontend Dev @ Acme Inc
   Fit: 87% ✅
   Pros: Next.js stack, UTC±3, $5k–$7k
   Red flags: None
   [Get Cover Note] [Skip]

2. Full Stack Engineer @ Beta Corp
   Fit: 72% ⚠️
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
- `jobs` — all fetched job postings
- `scored` — AI-scored jobs with fit %
- `selected` — jobs you picked for cover note generation
- `applied` — your application history

---

## Safety

- No auto-apply — against most job sites' terms and produces low quality
- Official APIs and RSS only — no scraping
- You control every application
