# Continuity Node — Reference Implementation

> Personal.ai remembers. A continuity node argues with you.

A user-owned, local-first, longitudinal **memory-and-interpretation** system. The durable
asset is not the AI model — it is the preserved, provenance-tagged map of how *you* reasoned
over time. Inference engines are interchangeable; the continuity layer persists.

This is the runnable reference for the **Continuity Node Framework** (defensive prior art,
CC BY-4.0, Joseph JM Walker, Pair A Dimes, Inc.). It exists to show the architecture is
buildable today, not vaporware — the whole loop runs on a laptop with no model and no cloud.

```
$ python -m continuity_node demo
```

## The three invariants

1. **Raw–interpretation separation.** Raw records are immutable and content-addressed
   (SHA-256). Every interpretation is a separate, derived record that points *back* to the raw
   source, the engine that produced it, and the lens it was produced under. Model output never
   silently becomes canon.
2. **Rebuildable from raw.** Search indexes and the pattern register are regenerable caches.
   Delete them and `rebuild()` reconstructs them from the raw archive plus the ledger. Only raw
   + ledger are canonical.
3. **Lineage over storage.** Reviews, dissent, and reinterpretation are *append-only* — a new
   entry supersedes its parent rather than overwriting it. Conflicting interpretations coexist.

## Quickstart

No dependencies required to run the demo (Python 3.9+):

```bash
git clone <your-repo-url> continuity-node
cd continuity-node
python -m continuity_node demo
```

Optional extras:

```bash
pip install jsonschema     # turn on runtime schema validation of every record
pip install -e .           # install the `continuity-node` CLI
```

For a real local LLM instead of the deterministic stub, run [Ollama](https://ollama.com),
pull a model, and pass `OllamaEngine` to the node (see `continuity_node/engines/ollama.py`).
No data leaves your machine.

## What the demo shows

The demo ingests four short journal entries, interprets each, derives patterns, then dissents
and rebuilds:

```
3. Derive patterns (promotion threshold = 3 distinct sources):
  - Impact-Oriented Decision Maker status=confirmed confidence=0.733 support=3
  - Financially Cautious           status=proposed  confidence=0.2   support=1

4. Dissent: user rejects one 'impact' interpretation (append-only supersede):
  - Impact-Oriented Decision Maker status=proposed  confidence=0.533 support=2
  (impact pattern loses a supporter and is demoted from confirmed to proposed)

5. Rebuildable invariant: wipe derived layers, rebuild from raw + ledger:
   derived state identical after rebuild: True
```

That single run exercises four framework claims: a provenance-tagged interpretive ledger,
user-governed pattern promotion, append-only dissent/demotion, and the rebuildable invariant.

## CLI

```bash
python -m continuity_node --root ./cn-data ingest --text "..." --title "..."
python -m continuity_node --root ./cn-data search "impact"
python -m continuity_node --root ./cn-data interpret <raw_id> --accept
python -m continuity_node --root ./cn-data review <interp_id> rejected
python -m continuity_node --root ./cn-data patterns
python -m continuity_node --root ./cn-data rebuild
```

## Architecture

Each module maps to a layer of the framework:

| Module | Framework layer | Canonical? |
|---|---|---|
| `raw_archive.py` | 1 · Raw Archive (immutable, content-addressed) | **canonical** |
| `search_index.py` | 2 · Search Index (lexical; swap in FTS5 + vectors) | rebuildable |
| `ledger.py` | 3 · Interpretive Ledger (append-only, provenance-tagged) | **canonical** |
| `patterns.py` | 4 · Pattern Register (governed promotion/demotion) | rebuildable |
| `engines/` | inference boundary (interchangeable) | — |
| `node.py` | orchestration + `rebuild()` | — |
| `schemas/` | record schemas (draft 2020-12) + validator | — |

### Engine interchangeability, in the code

`engines/base.py` defines the `InferenceEngine` contract. `StubEngine` (default, zero-deps,
deterministic) and `OllamaEngine` (real local LLM) both implement it. Swapping engines never
touches the archive, ledger, or patterns — which is the entire thesis. The engine identity is
recorded in each interpretation's provenance, so a future engine can reinterpret old raw data
without erasing the old reading.

### Schema-enforced records

`schemas/continuity-node-records.schema.json` is a formal JSON Schema (draft 2020-12) for all
nine record types. With `jsonschema` installed, the node validates every record as it is
written, so the data on disk is provably conformant. Validate examples or your own records:

```bash
python schemas/validate.py
```

## Status — honest about the boundary

This reference faithfully implements the framework's **Tier 1** core (raw archive, lexical
search, provenance ledger, governed patterns, rebuildable invariant, engine-interchangeable
inference). Several layers are intentionally stubbed or out of scope here and are flagged in
the framework's three-tier claim structure:

- **Implemented:** raw↔interpretation separation, append-only ledger with supersede-chains,
  pattern promotion/demotion with dissent, rebuildable derived layers, pluggable engines,
  schema validation, BagIt-friendly file layout.
- **Stubbed / simplified:** lexical-only search (no semantic vectors yet — and note the
  framework's finding that embeddings leak and must be treated as sensitive data); keyword
  stub engine; single-user; no encryption-at-rest wired in.
- **Not in this repo (research frontier):** witness federation, encrypted semantic search,
  continuity will / endowment, MASI export, posthumous-access ethics.

This is a starting point others can fork — not a finished product.

## Project layout

```
continuity-node/
├── continuity_node/
│   ├── ids.py  records.py  raw_archive.py  search_index.py
│   ├── ledger.py  patterns.py  node.py  cli.py
│   └── engines/  (base.py, stub.py, ollama.py)
├── schemas/      (JSON Schema + examples + validator)
├── tests/        (end-to-end test of the loop + invariants)
├── pyproject.toml
└── LICENSE
```

## Testing

```bash
python tests/test_loop.py        # or: python -m pytest
```

Asserts promotion, append-only dissent/demotion, that nothing is deleted from the ledger, and
that derived state is byte-for-byte identical after a wipe-and-rebuild.

## License & citation

Released under **CC BY-4.0**. Based on the Continuity Node Framework by Joseph Walker,
Pair A Dimes, Inc. (June 2026). If you build on this, please cite the framework and retain the
attribution. Defensive prior art: the goal is to keep human interpretive continuity in the
commons, not to capture it.
