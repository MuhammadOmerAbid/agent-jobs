import requests

from agent_jobs.db.repository import get_rate_limit_state, upsert_rate_limit_state
from agent_jobs.fetchers.base import RawJobPosting

SOURCE = "hn_whoishiring"
ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
FIREBASE_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

_CACHE_KEY = "hn_whoishiring_last_thread_id"


def _set_cached_thread_id(thread_id: str, last_seen_kid: int) -> None:
    # Reuse source_rate_limits as a tiny key-value cache: window_start holds
    # "<thread_id>:<last_seen_comment_id>", calls_made/call_budget unused (0).
    upsert_rate_limit_state(_CACHE_KEY, f"{thread_id}:{last_seen_kid}", 0, 0, 0)


def _find_latest_thread_id() -> int | None:
    response = requests.get(
        ALGOLIA_SEARCH_URL,
        params={"tags": "story,author_whoishiring", "query": "Ask HN: Who is hiring?"},
        timeout=20,
    )
    response.raise_for_status()
    hits = response.json().get("hits", [])
    if not hits:
        return None
    return int(hits[0]["objectID"])


def fetch() -> list[RawJobPosting]:
    thread_id = _find_latest_thread_id()
    if thread_id is None:
        return []

    thread_response = requests.get(FIREBASE_ITEM_URL.format(id=thread_id), timeout=20)
    thread_response.raise_for_status()
    thread = thread_response.json() or {}
    kid_ids = thread.get("kids", [])

    cached = get_rate_limit_state(_CACHE_KEY)
    last_seen_kid = 0
    if cached and cached.get("window_start", "").startswith(f"{thread_id}:"):
        last_seen_kid = int(cached["window_start"].split(":", 1)[1] or 0)

    new_kid_ids = [kid for kid in kid_ids if kid > last_seen_kid]

    postings = []
    for kid in new_kid_ids:
        comment_response = requests.get(FIREBASE_ITEM_URL.format(id=kid), timeout=20)
        if comment_response.status_code != 200:
            continue
        comment = comment_response.json()
        if not comment or comment.get("dead") or comment.get("deleted") or not comment.get("text"):
            continue

        text = comment["text"]
        title_line = text.split("<p>")[0][:120].strip() or "HN Who's Hiring posting"
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=str(kid),
                title=title_line,
                location="See posting",
                remote_type="unclear",
                jd_text=text,
                apply_url=f"https://news.ycombinator.com/item?id={kid}",
                posted_at=None,
                raw_json=comment,
            )
        )

    if kid_ids:
        _set_cached_thread_id(str(thread_id), max(kid_ids))

    return postings
