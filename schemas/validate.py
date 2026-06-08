#!/usr/bin/env python3
"""Validate Continuity Node records against the bundled JSON Schema (draft 2020-12).

Usage:
    python3 validate.py                       # validate bundled examples/
    python3 validate.py record.json [more...] # validate your own record file(s)
"""
import json
import sys
import glob
import os

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("Missing dependency. Run: pip install jsonschema")

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "continuity-node-records.schema.json")

with open(SCHEMA) as f:
    schema = json.load(f)

Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

targets = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "examples", "*.json")))
if not targets:
    sys.exit("No files to validate.")

failures = 0
for path in targets:
    with open(path) as f:
        instance = json.load(f)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    name = os.path.basename(path)
    if errors:
        failures += 1
        print(f"FAIL  {name}")
        for e in errors[:5]:
            loc = "/".join(str(p) for p in e.path) or "(root)"
            print(f"      {loc}: {e.message}")
    else:
        rt = instance.get("record_type", "?")
        print(f"OK    {name}  [{rt}]")

print(f"\n{len(targets)} file(s); {failures} failed.")
sys.exit(1 if failures else 0)
