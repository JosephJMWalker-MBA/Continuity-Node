"""A deterministic, dependency-free engine.

It is intentionally not "smart": it maps text to a coarse theme by keyword, so the
end-to-end loop (and the convergence that drives pattern promotion) is reproducible on any
machine with no model installed. Replace it with OllamaEngine or any other adapter; the
node does not change.
"""
import re

from .base import InferenceEngine

_TOKEN = re.compile(r"[a-z']+")

# (pattern_key, pattern_name, claim, trigger keywords)
_THEMES = [
    ("impact-oriented", "Impact-Oriented Decision Maker",
     "Prioritizes long-term impact and meaning over short-term financial comfort.",
     {"impact", "meaning", "values", "mission", "purpose", "matter", "difference", "contribution"}),
    ("frugal", "Financially Cautious",
     "Tends toward saving and financial caution.",
     {"save", "saving", "frugal", "budget", "spend", "money", "cost", "expense"}),
    ("risk-averse", "Risk-Averse",
     "Shows caution toward uncertainty and risk.",
     {"risk", "afraid", "worry", "worried", "safe", "secure", "cautious", "fear"}),
]


class StubEngine(InferenceEngine):
    name = "stub-heuristic"
    version = "1"
    provider = "local"

    def interpret(self, text: str, lens_id: str) -> dict:
        tokens = set(_TOKEN.findall(text.lower()))
        best, best_hits = None, 0
        for key, pname, claim, kws in _THEMES:
            hits = len(tokens & kws)
            if hits > best_hits:
                best, best_hits = (key, pname, claim), hits
        if best is None:
            return {
                "claim": "No clear value pattern detected in this entry.",
                "pattern_key": None, "pattern_name": None,
                "confidence": 0.3, "supporting_evidence": text[:120], "counter_evidence": [],
            }
        key, pname, claim = best
        return {
            "claim": claim,
            "pattern_key": key,
            "pattern_name": pname,
            "confidence": round(min(0.95, 0.5 + 0.1 * best_hits), 3),
            "supporting_evidence": text.strip()[:140],
            "counter_evidence": [],
        }
