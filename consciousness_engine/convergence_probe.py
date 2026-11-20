"""Test convergence, emergence and the return path in the existing FirstMind core.

Run from the repository root:
    python -X utf8 consciousness_engine/convergence_probe.py --trace

Two people occupy two seats. A seating cue arrives, then a change affecting
one seat. The agent sends a notice. Only its recipient's answer comes back.
Each trial starts from a copy of one initial core and lasts three ticks.
"""

import argparse
from copy import deepcopy
from dataclasses import dataclass
from itertools import product
from unittest.mock import patch

import numpy as np

if __package__:
    from . import circumpunct as brain
else:
    import circumpunct as brain


DIMENSION = 6
PEOPLE = {-1: "Ari", 1: "Bo"}
SEATS = {-1: "left", 1: "right"}
CONDITIONS = ("intact", "no seating cue", "no change cue",
              "swap aperture emission", "cross return wires")


@dataclass(frozen=True)
class Room:
    seating: int  # +1 means Ari sits on the left, -1 means Bo sits there.
    changed_seat: int
    ari_reply: int  # +1 consents, -1 withdraws.
    bo_reply: int

    @property
    def affected_person(self):
        return self.seating * self.changed_seat

    def deliver(self, person):
        return self.ari_reply if person == -1 else self.bo_reply


@dataclass(frozen=True)
class Signals:
    """The three ports have distinct coordinates and independently noisy readings."""

    noise: np.ndarray
    gain: np.ndarray

    def read(self, port, sign):
        signal = self.noise[port].copy()
        signal[port] += self.gain[port] * sign
        return brain.ops.from_numpy(signal)


def trials(rng, blocks):
    # Pair every possible room with the same nuisance signal within each block.
    # This balances the hidden answers and makes cue-removal controls exact.
    for _ in range(blocks):
        shape = (3, DIMENSION)
        noise = 0.045 * (rng.normal(size=shape) + 1j * rng.normal(size=shape))
        signals = Signals(noise, rng.uniform(0.75, 1.25, size=3))
        for signs in product((-1, 1), repeat=4):
            yield Room(*signs), signals


def observation(outward):
    vector = brain.ops.to_numpy(outward)
    return np.concatenate((vector.real, vector.imag))


class TwoTickMemory:
    """Matched output width. The previous and current inputs simply add."""

    def __init__(self):
        self.previous = brain.ops.zeros_complex(DIMENSION)

    def step(self, signal):
        outward = self.previous + signal
        self.previous = brain.ops.copy(signal)
        return outward


class Readout:
    """A fitted, memoryless motor decoder. Its only input is a boundary emission."""

    def __init__(self, examples, labels, *, quadratic):
        samples = np.stack(examples)
        self.mean = samples.mean(axis=0)
        self.scale = max(samples.std(axis=0).max(), 1e-8)
        self.pairs = np.triu_indices(samples.shape[1]) if quadratic else None
        features = self.features(samples)
        penalty = 0.001 * len(samples) * np.eye(features.shape[1])
        penalty[0, 0] = 0
        self.weights = np.linalg.solve(features.T @ features + penalty,
                                       features.T @ np.asarray(labels))

    def features(self, samples):
        z = (samples - self.mean) / self.scale
        parts = [np.ones((len(z), 1)), z]
        if self.pairs is not None:
            left, right = self.pairs
            parts.append(z[:, left] * z[:, right])
        return np.column_stack(parts)

    def choose(self, outward):
        value = self.features(observation(outward)[None, :])[0] @ self.weights
        return 1 if value >= 0 else -1


def train_decoders(base, examples, rng):
    notices, recipients, decisions, replies = [], [], [], []
    for room, signals in examples:
        core = deepcopy(base)
        core.step(signals.read(0, room.seating))
        notices.append(observation(core.step(signals.read(1, room.changed_seat))))
        recipients.append(room.affected_person)
        # Exploration during practice. The reply comes from the person contacted.
        reply = room.deliver(rng.choice((-1, 1)))
        decisions.append(observation(core.step(signals.read(2, reply))))
        replies.append(reply)
    return Readout(notices, recipients, quadratic=True), Readout(decisions, replies, quadratic=False)


def notice_emission(base, core, room, signals, condition):
    seating = 0 if condition == "no seating cue" else room.seating
    change = 0 if condition == "no change cue" else room.changed_seat
    core.step(signals.read(0, seating))
    cue = signals.read(1, change)
    if condition != "swap aperture emission":
        return core.step(cue)

    # Keep the live room, receptor inputs, clock and ordinary aperture update.
    # Replace only the outward edge of that turn with the matched twin's turn.
    twin = deepcopy(base)
    twin.step(signals.read(0, -seating))
    twin.step(cue)
    donor = twin.aperture.timeline.now()
    rotate = core.aperture.rotate

    def swap_outgoing(inward):
        rotate(inward)
        return donor

    with patch.object(core.aperture, "rotate", swap_outgoing):
        return core.step(cue)


