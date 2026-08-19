"""Layer 1 - Raw Archive: content-addressed, write-once-through-API source storage.

Content is keyed by SHA-256, so ingesting the same bytes twice is idempotent. Raw
records are treated as canonical and are not overwritten by this reference implementation;
everything else is derived from them. The backing files are ordinary local files, so this
module does not provide filesystem immutability, tamper protection, or encryption at rest.
"""
import json
import os

from .ids import now_iso, sha256_text
from .records import finalize


class RawArchive:
    def __init__(self, root: str):
        self.root = root
        self.blobs = os.path.join(root, "blobs")
        self.catalog = os.path.join(root, "catalog.jsonl")
        os.makedirs(self.blobs, exist_ok=True)

    def _hash_path(self, content_hash: str) -> str:
        return os.path.join(self.blobs, content_hash.replace("sha256:", "sha256-") + ".txt")

    def ingest_text(self, text, kind="journal_entry", title=None,
                    sensitivity="private", source="manual_import") -> dict:
        h = sha256_text(text)
        rid = f"raw:{h}"
        path = self._hash_path(h)
        if not os.path.exists(path):  # write once through this API + deduplicated
            with open(path, "w") as f:
                f.write(text)
        record = {
            "id": rid,
            "record_type": "raw",
            "kind": kind,
            "preservation_core": {
                "format": "text/markdown",
                "mime_type": "text/markdown",
                "content_hash": h,
                "storage_reference": os.path.relpath(path, self.root),
                "size_bytes": len(text.encode("utf-8")),
                "ingest_timestamp": now_iso(),
                "original_source": source,
            },
            "governance_core": {
                "sensitivity": sensitivity,
                "rights_basis": "user_owned",
                "legal_hold": False,
            },
            "descriptive_metadata": {
                "title": title or (text.strip().splitlines()[0][:60] if text.strip() else "untitled"),
                "date_created": now_iso()[:10],
            },
        }
        finalize(record)
        if rid not in self._ids():  # don't duplicate the catalog entry
            with open(self.catalog, "a") as f:
                f.write(json.dumps(record) + "\n")
        return record

    def _ids(self):
        return {r["id"] for r in self.all_records()}

    def all_records(self):
        if not os.path.exists(self.catalog):
            return []
        with open(self.catalog) as f:
            return [json.loads(line) for line in f if line.strip()]

    def get_content(self, raw_id: str) -> str:
        h = raw_id.split("raw:", 1)[1]
        with open(self._hash_path(h)) as f:
            return f.read()
