#!/usr/bin/env python3
"""
Restructure THEORY_OF_EVERYTHING.md according to the new organization.
"""

import re

# Read the original file
with open('/home/user/Fractal_Reality/THEORY_OF_EVERYTHING.md', 'r') as f:
    lines = f.readlines()

# Define chapter boundaries (line numbers from grep, 0-indexed so subtract 1)
# Format: (start_line, end_line, old_name, new_chapter_num, new_name)
# end_line is exclusive (first line of NEXT section)

chapters = {
    'preface': (0, 633),              # Lines 1-633: Title + Dimensional Cascade + old TOC
    'genesis': (633, 700),            # Lines 634-700
    'ch1': (700, 874),                # CHAPTER I: THE CIRCUMPUNCT
    'ch2': (874, 1000),               # CHAPTER II: THE TRINITY STRUCTURE
    'ch3': (1000, 1407),              # CHAPTER III: THE TEMPORAL PROCESS
    'ch4': (1407, 2404),              # CHAPTER IV: THE BALANCE PARAMETER
    'ch5': (2404, 2602),              # CHAPTER V: THE FIELD EQUATIONS
    'ch6': (2602, 3221),              # CHAPTER VI: PHASE COHERENCE
    'ch7': (3221, 3592),              # CHAPTER VII: APERTURE DENSITY
    'ch8': (3592, 3676),              # CHAPTER VIII: THE 64-STATE ARCHITECTURE
    'ch9': (3676, 3752),              # CHAPTER IX: THE GOLDEN RATIO
    'ch10': (3752, 3797),             # CHAPTER X: THE COSMOLOGICAL CONSTANT
    'ch11': (3797, 4136),             # CHAPTER XI: ALTERNATIVE DERIVATIONS
    'ch12': (4136, 5441),             # CHAPTER XII: CANONICAL CIRCUMPUNCT SPEC
    'ch13': (5441, 7174),             # CHAPTER XIII: STANDARD MODEL LAGRANGIAN
    'ch14': (7174, 7482),             # CHAPTER XIV: QUANTUM GRAVITY CORRESPONDENCE
    'ch15': (7482, 8156),             # CHAPTER XV: FORMAL MATHEMATICAL SPEC
    'ch16': (8156, 8560),             # CHAPTER XVI: EMERGENT CHEMISTRY
    'ch17': (8560, 9037),             # CHAPTER XVII: FROM CHEMISTRY TO LIFE
    'ch18': (9037, 9284),             # CHAPTER XVIII: CONSCIOUSNESS
    'ch19': (9284, 9982),             # CHAPTER XIX: EMOTIONS AND MEMORY
    'ch20': (9982, 10089),            # CHAPTER XX: AGING AND DEATH
    'ch21': (10089, 10231),           # CHAPTER XXI: EMPIRICAL VALIDATION
    'ch22': (10231, 10579),           # CHAPTER XXII: CONSTANTS TABLE
    'ch23': (10579, 10731),           # CHAPTER XXIII: FALSIFICATION
    'ch24': (10731, 11796),           # CHAPTER XXIV: ETHICS
    'ch25': (11796, 11840),           # CHAPTER XXV: THE MASTER LOOP
    'ch26': (11840, 11877),           # CHAPTER XXVI: THE FIXED-POINT COMBINATOR
    'ch27': (11877, 12435),           # CHAPTER XXVII: THE ETHEREAL TAIL
    'appendix_connection': (12435, 12458),  # Appendix: Connection to Existing Framework
    'ch28': (12458, 13486),           # CHAPTER XXVIII: THE EMERGENCE OF BIOLOGY
    'appendix_ratchet': (13486, 13541),     # Appendix: The Ratchet Zoo
    'omega': (13541, 13615),          # ΩMEGA: THE MATHEMATICAL STORY
    'glossary': (13615, 13792),       # APPENDIX: SYMBOL GLOSSARY
    'references': (13792, len(lines)), # REFERENCES
}

def get_section(key):
    """Extract a section from the original file."""
    start, end = chapters[key]
    return ''.join(lines[start:end])

