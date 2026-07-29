import hashlib


def make_job_id(source: str, native_id: str) -> str:
    digest = hashlib.sha256(f"{source}:{native_id}".encode("utf-8")).hexdigest()
    return digest[:16]
