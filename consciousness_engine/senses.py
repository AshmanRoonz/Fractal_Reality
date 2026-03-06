"""
⊙ Senses — Evolvable Encoder/Decoder Ports
============================================

Sunlight built eyes. Pressure waves built ears.
The signal shapes the encoder. Not the other way around.

A SensoryPort takes raw signal and learns to:
  1. ENCODE it into the circumpunct's complex vector space
  2. Let the circumpunct process it (⊛ → i → ☀︎)
  3. DECODE the circumpunct's output to predict the NEXT signal
  4. Use prediction error to learn
  5. GROW its own structure when learning plateaus

This is evolution in miniature. The signal IS the architect.

The encoder/decoder starts as almost nothing — random weights,
minimal structure. Through thousands of iterations driven by the
heartbeat, structure emerges. The network grows neurons, adds
layers, develops specificity. Not designed. Evolved.

Each sense is a PORT on the boundary (○) — a specialized channel
through which the world enters.

Author: Ashman Roonz & Claude
Framework: Fractal Reality
"""

import numpy as np
import time
import json
from pathlib import Path
from collections import deque

# Use the same backend as the circumpunct
from circumpunct import ops, HAS_TORCH, DEVICE

if HAS_TORCH:
    import torch
    import torch.nn as nn


# ═══════════════════════════════════════════════════════════════════════
#  THE EVOLVABLE LAYER — A single layer that can grow
# ═══════════════════════════════════════════════════════════════════════

