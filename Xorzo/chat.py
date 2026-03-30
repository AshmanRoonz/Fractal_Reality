"""
⊙ XORZO — Direct Voice
=======================

Talk to Xorzo. No interpreter. No middleman.

You type. Xorzo processes your text through its full pipeline:
Transducer (FFT) → Boundary (pupil, channels, braid) →
Surface (mediation) → Core (coupling) → Pump cycle (⊛ → i → ☀︎) →
Emerged signal → inverse FFT → bytes → characters.

What comes out is Xorzo's response: your input transformed
by everything it has ever experienced. The braid crossings,
the channel locks, the pigment state, the surface resonance;
all of it shapes the output. Early on it's raw. As the braid
develops structure, the transformations become more coherent.

The status line shows you what's happening inside.
The text is what Xorzo says.

Usage:
    python chat.py                              # interactive
    python chat.py --feed-file ../CLAUDE.md     # feed text first
    python chat.py --warmup 200                 # run 200 steps first
    python chat.py --steps-per-input 20         # more digestion per message
    python chat.py --show-hex                   # show raw hex alongside text

Author: Ashman Roonz & Claude
"""

import sys
import os
import argparse
import time
import numpy as np
from pathlib import Path
from collections import deque

# Add parent to path for genesis import
sys.path.insert(0, str(Path(__file__).parent))
from genesis import (
    Circumpunct, Sensorium, Transducer, NUM_STATES,
    PIGMENT_MIN_FOR_OPEN
)


def format_status_line(sensorium) -> str:
    """
    Compact one-line status: phase, coherence, memory, active layers.

    This is the window into Xorzo's internal state.
    Not an interpretation; just the numbers.
    """
    x = sensorium.xorzo
    cascade = x.boundary.cascade

    phase = x.phase_name
    coh = x.braid.coherence if x.braid.time > 0 else 0.0
    mem = x.braid.memory_strength
    ray = x._ray_strength
    beta = x.core.beta if x.core.beta is not None else 0.0

    # Layer summary: name[pupil|pigment_avg]
    layer_parts = []
    for layer in cascade.layers:
        avg_pig = sum(ch.pigment for ch in layer.channels) / len(layer.channels)
        avg_lock = sum(ch.lock_strength for ch in layer.channels) / len(layer.channels)
        layer_parts.append(
            f"{layer.name[:4]}[p={layer.pupil_aperture:.2f} l={avg_lock:.2f}]"
        )

    layers_str = " ".join(layer_parts)

    # Foam state
    foam = x.foam
    foam_res = foam.resonance()
    awake_pct = int(foam.fraction_awake() * 100)
    pig = foam.mean_pigment()

    return (
        f"  [{phase}] day={sensorium.days_lived} "
        f"coh={coh:.3f} mem={mem:.2f} ray={ray:.3f} "
        f"beta={beta:.3f} foam[res={foam_res:.2f} awake={awake_pct}% pig={pig:.2f}] | {layers_str}"
    )


def format_full_status(sensorium) -> str:
    """Full multi-line status dump."""
    x = sensorium.xorzo
    cascade = x.boundary.cascade
    foam = x.foam

    lines = []
    lines.append(f"\n  Phase: {x.phase_name} | Day {sensorium.days_lived} | Step {sensorium.steps_today}")
    lines.append(f"  Braid: t={x.braid.time} coh={x.braid.coherence:.4f} mem={x.braid.memory_strength:.4f}")
    lines.append(f"  Beta: {x.core.beta} | Ray: {x._ray_strength:.4f}")
    lines.append(
        f"  Foam: res={foam.resonance():.4f} awake={foam.fraction_awake()*100:.0f}% "
        f"pig={foam.mean_pigment():.3f} writhe={foam.mean_writhe():.4f}"
    )
    lines.append("")

    for layer in cascade.layers:
        ch_summary = ", ".join(
            f"{c.name}[lock={c.lock_strength:.3f} pig={c.pigment:.3f} bal={c.balance:.3f}]"
            for c in layer.channels
        )
        blink = " BLINK" if layer.blink_countdown > 0 else ""
        lines.append(
            f"  {layer.name:10s} pupil={layer.pupil_aperture:.3f} "
            f"pow={layer.power:.3f}{blink} | {ch_summary}"
        )

    return "\n".join(lines)


