"""Layer 2 - Search Index: a derived, rebuildable cache over the Raw Archive.

This reference uses a simple in-process lexical inverted index so the repo has no
search dependency. Swap in SQLite FTS5 + a vector store (Chroma/FAISS) for hybrid
retrieval; nothing else in the node depends on how this layer is implemented. The
index holds no canonical state and can be deleted and rebuilt at any time.
"""
import json
import os
import re

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return _TOKEN.findall(text.lower())


class SearchIndex:
    def __init__(self, path: str):
        self.path = path
        self.index = {}  # token -> {raw_id: count}
        self._load()

    def add(self, raw_id: str, text: str):
        for tok in tokenize(text):
            self.index.setdefault(tok, {})
            self.index[tok][raw_id] = self.index[tok].get(raw_id, 0) + 1
        self._save()

    def search(self, query: str, k: int = 5):
        scores = {}
        for tok in tokenize(query):
            for raw_id, c in self.index.get(tok, {}).items():
                scores[raw_id] = scores.get(raw_id, 0) + c
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:k]

    def rebuild(self, raw_archive):
        """Regenerate the entire index from the canonical Raw Archive."""
        self.index = {}
        for rec in raw_archive.all_records():
            self.add(rec["id"], raw_archive.get_content(rec["id"]))
        self._save()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                self.index = json.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.index, f)
