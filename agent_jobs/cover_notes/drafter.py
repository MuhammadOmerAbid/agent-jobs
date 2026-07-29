"""Cover note drafting — deferred to a fast-follow pass (see plan section E).

Not wired into the CLI yet. When built, this should follow scoring/scorer.py's
pattern: a JSON- or plain-text-instruction prompt through llm_client.call_llm,
writing the result into the `selected.cover_note` column via
agent_jobs.db.repository.
"""


def draft_cover_note(job: dict, profile: dict, resume_text: str | None = None) -> str:
    raise NotImplementedError("Cover note drafting is deferred — see project plan.")
