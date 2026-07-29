# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

### Added
- Initial project scaffold
- README with setup instructions
- MIT License
- Documented additional free job sources: Remotive, Arbeitnow, Himalayas, Jobicy, Adzuna
- Documented Adzuna's multi-country query strategy (19 countries, remote-keyword filter) since it lacks a dedicated remote-jobs feed
- Documented additional free sources: Hacker News "Who is Hiring" (Firebase/Algolia API), NoDesk (RSS), The Muse, Findwork.dev, Jooble
- Implemented the full `agent_jobs` package: shared SQLite schema/repository, ported Groq/Gemini LLM client, per-source rate limiter with automatic backoff, 16 source fetchers (13 original + Working Nomads, Jobspresso, 4dayweek.io confirmed via direct HTTP testing), LLM + rule-based scoring, and the `setup`/`run`/`schedule`/`cover`(stub) CLI
- Verified against real live APIs: 900+ postings fetched and scored across sources in a real run, rule-based fallback confirmed working with no LLM keys set
- Added agent-ats integration: `/api/jobs` router + SQLite read/write layer sharing the same DB file, and a new in-app Jobs dashboard (`/jobs`, `/jobs/[id]`) in the Next.js frontend with a one-click hand-off into the existing Match and Interview flows
- Evaluated 19 additional requested sources (Remote.co, Dynamite Jobs, Arc.dev, PowerToFly, etc.) via direct HTTP checks — none had a usable free API/RSS without scraping; documented in README
- Added Working Nomads, Jobspresso, and 4dayweek.io as 3 more confirmed-free sources (16 total), found via direct HTTP verification of a 22-source request list
- Fixed real bugs found via live runs: Jobicy's `jobIndustry`/`jobType` are arrays (not scalars) and broke the rule-based scorer; Working Nomads' `tags` is a comma-separated string (not an array)
- Verified the full closed-loop hand-off in a real browser (Playwright): Jobs dashboard → job detail → "Optimize resume for this job" pre-fills `/match`'s JD field with the job's full description (7,344 chars, zero re-pasting) → "Prep for this interview" does the same for `/interview`, zero console errors
