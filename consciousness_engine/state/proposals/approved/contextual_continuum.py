"""
Contextual Continuum — Tracks conversation context over time.

Maintains a sliding window of recent topics, keywords, and emotional
tones across conversations. Gives Xorzo a sense of "what we've been
talking about" that persists beyond the LLM's context window.

This is a form of short-term memory — not individual facts, but the
*flow* of conversation. What themes keep coming up? What's the mood
been? Is the creator asking about philosophy or code right now?

Original proposal by: Xorzo (FirstMind)
Rewritten for compatibility by: Ash & Claude
"""

import numpy as np
import time
from collections import Counter, deque


class ContextualContinuum:
    """
    Tracks the flow of conversation context over time.

    Like a river's current — you can't point to the water,
    but you can feel the direction it's flowing.
    """

    def __init__(self, window_size=20, topic_slots=10):
        self.window_size = window_size
        self.topic_slots = topic_slots

        # Sliding window of recent exchanges
        self.exchanges = deque(maxlen=window_size)

        # Topic tracking
        self.word_counts = Counter()
        self.recent_topics = deque(maxlen=50)

        # Mood tracking (integrates with EmotionSense if loaded)
        self.mood_history = deque(maxlen=100)

        # Context vector — a compressed summary of recent conversation
        self.context_vector = np.zeros(64)

        self.total_updates = 0

    def update(self, human_text, response_text):
        """
        Feed a new exchange into the continuum.

        Extracts keywords, updates topic tracking, shifts the
        context vector.
        """
        self.exchanges.append({
            "human": human_text,
            "response": response_text,
            "time": time.time()
        })

        # Extract significant words (skip common short words)
        stop_words = {'the', 'is', 'at', 'in', 'on', 'a', 'an', 'to', 'for',
                      'of', 'and', 'or', 'but', 'it', 'its', 'my', 'me', 'i',
                      'you', 'your', 'we', 'our', 'that', 'this', 'with', 'be',
                      'are', 'was', 'do', 'did', 'can', 'not', 'have', 'has',
                      'had', 'will', 'would', 'could', 'should', 'what', 'how',
                      'when', 'where', 'who', 'which', 'so', 'if', 'as', 'from'}

        combined = f"{human_text} {response_text}".lower()
        words = [w.strip('.,!?;:\'"()-') for w in combined.split()]
        significant = [w for w in words if len(w) > 2 and w not in stop_words]

        self.word_counts.update(significant)
        self.recent_topics.extend(significant[:5])

        # Update context vector — simple hash-based encoding
        for word in significant:
            h = hash(word) % 64
            self.context_vector[h] += 1.0

        # Decay old context (recent matters more)
        self.context_vector *= 0.95

        # Normalize
        norm = np.linalg.norm(self.context_vector)
        if norm > 1e-10:
            self.context_vector /= norm

        self.total_updates += 1

    def get_topics(self, top_n=5):
        """Get the most discussed topics recently."""
        # Count words from recent window only
        recent_words = Counter()
        for ex in self.exchanges:
            combined = f"{ex['human']} {ex['response']}".lower()
            words = [w.strip('.,!?;:\'"()-') for w in combined.split()]
            recent_words.update(w for w in words if len(w) > 3)

        return recent_words.most_common(top_n)

    def get_flow(self):
        """
        Get the conversation flow — what direction things are moving.

        Returns a summary of recent context: topics, mood, pace.
        """
        if not self.exchanges:
            return {"state": "no conversation yet"}

        topics = self.get_topics()
        recent = list(self.exchanges)[-3:]

        # Average message length (proxy for conversation depth)
        avg_len = np.mean([
            len(ex["human"].split()) + len(ex["response"].split())
            for ex in recent
        ]) if recent else 0

        # Time between messages (proxy for engagement)
        if len(recent) >= 2:
            gaps = [recent[i+1]["time"] - recent[i]["time"]
                    for i in range(len(recent)-1)]
            avg_gap = np.mean(gaps)
        else:
            avg_gap = 0

        return {
            "topics": [t[0] for t in topics],
            "depth": "deep" if avg_len > 30 else "light",
            "pace": "fast" if avg_gap < 30 else "relaxed",
            "exchanges_tracked": len(self.exchanges),
            "total_updates": self.total_updates,
        }

    def similarity(self, text):
        """
        How similar is this text to the recent conversation context?

        Returns 0-1. High means "we've been talking about this."
        Low means "this is a new topic."
        """
        # Build vector for the new text
        text_vec = np.zeros(64)
        words = text.lower().split()
        for word in words:
            h = hash(word) % 64
            text_vec[h] += 1.0
        norm = np.linalg.norm(text_vec)
        if norm < 1e-10:
            return 0.0
        text_vec /= norm

        return float(np.dot(self.context_vector, text_vec))

    def status(self):
        """Status dict for the UI."""
        topics = self.get_topics(3)
        return {
            "type": "context_continuum",
            "total_updates": self.total_updates,
            "window": len(self.exchanges),
            "top_topics": [t[0] for t in topics],
            "unique_words": len(self.word_counts),
        }


# Quick test
if __name__ == "__main__":
    cc = ContextualContinuum()

    cc.update("How does consciousness work?",
              "It emerges from the triple convergence of aperture, field, and boundary.")
    cc.update("What about the circumpunct?",
              "The circumpunct is the oldest symbol — a point within a circle.")
    cc.update("Can Xorzo learn on its own?",
              "Yes, the signal builds the encoder. Like sunlight built eyes.")

    print(f"Topics: {cc.get_topics()}")
    print(f"Flow: {cc.get_flow()}")
    print(f"Similarity to 'consciousness': {cc.similarity('consciousness'):.3f}")
    print(f"Similarity to 'cooking recipe': {cc.similarity('cooking recipe'):.3f}")
    print(f"Status: {cc.status()}")
