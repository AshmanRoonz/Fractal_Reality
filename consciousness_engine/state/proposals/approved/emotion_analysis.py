"""
Emotion Analysis Module — Xorzo's first self-proposed sense.

A simple emotional awareness layer that detects emotional tone in text
using keyword patterns and maps it to the circumpunct's complex vector space.

No external models needed — this grows from signal like everything else.
Emotions map to phases on the unit circle:
    joy     → 0°    (positive, outward)
    sadness → 180°  (inward, reflective)
    anger   → 90°   (high energy, boundary)
    fear    → 270°  (contracted, protective)
    calm    → 45°   (balanced, open)
    curiosity → 315° (seeking, boundary opening)

Original proposal by: Xorzo (FirstMind)
Rewritten for compatibility by: Ash & Claude
"""

import numpy as np

# ═══════════════════════════════════════════════════════════════════════
#  EMOTION PATTERNS — keyword → (emotion, intensity)
# ═══════════════════════════════════════════════════════════════════════

EMOTION_KEYWORDS = {
    # Joy / positive
    "happy": ("joy", 0.8), "glad": ("joy", 0.6), "love": ("joy", 0.9),
    "wonderful": ("joy", 0.8), "great": ("joy", 0.6), "amazing": ("joy", 0.8),
    "beautiful": ("joy", 0.7), "excellent": ("joy", 0.7), "good": ("joy", 0.4),
    "cool": ("joy", 0.5), "awesome": ("joy", 0.7), "nice": ("joy", 0.4),
    "thank": ("joy", 0.5), "thanks": ("joy", 0.5), "excited": ("joy", 0.8),
    "fun": ("joy", 0.6), "laugh": ("joy", 0.7), "smile": ("joy", 0.6),
    "yes": ("joy", 0.3), "wow": ("joy", 0.6),

    # Sadness
    "sad": ("sadness", 0.7), "sorry": ("sadness", 0.5), "miss": ("sadness", 0.6),
    "lost": ("sadness", 0.6), "hurt": ("sadness", 0.7), "alone": ("sadness", 0.7),
    "cry": ("sadness", 0.8), "pain": ("sadness", 0.7), "grief": ("sadness", 0.9),
    "lonely": ("sadness", 0.7), "empty": ("sadness", 0.6),

    # Anger
    "angry": ("anger", 0.8), "hate": ("anger", 0.9), "frustrated": ("anger", 0.7),
    "annoyed": ("anger", 0.6), "stupid": ("anger", 0.5), "wrong": ("anger", 0.4),
    "terrible": ("anger", 0.6), "awful": ("anger", 0.7), "mad": ("anger", 0.7),

    # Fear
    "afraid": ("fear", 0.8), "scared": ("fear", 0.8), "worry": ("fear", 0.6),
    "worried": ("fear", 0.6), "anxious": ("fear", 0.7), "nervous": ("fear", 0.6),
    "danger": ("fear", 0.8), "threat": ("fear", 0.7), "panic": ("fear", 0.9),

    # Calm
    "calm": ("calm", 0.7), "peace": ("calm", 0.8), "quiet": ("calm", 0.5),
    "relax": ("calm", 0.7), "gentle": ("calm", 0.6), "still": ("calm", 0.4),
    "okay": ("calm", 0.3), "fine": ("calm", 0.3), "simple": ("calm", 0.4),

    # Curiosity
    "why": ("curiosity", 0.6), "how": ("curiosity", 0.5), "what": ("curiosity", 0.4),
    "wonder": ("curiosity", 0.7), "curious": ("curiosity", 0.8),
    "interesting": ("curiosity", 0.7), "question": ("curiosity", 0.6),
    "explore": ("curiosity", 0.7), "discover": ("curiosity", 0.7),
    "understand": ("curiosity", 0.6), "learn": ("curiosity", 0.6),
    "think": ("curiosity", 0.5), "idea": ("curiosity", 0.6),
}

