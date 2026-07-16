#!/usr/bin/env python3
"""Formatting-invariant check for the translate-article skill.

Compares a source article and its translation and reports everything that
should have survived translation byte-identical but didn't: fenced code
blocks, inline code, URLs, image paths, heading structure, footnote ids,
frontmatter keys — plus a heuristic pass on number survival.

Usage:
  python3 check_invariants.py SOURCE.md TRANSLATION.md

Exit code: 0 = clean (warnings allowed), 1 = errors found, 2 = usage error.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

FENCE_RX = re.compile(r"^(```|~~~)[^\n]*\n(.*?)^\1[^\n]*$", re.S | re.M)
INLINE_CODE_RX = re.compile(r"`+([^`\n]+)`+")
URL_RX = re.compile(r"https?://[^\s)>\]\"']+")
LINK_TARGET_RX = re.compile(r"\]\(([^)\s]+)(?:\s[^)]*)?\)")
IMAGE_RX = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s[^)]*)?\)")
HEADING_RX = re.compile(r"^(#{1,6})\s", re.M)
FOOTNOTE_DEF_RX = re.compile(r"^\[\^([^\]]+)\]:", re.M)
# Digit tokens worth tracking: 2+ digits, or a decimal/percent/thousands form.
NUMBER_RX = re.compile(r"\d+(?:[.,]\d+)+%?|\d{2,}%?|\d%")


def read(path):
    p = Path(path)
    if not p.exists():
        print(f"error: file not found: {p}", file=sys.stderr)
        sys.exit(2)
    return p.read_text()


def frontmatter_keys(text):
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    keys = []
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+):", line)
        if km:
            keys.append(km.group(1))
    return keys


def strip_code(text):
    """Prose view: code blocks and inline code blanked, for number extraction."""
    text = FENCE_RX.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return INLINE_CODE_RX.sub(" ", text)


def multiset_diff(name, src_items, dst_items, errors, ordered=False):
    if ordered:
        if src_items != dst_items:
            for i, (a, b) in enumerate(zip(src_items, dst_items)):
                if a != b:
                    errors.append({"check": name, "index": i,
                                   "source": a[:120], "translation": b[:120]})
            if len(src_items) != len(dst_items):
                errors.append({"check": name,
                               "message": f"count differs: source {len(src_items)}, translation {len(dst_items)}"})
        return
    src_c, dst_c = Counter(src_items), Counter(dst_items)
    for item in (src_c - dst_c):
        errors.append({"check": name, "missing_in_translation": item[:120]})
    for item in (dst_c - src_c):
        errors.append({"check": name, "extra_in_translation": item[:120]})


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, dst = read(sys.argv[1]), read(sys.argv[2])
    errors, warnings = [], []

    # Fenced code blocks: order and content must both survive.
    multiset_diff("code_block",
                  [m.group(0) for m in FENCE_RX.finditer(src)],
                  [m.group(0) for m in FENCE_RX.finditer(dst)],
                  errors, ordered=True)

    # Inline code spans: same multiset (prose around them may reorder).
    multiset_diff("inline_code",
                  [m.group(1) for m in INLINE_CODE_RX.finditer(src)],
                  [m.group(1) for m in INLINE_CODE_RX.finditer(dst)],
                  errors)

    # URLs: bare + link targets, but only real URLs (fragments/relative paths
    # legitimately change when headings are translated → warning, not error).
    multiset_diff("url",
                  URL_RX.findall(src), URL_RX.findall(dst), errors)
    src_rel = [t for t in LINK_TARGET_RX.findall(src) if not t.startswith(("http://", "https://"))]
    dst_rel = [t for t in LINK_TARGET_RX.findall(dst) if not t.startswith(("http://", "https://"))]
    if len(src_rel) != len(dst_rel):
        errors.append({"check": "relative_link",
                       "message": f"count differs: source {len(src_rel)}, translation {len(dst_rel)}"})
    else:
        for a, b in zip(src_rel, dst_rel):
            if a != b and not a.startswith("#"):
                errors.append({"check": "relative_link", "source": a, "translation": b})
            elif a != b:
                warnings.append({"check": "fragment_link", "source": a, "translation": b,
                                 "note": "expected when headings are translated — verify it points at the translated heading"})

    # Image paths: ordered.
    multiset_diff("image_path", IMAGE_RX.findall(src), IMAGE_RX.findall(dst),
                  errors, ordered=True)

    # Heading structure: the sequence of levels must mirror.
    src_h = [len(m.group(1)) for m in HEADING_RX.finditer(strip_code(src))]
    dst_h = [len(m.group(1)) for m in HEADING_RX.finditer(strip_code(dst))]
    if src_h != dst_h:
        errors.append({"check": "heading_structure", "source": src_h, "translation": dst_h})

    # Footnote definition ids.
    multiset_diff("footnote_id", FOOTNOTE_DEF_RX.findall(src),
                  FOOTNOTE_DEF_RX.findall(dst), errors)

    # Frontmatter keys (values may be translated; keys may not).
    src_fm, dst_fm = frontmatter_keys(src), frontmatter_keys(dst)
    if src_fm is not None and src_fm != dst_fm:
        errors.append({"check": "frontmatter_keys", "source": src_fm, "translation": dst_fm})

    # Number survival (heuristic): digit tokens in source prose should appear
    # in the translation. Legit exceptions exist (2x → 两倍), hence warnings.
    dst_prose = strip_code(dst)
    dst_numbers = set(NUMBER_RX.findall(dst_prose))
    dst_numbers |= {n.replace(",", "") for n in dst_numbers}
    for n in NUMBER_RX.findall(strip_code(src)):
        if n not in dst_numbers and n.replace(",", "") not in dst_numbers:
            warnings.append({"check": "number_survival", "missing_in_translation": n})

    report = {
        "source": sys.argv[1],
        "translation": sys.argv[2],
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
