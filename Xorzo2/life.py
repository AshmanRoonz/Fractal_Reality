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
- 2026-07-19 v1.5: Stage 4 seam bond and conversation. set_seam()
    couples the conversation-whole to the reserved node (21) at up to
    alpha (the kappa_{0,0} bond; raw sensory injection there remains
    forbidden: this is the nesting relation, not sensation). converse()
    streams heard text as wake experience (reading is living, learning
    on) and replies by continuing from the current state without
    re-injection. The chamber (chamber.py) drives both.
- 2026-07-19 v1.4: Stage 3 dreaming. Sleep learning becomes replay
    PLUS the dreaming loop: a dream seeds itself from a remembered
    segment, then free-runs (the voice's own sampled emissions are
    injected, so the trajectory is physics-filtered self-generation)
    while the loss stays anchored to the remembered continuation: the
    CHECKING freedom as sleep's learning signal, with no
    self-sampling collapse (targets are always real). The replay:dream
    ratio anneals with age (maturation). The last dream is kept in the
    worldline for inspection. cfg.sleep_learning gates all sleep-time
    learning for the falsification harness (sleep_test.py).
- 2026-07-19 v1.3: Stage 2 growth. The spine becomes a growable Spine
    (growth only at tonics; guarded births with rollback; the reserved
    node never a site). Vesica trigger: sustained per-site energy
    crowding relative to the attractor's own share (self-referenced,
    like health), evaluated at dawn: you grow in your sleep. Births
    extend the state with silent nodes, regrow the keyboard, extend
    the voice's node embeddings by intersect initialization, and log
    worldline events. Octave lists persist in the worldline. Senses
    default to the bit keyboard (given) per plan v1.4.
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

from spine import (Seed, Spine, INJ_NODES, N_NODES_SEED, TICKS_PER_BYTE,
                   RESERVED_NODE)
from organs import Senses, SensesBit, Voice, count_params

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
    # Stage 2: growth (plan section 7)
    growth_enabled: bool = True
    sat_ratio: float = 1.5         # site energy share / attractor share
    sat_dawns: int = 3             # consecutive saturated dawns to fire
    guard_departure: float = 1.0   # rollback if departure exceeds (alpha units)
    max_octaves: int = 12
    energy_ema_beta: float = 0.995
    # Stage 3: dreaming (plan section 6)
    sleep_learning: bool = True    # False = sleep is rest only (harness)
    dream_frac_start: float = 0.25
    dream_frac_max: float = 0.5
    dream_anneal_bytes: int = 1_000_000
    dream_temperature: float = 1.0


