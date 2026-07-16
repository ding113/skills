#!/usr/bin/env python3
"""Mechanical QC for the translate-subtitle skill.

Parses SRT / VTT / ASS subtitle files, verifies that everything outside the
translatable payload survived translation byte-identical (against --source),
and runs the executable rules from the bundled zh-target rule set
(rules/subtitle-zh.rules.json): punctuation conventions, line length, reading
speed, cross-cue consistency. llm-gate rules are NOT executed here — print
them for the review pass with --judgment.

Usage:
  python3 lint.py OUT.srt --source IN.srt            # structure + zh checks
  python3 lint.py OUT.srt --source IN.srt --bilingual
  python3 lint.py OUT.ass --source IN.ass --target en  # structure checks only
  python3 lint.py --judgment                           # list llm rules

Exit code: 0 = clean, 1 = violations/structure errors, 2 = usage error.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BUNDLE = SKILL_DIR / "rules" / "subtitle-zh.rules.json"
MAX_MATCHES_PER_RULE = 30

SRT_TIME_RX = re.compile(
    r"(\d+):(\d\d):(\d\d)[,.](\d{1,3})\s*-->\s*(\d+):(\d\d):(\d\d)[,.](\d{1,3})")
ASS_TIME_RX = re.compile(r"(\d+):(\d\d):(\d\d)\.(\d\d)")
ASS_TAG_RX = re.compile(r"\{[^}]*\}")
BILINGUAL_SEP_RX = re.compile(r"^([^。]+)。([^。]+)$")
CJK_RX = re.compile(r"[⺀-鿿㐀-䶿豈-﫿]")

# Positive gates are conditional-presence checks (e.g. "uncertain content is
# marked with ※") — a scanner can't know when the condition holds, so only
# negative regex gates run mechanically; the rest go through --judgment.
SCAN_NEGATIVE_ONLY = True
# Rules whose hits are exempt inside on-screen-text lines (「（」 prefix).
SCREEN_EXEMPT = {"SUB-punct-no-terminal", "SUB-punct-minimal", "SUB-diction-bookish"}
# code-gate rules this script implements natively.
NATIVE_CODE_RULES = {
    "SUB-rhythm-line-length", "SUB-rhythm-density",
    "SUB-tone-annotation", "SUB-terms-consistency",
}


def ms(h, m, s, frac, frac_unit):
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(frac) * frac_unit


class Cue:
    def __init__(self, ident, timing_raw, start_ms, end_ms, payload_lines, prefix=""):
        self.ident = ident              # SRT index / VTT cue id / None
        self.timing_raw = timing_raw    # verbatim timing (+settings) line
        self.start_ms = start_ms
        self.end_ms = end_ms
        self.payload = payload_lines    # raw payload lines (tags intact)
        self.prefix = prefix            # ASS Dialogue prefix (fields before Text)

    def rendered_lines(self, fmt):
        """Visible text lines, styling stripped."""
        if fmt == "ass":
            text = self.payload[0] if self.payload else ""
            text = ASS_TAG_RX.sub("", text).replace(r"\h", " ")
            return [l for l in re.split(r"\\N|\\n", text)]
        return [re.sub(r"</?[^>]+>", "", l) for l in self.payload]  # strip vtt/srt tags


# ------------------------------------------------------------------ parsers

def detect_format(path, text):
    suffix = Path(path).suffix.lower()
    if suffix in (".ass", ".ssa") or "[Script Info]" in text[:200]:
        return "ass"
    if suffix == ".vtt" or text.lstrip("﻿").startswith("WEBVTT"):
        return "vtt"
    return "srt"


def parse_srt_vtt(text, fmt, problems):
    text = text.lstrip("﻿")
    body = text
    header = ""
    if fmt == "vtt":
        parts = re.split(r"\n\s*\n", text, maxsplit=1)
        header = parts[0]
        body = parts[1] if len(parts) > 1 else ""
    cues = []
    for block in re.split(r"\n\s*\n", body.strip()):
        lines = block.splitlines()
        if not lines or not any(l.strip() for l in lines):
            continue
        if fmt == "vtt" and lines[0].split(" ")[0] in ("NOTE", "STYLE", "REGION"):
            continue
        ident, ti = None, 0
        if "-->" not in lines[0]:
            ident, ti = lines[0].strip(), 1
        if ti >= len(lines) or "-->" not in lines[ti]:
            problems.append(f"unparseable block: {lines[0][:60]!r}")
            continue
        timing = lines[ti].strip()
        m = SRT_TIME_RX.search(timing)
        if not m:
            problems.append(f"unparseable timing: {timing[:60]!r}")
            continue
        g = m.groups()
        start = ms(g[0], g[1], g[2], g[3].ljust(3, "0"), 1)
        end = ms(g[4], g[5], g[6], g[7].ljust(3, "0"), 1)
        cues.append(Cue(ident, timing, start, end, lines[ti + 1:]))
    return header, cues


def parse_ass(text, problems):
    cues, skeleton = [], []
    fields, in_events = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("["):
            in_events = s.lower() == "[events]"
            skeleton.append(line)
            continue
        if in_events and s.lower().startswith("format:"):
            fields = [f.strip() for f in s.split(":", 1)[1].split(",")]
            skeleton.append(line)
            continue
        if in_events and s.startswith("Dialogue:") and fields:
            body = line.split(":", 1)[1]
            parts = body.split(",", len(fields) - 1)
            if len(parts) < len(fields):
                problems.append(f"malformed Dialogue: {line[:60]!r}")
                skeleton.append(line)
                continue
            text_field = parts[-1]
            prefix = line[: len(line) - len(text_field)]
            def field(name):
                try:
                    return parts[fields.index(name)].strip()
                except ValueError:
                    return ""
            def to_ms(v):
                m = ASS_TIME_RX.match(v)
                return ms(*m.groups(), 10) if m else None
            cues.append(Cue(None, f"{field('Start')} --> {field('End')}",
                            to_ms(field("Start")), to_ms(field("End")),
                            [text_field], prefix=prefix))
            skeleton.append(prefix + "\x00")
        else:
            skeleton.append(line)
    return "\n".join(skeleton), cues


def load(path):
    p = Path(path)
    if not p.exists():
        print(f"error: file not found: {p}", file=sys.stderr)
        sys.exit(2)
    text = p.read_text(encoding="utf-8-sig")
    fmt = detect_format(path, text)
    problems = []
    if fmt == "ass":
        skeleton, cues = parse_ass(text, problems)
    else:
        skeleton, cues = parse_srt_vtt(text, fmt, problems)
    return fmt, skeleton, cues, problems


# ------------------------------------------------------------- structure

def compare_structure(fmt, out, src, errors):
    if fmt != src[0]:
        errors.append({"check": "format", "message": f"source is {src[0]}, output is {fmt}"})
        return
    src_skel, src_cues = src[1], src[2]
    out_skel, out_cues = out[1], out[2]
    if fmt == "ass":
        if src_skel != out_skel:
            for i, (a, b) in enumerate(zip(src_skel.splitlines(), out_skel.splitlines())):
                if a != b:
                    errors.append({"check": "skeleton", "line": i + 1,
                                   "source": a[:100], "output": b[:100]})
                    break
            else:
                errors.append({"check": "skeleton", "message": "line count differs"})
    elif fmt == "vtt":
        if src[1] != out[1]:
            errors.append({"check": "vtt_header", "message": "header block changed"})
    if len(src_cues) != len(out_cues):
        errors.append({"check": "cue_count",
                       "message": f"source {len(src_cues)} cues, output {len(out_cues)}"})
    for i, (a, b) in enumerate(zip(src_cues, out_cues), 1):
        if a.timing_raw != b.timing_raw:
            errors.append({"check": "timing", "cue": i,
                           "source": a.timing_raw, "output": b.timing_raw})
        if a.ident != b.ident:
            errors.append({"check": "cue_id", "cue": i,
                           "source": a.ident, "output": b.ident})
        if fmt == "ass" and a.prefix != b.prefix:
            errors.append({"check": "dialogue_prefix", "cue": i,
                           "source": a.prefix[:100], "output": b.prefix[:100]})
        if not any(l.strip() for l in b.payload) and any(l.strip() for l in a.payload):
            errors.append({"check": "empty_translation", "cue": i,
                           "source": " ".join(a.payload)[:80]})


# ------------------------------------------------------------- zh checks

def visual_len(line):
    """Reading load: fullwidth chars count 1, halfwidth 0.5, spaces 0."""
    total = 0.0
    for ch in line:
        if ch.isspace():
            continue
        total += 1.0 if unicodedata.east_asian_width(ch) in ("W", "F") else 0.5
    return total


def is_screen_text(line):
    return line.lstrip().startswith(("（", "("))


def strip_latin_apostrophes(line):
    return re.sub(r"(?<=[A-Za-z])[’'](?=[A-Za-z])", "", line)


def add_violation(violations, rule, cue_no, line_no, match, message, confidence):
    violations.append({
        "rule_id": rule["id"], "name": rule["name"],
        "strength": rule["strength"]["level"],
        "confidence": confidence,
        "cue": cue_no, "line_in_cue": line_no,
        "match": match[:80], "message": message,
    })


def run_bundle_regexes(bundle, fmt, cues, bilingual, violations, skipped):
    for rule in bundle["rules"]:
        gates = rule.get("gates", {}).get("negative", [])
        patterns = [(g["pattern"], g.get("confidence", "exact"), g.get("description", rule["name"]))
                    for g in gates if g.get("type") == "regex" and g.get("pattern")]
        if not patterns:
            continue
        hits = 0
        for pat, confidence, desc in patterns:
            try:
                rx = re.compile(pat)
            except re.error as e:
                skipped.append({"rule_id": rule["id"], "reason": f"regex error: {e}"})
                continue
            for cue_no, cue in enumerate(cues, 1):
                for line_no, line in enumerate(cue.rendered_lines(fmt), 1):
                    view = line
                    if rule["id"] in SCREEN_EXEMPT and is_screen_text(view):
                        continue
                    if rule["id"] == "SUB-punct-quotes":
                        view = strip_latin_apostrophes(view)
                    if bilingual and rule["id"] == "SUB-punct-no-terminal":
                        m = BILINGUAL_SEP_RX.match(view.strip())
                        if m:  # drop the single separator 。 before scanning
                            view = m.group(1) + m.group(2)
                    for m in rx.finditer(view):
                        if hits >= MAX_MATCHES_PER_RULE:
                            break
                        hits += 1
                        add_violation(violations, rule, cue_no, line_no,
                                      m.group(0), desc, confidence)


def run_native_code_checks(bundle, fmt, cues, src_cues, violations):
    rules = {r["id"]: r for r in bundle["rules"]}

    r = rules.get("SUB-rhythm-line-length")
    if r:
        for cue_no, cue in enumerate(cues, 1):
            for line_no, line in enumerate(cue.rendered_lines(fmt), 1):
                vl = visual_len(line)
                if vl > 25:
                    add_violation(violations, r, cue_no, line_no, line,
                                  f"行长 {vl:g}（按汉字=1、西文=0.5 计），上限 25", "heuristic")

    r = rules.get("SUB-rhythm-density")
    if r:
        for cue_no, cue in enumerate(cues, 1):
            dur = (cue.end_ms - cue.start_ms) / 1000 if cue.end_ms and cue.start_ms is not None else 0
            if dur <= 0:
                continue
            chars = sum(visual_len(l) for l in cue.rendered_lines(fmt))
            cps = chars / dur
            if cps > 7:
                add_violation(violations, r, cue_no, 0, f"{cps:.1f} 字/秒",
                              "字速超过 7 字/秒硬线（目标 ≤5）", "heuristic")

    r = rules.get("SUB-tone-annotation")
    if r:
        for cue_no, cue in enumerate(cues, 1):
            for line_no, line in enumerate(cue.rendered_lines(fmt), 1):
                if "※" in line and visual_len(line.split("※", 1)[1]) > 40:
                    add_violation(violations, r, cue_no, line_no, line,
                                  "注释超过 40 字", "exact")

    r = rules.get("SUB-terms-consistency")
    if r and src_cues:
        def norm(cue):
            t = " ".join(cue.rendered_lines(fmt)).lower()
            return re.sub(r"[\s\W]+", "", t, flags=re.U)
        seen = {}
        for cue_no, (s, o) in enumerate(zip(src_cues, cues), 1):
            key = norm(s)
            if len(key) < 6:  # too short to be a meaningful repeated line
                continue
            val = norm(o)
            if key in seen and seen[key][1] != val:
                add_violation(violations, r, cue_no, 0,
                              " ".join(o.rendered_lines(fmt)),
                              f"与第 {seen[key][0]} 条相同的原文译法不一致", "heuristic")
            else:
                seen.setdefault(key, (cue_no, val))


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subtitle", nargs="?", help="translated subtitle file")
    ap.add_argument("--source", help="original subtitle file (enables structure diff)")
    ap.add_argument("--target", default="zh", choices=["zh", "en"],
                    help="target language; zh mechanical rules run only for zh")
    ap.add_argument("--bilingual", action="store_true",
                    help="bilingual subtitles: 「原文。译文」 separator is exempt")
    ap.add_argument("--bundle", default=str(DEFAULT_BUNDLE))
    ap.add_argument("--judgment", action="store_true",
                    help="print llm-gate rules for the review pass instead of linting")
    args = ap.parse_args()

    bundle = json.loads(Path(args.bundle).read_text())

    if args.judgment:
        print("# Judgment rules — apply cue by cue, reading the translation without the source")
        print("# 最高取舍标准: 意思准确、逻辑成立、情绪正确、中文自然、字幕可读性良好\n")
        for r in bundle["rules"]:
            gates = r.get("gates", {})
            descs = [g["description"] for side in ("negative", "positive")
                     for g in gates.get(side, []) if g.get("type") == "llm"]
            if descs:
                level = r["strength"]["level"]
                print(f"- [{level}] {r['id']} — {r['name']}: {'；'.join(descs)}")
                if r.get("notes"):
                    print(f"    note: {r['notes']}")
        return 0

    if not args.subtitle:
        print("error: subtitle file required for linting", file=sys.stderr)
        return 2

    fmt, skeleton, cues, problems = load(args.subtitle)
    structure_errors = [{"check": "parse", "message": p} for p in problems]
    src_cues = None
    if args.source:
        src = load(args.source)
        structure_errors += [{"check": "parse_source", "message": p} for p in src[3]]
        compare_structure(fmt, (fmt, skeleton, cues), src, structure_errors)
        src_cues = src[2]

    violations, skipped = [], []
    if args.target == "zh":
        run_bundle_regexes(bundle, fmt, cues, args.bilingual, violations, skipped)
        run_native_code_checks(bundle, fmt, cues, src_cues, violations)
    else:
        skipped.append({"rule_id": "*", "reason": "bundle is zh-target; en output gets structure checks only"})

    violations.sort(key=lambda v: (v["cue"], v["rule_id"]))
    report = {
        "file": args.subtitle,
        "source": args.source,
        "format": fmt,
        "bundle": Path(args.bundle).name,
        "summary": {
            "cues": len(cues),
            "structure_errors": len(structure_errors),
            "violations": len(violations),
            "must": sum(1 for v in violations if v["strength"] == "must"),
            "exact": sum(1 for v in violations if v["confidence"] == "exact"),
            "heuristic": sum(1 for v in violations if v["confidence"] == "heuristic"),
            "rules_skipped": len(skipped),
        },
        "structure_errors": structure_errors,
        "violations": violations,
        "skipped_rules": skipped,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if (violations or structure_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
