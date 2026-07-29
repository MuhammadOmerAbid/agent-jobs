import re
from dataclasses import dataclass, field
from typing import Any, Optional

from bs4 import BeautifulSoup


@dataclass
class RawJobPosting:
    source: str
    source_native_id: str
    title: str
    jd_text: str
    apply_url: str
    company: Optional[str] = None
    company_url: Optional[str] = None
    location: Optional[str] = None
    remote_type: str = "unclear"
    salary_min_usd: Optional[int] = None
    salary_max_usd: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    posted_at: Optional[str] = None
    raw_json: Any = None

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "source_native_id": self.source_native_id,
            "title": self.title,
            "company": self.company,
            "company_url": self.company_url,
            "location": self.location,
            "remote_type": self.remote_type,
            "salary_min_usd": self.salary_min_usd,
            "salary_max_usd": self.salary_max_usd,
            "tags": self.tags,
            "jd_text": self.jd_text,
            "apply_url": self.apply_url,
            "posted_at": self.posted_at,
            "raw_json": self.raw_json,
        }


def strip_html(text: Optional[str]) -> str:
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(separator="\n").strip()


REMOTE_KEYWORDS = re.compile(r"\b(remote|work from home|wfh|distributed team)\b", re.IGNORECASE)


def looks_remote(*texts: Optional[str]) -> bool:
    return any(t and REMOTE_KEYWORDS.search(t) for t in texts)
