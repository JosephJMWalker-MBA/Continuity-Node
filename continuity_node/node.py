"""The Continuity Node: wires the layers into the loop and enforces the invariants.

Invariants demonstrated here:
  1. Raw-interpretation separation - raw is canonical; interpretations point back to it.
  2. Rebuildable-from-raw         - `rebuild()` regenerates the search index from the raw
                                     archive and the pattern register from the ledger.
  3. Lineage over storage          - reviews/dissent are append-only supersede-chains.
"""
import os

from .ids import new_id, now_iso
from .ledger import Ledger
from .patterns import PatternRegister
from .raw_archive import RawArchive
from .records import finalize
from .search_index import SearchIndex
from .engines import StubEngine

USER_DID = "did:web:user.local"


class ContinuityNode:
    def __init__(self, root: str, engine=None, threshold: int = 3):
        self.root = root
        os.makedirs(root, exist_ok=True)
        self.raw = RawArchive(os.path.join(root, "raw"))
        self.index = SearchIndex(os.path.join(root, "index", "lexical.json"))
        self.ledger = Ledger(os.path.join(root, "ledger", "interpretations.jsonl"))
        self.patterns = PatternRegister(os.path.join(root, "patterns", "patterns.json"), threshold)
        self.engine = engine or StubEngine()

    # -- ingest -------------------------------------------------------------
    def ingest(self, text, **kw):
        rec = self.raw.ingest_text(text, **kw)
        self.index.add(rec["id"], text)
        return rec

    def search(self, query, k=5):
        return self.index.search(query, k)

    # -- interpret ----------------------------------------------------------
    def interpret(self, raw_id, lens_id="lens:moral-foundations-care", accept=False):
        text = self.raw.get_content(raw_id)
        out = self.engine.interpret(text, lens_id)
        record = {
            "id": new_id("interp"),
            "record_type": "interpretation",
            "raw_references": [{"raw_id": raw_id, "weight": 1.0}],
            "provenance": {
                "engine": {"provider": self.engine.provider, "model_name": self.engine.name,
                           "model_version": str(self.engine.version)},
                "lens_id": lens_id,
                "timestamp": now_iso(),
                "agent_type": "model",
                "agent_id": "did:web:engine.local",
            },
            "content": {
                "claim": out["claim"],
                "supporting_evidence": out.get("supporting_evidence", ""),
                "counter_evidence": out.get("counter_evidence", []),
                "confidence": out.get("confidence", 0.5),
                "pattern_key": out.get("pattern_key"),
                "pattern_name": out.get("pattern_name"),
            },
            "user_response": {"status": "accepted" if accept else "unreviewed"},
            "governance": {"status": "active"},
        }
        finalize(record)
        self.ledger.append(record)
        return record

    # -- review / dissent (append-only) ------------------------------------
    def review(self, interp_id, status, note=None):
        """Append a superseding entry recording the user's response. Never mutates."""
        parent = self.ledger.get(interp_id)
        if parent is None:
            raise KeyError(interp_id)
        record = {
            "id": new_id("interp"),
            "record_type": "interpretation",
            "parent_id": interp_id,
            "raw_references": parent["raw_references"],
            "provenance": {
                "engine": parent["provenance"]["engine"],
                "lens_id": parent["provenance"]["lens_id"],
                "timestamp": now_iso(),
                "agent_type": "user",
                "agent_id": USER_DID,
            },
            "content": dict(parent["content"]),
            "user_response": {"status": status, "notes": note} if note else {"status": status},
            "governance": {"status": "active"},
        }
        finalize(record)
        self.ledger.append(record)
        return record

    # -- derive / rebuild ---------------------------------------------------
    def derive_patterns(self):
        return self.patterns.rebuild(self.ledger)

    def rebuild(self):
        """Regenerate every derived layer from the canonical raw archive + ledger."""
        self.index.rebuild(self.raw)
        return self.patterns.rebuild(self.ledger)

    def lineage(self, raw_id):
        """Trace raw -> interpretations -> pattern for one source."""
        interps = [e for e in self.ledger.all()
                   if any(r["raw_id"] == raw_id for r in e.get("raw_references", []))]
        return {"raw": self.raw.get_content(raw_id), "interpretations": interps}
