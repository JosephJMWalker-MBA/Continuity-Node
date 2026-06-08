"""End-to-end tests. Run with `python -m pytest` or directly: `python tests/test_loop.py`."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from continuity_node import ContinuityNode  # noqa: E402

IMPACT = [
    "Impact and meaning matter more than money; I value purpose.",
    "Chose the mission-driven role; the difference it makes is what I value.",
    "I optimize for purpose and contribution because the work must matter.",
]
OTHER = ["Kept a tight budget and moved savings into the emergency fund."]


def build(root):
    node = ContinuityNode(root, threshold=3)
    ids = []
    for t in IMPACT + OTHER:
        r = node.ingest(t)
        ids.append(r["id"])
    interps = [node.interpret(rid, accept=True) for rid in ids]
    node.derive_patterns()
    return node, interps


def test_promotion_and_dissent_and_rebuild():
    root = tempfile.mkdtemp(prefix="cn-test-")
    try:
        node, interps = build(root)
        pats = node.patterns.patterns

        # promotion: three distinct sources converge -> confirmed
        assert "impact-oriented" in pats
        assert pats["impact-oriented"]["status"] == "confirmed"
        assert pats["impact-oriented"]["evidence_weight"] == 3
        # single source -> proposed, not confirmed
        assert pats["frugal"]["status"] == "proposed"

        # dissent (append-only) demotes the pattern on rebuild
        impact = [it for it in interps if it["content"]["pattern_key"] == "impact-oriented"]
        node.review(impact[0]["id"], "rejected")
        node.derive_patterns()
        assert node.patterns.patterns["impact-oriented"]["status"] == "proposed"
        assert node.patterns.patterns["impact-oriented"]["evidence_weight"] == 2

        # ledger is append-only: nothing was deleted
        assert len(node.ledger.all()) == len(interps) + 1

        # rebuildable invariant: derived state is identical after wipe + rebuild
        before = {k: (v["status"], v["confidence"], v["evidence_weight"])
                  for k, v in node.patterns.patterns.items()}
        os.remove(node.index.path)
        os.remove(node.patterns.path)
        fresh = ContinuityNode(root, threshold=3)
        fresh.rebuild()
        after = {k: (v["status"], v["confidence"], v["evidence_weight"])
                 for k, v in fresh.patterns.patterns.items()}
        assert before == after, (before, after)

        # raw archive is canonical and unchanged
        assert len(fresh.raw.all_records()) == 4
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    test_promotion_and_dissent_and_rebuild()
    print("all tests passed")
