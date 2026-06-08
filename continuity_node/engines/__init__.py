from .base import InferenceEngine
from .stub import StubEngine

__all__ = ["InferenceEngine", "StubEngine", "OllamaEngine"]


def __getattr__(name):
    # Import OllamaEngine lazily so urllib/model deps aren't touched unless used.
    if name == "OllamaEngine":
        from .ollama import OllamaEngine
        return OllamaEngine
    raise AttributeError(name)
