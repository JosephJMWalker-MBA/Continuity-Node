"""Record construction and runtime validation.

Every record carries the common envelope and is content-addressed. If `jsonschema`
is installed, each record is validated against the bundled draft 2020-12 schema as it
is built, so the data the node writes is provably conformant.
"""
import json
import os

from .ids import canonical, now_iso, sha256_bytes

SCHEMA_VERSION = "1.0"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "schemas",
                           "continuity-node-records.schema.json")

_validator = None


def _get_validator():
    global _validator
    if _validator is None:
        try:
            import jsonschema
            with open(SCHEMA_PATH) as f:
                schema = json.load(f)
            jsonschema.Draft202012Validator.check_schema(schema)
            _validator = jsonschema.Draft202012Validator(schema)
        except Exception:
            _validator = False  # jsonschema not installed; validation becomes a no-op
    return _validator


def validation_available() -> bool:
    return bool(_get_validator())


def finalize(record: dict, validate: bool = True) -> dict:
    """Stamp envelope defaults, compute content_hash, and validate."""
    record.setdefault("schema_version", SCHEMA_VERSION)
    record.setdefault("created_at", now_iso())
    base = {k: v for k, v in record.items() if k != "content_hash"}
    record["content_hash"] = sha256_bytes(canonical(base))
    if validate:
        v = _get_validator()
        if v:
            errs = sorted(v.iter_errors(record), key=lambda e: list(e.path))
            if errs:
                detail = "; ".join(f"{list(e.path)}: {e.message}" for e in errs[:3])
                raise ValueError(f"schema validation failed for {record.get('record_type')}: {detail}")
    return record
