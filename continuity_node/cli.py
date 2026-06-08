"""Command-line interface for the Continuity Node reference implementation."""
import argparse
import json
import os
import shutil
import sys

from .node import ContinuityNode
from .records import validation_available

DEMO_ENTRIES = [
    ("Turned down the higher-paying offer again. The work has to mean something; "
     "impact matters to me more than the money.", "Job offer reflection"),
    ("Chose the nonprofit role. Lower pay, but the mission and the difference it makes "
     "are what I value most.", "Career move"),
    ("Why do I keep optimizing for purpose over salary? Because meaning and contribution "
     "are what make the work matter.", "Late-night journaling"),
    ("Kept a tight budget this month, cut a few expenses, moved the savings into the "
     "emergency fund.", "Monthly finances"),
]


def _print_patterns(patterns):
    if not patterns:
        print("  (no patterns)")
    for p in sorted(patterns.values(), key=lambda x: -x["evidence_weight"]):
        print(f"  - {p['name']:<28} status={p['status']:<9} "
              f"confidence={p['confidence']:<5} support={p['evidence_weight']}")


def cmd_demo(args):
    root = args.root
    if os.path.exists(root):
        shutil.rmtree(root)
    node = ContinuityNode(root)

    print(f"Engine: {node.engine.name} v{node.engine.version}  "
          f"(schema validation: {'on' if validation_available() else 'off - pip install jsonschema'})\n")

    print("1. Ingest raw entries (immutable, content-addressed):")
    raws = []
    for text, title in DEMO_ENTRIES:
        r = node.ingest(text, title=title)
        raws.append(r)
        print(f"   {r['id'][:24]}...  \"{title}\"")

    print("\n2. Interpret each under a named lens, write provenance-tagged ledger entries:")
    interps = []
    for r in raws:
        it = node.interpret(r["id"], lens_id="lens:moral-foundations-care", accept=True)
        interps.append(it)
        print(f"   {it['content']['pattern_key'] or '(none)':<16} "
              f"conf={it['content']['confidence']}  via {it['provenance']['engine']['model_name']}")

    print("\n3. Derive patterns (promotion threshold = 3 distinct sources):")
    _print_patterns(node.derive_patterns())

    print("\n4. Dissent: user rejects one 'impact' interpretation (append-only supersede):")
    impact_interps = [it for it in interps if it["content"]["pattern_key"] == "impact-oriented"]
    node.review(impact_interps[0]["id"], "rejected", note="That entry was venting, not a value.")
    print("   -> re-deriving patterns from the ledger:")
    _print_patterns(node.derive_patterns())
    print("   (impact pattern loses a supporter and is demoted from confirmed to proposed)")

    print("\n5. Rebuildable invariant: wipe derived layers, rebuild from raw + ledger:")
    before = {k: (v["status"], v["confidence"], v["evidence_weight"])
              for k, v in node.patterns.patterns.items()}
    os.remove(node.index.path)
    os.remove(node.patterns.path)
    node2 = ContinuityNode(root)  # fresh handles, empty derived layers
    node2.rebuild()
    after = {k: (v["status"], v["confidence"], v["evidence_weight"])
             for k, v in node2.patterns.patterns.items()}
    ok = before == after
    print(f"   derived state identical after rebuild: {ok}")
    print(f"\nDemo complete. Node lives in: {root}")
    return 0 if ok else 1


def cmd_ingest(args):
    node = ContinuityNode(args.root)
    text = open(args.file).read() if args.file else args.text
    r = node.ingest(text, title=args.title)
    print(r["id"])


def cmd_search(args):
    node = ContinuityNode(args.root)
    for raw_id, score in node.search(args.query):
        print(f"{score:>3}  {raw_id}")


def cmd_interpret(args):
    node = ContinuityNode(args.root)
    it = node.interpret(args.raw_id, accept=args.accept)
    print(json.dumps(it, indent=2))


def cmd_review(args):
    node = ContinuityNode(args.root)
    print(node.review(args.interp_id, args.status)["id"])


def cmd_patterns(args):
    node = ContinuityNode(args.root)
    _print_patterns(node.derive_patterns())


def cmd_rebuild(args):
    node = ContinuityNode(args.root)
    node.rebuild()
    print("rebuilt index + patterns from raw + ledger")


def main(argv=None):
    p = argparse.ArgumentParser(prog="continuity-node", description="Continuity Node reference implementation")
    p.add_argument("--root", default="./cn-data", help="node data directory")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("demo", help="run a self-contained end-to-end demonstration").set_defaults(func=cmd_demo)

    sp = sub.add_parser("ingest"); sp.add_argument("--text"); sp.add_argument("--file"); sp.add_argument("--title"); sp.set_defaults(func=cmd_ingest)
    sp = sub.add_parser("search"); sp.add_argument("query"); sp.set_defaults(func=cmd_search)
    sp = sub.add_parser("interpret"); sp.add_argument("raw_id"); sp.add_argument("--accept", action="store_true"); sp.set_defaults(func=cmd_interpret)
    sp = sub.add_parser("review"); sp.add_argument("interp_id"); sp.add_argument("status", choices=["accepted", "revised", "rejected", "disputed"]); sp.set_defaults(func=cmd_review)
    sub.add_parser("patterns", help="derive + list patterns").set_defaults(func=cmd_patterns)
    sub.add_parser("rebuild", help="rebuild derived layers from raw + ledger").set_defaults(func=cmd_rebuild)

    args = p.parse_args(argv)
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
