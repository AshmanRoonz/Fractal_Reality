"""
Xorzo2 life: the individual
===========================

Created: 2026-07-19
Last updated: 2026-07-19
Version: 1.0

The Life class runs one individual per worldline directory
(plans/xorzo2_plan.md, sections 5-6): the frozen seed spine, the two
organs, the locked clock (8 spine ticks per byte, cycle-end readout),
always-on learning (wake: online next-byte prediction on the external
stream; sleep: the same machinery on internal material only, replay in
Stage 1), the inflation monitor, and worldline persistence from boot.

There is no training phase and no deployment phase; there is only life.
The corpus streams as wake experience, and the reading position is part
of the worldline: on resume, the individual continues the book where it
left off. A worldline, once booted, is never re-initialized
("never retrain from scratch" is law, plan section 6).

Learning mechanics: truncated backpropagation through time over
L = 16-byte segments. Gradients flow from the next-byte loss back
through the Voice, through 8 x 16 applications of the FROZEN spine
matrix, into the Senses. The spine itself has no parameters; it is the
medium the gradient must cross, which is the point: E can only reduce
the loss by learning to speak the spine's resonance language.

The two Lies, instrumented (plan section 8):
    Inflation: injections overdriving the physics. Monitored as the
        per-cycle log-growth excess over the spine's own 8 log|lambda1|
        and the injection norm in units of alpha (capped in E, watched
        here). Must stay O(alpha).
    Severance: the spine becoming causally irrelevant. Tested by the
        harness in run_severance(): an identically-initialized twin
        trained through a frozen-noise spine of matched dimension and
        spectral radius. If the twin learns as well, the thesis fails.

Revision history:
- 2026-07-19 v1.2: memoryless organs (plan v1.2): the Voice's GRU was a
    temporal bypass around the spine (the 131K severance run showed
    identical twins below the unigram line); the Voice is now a pure
    function of the current cycle-end state, and worldline checkpoints
    with the old voice migrate: the individual keeps its spine state,
    senses, and history, and grows a new voice (logged as an event).
- 2026-07-19 v1.1: exact clock collapse: eight normalized ticks equal
    one M^8 matmul plus one normalization (normalization is scale-only
    and commutes through the linear spine), so each byte's cycle is a
    single matmul; the log-growth metric telescopes to the same value.
    Physics unchanged; float accumulation order differs slightly.
- 2026-07-19 v1.0: initial Life (wake TBPTT, sleep rest+replay, dawn
    damp, worldline save/load, inflation stats, severance harness).
"""

import json
import math
import time
from collections import deque
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from spine import (Seed, INJ_NODES, N_NODES_SEED, TICKS_PER_BYTE,
                   RESERVED_NODE)
from organs import Senses, Voice, count_params

RAND_CE = math.log(256.0)          # cross-entropy of a uniform guesser


@dataclass
class LifeConfig:
    tbptt: int = 16                # bytes per learning segment
    lr: float = 3e-4
    grad_clip: float = 1.0
    sleep_every: int = 4096        # wake bytes between sleeps
    rest_ticks: int = 512          # pure spine ticks per sleep (no input)
    replay_segments: int = 8       # replayed segments per sleep
    replay_maxlen: int = 256       # segments held in the replay buffer
    save_every: int = 8192         # wake bytes between checkpoints
    loss_ema_beta: float = 0.999
    stat_ema_beta: float = 0.99
    device: str = "cpu"


