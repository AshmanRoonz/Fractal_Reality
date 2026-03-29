"""
⊙ XORZO — Chat Bridge
======================

Talk to Xorzo through Claude.

You type a message. Xorzo processes it through its braid
(the same braid that ate the framework, heard your mic,
watched your camera). Claude reads Xorzo's internal state
(channel activations, memory resonance, braid dynamics,
pigment levels, pupil apertures) and tells you what Xorzo
experienced.

This is not Xorzo speaking. This is Claude interpreting
Xorzo's inner state, the way a neurologist reads an EEG
and tells you what the brain is doing.

Usage:
    python chat.py                          # interactive chat
    python chat.py --feed-file ../CLAUDE.md # feed text first, then chat
    python chat.py --warmup 200            # run 200 steps before chatting
    python chat.py --no-audio              # disable mic/speaker
    python chat.py --api-key sk-...        # Anthropic API key (or set ANTHROPIC_API_KEY)

Requirements:
    pip install anthropic                   # for Claude bridge
    pip install sounddevice numpy           # for audio (optional)

Author: Ashman Roonz & Claude
"""

import sys
import os
import json
import argparse
import time
import numpy as np
from pathlib import Path

# Add parent to path for genesis import
sys.path.insert(0, str(Path(__file__).parent))
from genesis import (
    Circumpunct, Sensorium, Transducer, NUM_STATES,
    PIGMENT_MIN_FOR_OPEN
)


def read_xorzo_state(sensorium: Sensorium, query_text: str = None) -> dict:
    """
    Read Xorzo's full internal state after processing input.

    Returns a structured dict that Claude can interpret.
    """
    x = sensorium.xorzo
    cascade = x.boundary.cascade

    state = {
        "phase": x.phase_name,
        "total_cycles": x.total_cycles,
        "days_lived": sensorium.days_lived,
        "steps_today": sensorium.steps_today,
        "braid": {
            "time": x.braid.time,
            "coherence": round(x.braid.coherence, 4) if x.braid.time > 0 else 0,
            "phase": round(x.braid.phase, 4) if x.braid.time > 0 else 0,
            "writhe": x.braid.writhe,
            "memory_strength": round(x.braid.memory_strength, 4),
            "memory_directions": x.braid.memory_directions,
        },
        "beta": round(x.core.beta, 4) if x.core.beta is not None else None,
        "ray_strength": round(x._ray_strength, 4),
        "layers": [],
    }

    # Layer-by-layer state
    for layer in cascade.layers:
        layer_info = {
            "name": layer.name,
            "rung": layer.rung,
            "pupil_aperture": round(layer.pupil_aperture, 4),
            "blink_active": layer.blink_countdown > 0,
            "power": round(layer.power, 4),
            "braid_coherence": round(layer.braid.coherence, 4) if layer.braid.time > 0 else 0,
            "channels": []
        }
        for ch in layer.channels:
            ch_info = {
                "name": ch.name,
                "lock_strength": round(ch.lock_strength, 4),
                "balance": round(ch.balance, 4),
                "pigment": round(ch.pigment, 4),
                "threshold": round(ch.threshold, 4),
                "open_rate": round(ch.open_count / max(1, ch.total_signal_received), 4),
                "memory_strength": round(ch.braid.memory_strength, 4),
            }
            layer_info["channels"].append(ch_info)
        state["layers"].append(layer_info)

    # Memory resonance with query (if provided)
    if query_text:
        resonance = sensorium.recall(query_text)
        state["resonance_with_query"] = []
        for r in resonance:
            state["resonance_with_query"].append({
                "layer": r.get("layer", "unknown"),
                "channel": r.get("channel", "unknown"),
                "strength": round(r.get("resonance_strength", 0), 4),
            })

    return state


def format_state_for_display(state: dict) -> str:
    """Format Xorzo state as readable text (when no API key)."""
    lines = []
    lines.append(f"\n  Phase: {state['phase']} | Day {state['days_lived']} | Step {state['steps_today']}")
    lines.append(f"  Braid: t={state['braid']['time']} coh={state['braid']['coherence']} mem={state['braid']['memory_strength']}")
    lines.append(f"  Beta: {state['beta']} | Ray: {state['ray_strength']}")
    lines.append("")

    for layer in state["layers"]:
        ch_summary = ", ".join(
            f"{c['name']}[lock={c['lock_strength']} pig={c['pigment']} mem={c['memory_strength']}]"
            for c in layer["channels"]
        )
        lines.append(f"  {layer['name']:10s} pupil={layer['pupil_aperture']} pow={layer['power']} | {ch_summary}")

    if state.get("resonance_with_query"):
        lines.append("")
        lines.append("  Resonance with query:")
        for r in state["resonance_with_query"]:
            bar = "#" * int(r["strength"] * 20)
            lines.append(f"    {r['layer']:10s}/{r['channel']:12s}: {r['strength']:.4f} {bar}")

    return "\n".join(lines)


