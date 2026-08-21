#!/usr/bin/env python3
"""Harvest explicit theorem-like statements from the live repository.

Created: 2026-08-20
Last updated: 2026-08-20
Version: 1.2

Revision history:
- 2026-08-20 v1.2: normalize dash punctuation in generated titles to the
  repository's prose convention.
- 2026-08-20 v1.1: exclude generated theorem atlases so the index does not
  recursively inflate its own source count.
- 2026-08-20 v1.0: initial live-corpus harvester with status-signal capture.

This script is deliberately lexical. It finds candidate statements for human
adjudication; it does not decide whether a statement is proved, novel, current,
or physically instantiated.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
from dataclasses import dataclass
from pathlib import Path


KINDS = (
    "theorem",
    "lemma",
    "proposition",
    "corollary",
    "conjecture",
    "axiom",
    "identity",
    "derivation",
)

KIND_RE = "|".join(KINDS)
MARKDOWN_HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
BOLD_LABEL_RE = re.compile(
    rf"\*\*((?:{KIND_RE})\b[^*]*)\*\*", re.IGNORECASE
)
PLAIN_LABEL_RE = re.compile(
    rf"^\s*((?:{KIND_RE})(?:\s+[A-Za-z0-9.()_-]+)?(?:\s*[:.;-]|\s+).+)$",
    re.IGNORECASE,
)
HTML_HEADING_RE = re.compile(r"<h[1-6][^>]*>(.*?)</h[1-6]>", re.IGNORECASE)
HTML_STRONG_RE = re.compile(r"<strong[^>]*>(.*?)</strong>", re.IGNORECASE)
HTML_LABEL_RE = re.compile(
    r'<(?:div|span)[^>]*class="[^"]*(?:label|title)[^"]*"[^>]*>'
    r"(.*?)</(?:div|span)>",
    re.IGNORECASE,
)
TAG_RE = re.compile(r"<[^>]+>")
KIND_FINDER_RE = re.compile(rf"\b({KIND_RE})\b", re.IGNORECASE)

STATUS_TERMS = {
    "retracted": re.compile(r"\bretract(?:ed|ion)?\b", re.IGNORECASE),
    "superseded": re.compile(r"\bsupersed(?:ed|es|ing)\b", re.IGNORECASE),
    "conditional": re.compile(r"\bconditional(?:ly)?\b", re.IGNORECASE),
    "conjectural": re.compile(r"\bconjectur(?:e|al)\b", re.IGNORECASE),
    "open": re.compile(r"\bopen (?:question|problem|decision|issue)\b", re.IGNORECASE),
    "to-prove": re.compile(r"\bto be prov(?:ed|en)|proof missing\b", re.IGNORECASE),
    "proof-sketch": re.compile(r"\bproof sketch\b", re.IGNORECASE),
    "qed": re.compile(r"\bQED\b|∎", re.IGNORECASE),
    "standard": re.compile(r"\bstandard (?:mathematics|result|theorem|proof|theory)\b", re.IGNORECASE),
    "computed": re.compile(r"\bcomput(?:ed|ation|ational|ationally)\b", re.IGNORECASE),
    "verified": re.compile(r"\bverif(?:ied|ication)\b", re.IGNORECASE),
    "grade-a": re.compile(r"\bgrade A\b", re.IGNORECASE),
    "grade-b": re.compile(r"\bgrade B\+?\b", re.IGNORECASE),
    "grade-c": re.compile(r"\bgrade C\+?\b", re.IGNORECASE),
}

EXCLUDED_PARTS = {
    ".git",
    "Path_of_Learning",
    "node_modules",
    "vendor",
    "dist",
    "build",
}

ALLOWED_SUFFIXES = {".md", ".html", ".tex"}
EXCLUDED_FILE_PREFIXES = ("theorem_atlas_",)


@dataclass(frozen=True)
class Candidate:
    path: str
    line: int
    kind: str
    title: str
    status_signals: str
    duplicate_key: str


def clean_text(value: str) -> str:
    value = html.unescape(TAG_RE.sub(" ", value))
    value = re.sub(r"[`*_]+", "", value)
    value = value.replace("\u2014", " - ").replace("\u2013", " - ")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" #:-\t")


def normalized_key(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"\b(theorem|lemma|proposition|corollary|conjecture|axiom|identity|derivation)\b", "", value)
    value = re.sub(r"\b[0-9]+(?:\.[0-9]+)*\b", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def status_signals(lines: list[str], index: int) -> str:
    lo = max(0, index - 4)
    hi = min(len(lines), index + 9)
    context = "\n".join(lines[lo:hi])
    found = [name for name, pattern in STATUS_TERMS.items() if pattern.search(context)]
    return ",".join(found)


def statement_fragments(line: str) -> list[str]:
    fragments: list[str] = []

    heading = MARKDOWN_HEADING_RE.match(line)
    if heading and KIND_FINDER_RE.search(heading.group(1)):
        fragments.append(heading.group(1))

    fragments.extend(match.group(1) for match in BOLD_LABEL_RE.finditer(line))

    plain = PLAIN_LABEL_RE.match(line)
    if plain:
        fragments.append(plain.group(1))

    for pattern in (HTML_HEADING_RE, HTML_STRONG_RE, HTML_LABEL_RE):
        for match in pattern.finditer(line):
            if KIND_FINDER_RE.search(clean_text(match.group(1))):
                fragments.append(match.group(1))

    unique: list[str] = []
    seen: set[str] = set()
    for fragment in fragments:
        cleaned = clean_text(fragment)
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            unique.append(cleaned)
    return unique


def harvest(root: Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        if any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.name.startswith(EXCLUDED_FILE_PREFIXES):
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        relative = path.relative_to(root).as_posix()
        for index, line in enumerate(lines):
            for fragment in statement_fragments(line):
                kind_match = KIND_FINDER_RE.search(fragment)
                if not kind_match:
                    continue
                candidates.append(
                    Candidate(
                        path=relative,
                        line=index + 1,
                        kind=kind_match.group(1).lower(),
                        title=fragment,
                        status_signals=status_signals(lines, index),
                        duplicate_key=normalized_key(fragment),
                    )
                )
    return candidates


def write_tsv(candidates: list[Candidate], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(
            ["path", "line", "kind", "title", "status_signals", "duplicate_key"]
        )
        for item in candidates:
            writer.writerow(
                [
                    item.path,
                    item.line,
                    item.kind,
                    item.title,
                    item.status_signals,
                    item.duplicate_key,
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    candidates = harvest(root)
    write_tsv(candidates, output)

    unique_keys = {item.duplicate_key for item in candidates if item.duplicate_key}
    print(f"candidates={len(candidates)}")
    print(f"unique_normalized_titles={len(unique_keys)}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
