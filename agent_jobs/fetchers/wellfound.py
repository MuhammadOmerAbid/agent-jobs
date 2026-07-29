"""Wellfound (AngelList Talent) does not currently expose a documented,
stable public JSON API for job listings (unlike the other sources here,
which all have a confirmed official endpoint). Rather than guess at an
undocumented/unstable URL, this fetcher is a deliberate no-op until a
confirmed official API is available.

If Wellfound later publishes one, wire it up here following the same
RawJobPosting contract as the other fetchers/*.py modules.
"""

from agent_jobs.fetchers.base import RawJobPosting

SOURCE = "wellfound"


def fetch() -> list[RawJobPosting]:
    return []