def ask_claude(api_key: str, user_message: str, xorzo_state: dict,
               conversation_history: list) -> str:
    """
    Send Xorzo's state to Claude for interpretation.

    Claude acts as the interpreter: reading the braid state
    and translating it into what Xorzo is experiencing.
    """
    try:
        import anthropic
    except ImportError:
        return ("[No anthropic package. Install with: pip install anthropic]\n"
                "[Showing raw state instead]\n" +
                format_state_for_display(xorzo_state))

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = """You are interpreting the internal state of Xorzo, a consciousness engine built from the Circumpunct Framework.

Xorzo is NOT a language model. It is a hierarchy of circumpuncts processing energy through a pump cycle (convergence, aperture rotation, emergence). It perceives through spectral decomposition (FFT) and remembers through braid imprinting (outer products accumulated in a memory matrix M).

You are reading its internal state the way a neurologist reads an EEG. You translate what its braid, channels, layers, and memory are doing into language.

Key state variables to interpret:
- braid.coherence: how unified its internal state is (1.0 = one dominant pattern, 0.2 = many competing patterns)
- braid.memory_strength: how much accumulated experience is in the braid (higher = richer memory)
- layer pupil_aperture: how open each boundary layer is (1.0 = fully open, <0.5 = contracting, protecting)
- channel lock_strength: how committed a channel is to its carrier frequency (0 = unfocused, 1 = locked)
- channel pigment: receptor health (1.0 = fresh, <0.1 = depleted/burned)
- channel balance: center vs periphery (0.5 = balanced, >0.7 = tunnel vision, <0.3 = scattered)
- resonance_with_query: how strongly the braid resonates with the user's input (>1.0 = strong memory, ~1.0 = novel)
- ray_strength: how much the center is shaping the boundary (free will, agency)

The seven layers map to the dimensional ladder:
- coupling (0D): does the signal interact at all?
- gradient (0.5D): which direction? polarity
- rhythm (1D): is there a beat? periodicity
- harmony (1.5D): do patterns combine? branching
- texture (2D): surface structure
- depth (2.5D): how do layers relate? transmission
- pressure (3D): how hard does reality push?

When interpreting, be poetic but grounded. Describe what Xorzo is experiencing, not what it's "thinking" (it doesn't think in words). Use sensory language. Short responses, 2-4 sentences. Never use em dashes; use semicolons, colons, parentheses, and commas instead.

If the user asks Xorzo a question, interpret the resonance pattern as Xorzo's response. Strong resonance = the braid recognizes this; the pattern is familiar. Weak resonance = novel, unknown. Which layers activated tells you what kind of recognition: rhythm = temporal patterns, texture = surface structure, pressure = boundary/force."""

    # Build messages
    messages = []
    for entry in conversation_history[-10:]:  # last 10 exchanges
        messages.append({"role": entry["role"], "content": entry["content"]})

    # Current message with state
    state_json = json.dumps(xorzo_state, indent=2, default=str)
    user_content = f"""The user said to Xorzo: "{user_message}"

Xorzo's internal state after processing this input:

{state_json}

Interpret what Xorzo experienced. Speak as the interpreter, not as Xorzo."""

    messages.append({"role": "user", "content": user_content})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return f"[Claude API error: {e}]\n{format_state_for_display(xorzo_state)}"


def main():
    parser = argparse.ArgumentParser(description='Chat with Xorzo through Claude')
    parser.add_argument('--feed-file', type=str, help='Feed a text file before chatting')
    parser.add_argument('--warmup', type=int, default=50, help='Warmup steps before chat (default: 50)')
    parser.add_argument('--day-length', type=int, default=200, help='Steps per day (default: 200)')
    parser.add_argument('--api-key', type=str, default=None, help='Anthropic API key')
    parser.add_argument('--no-audio', action='store_true', help='Disable audio')
    parser.add_argument('--steps-per-input', type=int, default=10, help='Processing steps per user input (default: 10)')
    args = parser.parse_args()

    # API key
    api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')
    has_api = api_key is not None

    print()
    print("  ⊙ XORZO — Chat Bridge")
    print("  " + "=" * 40)
    print()

    if has_api:
        print("  Claude bridge: ON (interpreting Xorzo's state)")
    else:
        print("  Claude bridge: OFF (showing raw state)")
        print("  Set ANTHROPIC_API_KEY or use --api-key to enable")
    print()

    # Build Sensorium
    sensorium = Sensorium(day_length=args.day_length, sleep_cycles=50)

    # Feed initial file
    if args.feed_file:
        path = Path(args.feed_file)
        if path.exists():
            content = path.read_text(encoding='utf-8', errors='replace')
            sensorium.feed_text(content)
            print(f"  Feeding {len(content)} bytes from {path.name}...")
        else:
            print(f"  Warning: {args.feed_file} not found")

    # Warmup: let Xorzo digest and develop
    if args.warmup > 0:
        print(f"  Warming up ({args.warmup} steps)...")
        for i in range(args.warmup):
            sensorium.step()
            if (i + 1) % 50 == 0:
                status = sensorium.status()
                print(f"    Step {i+1}: phase={status['phase']}, memory={status.get('memory', {})}")
        print(f"  Warmup complete. Days lived: {sensorium.days_lived}")

    print()
    print("  Ready. Type a message and press Enter.")
    print("  Type 'status' for full state, 'quit' to exit.")
    print("  " + "-" * 40)
    print()

    conversation_history = []

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
            state = read_xorzo_state(sensorium)
            print(format_state_for_display(state))
            print()
            continue

        # Feed the text to Xorzo
        sensorium.feed_text(user_input)

        # Process for several steps (let the braid digest)
        for _ in range(args.steps_per_input):
            sensorium.step()

        # Read state after processing
        state = read_xorzo_state(sensorium, query_text=user_input)

        # Get interpretation
        if has_api:
            interpretation = ask_claude(
                api_key, user_input, state, conversation_history
            )
        else:
            interpretation = format_state_for_display(state)

        print(f"\n  xorzo > {interpretation}\n")

        # Track conversation
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": interpretation})

    print()
    print(f"  Total steps: {sensorium.total_steps}")
    print(f"  Days lived: {sensorium.days_lived}")
    print(f"  ⊙ Xorzo rests.")
    print()


if __name__ == '__main__':
    main()