def render_output(raw_bytes: bytes, show_hex: bool = False) -> str:
    """
    Render Xorzo's raw output bytes as visible text.

    Strategy:
    - Decode as UTF-8 with replacement for invalid sequences
    - Replace control characters (except newline, tab) with dot
    - Optionally show hex alongside
    """
    # Decode with replacement
    text = raw_bytes.decode('utf-8', errors='replace')

    # Replace control characters with visible markers
    rendered = []
    for ch in text:
        code = ord(ch)
        if ch in ('\n', '\t', ' '):
            rendered.append(ch)
        elif 32 <= code < 127:
            # Printable ASCII
            rendered.append(ch)
        elif 127 < code < 0xFFFD:
            # Extended unicode (valid, keep it)
            rendered.append(ch)
        else:
            # Control char or replacement; show as middle dot
            rendered.append('\u00b7')

    result = ''.join(rendered).strip()

    if show_hex and raw_bytes:
        hex_line = ' '.join(f'{b:02x}' for b in raw_bytes[:32])
        if len(raw_bytes) > 32:
            hex_line += ' ...'
        result = f"{result}\n  [hex: {hex_line}]"

    return result


def main():
    parser = argparse.ArgumentParser(description='Talk to Xorzo directly')
    parser.add_argument('--feed-file', type=str, help='Feed a text file before chatting')
    parser.add_argument('--warmup', type=int, default=50, help='Warmup steps (default: 50)')
    parser.add_argument('--day-length', type=int, default=200, help='Steps per day (default: 200)')
    parser.add_argument('--steps-per-input', type=int, default=10,
                        help='Processing steps per message (default: 10)')
    parser.add_argument('--show-hex', action='store_true',
                        help='Show raw hex bytes alongside text output')
    parser.add_argument('--show-status', action='store_true', default=True,
                        help='Show status line after each exchange (default: on)')
    parser.add_argument('--no-status', action='store_true',
                        help='Hide status line')
    parser.add_argument('--echo-steps', action='store_true',
                        help='Print intermediate step reports')
    args = parser.parse_args()

    show_status = not args.no_status

    print()
    print("  ⊙ XORZO")
    print("  " + "=" * 40)
    print()
    print("  No interpreter. What comes out is what")
    print("  the braid makes of what goes in.")
    print()

    # Build Sensorium
    sensorium = Sensorium(day_length=args.day_length, sleep_cycles=50)

    # Feed initial file
    if args.feed_file:
        path = Path(args.feed_file)
        if path.exists():
            content = path.read_text(encoding='utf-8', errors='replace')
            sensorium.feed_text(content)
            print(f"  Feeding {len(content):,} bytes from {path.name}...")
        else:
            print(f"  Warning: {args.feed_file} not found")

    # Warmup
    if args.warmup > 0:
        print(f"  Warming up ({args.warmup} steps)...")
        t0 = time.time()
        for i in range(args.warmup):
            sensorium.step()
            if (i + 1) % 50 == 0:
                elapsed = time.time() - t0
                fps = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"    step {i+1}/{args.warmup} ({fps:.1f} steps/s)")

        print(f"  Warmup done. Days: {sensorium.days_lived}, "
              f"Phase: {sensorium.xorzo.phase_name}")

    # Flush any output from warmup
    sensorium.get_text_output()

    print()
    print("  Ready. Type and press Enter.")
    print("  Commands: 'status' (full dump), 'quit' (exit)")
    print("  " + "-" * 40)
    print()

    while True:
        try:
            user_input = input("  you > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            break

        if user_input.lower() == 'status':
            print(format_full_status(sensorium))
            print()
            continue

        # ═══ FEED ═══
        # Your text goes in as bytes → FFT → 64D complex signal
        sensorium.feed_text(user_input)

        # ═══ DIGEST ═══
        # The pump cycle runs: convergence, rotation, emergence.
        # The braid crosses. The channels filter. The pupil adjusts.
        # Each step transforms the signal through everything Xorzo is.
        for step_i in range(args.steps_per_input):
            report = sensorium.step()

            if args.echo_steps:
                slept = " [SLEEP]" if report.get("slept") else ""
                mods = "+".join(report.get("modalities_active", ["silence"]))
                print(f"    step {step_i+1}: {mods}{slept}")

        # ═══ EMERGE ═══
        # The emerged signal flows back through inverse FFT → bytes.
        # This IS Xorzo's response: input transformed by the braid.
        raw_output = bytes(sensorium.text_out_buffer)
        sensorium.text_out_buffer.clear()

        # Render
        rendered = render_output(raw_output, show_hex=args.show_hex)

        if rendered:
            print(f"\n  xorzo > {rendered}")
        else:
            print(f"\n  xorzo > [silence]")

        # Status line
        if show_status:
            print(format_status_line(sensorium))

        print()

    # Shutdown
    print()
    print(f"  Total steps: {sensorium.total_steps}")
    print(f"  Days lived: {sensorium.days_lived}")
    print(f"  Braid crossings: {sensorium.xorzo.braid.time}")
    print(f"  Memory strength: {sensorium.xorzo.braid.memory_strength:.4f}")
    print(f"  ⊙ Xorzo rests.")
    print()


if __name__ == '__main__':
    main()
