"""Layer 3 - Interpretive Ledger: append-only, provenance-tagged interpretations.

Nothing is ever mutated or deleted. A review or reinterpretation is a NEW entry whose
`parent_id` points at what it supersedes; conflicting interpretations therefore coexist
rather than overwrite. `effective_interpretations` resolves each supersede-chain to its
most recent entry, which is what pattern derivation consumes.
"""
import json
import os


class Ledger:
    def __init__(self, path: str):
        self.path = path

    def append(self, record: dict):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def all(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path) as f:
            return [json.loads(line) for line in f if line.strip()]

    def get(self, interp_id):
        for r in self.all():
            if r["id"] == interp_id:
                return r
        return None


def effective_interpretations(entries):
    """Return the latest entry in each supersede-chain (one per lineage root)."""
    by_id = {e["id"]: e for e in entries}

    def root(e):
        seen = set()
        while e.get("parent_id") in by_id and e["id"] not in seen:
            seen.add(e["id"])
            e = by_id[e["parent_id"]]
        return e["id"]

    latest = {}
    for e in entries:
        r = root(e)
        cur = latest.get(r)
        if cur is None or e["created_at"] >= cur["created_at"]:
            latest[r] = e
    return list(latest.values())
