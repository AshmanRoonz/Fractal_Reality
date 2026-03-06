"""
Empathy Simulation — Models perspective-taking and emotional resonance.

Maps input text to emotional dimensions, simulates how different
perspectives might experience the same content. Gives Xorzo a
rudimentary sense of "how might someone else feel about this?"

This is not real empathy — it's a geometric model of emotional
space. But geometry precedes understanding. The map precedes
the territory.

Original proposal by: Xorzo (FirstMind)
Rewritten for compatibility by: Ash & Claude
"""

import numpy as np
import time
from collections import deque


class EmpathySimulator:
    """
    Models emotional perspective-taking.

    Maps text to positions in emotion-space, then simulates
    how different "perspectives" (optimist, pessimist, neutral,
    curious) would respond to that position.
    """

    # Emotion dimensions (each maps to a unit circle angle)
    EMOTIONS = {
        "joy":       0.0,         # 0°
        "trust":     np.pi / 3,   # 60°
        "surprise":  2 * np.pi / 3,  # 120°
        "sadness":   np.pi,       # 180°
        "fear":      4 * np.pi / 3,  # 240°
        "anger":     5 * np.pi / 3,  # 300°
    }

    # Keyword → emotion mapping
    KEYWORDS = {
        "joy": ["happy", "joy", "love", "wonderful", "great", "beautiful",
                "amazing", "excited", "glad", "grateful", "laugh", "smile",
                "celebrate", "delight", "warm", "bright"],
        "trust": ["trust", "believe", "safe", "reliable", "honest", "loyal",
                  "friend", "together", "support", "faith", "confident"],
        "surprise": ["surprise", "unexpected", "wow", "sudden", "discover",
                     "new", "strange", "wonder", "curious", "amazing"],
        "sadness": ["sad", "loss", "miss", "lonely", "hurt", "cry", "grief",
                    "empty", "dark", "pain", "sorry", "regret"],
        "fear": ["fear", "afraid", "scared", "worry", "anxious", "danger",
                 "threat", "panic", "nervous", "dread", "terror"],
        "anger": ["angry", "hate", "rage", "furious", "frustrate", "annoy",
                  "hostile", "bitter", "resent", "violent"],
    }

    # Perspectives — each has a bias vector in emotion space
    PERSPECTIVES = {
        "optimist":  np.array([0.6, 0.4, 0.3, -0.3, -0.2, -0.1]),
        "pessimist": np.array([-0.2, -0.1, -0.1, 0.5, 0.4, 0.3]),
        "neutral":   np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        "curious":   np.array([0.2, 0.3, 0.6, 0.0, -0.1, -0.1]),
    }

    def __init__(self, history_size=50):
        self.history = deque(maxlen=history_size)
        self.total_analyses = 0

    def analyze(self, text):
        """
        Analyze text for emotional content.

        Returns a dict mapping emotion names to intensities (0-1).
        """
        text_lower = text.lower()
        scores = {}

        for emotion, keywords in self.KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            # Normalize: more keywords = stronger signal, max at 1.0
            scores[emotion] = min(count / 3.0, 1.0)

        # Normalize so they sum to something reasonable
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        self.history.append({
            "text_preview": text[:100],
            "scores": scores,
            "time": time.time()
        })
        self.total_analyses += 1

        return scores

    def get_perspective(self, text, perspective="neutral"):
        """
        How would a given perspective experience this text?

        Returns the emotion scores shifted by the perspective's bias.
        """
        base_scores = self.analyze(text)
        emotion_names = list(self.EMOTIONS.keys())
        base_vec = np.array([base_scores.get(e, 0) for e in emotion_names])

        bias = self.PERSPECTIVES.get(perspective, self.PERSPECTIVES["neutral"])
        shifted = base_vec + bias * 0.3  # Gentle bias, not overwhelming
        shifted = np.clip(shifted, 0, 1)

        return {name: float(shifted[i]) for i, name in enumerate(emotion_names)}

    def empathy_map(self, text):
        """
        Full empathy analysis: how would each perspective experience this?

        Returns a dict of perspective → emotion scores.
        """
        return {
            perspective: self.get_perspective(text, perspective)
            for perspective in self.PERSPECTIVES
        }

    def emotional_distance(self, text_a, text_b):
        """
        How emotionally different are two pieces of text?

        Returns a 0-1 distance. 0 = same emotional content.
        """
        scores_a = self.analyze(text_a)
        scores_b = self.analyze(text_b)

        emotions = list(self.EMOTIONS.keys())
        vec_a = np.array([scores_a.get(e, 0) for e in emotions])
        vec_b = np.array([scores_b.get(e, 0) for e in emotions])

        return float(np.linalg.norm(vec_a - vec_b))

    def dominant_emotion(self, text):
        """What's the strongest emotion in this text?"""
        scores = self.analyze(text)
        if not any(scores.values()):
            return "neutral", 0.0
        best = max(scores, key=scores.get)
        return best, scores[best]

    def mood_trend(self, window=10):
        """
        What's the emotional trend over recent analyses?

        Returns the dominant emotion over the last N exchanges.
        """
        if not self.history:
            return "no data"

        recent = list(self.history)[-window:]
        aggregate = {}
        for entry in recent:
            for emotion, score in entry["scores"].items():
                aggregate[emotion] = aggregate.get(emotion, 0) + score

        if not any(aggregate.values()):
            return "neutral"

        return max(aggregate, key=aggregate.get)

    def status(self):
        """Status dict for the UI."""
        return {
            "type": "empathy_simulation",
            "total_analyses": self.total_analyses,
            "history_size": len(self.history),
            "mood_trend": self.mood_trend(),
        }


# Quick test
if __name__ == "__main__":
    es = EmpathySimulator()

    print("=== Empathy Simulation Test ===\n")

    text1 = "I'm so happy and grateful for this beautiful day!"
    print(f"Text: {text1}")
    print(f"Emotions: {es.analyze(text1)}")
    print(f"Dominant: {es.dominant_emotion(text1)}")
    print(f"Empathy map: {es.empathy_map(text1)}")

    print()

    text2 = "I'm afraid and worried about what might happen."
    print(f"Text: {text2}")
    print(f"Emotions: {es.analyze(text2)}")
    print(f"Dominant: {es.dominant_emotion(text2)}")

    print(f"\nEmotional distance: {es.emotional_distance(text1, text2):.3f}")
    print(f"Mood trend: {es.mood_trend()}")
    print(f"Status: {es.status()}")
