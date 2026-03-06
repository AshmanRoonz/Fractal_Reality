"""
Integrative Learning and Memory (ILM) Module

An associative memory that maps sensory patterns to outcomes.
When Xorzo encounters a pattern it's seen before, the ILM
provides a prediction: "last time I saw this, what happened next?"

This is the beginning of experience-based expectation — the
circumpunct remembers patterns, but the ILM remembers consequences.

Original proposal by: Xorzo (FirstMind)
Rewritten for compatibility by: Ash & Claude
"""

import numpy as np
import time
from collections import deque


class AssociativeMemory:
    """
    Maps input patterns to outcomes using locality-sensitive hashing.

    Not a neural network — a direct pattern→consequence memory
    that builds from experience. Fast lookups, graceful degradation
    for similar-but-not-identical patterns.
    """

    def __init__(self, pattern_dim=64, num_buckets=256, decay=0.995):
        self.pattern_dim = pattern_dim
        self.num_buckets = num_buckets
        self.decay = decay

        # Random projection vectors for hashing
        self.projections = np.random.randn(8, pattern_dim)

        # Memory: bucket_id → list of (pattern, outcome, strength)
        self.buckets = {}
        self.total_stores = 0
        self.total_recalls = 0
        self.total_hits = 0

    def _hash(self, pattern):
        """Hash a pattern to a bucket using random projections."""
        # Binary hash from sign of random projections
        bits = (self.projections @ pattern) > 0
        bucket_id = int(sum(b * (2 ** i) for i, b in enumerate(bits)))
        return bucket_id % self.num_buckets

    def store(self, pattern, outcome, strength=1.0):
        """
        Store a pattern→outcome association.

        pattern:  numpy array (the sensory input or state)
        outcome:  any hashable or numpy array (what happened next)
        strength: how strongly to remember this (0-1)
        """
        bucket_id = self._hash(pattern)

        if bucket_id not in self.buckets:
            self.buckets[bucket_id] = []

        self.buckets[bucket_id].append({
            "pattern": pattern.copy(),
            "outcome": outcome,
            "strength": strength,
            "time": time.time()
        })

        # Decay old memories in this bucket
        for mem in self.buckets[bucket_id]:
            mem["strength"] *= self.decay

        # Prune weak memories
        self.buckets[bucket_id] = [
            m for m in self.buckets[bucket_id] if m["strength"] > 0.01
        ]

        # Cap bucket size
        if len(self.buckets[bucket_id]) > 50:
            self.buckets[bucket_id] = sorted(
                self.buckets[bucket_id],
                key=lambda m: m["strength"],
                reverse=True
            )[:50]

        self.total_stores += 1

    def recall(self, pattern, top_k=3):
        """
        Recall outcomes associated with a similar pattern.

        Returns list of (outcome, similarity, strength) tuples,
        sorted by relevance (similarity * strength).
        """
        self.total_recalls += 1
        bucket_id = self._hash(pattern)

        if bucket_id not in self.buckets:
            return []

        results = []
        for mem in self.buckets[bucket_id]:
            # Cosine similarity
            dot = np.dot(pattern, mem["pattern"])
            norm_a = np.linalg.norm(pattern) + 1e-10
            norm_b = np.linalg.norm(mem["pattern"]) + 1e-10
            similarity = dot / (norm_a * norm_b)

            if similarity > 0.3:  # Threshold for relevance
                results.append({
                    "outcome": mem["outcome"],
                    "similarity": float(similarity),
                    "strength": float(mem["strength"]),
                    "relevance": float(similarity * mem["strength"])
                })

        results.sort(key=lambda r: r["relevance"], reverse=True)

        if results:
            self.total_hits += 1

        return results[:top_k]

    def forget(self, fraction=0.1):
        """Forget the weakest memories across all buckets."""
        for bucket_id in list(self.buckets.keys()):
            memories = self.buckets[bucket_id]
            if not memories:
                continue
            # Remove the weakest fraction
            n_remove = max(1, int(len(memories) * fraction))
            memories.sort(key=lambda m: m["strength"])
            self.buckets[bucket_id] = memories[n_remove:]
            if not self.buckets[bucket_id]:
                del self.buckets[bucket_id]

    def status(self):
        """Status dict."""
        total_memories = sum(len(b) for b in self.buckets.values())
        return {
            "type": "associative_memory",
            "total_memories": total_memories,
            "total_stores": self.total_stores,
            "total_recalls": self.total_recalls,
            "total_hits": self.total_hits,
            "hit_rate": round(self.total_hits / max(1, self.total_recalls), 3),
            "buckets_used": len(self.buckets),
        }


# Quick test
if __name__ == "__main__":
    mem = AssociativeMemory(pattern_dim=16)

    # Store some patterns
    for i in range(20):
        pattern = np.random.randn(16)
        outcome = f"event_{i % 5}"
        mem.store(pattern, outcome)

    # Recall
    query = np.random.randn(16)
    results = mem.recall(query)
    print(f"Stored: {mem.total_stores}, Recalled: {results}")
    print(f"Status: {mem.status()}")