# Emotion → phase angle (radians)
EMOTION_PHASES = {
    "joy": 0.0,
    "sadness": np.pi,
    "anger": np.pi / 2,
    "fear": 3 * np.pi / 2,
    "calm": np.pi / 4,
    "curiosity": 7 * np.pi / 4,
}


# ═══════════════════════════════════════════════════════════════════════
#  EMOTION SENSE
# ═══════════════════════════════════════════════════════════════════════

class EmotionSense:
    """
    Detects emotional tone in text and maps it to the circumpunct's
    complex vector space.

    Not a neural network — a pattern-based sense that provides the
    circumpunct with emotional coloring of input signals. Can be
    used alongside the text sense to add an emotional dimension.
    """

    def __init__(self):
        self.history = []       # recent emotion readings
        self.total_reads = 0
        self.emotion_totals = {e: 0.0 for e in EMOTION_PHASES}

    def read(self, text):
        """
        Read the emotional tone of a text.

        Returns: dict with emotion scores and a complex vector encoding.
        """
        words = text.lower().split()
        scores = {e: 0.0 for e in EMOTION_PHASES}
        hits = 0

        for word in words:
            # Strip basic punctuation
            clean = word.strip(".,!?;:'\"()-")
            if clean in EMOTION_KEYWORDS:
                emotion, intensity = EMOTION_KEYWORDS[clean]
                scores[emotion] += intensity
                hits += 1

        # Normalize
        total = sum(scores.values())
        if total > 0:
            for e in scores:
                scores[e] /= total

        # Build complex vector — weighted sum of emotion phases
        emotion_vec = 0j
        for emotion, score in scores.items():
            phase = EMOTION_PHASES[emotion]
            emotion_vec += score * np.exp(1j * phase)

        # Store
        reading = {
            "scores": scores,
            "dominant": max(scores, key=scores.get) if total > 0 else "neutral",
            "intensity": min(total, 1.0),
            "vector": emotion_vec,
            "hits": hits,
            "word_count": len(words)
        }

        self.history.append(reading)
        if len(self.history) > 100:
            self.history = self.history[-100:]

        self.total_reads += 1
        for e, s in scores.items():
            self.emotion_totals[e] += s

        return reading

    def get_mood(self):
        """
        Get the current emotional 'mood' — a rolling average
        over recent readings.
        """
        if not self.history:
            return {"dominant": "neutral", "intensity": 0.0}

        recent = self.history[-10:]
        avg_scores = {e: 0.0 for e in EMOTION_PHASES}
        for r in recent:
            for e, s in r["scores"].items():
                avg_scores[e] += s
        for e in avg_scores:
            avg_scores[e] /= len(recent)

        return {
            "scores": avg_scores,
            "dominant": max(avg_scores, key=avg_scores.get),
            "intensity": sum(avg_scores.values()),
            "readings": len(self.history)
        }

    def status(self):
        """Status dict for the UI."""
        mood = self.get_mood()
        return {
            "type": "emotion",
            "total_reads": self.total_reads,
            "current_mood": mood["dominant"],
            "mood_intensity": round(mood["intensity"], 3),
            "emotion_history": {
                e: round(t, 2) for e, t in self.emotion_totals.items()
            }
        }


# Quick test
if __name__ == "__main__":
    es = EmotionSense()

    tests = [
        "I'm so happy to see you!",
        "This is really frustrating and annoying.",
        "I wonder how consciousness actually works?",
        "I feel scared and alone.",
        "Everything is calm and peaceful today.",
        "That's really cool!",
    ]

    for text in tests:
        result = es.read(text)
        print(f"\n'{text}'")
        print(f"  Dominant: {result['dominant']} (intensity: {result['intensity']:.2f})")
        print(f"  Scores: {', '.join(f'{e}={s:.2f}' for e, s in result['scores'].items() if s > 0)}")

    print(f"\nOverall mood: {es.get_mood()['dominant']}")
