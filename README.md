# Continuity Node — Reference Implementation

A runnable Python reference implementation accompanying the **Continuity Node Framework** defensive publication.

**Framework publication:** [Continuity Node Framework — Technical Disclosure Commons](https://www.tdcommons.org/dpubs_series/10374/) (June 7, 2026, CC BY-4.0)

The project explores a user-owned, local-first, longitudinal **memory-and-interpretation** architecture in which preserved source material and governed interpretive lineage are more durable than any particular inference model. This repository implements a meaningful Tier-1 subset of the broader framework; it is not the complete architecture and not a finished product.

```bash
python -m continuity_node demo
```

## What this repository demonstrates

The reference implementation wires together:

- a local, content-addressed raw text archive;
- a rebuildable lexical search index;
- an append-oriented, provenance-tagged interpretive ledger;
- user review and dissent through superseding interpretation records;
- governed pattern promotion and demotion based on accepted supporting sources;
- a swappable inference-engine interface with deterministic stub and local Ollama adapters;
- record hashing and optional JSON Schema validation; and
- reconstruction of derived search/pattern state from the canonical raw archive plus ledger.

## The three core invariants

1. **Raw–interpretation separation.** Raw payloads are content-addressed with SHA-256 and are treated as write-once through this reference implementation. Interpretations are separate derived records that point back to their source and record the engine identity and interpretive lens. Model output does not silently become canonical source material.
2. **Rebuildable derived state.** The lexical search index and pattern register are regenerable caches. `rebuild()` reconstructs them from the raw archive plus interpretive ledger; the included end-to-end test checks equivalence of the governed pattern state it asserts after a wipe-and-rebuild.
3. **Lineage over overwrite.** Reviews and dissent are represented by new ledger entries whose `parent_id` points to the interpretation they supersede. Conflicting or revised readings therefore remain in the ledger rather than being replaced in place.

These are **application-level behaviors**, not tamper-proof storage guarantees. The reference uses ordinary local files; it does not currently enforce filesystem immutability, cryptographic append-only storage, or encryption at rest.

## Quickstart

No external dependencies are required to run the default deterministic demo on Python 3.9+:

```bash
git clone <your-repo-url> continuity-node
cd continuity-node
python -m continuity_node demo
```

Optional extras:

```bash
pip install jsonschema     # enable runtime JSON Schema validation
pip install -e .           # install the `continuity-node` CLI
```

For a local LLM instead of the deterministic stub, run [Ollama](https://ollama.com), pull a model, and pass `OllamaEngine` to the node (see `continuity_node/engines/ollama.py`). The bundled adapter targets a configurable Ollama endpoint and defaults to `http://localhost:11434`.

## What the demo shows

The demo ingests four short journal entries, interprets them, derives patterns, records dissent, and rebuilds the derived layers:

```text
3. Derive patterns (promotion threshold = 3 distinct sources):
  - Impact-Oriented Decision Maker status=confirmed confidence=0.733 support=3
  - Financially Cautious           status=proposed  confidence=0.2   support=1

4. Dissent: user rejects one 'impact' interpretation (append-only supersede):
  - Impact-Oriented Decision Maker status=proposed  confidence=0.533 support=2
  (impact pattern loses a supporter and is demoted from confirmed to proposed)

5. Rebuildable invariant: wipe derived layers, rebuild from raw + ledger:
   derived state identical after rebuild: True
```

That run exercises the implemented provenance ledger, acceptance threshold, dissent/demotion path, and rebuild logic. The printed `True` reflects the specific governed pattern-state comparison performed by the demo; it is not a byte-for-byte comparison of every regenerated file.

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

| Module | Implemented role | State |
|---|---|---|
| `raw_archive.py` | Content-addressed raw text storage | canonical source layer |
| `search_index.py` | Lexical inverted index | rebuildable derived cache |
| `ledger.py` | Provenance-tagged interpretation lineage | canonical interpretive history |
| `patterns.py` | Threshold-based pattern promotion/demotion | rebuildable derived cache |
| `engines/` | Inference boundary | swappable adapter layer |
| `node.py` | Orchestration and `rebuild()` | runtime coordinator |
| `schemas/` | Draft 2020-12 record schema and validator | optional validation support |

### Engine interchangeability

`engines/base.py` defines the `InferenceEngine` contract. `StubEngine` is deterministic and dependency-free; `OllamaEngine` implements the same interface against a local Ollama endpoint. Engine identity is recorded in each generated interpretation's provenance so later interpretations can coexist with earlier ones.

The current interpretation record also stores the lens identifier, supporting evidence, counter-evidence, confidence, and user-response state. **It does not persist the complete inference prompt in each interpretation record.** That distinction matters when comparing this Tier-1 implementation with the broader disclosure.

### JSON Schema validation

`schemas/continuity-node-records.schema.json` defines the framework's nine record types using JSON Schema draft 2020-12. When the optional `jsonschema` dependency is available, records created through `finalize()` are validated before being written. Without that dependency—or if the validator cannot be loaded—runtime validation is not enforced.

```bash
python schemas/validate.py
```

The schema covers more of the framework than the runtime currently operationalizes. A record type being defined in the schema does **not** mean the repository implements the corresponding subsystem.

## Implementation boundary

### Implemented

- SHA-256 content addressing and deduplication for ingested raw text;
- raw/interpretation separation;
- append-oriented interpretation records with supersede chains;
- accepted, revised, rejected, and disputed user-review states;
- governed pattern promotion/demotion from accepted distinct sources;
- rebuildable lexical search and pattern layers;
- deterministic stub inference;
- local Ollama inference adapter;
- record envelope/content hashes; and
- optional JSON Schema validation.

### Simplified

- search is lexical only; there is no semantic/vector retrieval;
- storage is local plaintext files with no encryption-at-rest implementation;
- append-only behavior is enforced by the application path, not by a tamper-evident storage backend;
- the bundled reference is single-user; and
- the deterministic stub uses coarse keyword heuristics rather than learned inference.

### Schema-defined but not operational subsystems

The schema includes record types for `lens`, `witness_packet`, `migration`, `continuity_will`, `audit_event`, and `interchange_abstraction`, but this reference runtime does not currently provide complete operational subsystems for those concepts.

### Not implemented here

- witness federation;
- encrypted semantic search;
- continuity will / endowment execution;
- MASI export;
- posthumous-access governance; and
- the broader multi-generation continuity mechanisms described by the framework.

## Project layout

```text
continuity-node/
├── continuity_node/
│   ├── ids.py  records.py  raw_archive.py  search_index.py
│   ├── ledger.py  patterns.py  node.py  cli.py
│   └── engines/  (base.py, stub.py, ollama.py)
├── schemas/      (JSON Schema + examples + validator)
├── tests/        (end-to-end test of the implemented loop)
├── pyproject.toml
└── LICENSE
```

## Testing

```bash
python tests/test_loop.py        # or: python -m pytest
```

The included end-to-end test asserts pattern promotion, dissent-driven demotion, ledger retention of superseded entries, preservation of the four raw records, and equivalence of the tested pattern fields (`status`, `confidence`, and `evidence_weight`) after derived files are removed and rebuilt.

This cleanup review inspected the test implementation but did not independently execute it.

## Publication, license, and citation

The repository is companion code to the **Continuity Node Framework** defensive publication in Technical Disclosure Commons:

- Joseph JM Walker, *Continuity Node Framework*, June 7, 2026
- https://www.tdcommons.org/dpubs_series/10374/

This repository is released under **CC BY-4.0**. If you build on it, retain appropriate attribution to the framework and this reference implementation.

The purpose of the defensive publication and public reference implementation is to place these architectural ideas in the commons while preserving clear provenance for the work.