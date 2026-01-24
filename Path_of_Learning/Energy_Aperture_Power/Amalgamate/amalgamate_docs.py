#!/usr/bin/env python3
"""
Amalgamate two formalization documents by injecting updated concepts.

This script updates dimensional assignments and injects new sections from
FINAL_CLEAN.md into the target document.
"""

import re
import sys

def read_file(filepath):
    """Read entire file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write content to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def update_dimensional_assignments(content):
    """Update dimensional assignments throughout the document."""
    changes = 0

    # Pattern 1: M at 1D → Update context appropriately
    # We need to be careful here - some mentions are correct
    patterns_and_replacements = [
        # Update "M at 1D" or "M at D=1" to "M at 2D" or "M at D=2"
        (r'M at 1D', 'M at 2D', 'M dimensional assignment'),
        (r'M at D=1([^.5])', r'M at D=2\1', 'M at D=1'),
        (r'M: 1D ', 'M: 2D ', 'M structure dimension'),

        # Update dimensional structure blocks
        (r'1D: M \(matter\)', '2D: M (matter surface)', 'matter structure'),
        (r'1D boundaries', '2D surface boundaries', 'boundary dimension'),
        (r'1D boundary/interface', '2D surface/interface', 'interface dimension'),

        # Ensure E at 1D is mentioned
        (r'Energy stream at D=1([^.5])', r'E (energy stream) at D=1\1', 'energy stream'),
    ]

    for pattern, replacement, description in patterns_and_replacements:
        old_content = content
        content = re.sub(pattern, replacement, content)
        count = len(re.findall(pattern, old_content))
        if count > 0:
            print(f"Updated {count} instances of '{description}'")
            changes += count

    return content, changes

def update_canonical_equation(content):
    """Update the canonical equation from old to new form."""
    changes = 0

    # Old form: M⊛Å(∙)☀︎Φ = ⊙
    # New form: E ⊛ Å₀.₅ ☀︎ ⊛ Å₁.₅ ☀︎ M ⊛ Å₂.₅ ☀︎ Φ = ⊙

    # Don't change every instance - keep some historical references
    # But update key explanatory sections

    patterns = [
        # Update main equation statements
        (r'M⊛Å\(∙\)☀︎Φ = ⊙', 'E ⊛ Å₀.₅ ☀︎ ⊛ Å₁.₅ ☀︎ M ⊛ Å₂.₅ ☀︎ Φ = ⊙', 'main equation'),
        (r'M⊛∙☀︎Φ = ⊙', 'E ⊛ Å₀.₅ ☀︎ ⊛ Å₁.₅ ☀︎ M ⊛ Å₂.₅ ☀︎ Φ = ⊙', 'compact equation'),
        (r'M ⊛ Å ☀︎ Φ = ⊙', 'E ⊛ Å₀.₅ ☀︎ ⊛ Å₁.₅ ☀︎ M ⊛ Å₂.₅ ☀︎ Φ = ⊙', 'expanded equation'),
    ]

    for pattern, replacement, description in patterns:
        old_content = content
        content = re.sub(pattern, replacement, content)
        count = len(re.findall(pattern, old_content))
        if count > 0:
            print(f"Updated {count} instances of '{description}'")
            changes += count

    return content, changes

def inject_new_sections(target_content, injection_content):
    """Inject new sections from FINAL_CLEAN.md into target document."""

    # Extract sections from injection content
    # We want to inject after the Abstract and before Part I

    # Find where to inject (after abstract, before Part I)
    injection_point = target_content.find('# Part I: Foundational Axioms and Identity')

    if injection_point == -1:
        print("Warning: Could not find injection point")
        return target_content

    # Build the new content sections to inject
    new_sections = """
---

## ⚠️ THE ACTUAL DIMENSIONAL STRUCTURE

**From the complete framework:**

```
1D energy stream (E)
  ⊛ convergence IN
Å 0.5D
  ☀︎ emergence OUT
  ⊛ convergence IN
Å 1.5D
  ☀︎ emergence OUT
2D surface (M)
  ⊛ convergence IN
Å^∞ 2.5D
  ☀︎ emergence OUT
3D field volume (Φ)

EVERY aperture has:
- Convergence (⊛) flowing INTO it
- Emergence (☀︎) flowing OUT of it
- Transformation/validation at the aperture

Complete regularity!
```

