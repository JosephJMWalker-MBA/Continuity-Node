"""Continuity Node - reference implementation of the Continuity Node Framework.

A user-owned, local-first longitudinal memory-and-interpretation system. Released as
defensive prior art under CC BY-4.0 (Joseph JM Walker, Pair A Dimes, Inc.).
"""
from .node import ContinuityNode
from .engines import InferenceEngine, StubEngine

__version__ = "0.1.0"
__all__ = ["ContinuityNode", "InferenceEngine", "StubEngine"]