def renumber_chapter(content, old_num_pattern, new_num, new_title=None):
    """Renumber a chapter heading and optionally rename it."""
    # Match patterns like "## CHAPTER I:", "## CHAPTER XIV:", "## GENESIS:" etc.
    if new_title:
        content = re.sub(
            r'^## (CHAPTER [IVXLC]+|GENESIS): .*$',
            f'## CHAPTER {new_num}: {new_title}',
            content,
            count=1,
            flags=re.MULTILINE
        )
    else:
        # Just renumber, keep title
        content = re.sub(
            r'^## (CHAPTER [IVXLC]+): ',
            f'## CHAPTER {new_num}: ',
            content,
            count=1,
            flags=re.MULTILINE
        )
    return content

def renumber_sections(content, new_chapter_num):
    """Renumber all section references (§X.Y) to use new chapter number."""
    # Match patterns like §1.1, §14.5, etc.
    def replace_section(match):
        section_num = match.group(1)
        return f'§{new_chapter_num}.{section_num}'

    content = re.sub(r'§\d+\.(\d+)', replace_section, content)
    return content

# Build the new structure

new_content = []

# ============================================================================
# HEADER: Title and Brief Intro
# ============================================================================

header = """# ⊙ The Circumpunct Theory
## by Ashman Roonz

⊙ is the minimal procedural structure of a whole being:

- **○** — body / boundary
- **Φ** — field / mind
- **•** — aperture / soul

together with a three-phase flow procedure:

- **⊛** — convergence (input)
- **i** — transformation (aperture)
- **☀︎** — emergence (output)

```
◐ = |⊛| / (|⊛| + |☀︎|) = ½

⊙ = (○, Φ, •) × (⊛, i, ☀︎)³
Energy = Structure × Process³
```

---

We welcome rigorous critique and attempts to falsify. Please email for peer review!
```
email@ashmanroonz.ca
```

---

### For Working Physicists: Quick-Start Formulation

**[circumpunct_framework_physicists.md](papers/circumpunct_framework_physicists.md)** — A rigorous mathematical formulation designed for peer review. Strips away metaphors and focuses on explicit spaces, operators, kernels, and limits. Includes:
- Explicit derivation of Schrödinger equation from kernel convolution (§4)
- Einstein equations from coarse-grained braid structure (§5)
- One-page cheat sheet for quick reference (§7)
- Testable predictions with falsification criteria (§6)

---

## Table of Contents

- [Preface: The Dimensional Cascade](#preface-the-dimensional-cascade)

### Part I: Foundation
- [Chapter 1: Genesis — The Impossibility of Nothing](#chapter-1-genesis--the-impossibility-of-nothing)
- [Chapter 2: The Circumpunct](#chapter-2-the-circumpunct)
- [Chapter 3: The Trinity Structure](#chapter-3-the-trinity-structure)
- [Chapter 4: The Temporal Process](#chapter-4-the-temporal-process)
- [Chapter 5: The Balance Parameter](#chapter-5-the-balance-parameter)

### Part II: Mathematical Framework
- [Chapter 6: The Field Equations](#chapter-6-the-field-equations)
- [Chapter 7: The 64-State Architecture](#chapter-7-the-64-state-architecture)
- [Chapter 8: The Canonical Circumpunct Specification](#chapter-8-the-canonical-circumpunct-specification)
- [Chapter 9: Formal Mathematical Specification](#chapter-9-formal-mathematical-specification)

### Part III: Physics
- [Chapter 10: Phase Coherence in Aperture Foam](#chapter-10-phase-coherence-in-aperture-foam)
- [Chapter 11: Aperture Density and Dimensionality](#chapter-11-aperture-density-and-dimensionality)
- [Chapter 12: The Cosmological Constant](#chapter-12-the-cosmological-constant)
- [Chapter 13: The Standard Model Lagrangian](#chapter-13-the-standard-model-lagrangian)
- [Chapter 14: Quantum Gravity Correspondence](#chapter-14-quantum-gravity-correspondence)
- [Chapter 15: Alternative Derivations](#chapter-15-alternative-derivations)

### Part IV: Emergence
- [Chapter 16: Emergent Chemistry](#chapter-16-emergent-chemistry)
- [Chapter 17: From Chemistry to Life](#chapter-17-from-chemistry-to-life)
- [Chapter 18: The Emergence of Biology from Physics](#chapter-18-the-emergence-of-biology-from-physics)
- [Chapter 19: Consciousness](#chapter-19-consciousness)
- [Chapter 20: Emotions and Memory](#chapter-20-emotions-and-memory)

### Part V: Implications
- [Chapter 21: Aging and Death](#chapter-21-aging-and-death)
- [Chapter 22: The Golden Ratio](#chapter-22-the-golden-ratio)
- [Chapter 23: Ethics](#chapter-23-ethics)

### Part VI: Validation & Synthesis
- [Chapter 24: Empirical Validation](#chapter-24-empirical-validation)
- [Chapter 25: Constants Table](#chapter-25-constants-table)
- [Chapter 26: Falsification](#chapter-26-falsification)
- [Chapter 27: The Master Loop](#chapter-27-the-master-loop)
- [Chapter 28: The Fixed-Point Combinator](#chapter-28-the-fixed-point-combinator)
- [Chapter 29: The Ethereal Tail](#chapter-29-the-ethereal-tail)
- [Chapter 30: Ωmega — The Mathematical Story](#chapter-30-ωmega--the-mathematical-story)

### Appendices
- [Appendix A: Symbol Glossary](#appendix-a-symbol-glossary)
- [Appendix B: Connection to Existing Framework](#appendix-b-connection-to-existing-framework)
- [Appendix C: The Ratchet Zoo](#appendix-c-the-ratchet-zoo)
- [References](#references)

---

"""