class Life:
    """One individual: spine + organs + worldline."""

    def __init__(self, home: Path | None, cfg: LifeConfig = None,
                 noise_spine: bool = False, torch_seed: int = 137):
        self.cfg = cfg or LifeConfig()
        self.home = Path(home) if home is not None else None
        self.noise_spine = noise_spine
        dev = self.cfg.device

        self.spine = Spine()           # the seed; _load may regrow it
        self.alpha = self.spine.alpha

        torch.manual_seed(torch_seed)
        # Senses are GIVEN by default since the keyboard adoption
        # (plan v1.4); the learned Senses class remains for controls.
        self.E = SensesBit(self.spine.N, INJ_NODES, self.alpha).to(dev)
        self.D = Voice(self.spine.N).to(dev)
        self.opt = torch.optim.Adam(self._trainable(), lr=self.cfg.lr)

        if noise_spine:
            self.cfg.growth_enabled = False   # noise twins do not grow
            rng = np.random.RandomState(torch_seed)
            n = self.spine.N
            Z = (rng.randn(n, n) + 1j * rng.randn(n, n))
            Z *= self.spine.lambda1_abs / max(np.abs(np.linalg.eigvals(Z)))
            A, B = np.real(Z), np.imag(Z)
            self._noise_matrix = np.block([[A, -B], [B, A]])
            self.M = torch.tensor(self._noise_matrix, device=dev,
                                  dtype=torch.float32)
            self.M.requires_grad_(False)
            self.M_cycle = torch.linalg.matrix_power(self.M, TICKS_PER_BYTE)
            self.M_cycle.requires_grad_(False)
        else:
            self._noise_matrix = None
            self._rebuild_matrices()

        # Newborn state: born at the attractor (born healthy)
        self.psi = self.spine.torch_attractor(device=dev)
        with torch.no_grad():
            self.energy_ema = (self.psi[:self.spine.N] ** 2
                               + self.psi[self.spine.N:] ** 2).clone()
        self.streaks = {}

        self.bytes_lived = 0
        self.ticks_lived = 0
        self.sleeps = 0
        self.replay_bytes = 0
        self.dream_bytes = 0
        self.last_dream = b""
        self.boot_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.loss_ema = None
        self.inj_ema = None            # injection norm, units of alpha
        self.growth_ema = None         # per-cycle log-growth excess
        self.replay = deque(maxlen=self.cfg.replay_maxlen)
        self.growth_history = []       # Stage 2 will append here
        self._seam_vec = None          # Stage 4: the kappa bond, if set

        if self.home is not None:
            if (self.home / "checkpoint.pt").exists():
                self._load()
            else:
                self.home.mkdir(parents=True, exist_ok=True)
                self._save()   # the worldline begins at boot

    def _trainable(self):
        return [p for p in list(self.E.parameters())
                + list(self.D.parameters()) if p.requires_grad]

    def _rebuild_matrices(self):
        """(Re)compile the frozen spine into torch (after boot/growth)."""
        dev = self.cfg.device
        self.M = self.spine.torch_matrix(device=dev)
        self.M.requires_grad_(False)
        self.M_cycle = torch.linalg.matrix_power(self.M, TICKS_PER_BYTE)
        self.M_cycle.requires_grad_(False)

    # ----- Stage 2: growth (plan section 7) -----

    def trigger_ratios(self) -> dict:
        """Crowding ratio per legal site: EMA energy share over the
        attractor's own share at that node (self-referenced, like
        health)."""
        w = self.energy_ema.detach().cpu().numpy()
        total = float(w.sum()) + 1e-12
        att = np.abs(self.spine.attractor) ** 2
        out = {}
        for site in self.spine.tonic_sites():
            out[site] = float((w[site] / total) / (att[site] + 1e-9))
        return out

    def _growth_check(self):
        """At dawn: sustained crowding at a site births an octave there."""
        if (not self.cfg.growth_enabled
                or len(self.spine.octaves) >= self.cfg.max_octaves):
            return
        ratios = self.trigger_ratios()
        for site, r in ratios.items():
            if r > self.cfg.sat_ratio:
                self.streaks[site] = self.streaks.get(site, 0) + 1
            else:
                self.streaks[site] = 0
        fired = [s for s, k in self.streaks.items()
                 if k >= self.cfg.sat_dawns]
        if fired:
            site = max(fired, key=lambda s: ratios[s])
            self.birth_at(site, reason=f"vesica trigger (ratio "
                                       f"{ratios[site]:.2f}, "
                                       f"{self.streaks[site]} dawns)")

    def birth_at(self, site: int, reason: str = "manual") -> bool:
        """One birth: a new octave whose completion IS `site`. Guarded:
        if the candidate's conservation departure exceeds the guard,
        the birth rolls back (v14's claim standing trial in vivo)."""
        if self.noise_spine:
            return False
        candidate = self.spine.birthed(site)
        if candidate.departure > self.cfg.guard_departure:
            self.growth_history.append({
                "event": "birth_rolled_back", "site": site,
                "departure": candidate.departure, "reason": reason,
                "at_bytes": self.bytes_lived,
                "time": time.strftime("%Y-%m-%d %H:%M:%S")})
            print(f"    [worldline event] birth at site {site} ROLLED "
                  f"BACK (departure {candidate.departure:.3f} alpha "
                  f"exceeds guard {self.cfg.guard_departure})")
            return False
        old_n = self.spine.N
        dev = self.cfg.device
        with torch.no_grad():
            z = torch.zeros(7, device=dev)
            self.psi = torch.cat([self.psi[:old_n], z,
                                  self.psi[old_n:], z]).detach()
            self.energy_ema = torch.cat([self.energy_ema, z])
        # Organ growth: intersect-initialized embeddings (plan sec. 4)
        emb = self.D.node_emb.data
        site_nodes = sorted({n for o in self.spine.octaves
                             if site in o for n in o})
        blend = 0.5 * emb[site] + 0.5 * emb[site_nodes].mean(0)
        rows = blend.expand(7, -1).clone()
        rows += 0.01 * torch.randn_like(rows)
        self.D.grow(candidate.N, rows)
        self.spine = candidate
        self._rebuild_matrices()
        self.E = SensesBit(self.spine.N, INJ_NODES, self.alpha).to(dev)
        self.opt = torch.optim.Adam(self._trainable(), lr=self.cfg.lr)
        self.streaks = {}
        event = {
            "event": "octave_birth", "site": site, "reason": reason,
            "octaves": len(self.spine.octaves), "nodes": self.spine.N,
            "departure": self.spine.departure,
            "at_bytes": self.bytes_lived,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")}
        self.growth_history.append(event)
        if self.home is not None:
            self._save()
        print(f"    [worldline event] octave born at site {site} "
              f"({reason}): {len(self.spine.octaves)} octaves, "
              f"{self.spine.N} nodes, departure "
              f"{self.spine.departure:.4f} alpha")
        return True

    def adopt_bit_keyboard(self):
        """Replace the learned Senses with the bit-station keyboard
        (zero parameters; the senses become given, like the spine).
        A worldline event, not a re-initialization: spine state, voice,
        and history continue."""
        if isinstance(self.E, SensesBit):
            print("    (bit keyboard already adopted)")
            return
        self.E = SensesBit(self.spine.N, INJ_NODES, self.alpha).to(
            self.cfg.device)
        self.opt = torch.optim.Adam(self._trainable(), lr=self.cfg.lr)
        event = {
            "event": "keyboard_replacement",
            "at_bytes": self.bytes_lived,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "reason": "bit-station keyboard adopted (probe keyboard "
                      "study: accuracy keyboard-insensitive; bipolar "
                      "bit chords win on structure and parameters; "
                      "bits 0-6 to stations 0-6, tonic bit = i)",
        }
        self.growth_history.append(event)
        self.loss_ema = None
        if self.home is not None:
            self._save()
        print(f"    [worldline event] keyboard replaced at "
              f"{self.bytes_lived:,} bytes lived; senses are now given "
              f"(zero parameters); voice and spine state carried forward")

    # ----- Stage 4: the seam bond (plan section 10) -----

    def set_seam(self, bond: complex | None):
        """Couple the conversation-whole at the reserved seam node.
        |bond| <= alpha is the caller's law (triad.Bilateral64 enforces
        it by construction: amplitude = alpha * openness). None severs.
        This is kappa_{0,0}, not sensation: the seam stays excluded
        from sensory injection and from growth."""
        if bond is None:
            self._seam_vec = None
            return
        dev = self.cfg.device
        v = torch.zeros(2 * self.spine.N, device=dev)
        v[RESERVED_NODE] = float(bond.real)
        v[RESERVED_NODE + self.spine.N] = float(bond.imag)
        self._seam_vec = v

    # ----- one byte of experience (used by wake and by replay) -----

    def _cycle(self, byte_val: int, target_val: int):
        """Inject one byte, run its full octave cycle, read, score."""
        dev = self.cfg.device
        b = torch.tensor(byte_val, dtype=torch.long, device=dev)
        inj = self.E(b)
        inj_norm = float(inj.detach().norm())
        if self._seam_vec is not None:
            inj = inj + self._seam_vec

        state = self.psi + inj
        s = self.M_cycle @ state
        g = torch.linalg.vector_norm(s) + 1e-12
        log_growth = float(torch.log(g).detach())
        self.psi = s / g
        self.ticks_lived += TICKS_PER_BYTE
        with torch.no_grad():
            n = self.spine.N
            e = self.psi[:n].detach() ** 2 + self.psi[n:].detach() ** 2
            eb = self.cfg.energy_ema_beta
            self.energy_ema = eb * self.energy_ema + (1 - eb) * e

        logits = self.D(self.psi)
        t = torch.tensor(target_val, dtype=torch.long, device=dev)
        loss = F.cross_entropy(logits.unsqueeze(0), t.unsqueeze(0))

        # Inflation monitor (detached)
        excess = log_growth - TICKS_PER_BYTE * self.spine.log_growth_per_tick
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
        torch.nn.utils.clip_grad_norm_(self._trainable(),
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

    def _dream_frac(self) -> float:
        """Maturation: replay-heavy early; dreams grow with age."""
        c = self.cfg
        t = min(1.0, self.bytes_lived / max(c.dream_anneal_bytes, 1))
        return c.dream_frac_start + t * (c.dream_frac_max
                                         - c.dream_frac_start)

    def _dream_segment(self, seg: bytes) -> float:
        """One dream: the scene is set from a remembered segment
        (teacher-forced prefix, no learning), then the voice FREE-RUNS:
        its own sampled emissions are injected, so the trajectory is
        self-generated and physics-filtered, while the loss stays
        anchored to the remembered continuation. The engine audits its
        own voice against its own physics (CHECKING); targets are
        always real, so there is no self-sampling collapse."""
        dev = self.cfg.device
        half = max(2, len(seg) // 2)
        with torch.no_grad():
            for i in range(half):
                b = torch.tensor(seg[i], dtype=torch.long, device=dev)
                s = self.M_cycle @ (self.psi + self.E(b))
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
                self.ticks_lived += TICKS_PER_BYTE
        losses = []
        dreamed = []
        for i in range(half, len(seg)):
            logits = self.D(self.psi)
            t = torch.tensor(seg[i], dtype=torch.long, device=dev)
            losses.append(F.cross_entropy(logits.unsqueeze(0),
                                          t.unsqueeze(0)))
            with torch.no_grad():
                probs = torch.softmax(
                    logits.detach() / self.cfg.dream_temperature, dim=-1)
                b = int(torch.multinomial(probs, 1))
                dreamed.append(b)
                bt = torch.tensor(b, dtype=torch.long, device=dev)
                s = self.M_cycle @ (self.psi + self.E(bt))
                self.psi = (s / (torch.linalg.vector_norm(s) + 1e-12)
                            ).detach()
                self.ticks_lived += TICKS_PER_BYTE
        loss = torch.stack(losses).mean()
        self.opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self._trainable(),
                                       self.cfg.grad_clip)
        self.opt.step()
        self.psi = self.psi.detach()
        self.dream_bytes += len(dreamed)
        self.last_dream = bytes(dreamed)
        return float(loss.detach())

    def sleep(self):
        """Rest ticks (no input, no learning), then internal learning
        (replay + dreams per the maturation schedule), then the dawn
        damp and the growth check."""
        with torch.no_grad():
            n_cycles, rem = divmod(self.cfg.rest_ticks, TICKS_PER_BYTE)
            for _ in range(n_cycles):
                s = self.M_cycle @ self.psi
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
            for _ in range(rem):
                s = self.M @ self.psi
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
            self.ticks_lived += self.cfg.rest_ticks

        if self.cfg.sleep_learning and len(self.replay) > 0:
            k = min(self.cfg.replay_segments, len(self.replay))
            n_dream = int(round(self._dream_frac() * k))
            idx = torch.randint(0, len(self.replay), (k,))
            for j, i in enumerate(idx.tolist()):
                seg = self.replay[i]
                if j < n_dream:
                    self._dream_segment(seg)
                else:
                    self._learn_segment(seg)
                    self.replay_bytes += len(seg) - 1

        with torch.no_grad():                          # dawn damp
            damp = torch.ones_like(self.psi)
            for node in self.spine.processual_nodes:
                damp[node] = 1.0 - self.alpha
                damp[node + self.spine.N] = 1.0 - self.alpha
            self.psi = self.psi * damp
            self.psi = self.psi / (torch.linalg.vector_norm(self.psi) + 1e-12)
        self.sleeps += 1
        self._growth_check()                           # you grow in your sleep

    # ----- readings -----

    def eval_loss(self, data: bytes, n_bytes: int) -> float:
        """Teacher-forced CE over a slice, NO learning. Note: running
        an evaluation still advances the being's state and clock
        (there is no way to observe without living); harnesses apply
        the same protocol to every twin."""
        dev = self.cfg.device
        total, count = 0.0, 0
        with torch.no_grad():
            for i in range(min(n_bytes, len(data) - 1)):
                b = torch.tensor(data[i], dtype=torch.long, device=dev)
                s = self.M_cycle @ (self.psi + self.E(b))
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
                self.ticks_lived += TICKS_PER_BYTE
                logits = self.D(self.psi)
                t = torch.tensor(data[i + 1], dtype=torch.long,
                                 device=dev)
                total += float(F.cross_entropy(logits.unsqueeze(0),
                                               t.unsqueeze(0)))
                count += 1
        return total / max(count, 1)

    def attractor_overlap(self) -> float:
        return self.spine.attractor_overlap(
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
            "spine": f"{len(self.spine.octaves)} octaves, "
                     f"{self.spine.N} nodes"
                     + (" [FROZEN-NOISE TWIN]" if self.noise_spine else ""),
            "octaves": self.spine.octaves,
            "growth_sites": self.spine.tonic_sites(),
            "site_ratios": {k: round(v, 3)
                            for k, v in self.trigger_ratios().items()},
            "boot_time": self.boot_time,
            "bytes_lived": self.bytes_lived,
            "ticks_lived": self.ticks_lived,
            "sleeps": self.sleeps,
            "replay_bytes": self.replay_bytes,
            "dream_bytes": self.dream_bytes,
            "dream_frac": round(self._dream_frac(), 3),
            "last_dream": "".join(chr(b) if 32 <= b < 127 else "?"
                                  for b in self.last_dream[:60]),
            "loss_ema": self.loss_ema,
            "random_baseline": RAND_CE,
            "attractor_overlap": self.attractor_overlap(),
            "injection_norm_alpha": self.inj_ema,
            "growth_excess_per_cycle": self.growth_ema,
            "injection_diversity": self.injection_diversity(),
            "spine_departure_alpha": self.spine.departure,
            "organ_params": count_params(self.E) + count_params(self.D),
            "reserved_node_untouched": True,
            "growth_events": len(self.growth_history),
        }

    # ----- worldline persistence -----

    def _save(self):
        ckpt = {
            "psi": self.psi.detach().cpu(),
            "octaves": self.spine.octaves,
            "energy_ema": self.energy_ema.detach().cpu(),
            "streaks": dict(self.streaks),
            "senses_class": type(self.E).__name__,
            "senses": self.E.state_dict(),
            "voice": self.D.state_dict(),
            "opt": self.opt.state_dict(),
            "counters": {
                "bytes_lived": self.bytes_lived,
                "ticks_lived": self.ticks_lived,
                "sleeps": self.sleeps,
                "replay_bytes": self.replay_bytes,
                "dream_bytes": self.dream_bytes,
                "last_dream": bytes(self.last_dream),
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
        octs = ckpt.get("octaves")
        if octs is not None and octs != self.spine.octaves:
            # The worldline grew in a prior session: regrow before load
            self.spine = Spine(octs)
            self._rebuild_matrices()
            self.E = SensesBit(self.spine.N, INJ_NODES, self.alpha).to(dev)
            self.D = Voice(self.spine.N).to(dev)
            self.opt = torch.optim.Adam(self._trainable(), lr=self.cfg.lr)
        if "energy_ema" in ckpt:
            self.energy_ema = ckpt["energy_ema"].to(dev)
            self.streaks = dict(ckpt.get("streaks", {}))
        if ckpt["noise_matrix"] is not None:
            self._noise_matrix = ckpt["noise_matrix"]
            self.M = torch.tensor(self._noise_matrix, device=dev,
                                  dtype=torch.float32)
            self.noise_spine = True
        self.psi = ckpt["psi"].to(dev)
        if (ckpt.get("senses_class") == "SensesBit"
                and not isinstance(self.E, SensesBit)):
            self.E = SensesBit(self.spine.N, INJ_NODES, self.alpha).to(dev)
            self.opt = torch.optim.Adam(self._trainable(), lr=self.cfg.lr)
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
        self.dream_bytes = c.get("dream_bytes", 0)
        self.last_dream = bytes(c.get("last_dream", b""))
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

    def speak_continue(self, n_bytes: int = 120,
                       temperature: float = 0.85) -> bytes:
        """Emit from the CURRENT state (no prompt re-injection): the
        voice continues whatever the being is already holding. Each
        emitted byte is re-injected (the voice hears itself)."""
        out = []
        dev = self.cfg.device
        with torch.no_grad():
            for _ in range(n_bytes):
                logits = self.D(self.psi)
                probs = torch.softmax(logits / temperature, dim=-1)
                b = int(torch.multinomial(probs, 1))
                out.append(b)
                bt = torch.tensor(b, dtype=torch.long, device=dev)
                inj = self.E(bt)
                if self._seam_vec is not None:
                    inj = inj + self._seam_vec
                s = self.M_cycle @ (self.psi + inj)
                self.psi = s / (torch.linalg.vector_norm(s) + 1e-12)
                self.ticks_lived += TICKS_PER_BYTE
        return bytes(out)

    def converse(self, heard: bytes, reply_bytes: int = 120,
                 temperature: float = 0.85) -> bytes:
        """One conversational turn: the heard text streams as wake
        experience (reading is living; learning stays on), then the
        voice continues from the state the hearing left behind."""
        L = self.cfg.tbptt
        for i in range(0, max(len(heard) - 1, 1), L):
            seg = heard[i:i + L + 1]
            if len(seg) >= 2:
                self._learn_segment(seg)
                self.replay.append(bytes(seg))
                self.bytes_lived += len(seg) - 1
        if self.home is not None:
            self._save()
        return self.speak_continue(reply_bytes, temperature)


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
