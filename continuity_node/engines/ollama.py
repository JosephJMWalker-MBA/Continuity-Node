"""Optional engine: a local LLM via Ollama (http://localhost:11434).

Demonstrates that the interpretation step is genuinely swappable - this adapter implements
the same `interpret` contract as StubEngine. Requires a running Ollama with a pulled model;
falls back with a clear error if unreachable. No data leaves the machine.
"""
import json
import urllib.request

from .base import InferenceEngine

_PROMPT = """You are an interpretation engine for a user-owned memory system.
Read the entry and respond with ONLY a JSON object, no prose:
{{"claim": str, "pattern_key": str (lowercase-hyphenated theme), "pattern_name": str,
  "confidence": float 0..1, "supporting_evidence": str, "counter_evidence": [str]}}

Interpretive lens: {lens}
Entry:
{text}
"""


class OllamaEngine(InferenceEngine):
    provider = "local"

    def __init__(self, model="llama3.1", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.name = f"ollama/{model}"
        self.version = model

    def interpret(self, text: str, lens_id: str) -> dict:
        payload = json.dumps({
            "model": self.model,
            "prompt": _PROMPT.format(lens=lens_id, text=text),
            "stream": False,
            "format": "json",
        }).encode("utf-8")
        req = urllib.request.Request(f"{self.host}/api/generate", data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read())
        out = json.loads(body["response"])
        out.setdefault("counter_evidence", [])
        out.setdefault("confidence", 0.5)
        return out
