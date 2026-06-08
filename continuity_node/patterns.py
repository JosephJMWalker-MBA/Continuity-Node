"""Layer 4 - Pattern Register: durable beliefs promoted from the ledger under governance.

Patterns are DERIVED: the register is rebuilt from the Interpretive Ledger. A pattern is
promoted to `confirmed` only when enough distinct accepted sources converge on it
(`threshold`); fewer supporters leave it `proposed`. Dissent is first-class - a superseding
interpretation marked rejected/disputed removes that source's support on the next rebuild,
which can demote a pattern. No belief is frozen; every rebuild reflects the current ledger.
"""
import json
import os

from .ids import new_id
from .ledger import effective_interpretations
from .records import finalize


class PatternRegister:
    def __init__(self, path: str, threshold: int = 3):
        self.path = path
        self.threshold = threshold
        self.patterns = {}
        self._load()

    def rebuild(self, ledger):
        """Regenerate all patterns from the canonical ledger state."""
        groups = {}
        for it in effective_interpretations(ledger.all()):
            content = it.get("content", {})
            key = content.get("pattern_key")
            if not key:
                continue
            status = it.get("user_response", {}).get("status")
            g = groups.setdefault(key, {
                "name": content.get("pattern_name", key),
                "accepted_raws": set(), "confs": [], "supporters": [],
            })
            raws = [r["raw_id"] for r in it.get("raw_references", [])]
            if status == "accepted":
                g["accepted_raws"].update(raws)
                g["confs"].append(content.get("confidence", 0.5))
                g["supporters"].append(it["id"])

        self.patterns = {}
        for key, g in groups.items():
            n = len(g["accepted_raws"])
            if n == 0:
                continue
            mean_conf = sum(g["confs"]) / len(g["confs"]) if g["confs"] else 0.0
            confidence = round(mean_conf * min(1.0, n / self.threshold), 3)
            status = "confirmed" if n >= self.threshold else "proposed"
            record = {
                "id": f"pattern:{key}",
                "record_type": "pattern",
                "name": g["name"],
                "category": "core_value",
                "status": status,
                "confidence": confidence,
                "evidence_weight": n,
                "supporting_interpretations": sorted(g["supporters"]),
            }
            finalize(record)
            self.patterns[key] = record
        self._save()
        return self.patterns

    def all(self):
        return list(self.patterns.values())

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                self.patterns = json.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.patterns, f, indent=2)