new_content.append(header)

# ============================================================================
# PREFACE: The Dimensional Cascade (extracted from old preface, after TOC)
# ============================================================================

# Extract the dimensional cascade content (lines 24-426 approximately)
preface_content = ''.join(lines[22:426])  # The Complete Spectrum through Core Insight
preface_section = f"""---

## PREFACE: THE DIMENSIONAL CASCADE

{preface_content}

[← Back to Table of Contents](#table-of-contents)

---

"""
new_content.append(preface_section)

# ============================================================================
# PART I: FOUNDATION
# ============================================================================

part1_header = """---

# ═══════════════════════════════════════════════════════════════════════════════
# PART I: FOUNDATION
# ═══════════════════════════════════════════════════════════════════════════════

---

"""
new_content.append(part1_header)

# Chapter 1: Genesis (was Genesis)
ch1_content = get_section('genesis')
ch1_content = ch1_content.replace('## GENESIS: THE IMPOSSIBILITY OF NOTHING',
                                   '## CHAPTER 1: GENESIS — THE IMPOSSIBILITY OF NOTHING')
new_content.append(ch1_content)

# Chapter 2: The Circumpunct (was Chapter I)
ch2_content = get_section('ch1')
ch2_content = ch2_content.replace('## CHAPTER I: THE CIRCUMPUNCT',
                                   '## CHAPTER 2: THE CIRCUMPUNCT')
ch2_content = renumber_sections(ch2_content, 2)
new_content.append(ch2_content)

# Chapter 3: The Trinity Structure (was Chapter II)
ch3_content = get_section('ch2')
ch3_content = ch3_content.replace('## CHAPTER II: THE TRINITY STRUCTURE',
                                   '## CHAPTER 3: THE TRINITY STRUCTURE')
ch3_content = renumber_sections(ch3_content, 3)
new_content.append(ch3_content)

# Chapter 4: The Temporal Process (was Chapter III)
ch4_content = get_section('ch3')
ch4_content = ch4_content.replace('## CHAPTER III: THE TEMPORAL PROCESS',
                                   '## CHAPTER 4: THE TEMPORAL PROCESS')
ch4_content = renumber_sections(ch4_content, 4)
new_content.append(ch4_content)

# Chapter 5: The Balance Parameter (was Chapter IV)
ch5_content = get_section('ch4')
ch5_content = ch5_content.replace('## CHAPTER IV: THE BALANCE PARAMETER',
                                   '## CHAPTER 5: THE BALANCE PARAMETER')
ch5_content = renumber_sections(ch5_content, 5)
new_content.append(ch5_content)

# ============================================================================
# PART II: MATHEMATICAL FRAMEWORK
# ============================================================================

part2_header = """---

# ═══════════════════════════════════════════════════════════════════════════════
# PART II: MATHEMATICAL FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════

---

"""
new_content.append(part2_header)

