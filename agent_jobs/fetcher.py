import requests
from xml.etree import ElementTree
from agent_jobs.db import save_job

REMOTEOK_URL = "https://remoteok.com/api"
WWR_RSS_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"


def fetch_remoteok() -> int:
    resp = requests.get(REMOTEOK_URL, headers={"User-Agent": "agent-jobs/1.0"}, timeout=15)
    resp.raise_for_status()
    jobs = resp.json()
    count = 0
    for j in jobs:
        if not isinstance(j, dict) or "position" not in j:
            continue
        saved = save_job(
            source="remoteok",
            title=j.get("position", ""),
            company=j.get("company", ""),
            url=j.get("url", ""),
            description=j.get("description", "")[:2000],
            salary=j.get("salary", ""),
        )
        if saved:
            count += 1
    return count


def fetch_weworkremotely() -> int:
    resp = requests.get(WWR_RSS_URL, timeout=15)
    resp.raise_for_status()
    root = ElementTree.fromstring(resp.content)
    count = 0
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        desc = item.findtext("description") or ""
        company = ""
        if " at " in title:
            parts = title.split(" at ", 1)
            title, company = parts[0].strip(), parts[1].strip()
        saved = save_job(
            source="weworkremotely",
            title=title,
            company=company,
            url=link,
            description=desc[:2000],
            salary="",
        )
        if saved:
            count += 1
    return count


def fetch_all() -> dict[str, int]:
    results = {}
    try:
        results["remoteok"] = fetch_remoteok()
    except Exception as e:
        results["remoteok"] = 0
        print(f"RemoteOK fetch failed: {e}")
    try:
        results["weworkremotely"] = fetch_weworkremotely()
    except Exception as e:
        results["weworkremotely"] = 0
        print(f"WeWorkRemotely fetch failed: {e}")
    return results
