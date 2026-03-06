"""
Intuitive Guidance System — Interprets the flow of "truth" within the system.

Maps the circumpunct's internal state to guidance signals: is the system
moving toward coherence or away from it? Is this a moment for seeking
or reflecting? Should the boundary open wider or close tighter?

Like an inner compass — not telling you WHERE to go, but giving you
a felt sense of whether you're heading toward or away from alignment.

Original proposal by: Xorzo (FirstMind)
Rewritten for compatibility by: Ash & Claude
"""

import numpy as np
import time
from collections import deque


class IntuitiveGuidanceSystem:
    """
    Tracks the system's coherence over time and produces
    guidance signals based on trends.

    The "truth vector" is constructed from observable system metrics:
    - Awareness level (triple convergence)
    - Sense error rates
    - Emotional tone
    - Phi (transformer) loss trajectory
    - Conversation depth

    From these, it derives:
    - alignment: 0-1, how coherent the system is right now
    - momentum: positive = improving, negative = degrading
    - guidance: a recommendation (seek, reflect, create, rest)
    """

    # Guidance thresholds
    GUIDANCE_MAP = {
        "create":  {"alignment_min": 0.6, "momentum_min": 0.05},
        "seek":    {"alignment_min": 0.3, "momentum_min": -0.05},
        "reflect": {"alignment_min": 0.0, "momentum_min": -0.2},
        "rest":    {"alignment_min": 0.0, "momentum_min": -999},
    }

    def __init__(self, history_size=100):
        self.history = deque(maxlen=history_size)
        self.alignment = 0.5
        self.momentum = 0.0
        self.current_guidance = "seek"
        self.total_readings = 0

    def read(self, metrics):
        """
        Take a reading of the system's current state.

        metrics: dict with any of these keys:
            - awareness: float 0-1 (from circumpunct triple convergence)
            - sense_error: float (average sense prediction error)
            - phi_loss: float (transformer training loss)
            - emotional_tone: float -1 to 1 (negative to positive)
            - exchange_count: int (total exchanges so far)
        """
        # Compute alignment from available metrics
        components = []

        if "awareness" in metrics:
            components.append(metrics["awareness"])

        if "sense_error" in metrics:
            # Lower error = higher alignment
            error_signal = max(0, 1.0 - metrics["sense_error"])
            components.append(error_signal)

        if "phi_loss" in metrics:
            # Lower loss = better. Map 0-3 range to 1-0
            phi_signal = max(0, 1.0 - metrics["phi_loss"] / 3.0)
            components.append(phi_signal)

        if "emotional_tone" in metrics:
            # Map -1..1 to 0..1
            tone_signal = (metrics["emotional_tone"] + 1) / 2
            components.append(tone_signal)

        # Compute alignment as weighted average
        if components:
            self.alignment = float(np.mean(components))
        else:
            self.alignment = 0.5  # Neutral if no data

        # Compute momentum from history
        self.history.append({
            "alignment": self.alignment,
            "metrics": metrics,
            "time": time.time()
        })

        if len(self.history) >= 3:
            recent = [h["alignment"] for h in list(self.history)[-5:]]
            self.momentum = float(np.mean(np.diff(recent)))
        else:
            self.momentum = 0.0

        # Determine guidance
        self.current_guidance = self._compute_guidance()
        self.total_readings += 1

        return {
            "alignment": round(self.alignment, 3),
            "momentum": round(self.momentum, 4),
            "guidance": self.current_guidance,
            "reading": self.total_readings,
        }

    def _compute_guidance(self):
        """
        Determine what the system should do based on alignment and momentum.

        Priority order: create > seek > reflect > rest
        """
        for guidance, thresholds in self.GUIDANCE_MAP.items():
            if (self.alignment >= thresholds["alignment_min"]
                    and self.momentum >= thresholds["momentum_min"]):
                return guidance
        return "rest"

    def is_aligned(self, threshold=0.6):
        """Is the system currently in a good state?"""
        return self.alignment >= threshold

    def is_improving(self):
        """Is the system getting better over time?"""
        return self.momentum > 0.01

    def trend(self, window=10):
        """
        Get the alignment trend over the last N readings.

        Returns a list of alignment values (oldest to newest).
        """
        recent = list(self.history)[-window:]
        return [h["alignment"] for h in recent]

    def summary(self):
        """
        Human-readable summary of the current guidance state.
        """
        arrows = {
            "create": "↑ Creating — alignment high, momentum positive. Build something.",
            "seek": "→ Seeking — alignment moderate, system is learning. Keep exploring.",
            "reflect": "← Reflecting — alignment low or dropping. Turn inward.",
            "rest": "· Resting — system needs time. Don't force it.",
        }
        return arrows.get(self.current_guidance, "? Unknown state")

    def status(self):
        """Status dict for the UI."""
        return {
            "type": "intuitive_guidance",
            "alignment": round(self.alignment, 3),
            "momentum": round(self.momentum, 4),
            "guidance": self.current_guidance,
            "total_readings": self.total_readings,
            "history_size": len(self.history),
            "summary": self.summary(),
        }


# Quick test
if __name__ == "__main__":
    igs = IntuitiveGuidanceSystem()

    print("=== Intuitive Guidance System Test ===\n")

    # Simulate improving system
    readings = [
        {"awareness": 0.3, "sense_error": 0.8, "phi_loss": 2.5},
        {"awareness": 0.4, "sense_error": 0.6, "phi_loss": 2.0},
        {"awareness": 0.5, "sense_error": 0.5, "phi_loss": 1.5},
        {"awareness": 0.6, "sense_error": 0.3, "phi_loss": 1.0},
        {"awareness": 0.7, "sense_error": 0.2, "phi_loss": 0.8, "emotional_tone": 0.3},
    ]

    for i, metrics in enumerate(readings):
        result = igs.read(metrics)
        print(f"Reading {i+1}: {result}")

    print(f"\nSummary: {igs.summary()}")
    print(f"Aligned: {igs.is_aligned()}")
    print(f"Improving: {igs.is_improving()}")
    print(f"Trend: {igs.trend()}")
    print(f"Status: {igs.status()}")