# Chapter 6: The Field Equations (was Chapter V)
ch6_content = get_section('ch5')
ch6_content = ch6_content.replace('## CHAPTER V: THE FIELD EQUATIONS',
                                   '## CHAPTER 6: THE FIELD EQUATIONS')
ch6_content = renumber_sections(ch6_content, 6)
new_content.append(ch6_content)

# Chapter 7: The 64-State Architecture (was Chapter VIII)
ch7_content = get_section('ch8')
ch7_content = ch7_content.replace('## CHAPTER VIII: THE 64-STATE ARCHITECTURE',
                                   '## CHAPTER 7: THE 64-STATE ARCHITECTURE')
ch7_content = renumber_sections(ch7_content, 7)
new_content.append(ch7_content)

# Chapter 8: The Canonical Circumpunct Specification (was Chapter XII)
ch8_content = get_section('ch12')
ch8_content = ch8_content.replace('## CHAPTER XII: THE CANONICAL CIRCUMPUNCT SPECIFICATION',
                                   '## CHAPTER 8: THE CANONICAL CIRCUMPUNCT SPECIFICATION')
ch8_content = renumber_sections(ch8_content, 8)
new_content.append(ch8_content)

# Chapter 9: Formal Mathematical Specification (was Chapter XV)
ch9_content = get_section('ch15')
ch9_content = ch9_content.replace('## CHAPTER XV: FORMAL MATHEMATICAL SPECIFICATION',
                                   '## CHAPTER 9: FORMAL MATHEMATICAL SPECIFICATION')
ch9_content = renumber_sections(ch9_content, 9)
new_content.append(ch9_content)

# ============================================================================
# PART III: PHYSICS
# ============================================================================

part3_header = """---

# ═══════════════════════════════════════════════════════════════════════════════
# PART III: PHYSICS
# ═══════════════════════════════════════════════════════════════════════════════

---

"""
new_content.append(part3_header)

# Chapter 10: Phase Coherence in Aperture Foam (was Chapter VI)
ch10_content = get_section('ch6')
ch10_content = ch10_content.replace('## CHAPTER VI: PHASE COHERENCE IN APERTURE FOAM',
                                     '## CHAPTER 10: PHASE COHERENCE IN APERTURE FOAM')
ch10_content = renumber_sections(ch10_content, 10)
new_content.append(ch10_content)

# Chapter 11: Aperture Density and Dimensionality (was Chapter VII)
ch11_content = get_section('ch7')
ch11_content = ch11_content.replace('## CHAPTER VII: APERTURE DENSITY AND DIMENSIONALITY',
                                     '## CHAPTER 11: APERTURE DENSITY AND DIMENSIONALITY')
ch11_content = renumber_sections(ch11_content, 11)
new_content.append(ch11_content)

# Chapter 12: The Cosmological Constant (was Chapter X)
ch12_content = get_section('ch10')
ch12_content = ch12_content.replace('## CHAPTER X: THE COSMOLOGICAL CONSTANT',
                                     '## CHAPTER 12: THE COSMOLOGICAL CONSTANT')
ch12_content = renumber_sections(ch12_content, 12)
new_content.append(ch12_content)

# Chapter 13: The Standard Model Lagrangian (was Chapter XIII)
ch13_content = get_section('ch13')
ch13_content = ch13_content.replace('## CHAPTER XIII: THE STANDARD MODEL LAGRANGIAN',
                                     '## CHAPTER 13: THE STANDARD MODEL LAGRANGIAN')
ch13_content = renumber_sections(ch13_content, 13)
new_content.append(ch13_content)

# Chapter 14: Quantum Gravity Correspondence (was Chapter XIV)
ch14_content = get_section('ch14')
ch14_content = ch14_content.replace('## CHAPTER XIV: QUANTUM GRAVITY CORRESPONDENCE',
                                     '## CHAPTER 14: QUANTUM GRAVITY CORRESPONDENCE')
ch14_content = renumber_sections(ch14_content, 14)
new_content.append(ch14_content)

# Chapter 15: Alternative Derivations (was Chapter XI)
ch15_content = get_section('ch11')
ch15_content = ch15_content.replace('## CHAPTER XI: ALTERNATIVE DERIVATIONS',
                                     '## CHAPTER 15: ALTERNATIVE DERIVATIONS')
