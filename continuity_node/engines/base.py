"""The inference engine boundary.

Engines are interchangeable: the node owns the archive, ledger, and patterns; the engine
only turns raw text into a structured interpretation. Swapping engines never touches the
continuity layer - that is the whole point of the architecture, made explicit in code.

An engine returns a dict with:
    claim            (str)   - the interpretation
    pattern_key      (str)   - stable key used to group convergent interpretations
    pattern_name     (str)   - human-readable name for a promoted pattern
    confidence       (float) - 0..1
    supporting_evidence (str)
    counter_evidence (list[str])
plus `name` / `version` identifying the engine for provenance.
"""
from abc import ABC, abstractmethod


class InferenceEngine(ABC):
    name = "base"
    version = "0"
    provider = "unknown"

    @abstractmethod
    def interpret(self, text: str, lens_id: str) -> dict:
        ...