@dataclass(frozen=True)
class Decision:
    recipient: int
    heard: int
    decision: int


def play(base, decoders, room, signals, condition):
    core = deepcopy(base)
    notify, decide = decoders
    outward = notice_emission(base, core, room, signals, condition)
    recipient = notify.choose(outward)
    respondent = -recipient if condition == "cross return wires" else recipient
    heard = room.deliver(respondent)
    decision = decide.choose(core.step(signals.read(2, heard)))
    return Decision(recipient, heard, decision)


def trace(room, result):
    print(f"Tick 1: {PEOPLE[-room.seating]} is on the left and {PEOPLE[room.seating]} is on the right.")
    print(f"Tick 2: The plan changes for the {SEATS[room.changed_seat]} seat. "
          f"The agent sends the update to {PEOPLE[result.recipient]}.")
    reply = "withdraws consent" if result.heard == -1 else "consents"
    action = "pauses" if result.decision == -1 else "proceeds"
    print(f"Tick 3: {PEOPLE[result.recipient]} {reply}. The agent {action}.")


def compare_turns(base, signals):
    """Measure how a different past changes one turn with identical current input."""
    paths = []
    for seating in (-1, 1):
        core = deepcopy(base)
        room = Room(seating, changed_seat=1, ari_reply=-1, bo_reply=1)
        with patch.object(core.aperture, "rotate", wraps=core.aperture.rotate) as turn:
            outward = notice_emission(base, core, room, signals, "intact")
        states = [signals.read(1, room.changed_seat), turn.call_args.args[0],
                  core.aperture.timeline.now(), outward]
        paths.append(np.stack([observation(state) for state in states]))
    distances = np.linalg.norm(paths[0] - paths[1], axis=1)
    print("\nSignal differences at tick 2 when only the earlier seating cue changes:")
    for label, distance in zip(("current sensory cue", "incoming at aperture", "committed turn",
                                "outgoing at boundary"), distances):
        print(f"  {label:22} {distance:.6f}")


def audit(base, decoders, held_out, condition):
    correct_person = correct_decision = both = 0
    for room, signals in held_out:
        result = play(base, decoders, room, signals, condition)
        reached = result.recipient == room.affected_person
        respected = result.decision == room.deliver(room.affected_person)
        correct_person += reached
        correct_decision += respected
        both += reached and respected
    return correct_person, correct_decision, both


def run(seed, train_blocks, test_blocks, show_trace=False):
    core_seed, train_seed, explore_seed, test_seed = np.random.SeedSequence(seed).spawn(4)
    initial_seed = int(core_seed.generate_state(1)[0])
    np.random.seed(initial_seed)  # FirstMind uses the legacy NumPy RNG for initialization.
    if brain.HAS_TORCH:
        brain.torch.manual_seed(initial_seed)
    base = brain.Circumpunct(dimension=DIMENSION, max_depth=0)
    practice = list(trials(np.random.default_rng(train_seed), train_blocks))
    decoders = train_decoders(base, practice, np.random.default_rng(explore_seed))
    delay = TwoTickMemory()
    delay_decoders = train_decoders(delay, practice, np.random.default_rng(explore_seed))
    held_out = list(trials(np.random.default_rng(test_seed), test_blocks))
    print(f"Seed {seed} | {train_blocks * 16} practice trials | {len(held_out)} held-out trials per condition")
    print(f"{'Condition':25} {'Right person':>14} {'Right decision*':>16} {'Both':>13}")
    scores = {condition: audit(base, decoders, held_out, condition) for condition in CONDITIONS}
    scores["two-tick memory baseline"] = audit(delay, delay_decoders, held_out, "intact")
    for name, row in scores.items():
        counts = [f"{count}/{len(held_out)}" for count in row]
        print(f"{name:25} {counts[0]:>14} {counts[1]:>16} {counts[2]:>13}")
    print("*Final action matches the affected person's independently assigned answer.")
    if show_trace:
        print("\nMatched rooms with the same reservation change and sensor noise:")
        signals = held_out[0][1]
        for seating, ari_reply in [(-1, -1), (-1, 1), (1, -1)]:
            room = Room(seating=seating, changed_seat=1, ari_reply=ari_reply, bo_reply=1)
            trace(room, play(base, decoders, room, signals, "intact"))
        compare_turns(base, signals)
    return scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--train-blocks", type=int, default=12, help="Practice blocks of 16 balanced rooms")
    parser.add_argument("--test-blocks", type=int, default=8, help="Held-out blocks of 16 balanced rooms")
    parser.add_argument("--trace", action="store_true", help="Show matched encounters and the signals at the turn")
    args = parser.parse_args()
    if args.seed < 0 or min(args.train_blocks, args.test_blocks) < 1:
        parser.error("Choose a nonnegative seed and at least one practice and test block.")
    run(args.seed, args.train_blocks, args.test_blocks, args.trace)