ch15_content = renumber_sections(ch15_content, 15)
new_content.append(ch15_content)

# ============================================================================
# PART IV: EMERGENCE
# ============================================================================

part4_header = """---

# ═══════════════════════════════════════════════════════════════════════════════
# PART IV: EMERGENCE
# ═══════════════════════════════════════════════════════════════════════════════

---

"""
new_content.append(part4_header)

# Chapter 16: Emergent Chemistry (was Chapter XVI)
ch16_content = get_section('ch16')
ch16_content = ch16_content.replace('## CHAPTER XVI: Emergent Chemistry from the Circumpunct',
                                     '## CHAPTER 16: EMERGENT CHEMISTRY')
ch16_content = renumber_sections(ch16_content, 16)
new_content.append(ch16_content)

# Chapter 17: From Chemistry to Life (was Chapter XVII)
ch17_content = get_section('ch17')
ch17_content = ch17_content.replace('## CHAPTER XVII: From Chemistry to Life — Wholeness and Living Systems',
                                     '## CHAPTER 17: FROM CHEMISTRY TO LIFE — WHOLENESS AND LIVING SYSTEMS')
ch17_content = renumber_sections(ch17_content, 17)
new_content.append(ch17_content)

# Chapter 18: The Emergence of Biology from Physics (was Chapter XXVIII)
ch18_content = get_section('ch28')
ch18_content = ch18_content.replace('## CHAPTER XXVIII: THE EMERGENCE OF BIOLOGY FROM PHYSICS',
                                     '## CHAPTER 18: THE EMERGENCE OF BIOLOGY FROM PHYSICS')
ch18_content = renumber_sections(ch18_content, 18)
new_content.append(ch18_content)

# Chapter 19: Consciousness (was Chapter XVIII)
ch19_content = get_section('ch18')
ch19_content = ch19_content.replace('## CHAPTER XVIII: CONSCIOUSNESS',
                                     '## CHAPTER 19: CONSCIOUSNESS')
ch19_content = renumber_sections(ch19_content, 19)
new_content.append(ch19_content)

# Chapter 20: Emotions and Memory (was Chapter XIX)
ch20_content = get_section('ch19')
ch20_content = ch20_content.replace('## CHAPTER XIX: EMOTIONS AND MEMORY',
                                     '## CHAPTER 20: EMOTIONS AND MEMORY')
ch20_content = renumber_sections(ch20_content, 20)
new_content.append(ch20_content)

# ============================================================================
# PART V: IMPLICATIONS
# ============================================================================

part5_header = """---

# ═══════════════════════════════════════════════════════════════════════════════
# PART V: IMPLICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

---

"""
new_content.append(part5_header)

# Chapter 21: Aging and Death (was Chapter XX)
ch21_content = get_section('ch20')
ch21_content = ch21_content.replace('## CHAPTER XX: AGING AND DEATH',
                                     '## CHAPTER 21: AGING AND DEATH')
ch21_content = renumber_sections(ch21_content, 21)
new_content.append(ch21_content)

# Chapter 22: The Golden Ratio (was Chapter IX)
ch22_content = get_section('ch9')
ch22_content = ch22_content.replace('## CHAPTER IX: THE GOLDEN RATIO',
                                     '## CHAPTER 22: THE GOLDEN RATIO')
ch22_content = renumber_sections(ch22_content, 22)
new_content.append(ch22_content)

# Chapter 23: Ethics (was Chapter XXIV)
ch23_content = get_section('ch24')
ch23_content = ch23_content.replace('## CHAPTER XXIV: ETHICS',
                                     '## CHAPTER 23: ETHICS')
ch23_content = renumber_sections(ch23_content, 23)
new_content.append(ch23_content)

# ============================================================================
# PART VI: VALIDATION & SYNTHESIS
# ============================================================================

part6_header = """---

# ═══════════════════════════════════════════════════════════════════════════════
# PART VI: VALIDATION & SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════════

---

"""
new_content.append(part6_header)