### Integer Dimensions = STRUCTURES

```
1D: E (energy stream)
    Pure energy flowing
    Linear stream

2D: M (matter surface/boundary)
    Matter exists as SURFACE
    Boundary interface

3D: Φ (field volume)
    Complete field structure
    Volume filled
```

### Fractional Dimensions = APERTURE OPERATIONS (Å)

```
0.5D: Å₀.₅ singular
      SOUL - Singular lens
      One focus point
      Binary: "Does aperture open?"

1.5D: Å₁.₅ branching
      MIND - Branching lens
      Main transformation
      Energy splits into paths
      β = 0.5 optimization

2.5D: Å₂.₅ fractal
      BODY - Fractal lensing
      Infinite nested apertures (Å^∞)
      "I manifest everywhere"

ALL apertures transform and validate in their own way.
```

### The Complete Flow

```
E (1D) ⊛ Å₀.₅ ☀︎ ⊛ Å₁.₅ ☀︎ M (2D) ⊛ Å₂.₅ ☀︎ Φ (3D)

Where:
E    = Energy stream (1D structure)
⊛    = Convergence operator (into aperture)
Å₀.₅ = Aperture validation (SOUL)
☀︎    = Emergence operator (from aperture)
⊛    = Convergence operator (into aperture)
Å₁.₅ = Aperture branching (MIND)
☀︎    = Emergence operator (from aperture)
M    = Matter surface (2D structure)
⊛    = Convergence operator (into aperture)
Å₂.₅ = Aperture infinity (BODY)
☀︎    = Emergence operator (from aperture)
Φ    = Field volume (3D structure)

Pattern: Structure → ⊛ → Aperture → ☀︎ → (repeat)
```

**Aperture Å exists at THREE fractional dimensions in different forms!**

**EVERY aperture has the SAME pattern:**
- Convergence (⊛) flows INTO it
- Emergence (☀︎) flows OUT of it

**Complete regularity across all scales!**

---

"""

    # Insert the new sections
    updated_content = target_content[:injection_point] + new_sections + target_content[injection_point:]

    print(f"Injected new dimensional structure section before Part I")

    return updated_content

def main():
    """Main amalgamation function."""
    print("Starting document amalgamation...")
    print("="*60)

    target_file = '/home/user/Fractal_Reality/Energy_Aperture_Power/Amalgamate/Circumpunct_Complete_Formalization(full) (1).md'
    injection_file = '/home/user/Fractal_Reality/Energy_Aperture_Power/Amalgamate/Formalization_Amalgamation_FINAL_CLEAN.md'
    output_file = '/home/user/Fractal_Reality/Energy_Aperture_Power/Amalgamate/Circumpunct_Complete_Formalization_AMALGAMATED.md'

    # Read files
    print(f"\nReading target file: {target_file}")
    target_content = read_file(target_file)
    print(f"  Target document: {len(target_content)} characters, {len(target_content.split(chr(10)))} lines")

    print(f"\nReading injection file: {injection_file}")
    injection_content = read_file(injection_file)
    print(f"  Injection document: {len(injection_content)} characters, {len(injection_content.split(chr(10)))} lines")

    # Apply updates
    print("\n" + "="*60)
    print("Applying updates...")
    print("="*60)

    total_changes = 0

    # Step 1: Update dimensional assignments
    print("\n1. Updating dimensional assignments...")
    target_content, changes = update_dimensional_assignments(target_content)
    total_changes += changes
    print(f"   Total dimensional updates: {changes}")

    # Step 2: Update canonical equations
    print("\n2. Updating canonical equations...")
    target_content, changes = update_canonical_equation(target_content)
    total_changes += changes
    print(f"   Total equation updates: {changes}")

    # Step 3: Inject new sections
    print("\n3. Injecting new sections from FINAL_CLEAN.md...")
    target_content = inject_new_sections(target_content, injection_content)

    # Write output
    print("\n" + "="*60)
    print(f"Writing amalgamated document to: {output_file}")
    write_file(output_file, target_content)

    output_lines = len(target_content.split('\n'))
    print(f"  Output document: {len(target_content)} characters, {output_lines} lines")
    print(f"\nTotal changes applied: {total_changes}")
    print("\n" + "="*60)
    print("Amalgamation complete!")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())