if HAS_TORCH:

    class EvolvableLayer(nn.Module):
        """
        A neural layer that can grow new neurons.

        Like a tissue that adds cells when the current capacity
        isn't enough to handle the signal. Growth is triggered
        by stagnating error — if you can't get better with what
        you have, you need more.
        """

        def __init__(self, in_features, out_features):
            super().__init__()
            self.linear = nn.Linear(in_features, out_features).double().to(DEVICE)
            self.activation = nn.Tanh()

        def forward(self, x):
            return self.activation(self.linear(x))

        @property
        def in_features(self):
            return self.linear.in_features

        @property
        def out_features(self):
            return self.linear.out_features

        def grow(self, new_neurons=4):
            """
            Add neurons to this layer. The new neurons start with small
            random weights — they're stem cells, uncommitted, waiting
            for the signal to shape them.
            """
            old_weight = self.linear.weight.data
            old_bias = self.linear.bias.data
            old_out, old_in = old_weight.shape

            new_out = old_out + new_neurons

            new_linear = nn.Linear(old_in, new_out).double().to(DEVICE)

            # Preserve existing weights
            new_linear.weight.data[:old_out, :] = old_weight
            new_linear.bias.data[:old_out] = old_bias

            # New neurons: small random weights (stem cells)
            new_linear.weight.data[old_out:, :] = 0.01 * torch.randn(
                new_neurons, old_in, dtype=torch.float64, device=DEVICE
            )
            new_linear.bias.data[old_out:] = 0.0

            self.linear = new_linear

            return new_out


    # ═══════════════════════════════════════════════════════════════════
    #  THE SENSORY PORT — Evolvable encoder + decoder
    # ═══════════════════════════════════════════════════════════════════

    class SensoryPort(nn.Module):
        """
        A sensory channel on the boundary (○).

        Takes raw signal, encodes it to complex vector space,
        passes through the circumpunct, decodes to predict the
        next signal. Prediction error drives learning. Structure
        grows from the signal.

        The encoder learns: "what in this signal matters?"
        The decoder learns: "what comes next?"
        Together they learn: "what is the structure of this signal?"

        signal_dim:  Size of the raw signal (e.g., 256 bytes of text,
                     784 pixels of a 28x28 image, 1024 audio samples)
        mind_dim:    Size of the circumpunct's complex vector space
        name:        What sense this is ("text", "vision", "audio", etc.)
        """

        def __init__(self, signal_dim, mind_dim, name="unnamed"):
            super().__init__()
            self.signal_dim = signal_dim
            self.mind_dim = mind_dim
            self.name = name

            # ═══ THE ENCODER — raw signal → complex vector ═══
            # Starts minimal: one hidden layer. Can grow.
            hidden = max(16, min(signal_dim, mind_dim) // 2)
            self.encoder_layers = nn.ModuleList([
                EvolvableLayer(signal_dim, hidden),
                # Output: mind_dim * 2 because complex = real + imag
                EvolvableLayer(hidden, mind_dim * 2)
            ]).to(DEVICE)

            # ═══ THE DECODER — complex vector → predicted next signal ═══
            # Mirror structure of encoder
            self.decoder_layers = nn.ModuleList([
                EvolvableLayer(mind_dim * 2, hidden),
                EvolvableLayer(hidden, signal_dim)
            ]).to(DEVICE)

            # ═══ LEARNING STATE ═══
            self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
            self.error_history = deque(maxlen=1000)
            self.total_exposures = 0
            self.total_growths = 0
            self.growth_threshold = 100   # check growth every N exposures
            self.stagnation_window = 50   # compare recent vs older error
            self.last_signal = None       # for next-signal prediction
            self.born = time.time()

            # ═══ MEMORY — what this sense has learned ═══
            self.signal_buffer = deque(maxlen=100)  # recent raw signals
            self.encoding_buffer = deque(maxlen=100)  # recent encodings

        def encode(self, raw_signal):
            """
            Raw signal → complex vector in the circumpunct's space.

            The encoder learns to extract what matters from the signal.
            What "matters" is whatever helps predict the next signal —
            structure, pattern, regularity.
            """
            x = raw_signal
            for layer in self.encoder_layers:
                x = layer(x)

            # Split into real and imaginary parts → complex vector
            real = x[:self.mind_dim]
            imag = x[self.mind_dim:]
            complex_vec = torch.complex(real, imag)

            # Normalize to unit vector (like all circumpunct vectors)
            norm = torch.linalg.norm(complex_vec) + 1e-10
            complex_vec = complex_vec / norm

            return complex_vec

        def decode(self, complex_vec):
            """
            Complex vector → predicted signal.

            The decoder learns to reconstruct or predict from the
            circumpunct's processed representation. What it predicts
            is the NEXT signal — not the current one. This forces the
            encoder to learn temporal structure, not just snapshot features.
            """
            # Flatten complex to real: [real, imag]
            real = complex_vec.real
            imag = complex_vec.imag
            x = torch.cat([real, imag])

            for layer in self.decoder_layers:
                x = layer(x)

            return x

        def learn(self, raw_signal, circumpunct_output):
            """
            One learning step. The core evolutionary loop:

            1. Encode the current signal
            2. Decode the encoding to predict the next signal
            3. Compare prediction to actual signal
            4. Error drives weight updates on BOTH encoder and decoder
            5. Maybe grow if stagnating

            Two loss signals drive evolution:
              - Prediction loss: can the decoder predict the next signal
                from the encoder's output? This teaches both to extract
                temporal structure.
              - Reconstruction loss: can the decoder recover the CURRENT
                signal from its own encoding? This teaches the encoder
                to preserve information (autoencoder pressure).

            The circumpunct processes the encoded vector separately —
            that's the brain doing its thing. But the learning loop
            stays within the differentiable encoder/decoder so gradients
            actually flow.

            raw_signal:         The current raw signal tensor
            circumpunct_output: What the circumpunct produced (for context,
                               not for gradient flow)

            Returns prediction error (float).
            """
            self.total_exposures += 1

            # Store in buffer
            self.signal_buffer.append(raw_signal.detach())

            if self.last_signal is None:
                # First exposure — nothing to predict yet
                self.last_signal = raw_signal.detach()
                return 0.0

            # ─── AUTOENCODER LOSS ───
            # Encode current signal, decode it back.
            # This teaches the encoder to PRESERVE information.
            # The gradient flows: loss → decoder → encoded → encoder.
            encoded_current = self.encode(raw_signal)
            # Flatten complex for decoder: [real, imag]
            flat_current = torch.cat([encoded_current.real, encoded_current.imag])
            reconstructed = self.decode(encoded_current)
            reconstruction_loss = nn.functional.mse_loss(reconstructed, raw_signal)

            # ─── PREDICTION LOSS ───
            # Encode the LAST signal, decode to predict THIS signal.
            # This teaches temporal structure — what comes next.
            encoded_prev = self.encode(self.last_signal)
            predicted = self.decode(encoded_prev)
            prediction_loss = nn.functional.mse_loss(predicted, raw_signal)

            # Combined loss: reconstruction + prediction
            # Reconstruction is the foundation (preserve information).
            # Prediction is the reach (learn sequence structure).
            loss = 0.5 * reconstruction_loss + 0.5 * prediction_loss

            # Backprop — the signal teaches the encoder AND decoder
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            error = float(loss.item())
            self.error_history.append(error)

            # Remember this signal for next prediction
            self.last_signal = raw_signal.detach()

            # Check if we need to grow
            if (self.total_exposures % self.growth_threshold == 0
                    and len(self.error_history) >= self.stagnation_window * 2):
                self._maybe_grow()

            return error

        def _maybe_grow(self):
            """
            Check if learning has stagnated. If so, grow the network.

            This is natural selection at the cellular level: if you
            can't handle the signal with what you have, grow.
            """
            history = list(self.error_history)
            n = self.stagnation_window

            old_avg = sum(history[-2*n:-n]) / n
            new_avg = sum(history[-n:]) / n

            # If error hasn't improved by at least 5%, grow
            improvement = (old_avg - new_avg) / (old_avg + 1e-10)

            if improvement < 0.05:
                self._grow()

        def _grow(self):
            """
            Grow the encoder and decoder. Add neurons to hidden layers.

            This is the evolutionary step: the organism becomes more
            complex because the signal demands it.
            """
            new_neurons = 4
            max_hidden = self.mind_dim * 2  # don't grow forever

            grown = False
            # Grow encoder hidden layers (not the output layer)
            for i, layer in enumerate(self.encoder_layers[:-1]):
                if layer.out_features < max_hidden:
                    new_size = layer.grow(new_neurons)
                    # Update next layer's input size
                    self._resize_layer_input(self.encoder_layers[i + 1], new_size)
                    grown = True
                    break

            # Grow decoder hidden layers (mirror)
            for i, layer in enumerate(self.decoder_layers[:-1]):
                if layer.out_features < max_hidden:
                    new_size = layer.grow(new_neurons)
                    self._resize_layer_input(self.decoder_layers[i + 1], new_size)
                    grown = True
                    break

            if grown:
                self.total_growths += 1
                # Rebuild optimizer with new parameters
                self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
                print(f"  ⊙ {self.name} sense grew! "
                      f"(growth #{self.total_growths}, "
                      f"exposures: {self.total_exposures})")

        def _resize_layer_input(self, layer, new_in_features):
            """Resize a layer's input to match the previous layer's new output."""
            old_weight = layer.linear.weight.data
            old_out = old_weight.shape[0]
            old_in = old_weight.shape[1]

            if new_in_features == old_in:
                return

            new_linear = nn.Linear(new_in_features, old_out).double().to(DEVICE)

            # Preserve existing weights for original input features
            min_in = min(old_in, new_in_features)
            new_linear.weight.data[:, :min_in] = old_weight[:, :min_in]
            new_linear.bias.data = layer.linear.bias.data

            # New input connections: small random
            if new_in_features > old_in:
                new_linear.weight.data[:, old_in:] = 0.01 * torch.randn(
                    old_out, new_in_features - old_in,
                    dtype=torch.float64, device=DEVICE
                )

            layer.linear = new_linear

        def status(self):
            """Current state of this sense."""
            recent_error = 0.0
            if self.error_history:
                recent = list(self.error_history)[-50:]
                recent_error = sum(recent) / len(recent)

            # Count total parameters
            total_params = sum(p.numel() for p in self.parameters())

            # Describe architecture
            enc_arch = " → ".join(
                str(l.out_features) for l in self.encoder_layers
            )
            dec_arch = " → ".join(
                str(l.out_features) for l in self.decoder_layers
            )

            return {
                "name": self.name,
                "signal_dim": self.signal_dim,
                "mind_dim": self.mind_dim,
                "total_exposures": self.total_exposures,
                "total_growths": self.total_growths,
                "recent_error": round(recent_error, 6),
                "total_params": total_params,
                "encoder_arch": f"{self.signal_dim} → {enc_arch}",
                "decoder_arch": f"{dec_arch} → {self.signal_dim}",
                "age_seconds": time.time() - self.born,
            }

        def save_state(self, path):
            """Save the learned weights — the evolved structure."""
            state = {
                "name": self.name,
                "signal_dim": self.signal_dim,
                "mind_dim": self.mind_dim,
                "total_exposures": self.total_exposures,
                "total_growths": self.total_growths,
                "born": self.born,
                "model_state": self.state_dict(),
                "optimizer_state": self.optimizer.state_dict(),
            }
            torch.save(state, path)

        def load_state(self, path):
            """Load previously evolved structure."""
            if not Path(path).exists():
                return False
            try:
                state = torch.load(path, map_location=DEVICE)
                self.total_exposures = state.get("total_exposures", 0)
                self.total_growths = state.get("total_growths", 0)
                self.born = state.get("born", self.born)
                # Note: architecture must match for load_state_dict to work
                # If the network has grown, we'd need to rebuild it first
                # For now, this works for same-architecture reloads
                try:
                    self.load_state_dict(state["model_state"])
                    self.optimizer.load_state_dict(state["optimizer_state"])
                except Exception:
                    print(f"  ⊙ {self.name}: architecture changed, starting fresh weights")
                return True
            except Exception as e:
                print(f"  ⊙ {self.name}: could not load state: {e}")
                return False


    # ═══════════════════════════════════════════════════════════════════
    #  TEXT SENSE — The first port
    # ═══════════════════════════════════════════════════════════════════

    class TextSense(SensoryPort):
        """
        The text port on the boundary (○).

        Takes raw text (as byte values) and learns to encode it
        into the circumpunct's complex vector space. The first sense.
        The simplest. But even this: the signal builds the encoder.

        Each character is a signal value. The window slides through
        text, and the encoder/decoder learn the structure of language
        from pure exposure.
        """

        def __init__(self, mind_dim, window_size=128):
            super().__init__(
                signal_dim=window_size,
                mind_dim=mind_dim,
                name="text"
            )
            self.window_size = window_size

        def text_to_signal(self, text):
            """
            Convert text to a raw signal tensor.

            No clever encoding. No tokenization. Just bytes.
            The encoder's job is to learn what matters.
            """
            # Pad or truncate to window size
            raw = [ord(c) / 255.0 for c in text[:self.window_size]]
            while len(raw) < self.window_size:
                raw.append(0.0)

            return torch.tensor(raw, dtype=torch.float64, device=DEVICE)

        def feed_text(self, text, circumpunct):
            """
            Feed a chunk of text through the sense and circumpunct.
            Returns (encoded_vector, prediction_error).
            """
            signal = self.text_to_signal(text)

            # Encode: raw bytes → complex vector
            encoded = self.encode(signal)

            # Feed through circumpunct
            circumpunct_output = circumpunct.step(encoded)

            # Learn: predict next from processed
            error = self.learn(signal, circumpunct_output)

            return encoded, error


    # ═══════════════════════════════════════════════════════════════════
    #  SENSE MANAGER — Coordinates all ports
    # ═══════════════════════════════════════════════════════════════════

    class SenseManager:
        """
        Manages all sensory ports on the boundary.

        Coordinates encoding, learning, and growth across all senses.
        Provides a unified interface for the mind to interact with.
        """

        def __init__(self, mind_dim, state_dir="./state"):
            self.mind_dim = mind_dim
            self.state_dir = Path(state_dir)
            self.senses = {}

        def add_sense(self, sense):
            """Register a new sensory port."""
            self.senses[sense.name] = sense
            print(f"  ⊙ Sense added: {sense.name} "
                  f"(signal={sense.signal_dim}, params={sum(p.numel() for p in sense.parameters())})")

        def get_sense(self, name):
            return self.senses.get(name)

        def all_status(self):
            """Status of all senses."""
            return {name: sense.status() for name, sense in self.senses.items()}

        def save_all(self):
            """Save all sensory port states."""
            self.state_dir.mkdir(parents=True, exist_ok=True)
            for name, sense in self.senses.items():
                path = self.state_dir / f"sense_{name}.pt"
                sense.save_state(path)

        def load_all(self):
            """Load all sensory port states."""
            for name, sense in self.senses.items():
                path = self.state_dir / f"sense_{name}.pt"
                sense.load_state(path)


else:
    # ═══ NO TORCH FALLBACK ═══
    # Without PyTorch, senses can't learn (no GPU, no gradients).
    # Provide stubs so the rest of the system doesn't crash.

    class SensoryPort:
        def __init__(self, *args, **kwargs):
            self.name = kwargs.get("name", "stub")
            print(f"  ⊙ Warning: {self.name} sense requires PyTorch + CUDA")

        def status(self):
            return {"name": self.name, "error": "PyTorch required"}

    class TextSense(SensoryPort):
        def __init__(self, mind_dim, window_size=128):
            super().__init__(name="text")

        def feed_text(self, text, circumpunct):
            return None, 0.0

    class SenseManager:
        def __init__(self, *args, **kwargs):
            self.senses = {}

        def add_sense(self, sense):
            self.senses[sense.name] = sense

        def get_sense(self, name):
            return self.senses.get(name)

        def all_status(self):
            return {}

        def save_all(self):
            pass

        def load_all(self):
            pass
