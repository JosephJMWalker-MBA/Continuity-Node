"""Content addressing, hashing, and identifier helpers."""
import hashlib
import json
import uuid
from datetime import datetime, timezone


def now_iso() -> str:
    """RFC 3339 timestamp with microsecond resolution (so lineage ordering is unambiguous)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def canonical(obj) -> bytes:
    """Deterministic serialization used for content hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def new_id(prefix: str) -> str:
    # The framework specifies UUIDv7; uuid4 is used here for stdlib-only portability.
    return f"{prefix}:uuid-{uuid.uuid4()}"