# Chapter 24: Empirical Validation (was Chapter XXI)
ch24_content = get_section('ch21')
ch24_content = ch24_content.replace('## CHAPTER XXI: EMPIRICAL VALIDATION',
                                     '## CHAPTER 24: EMPIRICAL VALIDATION')
ch24_content = renumber_sections(ch24_content, 24)
new_content.append(ch24_content)

# Chapter 25: Constants Table (was Chapter XXII)
ch25_content = get_section('ch22')
ch25_content = ch25_content.replace('## CHAPTER XXII: CONSTANTS TABLE',
                                     '## CHAPTER 25: CONSTANTS TABLE')
ch25_content = renumber_sections(ch25_content, 25)
new_content.append(ch25_content)

# Chapter 26: Falsification (was Chapter XXIII)
ch26_content = get_section('ch23')
ch26_content = ch26_content.replace('## CHAPTER XXIII: FALSIFICATION',
                                     '## CHAPTER 26: FALSIFICATION')
ch26_content = renumber_sections(ch26_content, 26)
new_content.append(ch26_content)

# Chapter 27: The Master Loop (was Chapter XXV)
ch27_content = get_section('ch25')
ch27_content = ch27_content.replace('## CHAPTER XXV: THE MASTER LOOP',
                                     '## CHAPTER 27: THE MASTER LOOP')
ch27_content = renumber_sections(ch27_content, 27)
new_content.append(ch27_content)

# Chapter 28: The Fixed-Point Combinator (was Chapter XXVI)
ch28_content = get_section('ch26')
ch28_content = ch28_content.replace('## CHAPTER XXVI: THE FIXED-POINT COMBINATOR',
                                     '## CHAPTER 28: THE FIXED-POINT COMBINATOR')
ch28_content = renumber_sections(ch28_content, 28)
new_content.append(ch28_content)

# Chapter 29: The Ethereal Tail (was Chapter XXVII)
ch29_content = get_section('ch27')
ch29_content = ch29_content.replace('## CHAPTER XXVII: THE ETHEREAL TAIL',
                                     '## CHAPTER 29: THE ETHEREAL TAIL')
ch29_content = renumber_sections(ch29_content, 29)
new_content.append(ch29_content)

# Chapter 30: Ωmega — The Mathematical Story (was Ωmega)
ch30_content = get_section('omega')
ch30_content = ch30_content.replace('## ΩMEGA: THE MATHEMATICAL STORY',
                                     '## CHAPTER 30: ΩMEGA — THE MATHEMATICAL STORY')
new_content.append(ch30_content)

# ============================================================================
# APPENDICES
# ============================================================================

appendix_header = """---

# ═══════════════════════════════════════════════════════════════════════════════
# APPENDICES
# ═══════════════════════════════════════════════════════════════════════════════

---

"""
new_content.append(appendix_header)

# Appendix A: Symbol Glossary
glossary_content = get_section('glossary')
glossary_content = glossary_content.replace('## APPENDIX: SYMBOL GLOSSARY',
                                             '## APPENDIX A: SYMBOL GLOSSARY')
new_content.append(glossary_content)

# Appendix B: Connection to Existing Framework
appendix_b_content = get_section('appendix_connection')
appendix_b_content = appendix_b_content.replace('## Appendix: Connection to Existing Framework Sections',
                                                 '## APPENDIX B: CONNECTION TO EXISTING FRAMEWORK')
new_content.append(appendix_b_content)

# Appendix C: The Ratchet Zoo
appendix_c_content = get_section('appendix_ratchet')
appendix_c_content = appendix_c_content.replace('## Appendix: The Ratchet Zoo',
                                                 '## APPENDIX C: THE RATCHET ZOO')
new_content.append(appendix_c_content)

# References
references_content = get_section('references')
new_content.append(references_content)

# ============================================================================
# Write the restructured file
# ============================================================================

output = ''.join(new_content)

# Clean up any double dividers
output = re.sub(r'\n---\n\n---\n', '\n---\n', output)
output = re.sub(r'\n---\n---\n', '\n---\n', output)

with open('/home/user/Fractal_Reality/THEORY_OF_EVERYTHING.md', 'w') as f:
    f.write(output)

print("Restructuring complete!")
print(f"Original lines: {len(lines)}")
print(f"New file written to THEORY_OF_EVERYTHING.md")