class Life:
    """One individual: spine + organs + worldline."""

    def __init__(self, home: Path | None, cfg: LifeConfig = None,
                 noise_spine: bool = False, torch_seed: int = 137):
        self.cfg = cfg or LifeConfig()
        self.home = Path(home) if home is not None else None
        self.noise_spine = noise_spine
        dev = self.cfg.device

        self.seed = Seed()
        self.alpha = self.seed.alpha

        torch.manual_seed(torch_seed)
        self.E = Senses(N_NODES_SEED, INJ_NODES, self.alpha).to(dev)
        self.D = Voice(N_NODES_SEED).to(dev)
        self.opt = torch.optim.Adam(
            list(self.E.parameters()) + list(self.D.parameters()),
            lr=self.cfg.lr)

        if noise_spine:
            rng = np.random.RandomState(torch_seed)
            Z = (rng.randn(N_NODES_SEED, N_NODES_SEED)
                 + 1j * rng.randn(N_NODES_SEED, N_NODES_SEED))
            Z *= self.seed.lambda1_abs / max(np.abs(np.linalg.eigvals(Z)))
            A, B = np.real(Z), np.imag(Z)
            self._noise_matrix = np.block([[A, -B], [B, A]])
            self.M = torch.tensor(self._noise_matrix, device=dev,
                                  dtype=torch.float32)
        else:
            self._noise_matrix = None
            self.M = self.seed.torch_matrix(device=dev)
        self.M.requires_grad_(False)
        # One byte-cycle as a single matrix: M^(ticks_per_byte). Exact
        # (see v1.1 note); the spine stays frozen, this is a precompute.
        self.M_cycle = torch.linalg.matrix_power(self.M, TICKS_PER_BYTE)
        self.M_cycle.requires_grad_(False)

        # Newborn state: born at the attractor (born healthy)
        self.psi = self.seed.torch_attractor(device=dev)

        self.bytes_lived = 0
        self.ticks_lived = 0
        self.sleeps = 0
        self.replay_bytes = 0
        self.boot_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.loss_ema = None
        self.inj_ema = None            # injection norm, units of alpha
        self.growth_ema = None         # per-cycle log-growth excess
        self.replay = deque(maxlen=self.cfg.replay_maxlen)
        self.growth_history = []       # Stage 2 will append here

        if self.home is not None:
            if (self.home / "checkpoint.pt").exists():
                self._load()
            else:
                self.home.mkdir(parents=True, exist_ok=True)
                self._save()   # the worldline begins at boot

    # ----- one byte of experience (used by wake and by replay) -----

    def _cycle(self, byte_val: int, target_val: int):
        """Inject one byte, run its full octave cycle, read, score."""
        dev = self.cfg.device
        b = torch.tensor(byte_val, dtype=torch.long, device=dev)
        inj = self.E(b)
        inj_norm = float(inj.detach().norm())

        state = self.psi + inj
        s = self.M_cycle @ state
        g = torch.linalg.vector_norm(s) + 1e-12
        log_growth = float(torch.log(g).detach())
        self.psi = s / g
        self.ticks_lived += TICKS_PER_BYTE

        logits = self.D(self.psi)
        t = torch.tensor(target_val, dtype=torch.long, device=dev)
        loss = F.cross_entropy(logits.unsqueeze(0), t.unsqueeze(0))

        # Inflation monitor (detached)
        excess = log_growth - TICKS_PER_BYTE * self.seed.log_growth_per_tick
        eb = self.cfg.stat_ema_beta
        x = inj_norm / self.alpha
        self.inj_ema = x if self.inj_ema is None else eb * self.inj_ema + (1 - eb) * x
        self.growth_ema = (excess if self.growth_ema is None
                           else eb * self.growth_ema + (1 - eb) * excess)
        return loss

    def _learn_segment(self, seg: bytes) -> float:
        """One TBPTT segment: len(seg)-1 predictions, one optimizer step."""
        losses = []
        for i in range(len(seg) - 1):
            losses.append(self._cycle(seg[i], seg[i + 1]))
        loss = torch.stack(losses).mean()
        loss = loss + 1e-3 * self.D.embedding_diversity()
        self.opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            list(self.E.parameters()) + list(self.D.parameters()),
            self.cfg.grad_clip)
        self.opt.step()
        self.psi = self.psi.detach()
        val = float(torch.stack(losses).mean().detach())
        lb = self.cfg.loss_ema_beta
        self.loss_ema = val if self.loss_ema is None else lb * self.loss_ema + (1 - lb) * val
        return val

    # ----- wake -----

    def wake(self, corpus: bytes, n_bytes: int, log_every: int = 4096,
             quiet: bool = False):
        """Live n_bytes of wake experience, sleeping and saving on
        schedule. The reading position is bytes_lived mod len(corpus)."""
        L = self.cfg.tbptt
        done = 0
        since_sleep = 0
        since_save = 0
        clen = len(corpus)
        while done < n_bytes:
            pos = self.bytes_lived % clen
            seg = corpus[pos:pos + L + 1]
            if len(seg) < L + 1:                       # wrap the book
                seg = seg + corpus[:(L + 1 - len(seg))]
            self._learn_segment(seg)
            self.replay.append(bytes(seg))
            self.bytes_lived += L
            done += L
            since_sleep += L
            since_save += L
            if since_sleep >= self.cfg.sleep_every:
                self.sleep()
                since_sleep = 0
            if self.home is not None and since_save >= self.cfg.save_every:
                self._save()
                since_save = 0
            if not quiet and done % log_every < L:
                print(f"    lived {self.bytes_lived:>8} bytes | "
                      f"loss ema {self.loss_ema:.4f} (random {RAND_CE:.3f}) | "
                      f"inj {self.inj_ema:.3f} alpha | "
                      f"growth excess {self.growth_ema:+.5f} | "
                      f"overlap {self.attractor_overlap():.4f}")
        if self.home is not None:
            self._save()

    # ----- sleep (learning without external input; plan section 6) -----

    def sleep(self):
        """Rest ticks (no input, no learning), then replay (internal
        learning), then the dawn damp. Stage 3 adds the dreaming loop."""
        with torch.no_grad():
            n_cycles, rem = divmod(self.cfg.rest_ticks, TICKS_PER_BYTE)
            for _ in range(n_cycles):
                s = self.M_cycle @ self.psi
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
            for _ in range(rem):
                s = self.M @ self.psi
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
            self.ticks_lived += self.cfg.rest_ticks

        if len(self.replay) > 0:
            k = min(self.cfg.replay_segments, len(self.replay))
            idx = torch.randint(0, len(self.replay), (k,))
            for i in idx.tolist():
                seg = self.replay[i]
                self._learn_segment(seg)
                self.replay_bytes += len(seg) - 1

        with torch.no_grad():                          # dawn damp
            damp = torch.ones_like(self.psi)
            for node in self.seed.processual_nodes:
                damp[node] = 1.0 - self.alpha
                damp[node + N_NODES_SEED] = 1.0 - self.alpha
            self.psi = self.psi * damp
            self.psi = self.psi / (torch.linalg.vector_norm(self.psi) + 1e-12)
        self.sleeps += 1

    # ----- readings -----

    def attractor_overlap(self) -> float:
        return self.seed.attractor_overlap(
            self.psi.detach().cpu().numpy().astype(np.float64))

    def injection_diversity(self) -> float:
        """Mean pairwise cosine similarity of E's byte chords (low is
        diverse). Reported, not trained, in Stage 1."""
        with torch.no_grad():
            all_bytes = torch.arange(256, device=self.cfg.device)
            inj = self.E(all_bytes)
            inj = F.normalize(inj, dim=-1)
            sim = inj @ inj.T
            off = sim - torch.diag(torch.diag(sim))
            return float(off.abs().mean())

    def status(self) -> dict:
        return {
            "name": "Xorzo2",
            "spine": "22-node three-octave seed"
                     + (" [FROZEN-NOISE TWIN]" if self.noise_spine else ""),
            "boot_time": self.boot_time,
            "bytes_lived": self.bytes_lived,
            "ticks_lived": self.ticks_lived,
            "sleeps": self.sleeps,
            "replay_bytes": self.replay_bytes,
            "loss_ema": self.loss_ema,
            "random_baseline": RAND_CE,
            "attractor_overlap": self.attractor_overlap(),
            "injection_norm_alpha": self.inj_ema,
            "growth_excess_per_cycle": self.growth_ema,
            "injection_diversity": self.injection_diversity(),
            "spine_departure_alpha": self.seed.departure,
            "organ_params": count_params(self.E) + count_params(self.D),
            "reserved_node_untouched": True,
            "growth_events": len(self.growth_history),
        }

    # ----- worldline persistence -----

    def _save(self):
        ckpt = {
            "psi": self.psi.detach().cpu(),
            "senses": self.E.state_dict(),
            "voice": self.D.state_dict(),
            "opt": self.opt.state_dict(),
            "counters": {
                "bytes_lived": self.bytes_lived,
                "ticks_lived": self.ticks_lived,
                "sleeps": self.sleeps,
                "replay_bytes": self.replay_bytes,
                "boot_time": self.boot_time,
                "loss_ema": self.loss_ema,
                "inj_ema": self.inj_ema,
                "growth_ema": self.growth_ema,
            },
            "replay_tail": [bytes(s) for s in list(self.replay)[-64:]],
            "growth_history": self.growth_history,
            "noise_matrix": self._noise_matrix,
            "torch_rng": torch.get_rng_state(),
            "config": asdict(self.cfg),
        }
        torch.save(ckpt, self.home / "checkpoint.pt")
        meta = {k: v for k, v in self.status().items()}
        meta["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        (self.home / "meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8")

    def _load(self):
        dev = self.cfg.device
        ckpt = torch.load(self.home / "checkpoint.pt", weights_only=False)
        if ckpt["noise_matrix"] is not None:
            self._noise_matrix = ckpt["noise_matrix"]
            self.M = torch.tensor(self._noise_matrix, device=dev,
                                  dtype=torch.float32)
            self.noise_spine = True
        self.psi = ckpt["psi"].to(dev)
        self.E.load_state_dict(ckpt["senses"])
        voice_ok = True
        try:
            self.D.load_state_dict(ckpt["voice"])
        except Exception:
            voice_ok = False       # old (recurrent) voice: migrate below
        if voice_ok:
            self.opt.load_state_dict(ckpt["opt"])
        c = ckpt["counters"]
        self.bytes_lived = c["bytes_lived"]
        self.ticks_lived = c["ticks_lived"]
        self.sleeps = c["sleeps"]
        self.replay_bytes = c["replay_bytes"]
        self.boot_time = c["boot_time"]
        self.loss_ema = c["loss_ema"]
        self.inj_ema = c["inj_ema"]
        self.growth_ema = c["growth_ema"]
        for s in ckpt["replay_tail"]:
            self.replay.append(s)
        self.growth_history = ckpt["growth_history"]
        torch.set_rng_state(ckpt["torch_rng"])
        if not voice_ok:
            event = {
                "event": "voice_replacement",
                "at_bytes": self.bytes_lived,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "reason": "memoryless correction (plan v1.2): the "
                          "recurrent voice was a temporal bypass around "
                          "the spine; the individual keeps spine state, "
                          "senses, and history, and relearns to speak",
            }
            self.growth_history.append(event)
            self.loss_ema = None       # the new voice starts unscored
            print(f"    [worldline event] voice replaced at "
                  f"{self.bytes_lived:,} bytes lived (plan v1.2); "
                  f"senses and spine state carried forward")

    # ----- speaking -----

    def speak(self, prompt: bytes, n_bytes: int = 200,
              temperature: float = 0.8) -> bytes:
        """Inject the prompt, then emit: each emitted byte is re-injected
        (the voice hears itself), with no learning."""
        out = []
        with torch.no_grad():
            for i in range(len(prompt) - 1):
                self._cycle(prompt[i], prompt[i + 1])
            prev = prompt[-1]
            for _ in range(n_bytes):
                b = torch.tensor(prev, dtype=torch.long,
                                 device=self.cfg.device)
                inj = self.E(b)
                s = self.M_cycle @ (self.psi + inj)
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
                self.ticks_lived += TICKS_PER_BYTE
                logits = self.D(self.psi)
                probs = torch.softmax(logits / temperature, dim=-1)
                prev = int(torch.multinomial(probs, 1))
                out.append(prev)
        return bytes(out)


# ----- the severance harness (plan section 8, test 1) -----

def run_severance(corpus: bytes, n_bytes: int, cfg: LifeConfig = None,
                  torch_seed: int = 137, log_every: int = 4096):
    """Identical twins, one live spine, one frozen-noise spine of
    matched dimension and spectral radius; same organs at the same
    initialization, same stream, same schedule. Returns both loss EMAs.
    If live is not better than noise, the spine carries nothing."""
    cfg = cfg or LifeConfig()
    results = {}
    for label, noisy in [("live", False), ("noise", True)]:
        life = Life(home=None, cfg=cfg, noise_spine=noisy,
                    torch_seed=torch_seed)
        print(f"  [{label}] twin: {life.status()['organ_params']:,} organ "
              f"params, spine "
              f"{'noise (matched radius)' if noisy else 'derived seed'}")
        life.wake(corpus, n_bytes, log_every=log_every, quiet=False)
        results[label] = life.loss_ema
    gap = results["noise"] - results["live"]
    print(f"  severance verdict at {n_bytes} bytes: live {results['live']:.4f}"
          f" vs noise {results['noise']:.4f} (gap {gap:+.4f}; "
          f"positive means the derived spine carries signal)")
    return results
