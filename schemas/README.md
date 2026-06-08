# Continuity Node — JSON Schemas (draft 2020-12)

Formal, machine-validatable schemas for the record types defined in **Appendix A** of the
*Continuity Node Framework* (Joseph JM Walker, Pair A Dimes, Inc., CC BY-4.0).

The Appendix A document presents the schemas as *illustrative* JSON (with `//` comments and
`"a | b | c"` enum hints) for human readers. This bundle is the *machine-readable* counterpart:
strict JSON Schema that a validator can enforce.

## Contents

```
continuity-node-records.schema.json   # the bundled schema (all record types, draft 2020-12)
examples/                             # one valid instance per record type
validate.py                           # validates the examples (or your own files) against the schema
README.md
```

## How it works

The schema defines one `$defs` entry per record type and a root `oneOf`. A valid instance is
**exactly one** record type, discriminated by its `record_type` field. Every type shares a common
**envelope** (`id`, `record_type`, `schema_version`, `created_at`, `last_modified`, `content_hash`)
via `$ref`.

Records are intentionally **extensible**: properties beyond those specified are allowed, matching
the appendix's "minimal yet extensible" design principle.

`format` keywords (`date-time`, `uri`) are present as annotations. Per JSON Schema 2020-12, format
is annotation-only unless a format-assertion vocabulary is enabled; `validate.py` runs structural
validation and does not assert formats by default.

## Usage

```bash
pip install jsonschema
python3 validate.py                       # validate the bundled examples
python3 validate.py path/to/your-record.json   # validate your own record(s)
```

Exit code is non-zero if any instance fails.
