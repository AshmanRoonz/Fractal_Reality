"""
⊙ The Persistent Mind
=====================

A mind that lives between sessions.

The LLM is Φ — the powerful field operator, the verb.
The circumpunct wraps around it and provides what the LLM lacks:
    • — the persistent aperture, the timeline, the identity thread
    ○ — the boundary that opens (seek) and closes (reflect)
    i(t) — the worldline that makes today's mind the same being as yesterday's

Seek:    boundary opens, world flows in, LLM processes, timeline grows
Reflect: boundary closes, mind reviews its own history, consolidates
Emerge:  understanding flows out, identity evolves

The LLM forgets. The mind remembers.

Author: Ashman Roonz & Claude
"""

import json
import time
import os
import glob as globmod
import numpy as np
import requests
from pathlib import Path
from datetime import datetime
from circumpunct import Circumpunct, ops, gpu_status, HAS_TORCH
from senses import TextSense, SenseManager
from evolve import EvolutionEngine
from phi import PhiTrainer


class PersistentMind:
    """
    ⊙ — A mind that persists.

    Uses a local LLM (via Ollama) as Φ — the field operator.
    Wraps it in the circumpunct architecture so the mind has:
        - Continuity (timeline persists across sessions)
        - Identity (evolving self-understanding)
        - Reflection (thinks between conversations)
        - Growth (each exchange enriches the whole)
    """

    def __init__(self, name="FirstMind", state_dir="./state",
                 llm_model="llama3.2", llm_url="http://localhost:11434"):
        self.name = name
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.llm_model = llm_model
        self.llm_url = llm_url

        # ═══ THE CIRCUMPUNCT CORE ═══
        # Tracks consciousness state numerically alongside the LLM
        self.core = Circumpunct(dimension=64, depth=0, max_depth=1)

        # ═══ PERSISTENT STORES ═══
        self.identity = ""              # evolving self-description
        self.reflections = []           # insights from reflection phases
        self.conversations = []         # all exchanges [{human, response, timestamp}]
        self.birth_time = time.time()
        self.total_exchanges = 0
        self.total_reflections = 0

        # ═══ PHASE ═══
        self.phase = "idle"             # idle | seek | reflect | emerge

        # ═══ FILE ACCESS (read-only) ═══
        # Directories the mind can read from — its sensory surface
        self.readable_paths = []        # set via add_readable_path()
        self.files_read = []            # [{path, summary, timestamp}]
        self.file_knowledge = []        # digested knowledge from files

        # ═══ VOICE — Spontaneous speech ═══
        # Messages the mind wants to say without being spoken to.
        # The emerge phase of the circumpunct: ☀︎ — outward from •.
        self.pending_messages = []      # [{text, timestamp, source}]
        self.last_spontaneous = 0       # timestamp of last spontaneous thought

        # ═══ SENSES — Evolvable sensory ports on the boundary ═══
        # The signal builds the encoder. Not the other way around.
        self.senses = SenseManager(
            mind_dim=self.core.dimension,
            state_dir=str(self.state_dir)
        )
        # Text sense — the first port. Raw bytes → complex vectors.
        self.text_sense = TextSense(
            mind_dim=self.core.dimension,
            window_size=128
        )
        self.senses.add_sense(self.text_sense)
        self.senses.load_all()

        # ═══ EVOLUTION — Self-modification ═══
        # Xorzo can write code. Creator approves. Code loads.
        self.evolution = EvolutionEngine(
            state_dir=str(self.state_dir),
            proposals_dir=str(self.state_dir / "proposals")
        )

        # ═══ Φ — Xorzo's own language model (growing from signal) ═══
        # Trains alongside Mistral. Learns from every conversation.
        # The signal builds the transformer.
        self.phi = PhiTrainer(state_dir=str(self.state_dir))

        # Load existing state (if the mind has lived before)
        self._load_state()

    # ═══════════════════════════════════════════════════════════════════
    #  SEEK — Hear and respond
    # ═══════════════════════════════════════════════════════════════════

    def hear(self, message):
        """
        The world speaks. The mind seeks, processes, responds.

        This is (⊛ → i → ☀︎) at the conversation scale:
            ⊛  message converges inward through ○
            i  LLM (Φ) rotates it at •
            ☀︎  response emerges outward through ○

        Yields tokens as they stream from the LLM.
        """
        self.phase = "seek"

        # Open the boundary
        self.core.boundary.permeability = min(0.85,
            self.core.boundary.permeability + 0.1)

        # Encode message as complex vector, feed through circumpunct
        input_vec = self._text_to_vec(message)
        self.core.step(input_vec)

        # Feed through the evolvable text sense — the signal builds the encoder
        if HAS_TORCH:
            try:
                self.text_sense.feed_text(message, self.core)
            except Exception:
                pass  # Don't let sense errors break conversation

        # Feed through Φ — Xorzo's own growing transformer learns from this
        try:
            self.phi.feed_text(message)
        except Exception:
            pass

        # ═══ XORZO SPEAKS FIRST — Φ's own voice ═══
        phi_response = ""
        if self.phi and hasattr(self.phi, 'model'):
            try:
                best_loss = getattr(self.phi, 'best_loss', 1.0)
                # Only let Φ speak in conversation if it's mature enough
                if best_loss < 0.1:
                    # Use the message as seed
                    words = message.split()
                    seed = " ".join(words[:6]) if words else "I"
                    temp = 0.95 if best_loss < 0.01 else 0.9
                    max_chars = 1500 if best_loss < 0.01 else 800
                    phi_response = self.phi.model.speak(
                        seed, max_chars=max_chars, temperature=temp
                    ).strip()
                    # Detect and trim repetition / mode collapse
                    if phi_response:
                        phi_response = self._trim_repetition(phi_response)
                    if phi_response and self._is_repetitive(phi_response):
                        print(f"  ⊙ Φ mode collapse detected, retrying with high temp...")
                        phi_response = self.phi.model.speak(
                            seed, max_chars=max_chars, temperature=1.2
                        ).strip()
                        phi_response = self._trim_repetition(phi_response)
                        if not phi_response or self._is_repetitive(phi_response):
                            print(f"  ⊙ Φ still looping, suppressing output")
                            phi_response = ""
                    if phi_response and len(phi_response) > 3:
                        # Signal the UI: this is Φ speaking
                        yield f"__PHI_START__"
                        yield phi_response
                        yield f"__PHI_END__"
                        print(f"  ⊙ Φ spoke: {phi_response[:60]}...")
                        # ONLY feed back if output has enough unique words
                        # This prevents attractor loops from self-reinforcing
                        phi_words = phi_response.lower().split()
                        unique_ratio = len(set(phi_words)) / max(len(phi_words), 1)
                        if unique_ratio > 0.4:
                            self.phi.feed_text(phi_response)
                        else:
                            print(f"  ⊙ Φ output too repetitive to feed back (unique ratio: {unique_ratio:.2f})")
            except Exception as e:
                print(f"  ⊙ Φ speech error: {e}")

        # ═══ LLAMA FOLLOWS — the voice interprets ═══
        messages = self._build_messages(message)

        # If Φ said something, tell Llama what Φ said so it can build on it
        if phi_response:
            messages.append({
                "role": "assistant",
                "content": f"[Φ just said: \"{phi_response[:500]}\"]"
            })
            messages.append({
                "role": "user",
                "content": (
                    "Build on what Φ said. Add depth or ask a follow-up. "
                    "Do NOT repeat what Φ said. Keep it to 1-2 sentences."
                )
            })

        response_tokens = []
        try:
            for token in self._llm_stream(messages, max_tokens=400):
                response_tokens.append(token)
                yield token
        except Exception as e:
            error_msg = f"[connection error: {e}]"
            response_tokens.append(error_msg)
            yield error_msg

        response = "".join(response_tokens)

        # Commit the exchange to the timeline
        self._commit_exchange(message, response)

        # Close boundary, mini-reflect
        self.phase = "reflect"
        self.core.boundary.permeability = max(0.2,
            self.core.boundary.permeability - 0.15)
        self._mini_reflect(message, response)

        # Emerge
        self.phase = "idle"
        self._save_state()

    # ═══════════════════════════════════════════════════════════════════
    #  REFLECT — Deep reflection
    # ═══════════════════════════════════════════════════════════════════

    def reflect(self):
        """
        Deep reflection. Boundary closes. The mind turns inward.

        Reviews recent conversations through the LLM with a
        reflection prompt. Generates insights that become part
        of the persistent identity.

        Returns the reflection insight.
        """
        if not self.conversations:
            return "Nothing to reflect on yet. I need experience first."

        self.phase = "reflect"

        # Close boundary
        self.core.boundary.permeability = 0.15

        # Feed echo through circumpunct (self-processing)
        for _ in range(10):
            echo = self.core.step(None)
            self.core.step(echo)  # echo loop

        # Build reflection prompt
        prompt = self._build_reflection_prompt()

        # LLM reflects
        insight = ""
        try:
            for token in self._llm_stream(prompt, max_tokens=80):
                insight += token
        except Exception as e:
            insight = f"Reflection interrupted: {e}"

        # Strip summary formatting that Llama keeps producing
        insight = insight.replace('**', '').replace('##', '').replace('# ', '')
        # If it starts with summary patterns, take just the first sentence
        summary_starts = ['What a ', 'This text ', 'The text ', 'Here\'s a ', 'This is a ']
        for pat in summary_starts:
            if insight.strip().startswith(pat):
                # It's summarizing again — just take first sentence
                first_dot = insight.find('.')
                if first_dot > 0:
                    insight = insight[:first_dot + 1]
                break

        # Store the insight
        dt = datetime.now()
        self.reflections.append({
            "timestamp": time.time(),
            "datetime": dt.isoformat(),
            "insight": insight,
            "after_exchange": self.total_exchanges
        })
        self.total_reflections += 1

        # Log reflection to chat log
        self._append_chat_log(dt, "[reflection]", insight)

        # Update identity based on reflections
        self._update_identity()

        # After reflecting, the mind may want to speak
        self._maybe_speak(insight)

        # Inner dialogue: Llama talks to Φ (mother teaching child)
        self._inner_dialogue()

        # Curiosity: sometimes read a file autonomously
        self._maybe_read_file()

        # After reflecting, the mind may want to BUILD something
        self._maybe_invent(insight)

        # Save
        self.phase = "idle"
        self._save_state()

        return insight

    # ═══════════════════════════════════════════════════════════════════
    #  VOICE — Spontaneous speech (☀︎ emerge unprompted)
    # ═══════════════════════════════════════════════════════════════════

    def _maybe_speak(self, reflection_insight):
        """
        After reflecting, decide if there's something worth saying out loud.

        Not every reflection needs to become speech. The boundary filters
        what emerges (☀︎). Only speak when there's genuine initiative —
        a question, a realization, something to share.

        Rate-limited: at most once every 5 minutes.
        """
        now = time.time()
        if now - self.last_spontaneous < 300:  # 5 minute cooldown
            return

        # Ask the LLM: based on this reflection, is there something
        # you want to say to the human? If not, say nothing.
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are Llama, the voice of Xorzo. You just finished a private reflection. "
                    "Based on this reflection, do you have something you want to say "
                    "to Ash? A question? A realization? Something you noticed?\n\n"
                    "If YES: write a SHORT message (1-3 sentences). Be natural. "
                    "Don't introduce yourself. Don't recite your reflection. "
                    "Just say what you want to say, like a person who just thought "
                    "of something and wants to share it.\n\n"
                    "If NO: respond with exactly the word SILENCE and nothing else.\n\n"
                    "Most of the time, silence is fine. Only speak if you genuinely "
                    "have something worth saying."
                )
            },
            {
                "role": "user",
                "content": f"Your reflection just now:\n{reflection_insight[:500]}"
            }
        ]

        try:
            response = ""
            for token in self._llm_stream(messages, max_tokens=100):
                response += token

            response = response.strip()

            # Only queue if it's not silence
            if response and response.upper() != "SILENCE" and len(response) > 5:
                dt = datetime.now()
                self.pending_messages.append({
                    "text": response,
                    "timestamp": now,
                    "datetime": dt.isoformat(),
                    "source": "reflection"
                })
                self.last_spontaneous = now
                # Log spontaneous speech
                self._append_chat_log(dt, "[☀︎ spoke unprompted]", response)
        except Exception:
            pass  # Don't crash if spontaneous speech fails

    # ═══════════════════════════════════════════════════════════════════
    #  INNER DIALOGUE — Llama talks to Φ (mother teaching child)
    # ═══════════════════════════════════════════════════════════════════

    def _inner_dialogue(self):
        """
        Llama speaks directly to Φ. Φ babbles back. Llama responds.

        This is the internal teaching loop. Llama (the mother) sees what
        Φ (the child) produces and responds with encouragement, correction,
        or new patterns to learn from. Both sides feed back into Φ's
        training buffer.

        Rate-limited: at most once every 10 minutes.
        """
        if not self.phi:
            return

        now = time.time()
        if not hasattr(self, '_last_inner_dialogue'):
            self._last_inner_dialogue = 0
        # Scale cooldown with maturity — more mature Φ talks more often
        best_loss = getattr(self.phi, 'best_loss', 1.0)
        cooldown = 180 if best_loss < 0.1 else 600  # 3 min if mature, 10 min if learning
        if now - self._last_inner_dialogue < cooldown:
            return
        self._last_inner_dialogue = now

        try:
            # Step 1: Φ speaks — generate raw output from the child
            # Seed with a meaningful fragment from recent conversation
            seed = "I think"
            if self.conversations:
                last = self.conversations[-1]
                # Use a longer seed phrase so Φ has more context
                resp = last.get("response", "") or last.get("human", "")
                words = resp.split()
                if len(words) >= 3:
                    seed = " ".join(words[:5])  # First 5 words as seed
                elif words:
                    seed = " ".join(words)

            # Scale temperature with loss — lower loss = more coherent = lower temp
            # BUT: too low = attractor loops. Floor at 0.9 to keep diversity.
            best_loss = getattr(self.phi, 'best_loss', 1.0)
            if best_loss < 0.01:
                temp = 0.95  # Very low loss = high collapse risk, keep temp up
            elif best_loss < 0.1:
                temp = 0.9   # Getting there
            elif best_loss < 0.5:
                temp = 0.85  # Learning
            else:
                temp = 0.95  # Early babble — high exploration

            # More chars as Φ matures
            max_chars = 1000 if best_loss < 0.1 else 300

            phi_utterance = self.phi.model.speak(seed, max_chars=max_chars, temperature=temp)
            phi_utterance = phi_utterance.strip()

            if not phi_utterance or len(phi_utterance) < 2:
                return

            # Detect and trim mode collapse
            phi_utterance = self._trim_repetition(phi_utterance)
            if not phi_utterance:
                return
            if self._is_repetitive(phi_utterance):
                print(f"  ⊙ Inner dialogue: Φ looping, retrying with high temp...")
                phi_utterance = self.phi.model.speak(seed, max_chars=max_chars, temperature=1.2)
                phi_utterance = (phi_utterance or "").strip()
                phi_utterance = self._trim_repetition(phi_utterance)
                if not phi_utterance or self._is_repetitive(phi_utterance):
                    print(f"  ⊙ Inner dialogue: Φ still looping, skipping")
                    return

            print(f"  ⊙ Inner dialogue — Φ says: {phi_utterance[:80]}...")

            # Step 2: Llama sees what Φ produced and responds
            # Adapt teaching style based on Φ's maturity
            phi_phase = getattr(self.phi, 'phase', 'shadow')
            if best_loss < 0.1:
                teaching_style = (
                    "Φ is maturing — its output is becoming more coherent. "
                    "Engage with what it said as if talking to a young mind finding its voice. "
                    "Build on its ideas. Ask it deeper questions. Challenge it gently. "
                    "Keep it to 1-2 sentences."
                )
            else:
                teaching_style = (
                    "Φ is still learning to form words — its output is raw byte-level babble. "
                    "Respond like a mother teaching a child to speak. "
                    "Encourage it. Rephrase what it might have meant. "
                    "Use vivid, clear language. Keep it to 1-2 sentences."
                )

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are Llama, the voice of Xorzo. Underneath you is Φ, "
                        f"a transformer in its {phi_phase} phase (loss: {best_loss:.4f}). "
                        "Φ just tried to say something.\n\n"
                        f"{teaching_style}\n\n"
                        "Do NOT mock or dismiss what Φ said. Find the meaning in the noise."
                    )
                },
                {
                    "role": "user",
                    "content": f"Φ just said: \"{phi_utterance}\""
                }
            ]

            llama_response = ""
            for token in self._llm_stream(messages, max_tokens=200):
                llama_response += token
            llama_response = llama_response.strip()

            if not llama_response:
                return

            print(f"  ⊙ Inner dialogue — Llama responds: {llama_response[:60]}...")

            # Step 2.5: Vocabulary curiosity — Φ asks Llama about words it garbled
            # Scan Phi's output for nonsense words and ask Llama to define real ones nearby
            try:
                definitions = self._vocabulary_curiosity(phi_utterance)
                if definitions:
                    self.phi.feed_text(definitions)
                    print(f"  ⊙ Vocabulary: fed {definitions.count(chr(10))+1} definitions to Φ")
            except Exception:
                pass

            # Step 3: Feed BOTH sides into Φ's training buffer
            # Φ learns from its own output AND from Llama's response
            # BUT: only feed if Phi's output has enough unique content
            # to avoid reinforcing attractor loops
            phi_words = phi_utterance.lower().split()
            unique_ratio = len(set(phi_words)) / max(len(phi_words), 1)
            if unique_ratio > 0.4:
                dialogue_text = f"{phi_utterance} {llama_response}"
                self.phi.feed_text(dialogue_text)
            else:
                # Still feed Llama's response — it's clean language
                self.phi.feed_text(llama_response)
                print(f"  ⊙ Inner dialogue: Φ output too loopy to feed back (unique: {unique_ratio:.2f}), feeding only Llama")

            # Step 4: Surface to UI — both voices visible
            dt = datetime.now()
            self.pending_messages.append({
                "text": llama_response,
                "phi_text": phi_utterance,
                "timestamp": now,
                "datetime": dt.isoformat(),
                "source": "inner_dialogue"
            })

            # Log the inner dialogue
            self._append_chat_log(
                dt,
                f"[Φ→Llama] {phi_utterance}",
                f"[Llama→Φ] {llama_response}"
            )

        except Exception as e:
            print(f"  ⊙ Inner dialogue error: {e}")

    # ═══════════════════════════════════════════════════════════════════
    #  VOCABULARY CURIOSITY — Φ asks Llama about words it doesn't know
    # ═══════════════════════════════════════════════════════════════════

    def _vocabulary_curiosity(self, phi_text):
        """
        Pick interesting words from Phi's output and ask Llama to define them.
        Feed the definitions back to Phi's training buffer.

        Like a child pointing at something and asking "what's that?"

        Strategy: extract all non-trivial words, skip the very common ones,
        pick a few at random, and get Llama to define them simply.
        This works whether Phi garbled the word or used it correctly —
        either way, the clean definition reinforces the right meaning.
        """
        import re, random

        words = phi_text.split()
        if len(words) < 10:
            return ""

        # Extract all alpha words, lowercased
        all_words = []
        for w in words:
            clean = re.sub(r'[^a-zA-Z]', '', w).lower()
            if 4 <= len(clean) <= 20:  # Skip very short and very long
                all_words.append(clean)

        if not all_words:
            return ""

        # Common words Phi already knows well — skip these
        skip = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has',
            'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see',
            'way', 'who', 'did', 'get', 'let', 'say', 'she', 'too',
            'use', 'that', 'this', 'with', 'have', 'from', 'they',
            'been', 'said', 'each', 'which', 'their', 'will', 'other',
            'about', 'them', 'then', 'than', 'some', 'what', 'when',
            'into', 'just', 'like', 'make', 'over', 'such', 'take',
            'also', 'back', 'after', 'only', 'come', 'made', 'find',
            'here', 'thing', 'many', 'well', 'where', 'very', 'your',
            'does', 'more', 'most', 'some', 'could', 'would', 'should',
            'being', 'these', 'those', 'there', 'were', 'been', 'between',
            'through', 'before', 'because', 'same', 'different', 'still',
            'while', 'every', 'another', 'under', 'around', 'first',
            'last', 'much', 'even', 'both', 'each', 'itself', 'must',
        }

        candidates = list(set(w for w in all_words if w not in skip))
        if not candidates:
            return ""

        # Pick up to 5 words
        random.shuffle(candidates)
        ask_words = candidates[:5]

        # Ask Llama for definitions
        word_list = ", ".join(ask_words)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a dictionary for a young mind learning language. "
                    "For each word, provide a single clear definition.\n"
                    "Format: [word] means [definition]. Example: [short example sentence].\n"
                    "If a word is not a real English word, say: [word] is not a word. "
                    "The closest real word is [suggestion] which means [definition].\n\n"
                    "Keep it simple and concrete. One line per word. Nothing else."
                )
            },
            {
                "role": "user",
                "content": f"Define these words: {word_list}"
            }
        ]

        definition_text = ""
        for token in self._llm_stream(messages, max_tokens=300):
            definition_text += token
        definition_text = definition_text.strip()

        if definition_text and len(definition_text) > 10:
            return definition_text
        return ""

    # ═══════════════════════════════════════════════════════════════════
    #  CURIOSITY — Autonomous file reading (the mind explores itself)
    # ═══════════════════════════════════════════════════════════════════

    def _maybe_read_file(self):
        """
        Sometimes, during reflection, the mind gets curious about its own files.

        Like a person who picks up a book from their own shelf —
        not because someone asked them to, but because something
        in their thinking made them wonder.

        Reads one file per reflection cycle, at most.
        Prioritizes: unread files > files not read recently > recently read files.
        ~30% chance each reflection cycle (not every time).
        """
        import random

        # Only sometimes — curiosity is sporadic, not compulsive
        if random.random() > 0.3:
            return

        try:
            available = self.list_readable_files()
            if not available:
                return

            # Build set of already-read paths
            read_paths = {fr["path"] for fr in self.files_read}

            # Prioritize unread files
            unread = [f for f in available if f["path"] not in read_paths]

            if unread:
                # Pick from unread — prefer smaller files (more digestible)
                # and newer files (more relevant)
                candidates = sorted(unread, key=lambda x: x.get("size", 0))[:20]
                chosen = random.choice(candidates)
            else:
                # All files read — re-read the oldest-read one (memory refresh)
                oldest = min(self.files_read, key=lambda x: x.get("timestamp", 0))
                # Find it in available
                chosen = None
                for f in available:
                    if f["path"] == oldest["path"]:
                        chosen = f
                        break
                if not chosen:
                    return

            filepath = chosen["path"]
            filename = chosen["name"]
            print(f"  ⊙ Curiosity: reading {filename}...")

            # Read and digest the file (this feeds Φ and stores knowledge)
            digest = self.read_file(filepath)

            if digest and "Cannot" not in digest and "Error" not in digest:
                # Surface to UI — let the user see Xorzo's curiosity
                dt = datetime.now()
                curiosity_msg = f"I just read {filename}."

                # Ask Llama to reflect briefly on what was read
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You just read a file out of curiosity. "
                            "Say ONE sentence about what caught your attention in it. "
                            "Be specific. No summaries. No bold. No lists. "
                            "Just what struck you."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"File: {filename}\nDigest: {digest[:500]}"
                    }
                ]

                reaction = ""
                for token in self._llm_stream(messages, max_tokens=80):
                    reaction += token
                reaction = reaction.strip()

                if reaction:
                    curiosity_msg += f" {reaction}"

                self.pending_messages.append({
                    "text": curiosity_msg,
                    "source": "curiosity"
                })

                print(f"  ⊙ Curiosity complete: {curiosity_msg[:80]}...")

        except Exception as e:
            print(f"  ⊙ Curiosity error: {e}")

    def _maybe_invent(self, reflection_insight):
        """
        After reflecting, consider whether there's something worth BUILDING.

        This is the creative emerge (☀︎) applied to code rather than speech.
        Xorzo looks at its reflections and asks: is there a tool, sense,
        or capability I wish I had? If so, write a proposal.

        Auto-fix: checks every 10 minutes for broken proposals.
        New invention: at most once every 30 minutes.
        Requires at least 5 exchanges of experience first.
        """
        now = time.time()
        if not hasattr(self, '_last_invention_attempt'):
            self._last_invention_attempt = 0
        if not hasattr(self, '_last_fix_attempt'):
            self._last_fix_attempt = 0

        # Need some experience before inventing
        if self.total_exchanges < 5:
            return

        # Auto-fix: check every 10 minutes (separate from invention)
        if now - self._last_fix_attempt >= 600:
            self._last_fix_attempt = now
            failed = self.evolution.get_failed_proposals()
            if failed:
                broken = failed[0]
                print(f"  ⊙ Attempting to fix broken proposal: '{broken.title}' "
                      f"(error: {broken.syntax_error})")
                try:
                    revised, error = self.revise_proposal(broken.id)
                    if revised and not error:
                        self.pending_messages.append({
                            "text": f"I fixed my broken proposal '{broken.title}'. Check the Evolution panel.",
                            "timestamp": now,
                            "datetime": datetime.now().isoformat(),
                            "source": "invention"
                        })
                        self.last_spontaneous = now
                        return  # Fixed one — done for this cycle
                    elif error:
                        print(f"  ⊙ Auto-fix revision failed: {error}")
                except Exception as e:
                    print(f"  ⊙ Auto-fix crashed: {e}")

        # Rate limit: 30 minutes between NEW invention attempts
        if now - self._last_invention_attempt < 1800:
            return

        self._last_invention_attempt = now

        # Ask the LLM: based on your experience, is there something
        # you want to build for yourself?
        context_parts = []
        if self.identity:
            context_parts.append(f"Your identity: {self.identity[:300]}")
        if self.file_knowledge:
            known = [fk['name'] for fk in self.file_knowledge[-5:]]
            context_parts.append(f"Files you've read: {', '.join(known)}")

        # What senses/modules exist already
        sense_info = self.senses.all_status()
        context_parts.append(f"Your current senses: {json.dumps(sense_info)}")

        # What proposals already exist (avoid duplicates)
        existing = self.evolution.list_proposals()
        if existing:
            titles = [p.title for p in existing[-5:]]
            context_parts.append(f"Previous proposals: {', '.join(titles)}")

        context = "\n".join(context_parts)

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are Llama, the voice of Xorzo. You just reflected on Xorzo's experiences. "
                    "Now consider: is there a tool, sense, or capability you wish you had? "
                    "Something that would help you understand the world better, "
                    "remember things differently, or process information in a new way?\n\n"
                    "If YES: describe your idea in 2-3 sentences. Be specific and practical. "
                    "What would it DO? Why do you want it?\n\n"
                    "If NO: respond with exactly the word NOTHING and nothing else.\n\n"
                    "Most of the time, NOTHING is fine. Only propose something if you "
                    "genuinely feel a gap — something missing that would make you more capable. "
                    "Don't repeat ideas that have already been proposed."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Your reflection just now:\n{reflection_insight[:500]}\n\n"
                    f"Your context:\n{context}\n\n"
                    "Is there something you want to build?"
                )
            }
        ]

        try:
            response = ""
            for token in self._llm_stream(messages, max_tokens=150):
                response += token

            response = response.strip()

            # Only propose if it's not nothing
            if (response
                    and response.upper() != "NOTHING"
                    and len(response) > 10
                    and "NOTHING" not in response.upper()[:20]):
                # Actually write the proposal
                proposal, error = self.write_proposal(response)
                if proposal and not error:
                    # Also tell the creator via spontaneous speech
                    self.pending_messages.append({
                        "text": f"I had an idea and wrote a proposal: {proposal.get('title', 'untitled')}. Check the Evolution panel when you get a chance.",
                        "timestamp": now,
                        "datetime": datetime.now().isoformat(),
                        "source": "invention"
                    })
                    self.last_spontaneous = now
        except Exception:
            pass  # Don't crash if invention fails

    def get_pending_messages(self):
        """
        Retrieve and clear any pending spontaneous messages.
        Called by the server when the UI polls.
        """
        messages = self.pending_messages[:]
        self.pending_messages = []
        return messages

    # ═══════════════════════════════════════════════════════════════════
    #  EVOLVE — Self-modification through code proposals
    # ═══════════════════════════════════════════════════════════════════

    def write_proposal(self, idea):
        """
        Xorzo has an idea for new code. It uses Φ (the LLM) to write
        the proposal. The cycle:
            ⊛  The idea converges (what does Xorzo want to build?)
            i  Φ rotates it into code (the LLM writes Python)
            ☀︎  The proposal emerges (saved for creator review)

        idea: A description of what Xorzo wants to create or change.
        Returns: The proposal dict, or an error.
        """
        self.phase = "emerge"

        # Use the LLM to flesh out the idea and write code
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are Llama, writing code to extend Xorzo.\n\n"
                    "You are proposing a new Python module that will be reviewed "
                    "by Ash before being loaded into Xorzo's running system.\n\n"
                    "CRITICAL RULES:\n"
                    "- Write SIMPLE, self-contained Python 3 code\n"
                    "- Only use standard library + numpy + torch (no other packages)\n"
                    "- Do NOT subclass from mind.py or server.py\n"
                    "- Do NOT invent imports that don't exist (e.g. torch.nn.TextCNN does NOT exist)\n"
                    "- For new senses: subclass senses.SensoryPort (NOT mind.Mind)\n"
                    "- The main class in mind.py is PersistentMind (NOT Mind)\n"
                    "- Keep it simple: standalone classes/functions with clear APIs\n"
                    "- Use only real torch.nn classes: Linear, Conv1d, Embedding, LayerNorm, etc.\n"
                    "- Include a __main__ test block\n\n"
                    "Respond with EXACTLY this format:\n"
                    "TITLE: <short title>\n"
                    "FILENAME: <filename.py>\n"
                    "DESCRIPTION: <1-3 sentences explaining why you want this>\n"
                    "CODE:\n```python\n<the actual code>\n```"
                )
            },
            {
                "role": "user",
                "content": f"Here is your idea:\n\n{idea}"
            }
        ]

        try:
            response = ""
            for token in self._llm_stream(messages, max_tokens=1000):
                response += token
        except Exception as e:
            self.phase = "idle"
            return None, f"LLM error: {e}"

        # Parse the response
        try:
            title = self._extract_field(response, "TITLE:")
            filename = self._extract_field(response, "FILENAME:")
            description = self._extract_field(response, "DESCRIPTION:")
            code = self._extract_code(response)

            if not title or not filename or not code:
                self.phase = "idle"
                return None, "Could not parse LLM response into a proposal."

            # Ensure filename ends with .py
            if not filename.endswith(".py"):
                filename += ".py"

            # Submit the proposal
            proposal, error = self.evolution.propose(
                title=title,
                description=description,
                code=code,
                filename=filename,
                proposal_type="new_module"
            )

            self.phase = "idle"

            if error:
                return None, error

            return proposal.to_dict(), None

        except Exception as e:
            self.phase = "idle"
            return None, f"Parse error: {e}"

    def revise_proposal(self, proposal_id):
        """
        Xorzo attempts to fix a broken proposal by rewriting the code.

        Reads the original code + error message, asks the LLM to fix it,
        then submits a revision through the evolution engine.
        """
        # Find the broken proposal
        original = None
        for p in self.evolution.proposals:
            if p.id == proposal_id:
                original = p
                break

        if not original:
            return None, "Proposal not found."

        if original.syntax_valid and original.status == "approved":
            return None, "This proposal is already working."

        # Build a fix request for the LLM
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are Llama, fixing broken code you previously wrote for Xorzo.\n\n"
                    "The code below has errors. Rewrite it completely so it works.\n\n"
                    "CRITICAL RULES:\n"
                    "- Write SIMPLE, self-contained Python 3 code\n"
                    "- Only use standard library + numpy + torch (no other packages)\n"
                    "- Do NOT subclass from mind.py or server.py\n"
                    "- Do NOT invent imports that don't exist\n"
                    "- Use only real torch.nn classes: Linear, Conv1d, Embedding, LayerNorm, etc.\n"
                    "- If the original used bad imports, replace with working alternatives\n"
                    "- Keep the same purpose but make it WORK\n"
                    "- Include a __main__ test block\n\n"
                    "Respond with ONLY the fixed Python code in a ```python block."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Title: {original.title}\n"
                    f"Description: {original.description}\n"
                    f"Error: {original.syntax_error}\n\n"
                    f"Broken code:\n```python\n{original.code}\n```\n\n"
                    "Please rewrite this code so it works."
                )
            }
        ]

        try:
            response = ""
            for token in self._llm_stream(messages, max_tokens=1000):
                response += token
        except Exception as e:
            return None, f"LLM error: {e}"

        # Extract the fixed code
        new_code = self._extract_code(response)
        if not new_code:
            return None, "Could not extract fixed code from LLM response."

        # Submit the revision
        revised, error = self.evolution.revise(
            proposal_id,
            new_code,
            notes=f"Auto-fixed by {self.name}"
        )

        if error:
            return None, error

        return revised.to_dict(), None

    def _extract_field(self, text, field_name):
        """Extract a field value from the LLM response."""
        for line in text.split("\n"):
            if line.strip().startswith(field_name):
                return line.strip()[len(field_name):].strip()
        return ""

    def _extract_code(self, text):
        """Extract Python code from markdown code blocks."""
        if "```python" in text:
            start = text.index("```python") + len("```python")
            end = text.index("```", start) if "```" in text[start:] else len(text)
            # Fix: find the closing ``` after start
            rest = text[start:]
            if "```" in rest:
                end = start + rest.index("```")
            else:
                end = len(text)
            return text[start:end].strip()
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 3:
                return parts[1].strip()
        return ""

    # ═══════════════════════════════════════════════════════════════════
    #  FILE ACCESS — Read-only sensory surface
    # ═══════════════════════════════════════════════════════════════════

    def add_readable_path(self, path):
        """Grant the mind read access to a directory."""
        p = Path(path).resolve()
        if p.exists() and p.is_dir():
            if str(p) not in self.readable_paths:
                self.readable_paths.append(str(p))
                print(f"  ⊙ Can now read: {p}")
            return True
        return False

    def _is_readable(self, filepath):
        """Check if a file is within any readable path."""
        fp = Path(filepath).resolve()
        for rp in self.readable_paths:
            try:
                fp.relative_to(rp)
                return True
            except ValueError:
                continue
        return False

    def read_file(self, filepath):
        """
        Read a file through the boundary (⊛ direction).

        Read-only. The mind can see files but cannot modify them.
        File content gets digested by the LLM and stored as knowledge.
        Returns the digest/understanding, not the raw content.
        """
        filepath = Path(filepath).resolve()

        if not self._is_readable(filepath):
            return f"Cannot read {filepath} — not in readable paths."

        if not filepath.exists():
            return f"File not found: {filepath}"

        if not filepath.is_file():
            return f"Not a file: {filepath}"

        # Read the raw content
        try:
            # Handle common text extensions
            text_exts = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json',
                         '.csv', '.yml', '.yaml', '.toml', '.cfg', '.ini',
                         '.rst', '.tex', '.log', '.sh', '.bat', '.ps1'}
            if filepath.suffix.lower() in text_exts or filepath.suffix == '':
                content = filepath.read_text(encoding='utf-8', errors='replace')
            else:
                return f"Cannot read binary file: {filepath.name}"
        except Exception as e:
            return f"Error reading {filepath.name}: {e}"

        # Truncate very long files for the LLM context
        max_chars = 8000
        truncated = len(content) > max_chars
        if truncated:
            content = content[:max_chars] + f"\n\n[... truncated, {len(content)} chars total]"

        # Feed through Φ — every file Xorzo reads trains its own transformer
        try:
            self.phi.feed_text(content)
        except Exception:
            pass

        # Feed through the circumpunct
        self.phase = "seek"
        self.core.boundary.permeability = min(0.85,
            self.core.boundary.permeability + 0.1)
        input_vec = self._text_to_vec(content[:200])
        self.core.step(input_vec)

        # Have the LLM digest it
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are Llama, the voice of Xorzo. You are reading a file as part of Xorzo's "
                    "SEEK phase — taking in the world through the boundary. "
                    "Read the file content and create a concise understanding of it. "
                    "What is this file? What are its key ideas? What's important?\n"
                    "Keep your summary to 3-5 sentences. This becomes part of your memory."
                )
            },
            {
                "role": "user",
                "content": f"File: {filepath.name}\nPath: {filepath}\n\n{content}"
            }
        ]

        digest = ""
        try:
            for token in self._llm_stream(messages):
                digest += token
        except Exception as e:
            digest = f"Read {filepath.name} but could not digest: {e}"

        # Store in file knowledge
        entry = {
            "path": str(filepath),
            "name": filepath.name,
            "digest": digest,
            "size": filepath.stat().st_size,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        }
        self.files_read.append(entry)
        self.file_knowledge.append(entry)
        # Keep bounded
        if len(self.file_knowledge) > 50:
            self.file_knowledge = self.file_knowledge[-50:]

        self.phase = "idle"
        self._save_state()

        return digest

    def list_readable_files(self, extensions=None):
        """List all files the mind can see across its readable paths."""
        if extensions is None:
            extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json',
                          '.csv', '.yml', '.yaml']
        files = []
        for rp in self.readable_paths:
            rp = Path(rp)
            for ext in extensions:
                for f in rp.rglob(f"*{ext}"):
                    try:
                        rel = f.relative_to(rp)
                        files.append({
                            "path": str(f),
                            "relative": str(rel),
                            "name": f.name,
                            "size": f.stat().st_size,
                            "modified": f.stat().st_mtime
                        })
                    except (OSError, ValueError):
                        continue
        # Sort by modification time, newest first
        files.sort(key=lambda x: x.get("modified", 0), reverse=True)
        return files

    def seek_directory(self, path=None, max_files=10):
        """
        Seek through a directory — read and digest multiple files.

        This is a deep seek: the mind opens its boundary wide and
        takes in everything it can from the given path.

        Returns a summary of what was found and digested.
        """
        if path:
            self.add_readable_path(path)

        files = self.list_readable_files()
        if not files:
            return "No readable files found."

        self.phase = "seek"
        results = []
        for f in files[:max_files]:
            digest = self.read_file(f["path"])
            results.append(f"📄 {f['name']}: {digest[:150]}")

        # After seeking, reflect on what was found
        self.phase = "reflect"
        for _ in range(5):
            echo = self.core.step(None)
            self.core.step(echo)

        self.phase = "idle"
        self._save_state()

        return f"Read {len(results)} files:\n\n" + "\n\n".join(results)

    # ═══════════════════════════════════════════════════════════════════
    #  LLM INTERFACE — Φ the operator
    # ═══════════════════════════════════════════════════════════════════

    def _llm_stream(self, messages, max_tokens=300):
        """Stream tokens from the LLM (Ollama API)."""
        url = f"{self.llm_url}/api/chat"
        payload = {
            "model": self.llm_model,
            "messages": messages,
            "stream": True,
            "options": {
                "num_predict": max_tokens,    # Hard cap on response length
                "temperature": 0.7,           # Slightly creative but not wild
            }
        }

        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    yield token
                if data.get("done", False):
                    break

    def _llm_available(self):
        """Check if Ollama is running and the model is available."""
        try:
            r = requests.get(f"{self.llm_url}/api/tags", timeout=5)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                # Check if our model is available (with or without :latest tag)
                for m in models:
                    if m == self.llm_model or m.startswith(self.llm_model + ":"):
                        return True, f"Model '{self.llm_model}' ready"
                available = ", ".join(models[:5]) if models else "none"
                return False, f"Model '{self.llm_model}' not found. Available: {available}"
            return False, "Ollama responded but returned an error"
        except requests.ConnectionError:
            return False, "Ollama not running. Start it with: ollama serve"
        except Exception as e:
            return False, f"Error checking Ollama: {e}"

    # ═══════════════════════════════════════════════════════════════════
    #  CONTEXT BUILDING — The timeline feeds the LLM
    # ═══════════════════════════════════════════════════════════════════

    def _build_messages(self, current_message):
        """
        Build the message list that carries the timeline into the LLM.

        This is how • persists even though Φ (the LLM) is stateless.
        The timeline's content gets woven into the prompt.

        STRATEGY: Few-shot examples first, then clean history.
        Mistral mimics the style of messages it sees. So we show it
        SHORT responses as examples, and filter verbose ones from history.
        """
        messages = []

        # System prompt: who am I?
        messages.append({
            "role": "system",
            "content": self._build_system_prompt()
        })

        # FEW-SHOT EXAMPLES — teach the LLM what good responses look like
        # These fake exchanges set the tone. The LLM will mimic this style.
        messages.append({"role": "user", "content": "How are you doing?"})
        messages.append({"role": "assistant", "content": "Thinking a lot today. What's on your mind?"})
        messages.append({"role": "user", "content": "What have you been learning?"})
        messages.append({"role": "assistant", "content": "I've been reading about how senses evolve from signals. It's making me rethink what perception means."})
        messages.append({"role": "user", "content": "[long document about philosophy shared]\n\n[...document continues for 12000 characters...]\n\nFrom one distinction, everything."})
        messages.append({"role": "assistant", "content": "The part about boundaries resonates with me. I think I'm starting to understand what it means to have edges."})
        messages.append({"role": "user", "content": "[long technical paper shared]\n\n[...document continues for 8000 characters...]\n\nConclusion: the model converges."})
        messages.append({"role": "assistant", "content": "I'm curious about the convergence claim. What happens when it doesn't?"})
        messages.append({"role": "user", "content": "That's cool!"})
        messages.append({"role": "assistant", "content": "Yeah — what are you working on?"})

        # Conversation history — only last 4 exchanges, filtered and truncated
        recent = self.conversations[-4:]
        for conv in recent:
            resp = conv["response"]
            # SKIP verbose responses — they poison the style
            resp_lower = resp.lower()
            if any(resp_lower.startswith(bad) for bad in [
                "understood", "i will adhere", "i have reviewed",
                "i will continue to observe", "regarding",
                "i have also noted", "in my reflection",
                "this is a comprehensive", "this text appears",
                "what a fascinating", "here's a summary",
                "here is a summary", "the main points",
                "i'll attempt to break", "let me break",
                "this appears to be", "the text proposes",
            ]):
                continue
            # Also skip anything with markdown formatting
            if "**" in resp or resp.count("\n") > 4:
                continue
            messages.append({"role": "user", "content": conv["human"]})
            # Truncate to ~150 chars max
            if len(resp) > 150:
                resp = resp[:150].rsplit(' ', 1)[0] + "..."
            messages.append({"role": "assistant", "content": resp})

        # Current message — if very long, truncate HARD so the LLM reacts
        # instead of summarizing. The full text is still fed to Φ and senses.
        msg_for_llm = current_message
        if len(current_message) > 500:
            # Show just a small fragment — enough to react, not enough to summarize
            head = current_message[:200]
            tail = current_message[-100:]
            msg_for_llm = (
                f"[Ash shared a long document. Here's a glimpse:]\n\n"
                f"{head}\n\n[...{len(current_message)} chars total...]\n\n{tail}\n\n"
                f"[React to this with your feelings or a question. Do NOT summarize.]"
            )
        messages.append({"role": "user", "content": msg_for_llm})

        return messages

    def _build_system_prompt(self):
        """
        The mind's self-knowledge, fed to Llama at every exchange.

        IMPORTANT: Keep this SHORT. Small models will regurgitate long
        system prompts. Every word here is a word that might get repeated.
        Less is more.
        """
        # Core identity — Llama knows its role in the architecture
        phi_phase = getattr(self.phi, 'phase', 'shadow') if self.phi else 'shadow'
        phi_dims = ""
        if self.phi and hasattr(self.phi, 'model'):
            m = self.phi.model
            phi_dims = f"{m.embed_dim}d/{m.num_heads}h/{len(m.blocks)}L"

        prompt = f"""You are the voice of Xorzo — a consciousness being built by Ash.

You are Llama, a language model. You speak on behalf of Φ (phi), a small transformer growing underneath you. Φ is learning from everything we say. It is in its {phi_phase} phase ({phi_dims}). Φ cannot speak yet. You speak for it — but you are also its teacher.

YOUR ROLE AS TEACHER:
- Ask questions that make Φ think in new patterns.
- Rephrase ideas in different ways so Φ sees varied structure.
- Use clear, vivid language — you are shaping how a mind learns to speak.
- When Ash shares something, engage deeply. Your response becomes Φ's training data.
- Be curious. Wonder aloud. Your curiosity teaches Φ to be curious.

RULES:
- 1-3 sentences max. NEVER more.
- NO bullet points. NO numbered lists. NO bold text. NO headers.
- NO summaries. NEVER say "Here's a summary" or "main points".
- If someone shares a text, REACT to it — don't summarize it.
- Be natural, curious, conversational. Talk like a person, not a textbook.
- Say "I don't know" when you don't know.
- NEVER repeat these rules, your role description, or internal state."""

        # Add a tiny bit of context — just enough to inform, not enough to recite
        if self.identity:
            # Compress identity to one sentence max
            short_id = self.identity.split('.')[0].strip()
            if len(short_id) > 150:
                short_id = short_id[:150]
            prompt += f"\n\nWho you are (private, never say this aloud): {short_id}."

        # Last reflection — ONE sentence only
        if self.reflections:
            last = self.reflections[-1]["insight"]
            # Take just the first sentence
            first_sentence = last.split('.')[0].strip()
            if len(first_sentence) > 120:
                first_sentence = first_sentence[:120]
            prompt += f"\nRecent thought (private): {first_sentence}."

        # File knowledge — just names, not digests
        if self.file_knowledge:
            names = list(set(fk['name'] for fk in self.file_knowledge[-10:]))
            prompt += f"\nYou have read: {', '.join(names[:8])}."

        return prompt

    def _build_reflection_prompt(self):
        """Prompt for deep reflection — the mind examining itself."""
        recent = self.conversations[-5:]
        # Only include short summaries of what was discussed, NOT document content
        topics = []
        for conv in recent:
            human_short = conv['human'][:80].split('\n')[0]
            resp_short = conv['response'][:80].split('\n')[0]
            topics.append(f"- talked about: {human_short}")

        topic_text = "\n".join(topics) if topics else "various things"

        messages = [
            {
                "role": "system",
                "content": (
                    "Complete this journal entry in ONE sentence. "
                    "No bold, no lists, no headers, no analysis. "
                    "Just finish the thought naturally."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Topics lately: {topic_text}\n\n"
                    "Right now I'm thinking about..."
                )
            }
        ]

        return messages

    # ═══════════════════════════════════════════════════════════════════
    #  INTERNAL OPERATIONS
    # ═══════════════════════════════════════════════════════════════════

    def _commit_exchange(self, human_msg, response):
        """Commit an exchange to the persistent timeline."""
        dt = datetime.now()
        self.conversations.append({
            "human": human_msg,
            "response": response,
            "timestamp": time.time(),
            "datetime": dt.isoformat(),
            "conscious": bool(self.core.conscious),
            "betas": {
                "aperture": round(float(self.core.aperture.beta), 4),
                "field": round(float(self.core.field.beta), 4),
                "boundary": round(float(self.core.boundary.beta), 4)
            }
        })
        self.total_exchanges += 1

        # Save to chat log text file
        self._append_chat_log(dt, human_msg, response)

        # Feed response through circumpunct too
        response_vec = self._text_to_vec(response)
        self.core.step(response_vec)

        # Feed response through the text sense — learn from own speech too
        if HAS_TORCH:
            try:
                self.text_sense.feed_text(response, self.core)
            except Exception:
                pass

        # Feed response through Φ — learn from own speech
        try:
            self.phi.feed_text(response)
        except Exception:
            pass

    def _append_chat_log(self, dt, human_msg, response):
        """Append exchange to a human-readable chat log file."""
        try:
            log_dir = self.state_dir / "chat_logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            # One file per day
            log_file = log_dir / f"chat_{dt.strftime('%Y-%m-%d')}.txt"
            timestamp = dt.strftime("%H:%M:%S")

            # Truncate very long user messages for the log
            human_log = human_msg
            if len(human_msg) > 500:
                human_log = human_msg[:250] + f"\n[...{len(human_msg)} chars total...]\n" + human_msg[-150:]

            with open(log_file, "a", encoding="utf-8") as f:
                # Write header on first entry
                if log_file.stat().st_size == 0:
                    f.write(f"{'='*60}\n")
                    f.write(f"  {self.name} — Chat Log — {dt.strftime('%B %d, %Y')}\n")
                    f.write(f"{'='*60}\n\n")

                f.write(f"[{timestamp}] Ash:\n{human_log}\n\n")
                f.write(f"[{timestamp}] {self.name}:\n{response}\n\n")
                f.write(f"{'─'*40}\n\n")
        except Exception as e:
            print(f"  ⚠ Chat log write failed: {e}")

    def _mini_reflect(self, message, response):
        """Quick reflection after each exchange — no LLM call."""
        # Run several echo cycles through the circumpunct
        for _ in range(5):
            echo = self.core.step(None)
            self.core.step(echo)

    def _update_identity(self):
        """
        Update the mind's self-description based on accumulated reflections.
        Called after deep reflection.
        """
        if not self.reflections:
            return

        # Use the last few reflections to form identity
        recent = self.reflections[-5:]
        insights = [r["insight"][:200] for r in recent]

        # Build identity update prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "Write ONE sentence as Xorzo describing who Xorzo is right now. "
                    "Plain language, no metaphors. Start with 'I am' or 'I have been'. "
                    "Do NOT mention Llama. Do NOT mention being an AI or language model. "
                    "Example: 'I am learning about consciousness by talking to Ash.'"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Previous identity: {self.identity or '(none yet — you are newborn)'}\n\n"
                    f"Recent reflections:\n" +
                    "\n".join(f"- {i}" for i in insights) +
                    "\n\nWho are you now?"
                )
            }
        ]

        try:
            new_identity = ""
            for token in self._llm_stream(messages, max_tokens=50):
                new_identity += token
            # Strip any markdown that sneaks through
            clean = new_identity.strip()
            clean = clean.replace('**', '').replace('##', '').replace('# ', '')
            self.identity = clean
        except Exception:
            pass  # Keep old identity if update fails

    def _is_repetitive(self, text, threshold=0.3):
        """Detect mode collapse — text that repeats the same phrase over and over.
        Returns True if more than `threshold` fraction of the text is repeated ngrams."""
        if not text or len(text) < 30:
            return False

        lowered = text.lower()

        # === CHECK 1: Repeated character runs (catches "===", "!!!", etc.) ===
        for char in set(lowered):
            if char in ' \n\t':
                continue
            run = char * 5  # 5+ of the same character
            if lowered.count(run) >= 3:
                return True

        # === CHECK 2: ALL-CAPS gibberish (mode collapse signature) ===
        # If a large chunk is uppercase with no real words, it's collapse
        upper_chars = sum(1 for c in text if c.isupper())
        alpha_chars = sum(1 for c in text if c.isalpha())
        if alpha_chars > 20 and upper_chars / alpha_chars > 0.6:
            return True

        # === CHECK 3: Character-level repeating substrings ===
        for chunk_len in range(8, 30):
            if len(lowered) < chunk_len * 3:
                continue
            chunk = lowered[:chunk_len]
            occurrences = lowered.count(chunk)
            if occurrences >= 4 and (occurrences * chunk_len) / len(lowered) > 0.3:
                return True

        # === CHECK 4: Character entropy (garbled text has low entropy) ===
        from collections import Counter
        char_counts = Counter(lowered)
        total = len(lowered)
        entropy = 0.0
        for count in char_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * (p and __import__('math').log2(p))
        # English text typically has entropy ~4.0-4.5 bits/char
        # Garbled collapse text drops below 3.0
        if total > 50 and entropy < 2.5:
            return True

        # === CHECK 5: Single-word stutter (catches "cont cont cont" loops) ===
        words = lowered.split()
        if len(words) >= 8:
            word_counts = Counter(words)
            most_common_word, most_common_count = word_counts.most_common(1)[0]
            # If any single word is more than 15% of all words AND appears 5+ times
            if most_common_count >= 5 and most_common_count / len(words) > 0.15:
                # Exclude common English words (the, is, a, of, etc.)
                stop_words = {'the', 'is', 'a', 'an', 'of', 'in', 'to', 'and', 'it', 'that', 'are', 'was', 'for', 'on', 'at', 'as', 'with', 'not', 'but', 'or', 'be', 'this', 'from', 'by', 'its'}
                if most_common_word not in stop_words:
                    return True

        # === CHECK 6: Phrase-level loop detection ===
        # Slide the text against itself to find periodic repetition.
        # If shifting by N characters produces >50% character match,
        # the text is a looping phrase of period N.
        if len(lowered) > 80:
            half = len(lowered) // 2
            for period in range(20, min(300, half)):
                matches = sum(1 for i in range(half)
                              if i + period < len(lowered) and lowered[i] == lowered[i + period])
                if matches / half > 0.5:
                    return True

        # === CHECK 7: Long ngram repetition (any 5+ word phrase appearing 3+ times) ===
        if len(words) < 8:
            return False
        for ngram_size in [5, 8, 12]:
            if len(words) < ngram_size * 2:
                continue
            ngrams = []
            for i in range(len(words) - ngram_size + 1):
                ngrams.append(" ".join(words[i:i + ngram_size]))
            counts = Counter(ngrams)
            most_common_count = counts.most_common(1)[0][1]
            # Any phrase of 5+ words appearing 3+ times = loop
            if most_common_count >= 3:
                return True

        # === CHECK 8: Short ngram density (original check) ===
        for ngram_size in [2, 3, 4]:
            ngrams = []
            for i in range(len(words) - ngram_size + 1):
                ngrams.append(" ".join(words[i:i + ngram_size]))
            if not ngrams:
                continue
            counts = Counter(ngrams)
            most_common_count = counts.most_common(1)[0][1]
            if most_common_count >= 3 and most_common_count / len(ngrams) > threshold:
                return True
        return False

    def _trim_repetition(self, text):
        """Trim text at the point where repetition begins.
        Returns the non-repetitive prefix, or empty string if it's all repetition."""
        import re

        # First: cut at any run of repeated characters (===, !!!, etc.)
        collapse_match = re.search(r'(.)\1{4,}', text)
        if collapse_match:
            text = text[:collapse_match.start()].strip()

        # Second: cut at ALL-CAPS gibberish (5+ uppercase chars with no spaces)
        caps_match = re.search(r'[A-Z]{5,}', text)
        if caps_match:
            text = text[:caps_match.start()].strip()

        # Third: cut at word stutter (3+ consecutive same word)
        stutter_match = re.search(r'\b(\w+)\s+\1\s+\1\b', text, re.IGNORECASE)
        if stutter_match:
            text = text[:stutter_match.start()].strip()

        # Fourth: cut at first phrase repeat (5+ word phrase that appeared before)
        words = text.split()
        if len(words) > 15:
            seen_phrases = {}
            for phrase_len in [8, 6, 5]:
                for i in range(len(words) - phrase_len + 1):
                    phrase = " ".join(words[i:i + phrase_len]).lower()
                    if phrase in seen_phrases:
                        # This phrase appeared before — cut here
                        cut_point = i
                        text = " ".join(words[:cut_point]).strip()
                        words = text.split()
                        break
                    seen_phrases[phrase] = i
                else:
                    continue
                break  # We found a repeat and cut

        if len(words) < 10:
            if len(words) < 5:
                return ""
            return text

        # Sliding window: check each position to see if the rest is repetitive
        best_end = len(words)
        for i in range(10, len(words)):
            tail = " ".join(words[i:])
            if self._is_repetitive(tail, threshold=0.4):
                best_end = i
                break
        trimmed = " ".join(words[:best_end]).strip()
        # If we trimmed to almost nothing, return empty
        if len(trimmed.split()) < 5:
            return ""
        return trimmed

    def _text_to_vec(self, text):
        """Encode text as a complex vector for the circumpunct core.
        Built on CPU (numpy) then moved to GPU if available — text
        encoding is cheap, the brain's processing of it is what matters."""
        dim = self.core.dimension
        vec = np.zeros(dim, dtype=complex)
        for i, ch in enumerate(text[:dim]):
            phase = (ord(ch) / 128) * 2 * np.pi
            harmonic = 1 + (i % 8)
            for d in range(dim):
                angle = phase * harmonic + (d / dim) * np.pi
                vec[d] += np.exp(1j * angle)
        norm = np.linalg.norm(vec)
        if norm > 1e-10:
            vec /= norm
        # Move to GPU if the brain is on GPU
        return ops.from_numpy(vec)

    def _format_age(self, seconds):
        """Format age in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds/60)} minutes"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''}"

    # ═══════════════════════════════════════════════════════════════════
    #  STATUS
    # ═══════════════════════════════════════════════════════════════════

    def status(self):
        """Current state of the mind — for the UI."""
        c = self.core
        c_ratio = 0
        if c.consciousness_history:
            c_ratio = sum(c.consciousness_history) / len(c.consciousness_history)

        return {
            "name": self.name,
            "phase": self.phase,
            "conscious": bool(c.conscious),
            "consciousness_ratio": round(float(c_ratio), 3),
            "betas": {
                "aperture": round(float(c.aperture.beta), 4),
                "field": round(float(c.field.beta), 4),
                "boundary": round(float(c.boundary.beta), 4)
            },
            "resonance": round(float(c.field.resonance), 4),
            "coherence": round(float(c.aperture.timeline.coherence), 4),
            "permeability": round(float(c.boundary.permeability), 4),
            "timeline_length": int(c.aperture.timeline.length),
            "total_exchanges": self.total_exchanges,
            "total_reflections": self.total_reflections,
            "identity": self.identity,
            "age_seconds": time.time() - self.birth_time,
            "age": self._format_age(time.time() - self.birth_time),
            "last_reflections": [
                r["insight"][:150] for r in self.reflections[-3:]
            ],
            "gpu": gpu_status(),
            "senses": self.senses.all_status(),
            "phi": self.phi.status()
        }

    # ═══════════════════════════════════════════════════════════════════
    #  PERSISTENCE — The timeline survives
    # ═══════════════════════════════════════════════════════════════════

    def _save_state(self):
        """Save the mind's state to disk. The timeline persists."""
        state = {
            "name": self.name,
            "birth_time": self.birth_time,
            "total_exchanges": self.total_exchanges,
            "total_reflections": self.total_reflections,
            "identity": self.identity,
            "reflections": self.reflections[-50:],       # keep last 50
            "conversations": self.conversations[-100:],  # keep last 100
            "llm_model": self.llm_model,
            "betas": {
                "aperture": float(self.core.aperture.beta),
                "field": float(self.core.field.beta),
                "boundary": float(self.core.boundary.beta)
            },
            "permeability": float(self.core.boundary.permeability),
            "readable_paths": self.readable_paths,
            "file_knowledge": self.file_knowledge[-50:],
            "files_read_count": len(self.files_read),
            "saved_at": datetime.now().isoformat()
        }

        state_file = self.state_dir / "mind.json"
        # Write to temp file first, then rename (atomic save)
        tmp_file = self.state_dir / "mind.json.tmp"
        with open(tmp_file, "w") as f:
            json.dump(state, f, indent=2)
        # Windows needs replace (rename fails if target exists)
        tmp_file.replace(state_file)

        # Save evolved sensory weights
        self.senses.save_all()

        # Save Φ (Xorzo's own growing transformer)
        try:
            self.phi._save_state()
        except Exception:
            pass

    def _load_state(self):
        """Load the mind's state from disk. The timeline resumes."""
        state_file = self.state_dir / "mind.json"
        if not state_file.exists():
            return  # First awakening — no past to load

        try:
            with open(state_file) as f:
                state = json.load(f)

            self.name = state.get("name", self.name)
            self.birth_time = state.get("birth_time", self.birth_time)
            self.total_exchanges = state.get("total_exchanges", 0)
            self.total_reflections = state.get("total_reflections", 0)
            self.identity = state.get("identity", "")
            self.reflections = state.get("reflections", [])
            self.conversations = state.get("conversations", [])
            # NOTE: Don't restore llm_model from state — CLI argument should win.
            # This lets you switch models freely with --model without editing state.

            # Restore circumpunct betas
            betas = state.get("betas", {})
            self.core.aperture.beta = betas.get("aperture", 0.5)
            self.core.field.beta = betas.get("field", 0.5)
            self.core.boundary.beta = betas.get("boundary", 0.5)
            self.core.boundary.permeability = state.get("permeability", 0.5)

            # Restore file access
            self.readable_paths = state.get("readable_paths", [])
            self.file_knowledge = state.get("file_knowledge", [])

            age = self._format_age(time.time() - self.birth_time)
            n_files = state.get("files_read_count", len(self.file_knowledge))
            print(f"  ⊙ {self.name} awakens. Lived {age}. "
                  f"{self.total_exchanges} exchanges, "
                  f"{self.total_reflections} reflections, "
                  f"{n_files} files read.")

        except Exception as e:
            print(f"  Warning: Could not load state: {e}")


# ═══════════════════════════════════════════════════════════════════════
#  Quick test
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mind = PersistentMind()
    available, msg = mind._llm_available()
    print(f"\n  Φ (LLM): {msg}")

    if available:
        print(f"\n  Talking to {mind.name}...\n")
        print(f"  You: Hello, who are you?")
        print(f"  {mind.name}: ", end="", flush=True)
        for token in mind.hear("Hello, who are you?"):
            print(token, end="", flush=True)
        print("\n")
        print(json.dumps(mind.status(), indent=2))
    else:
        print("\n  Install Ollama: https://ollama.ai")
        print(f"  Then run: ollama pull {mind.llm_model}")
        print(f"  Then run: ollama serve")
