#!/usr/bin/env python3
"""
Fix LaTeX math formatting in Markdown files.
Adds blank lines before display math blocks ($$) where missing.
"""

import sys
import re

def fix_math_formatting(input_file, output_file=None):
    """
    Fix missing blank lines before display math blocks.

    Args:
        input_file: Path to input markdown file
        output_file: Path to output file (if None, overwrites input)
    """
    if output_file is None:
        output_file = input_file

    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0
    fixes_count = 0

    while i < len(lines):
        current_line = lines[i]

        # Check if next line starts with $$ (display math block)
        if i + 1 < len(lines):
            next_line = lines[i + 1]

            # If current line is not blank and next line starts with $$
            if (current_line.strip() != '' and
                next_line.strip().startswith('$$') and
                not current_line.strip().startswith('$$')):

                # Add the current line
                fixed_lines.append(current_line)
                # Add a blank line
                fixed_lines.append('\n')
                fixes_count += 1
                i += 1
                continue

        # Otherwise, just add the current line as-is
        fixed_lines.append(current_line)
        i += 1

    # Write the fixed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    print(f"Fixed {fixes_count} missing blank lines before display math blocks")
    return fixes_count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix_math_formatting.py <markdown_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fixes_count = fix_math_formatting(input_file, output_file)

    if fixes_count > 0:
        print(f"✓ Successfully fixed {fixes_count} formatting errors")
    else:
        print("✓ No formatting errors found")
