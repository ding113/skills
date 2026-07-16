#!/usr/bin/env python3
"""Mechanical review pass for the article-writing skill.

Runs every executable rule (regex + terminology) from a compiled genre
bundle against an article, plus markdownlint if available, and emits a
structured JSON violation report. Judgment-type rules are NOT executed
here — print them for the review agent with --judgment.

Usage:
  python3 lint.py ARTICLE.md --genre zh-blog          # lint
  python3 lint.py --genre zh-blog --judgment           # list judgment rules
  python3 lint.py ARTICLE.md --bundle path/to.rules.json

Exit code: 0 = clean, 1 = violations found, 2 = usage/config error.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MAX_MATCHES_PER_RULE = 20

FLAG_MAP = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}


def compile_pattern(pattern, flags=""):
    f = 0
    for ch in flags or "":
        f |= FLAG_MAP.get(ch, 0)
    return re.compile(pattern, f)


# ------------------------------------------------------------------ scopes

def scope_ranges(text):
    """Map scope name -> list of (start, end) character ranges."""
    scopes = {k: [] for k in (
        "frontmatter", "code_block", "inline_code", "url",
        "link_target", "heading", "html_tag", "table",
    )}
    m = re.match(r"\A---\n.*?\n---\n", text, re.S)
    if m:
        scopes["frontmatter"].append((0, m.end()))
    for m in re.finditer(r"^(```|~~~)[^\n]*\n.*?^\1[^\n]*$", text, re.S | re.M):
        scopes["code_block"].append(m.span())
    for m in re.finditer(r"`+[^`\n]+`+", text):
        scopes["inline_code"].append(m.span())
    for m in re.finditer(r"https?://[^\s)>\]]+", text):
        scopes["url"].append(m.span())
    for m in re.finditer(r"\]\(([^)\s]+)[^)]*\)", text):
        scopes["link_target"].append(m.span(1))
    for m in re.finditer(r"^\[[^\]]+\]:\s*\S+.*$", text, re.M):
        scopes["link_target"].append(m.span())
    for m in re.finditer(r"^#{1,6}\s[^\n]*$", text, re.M):
        scopes["heading"].append(m.span())
    for m in re.finditer(r"<[^>\n]+>", text):
        scopes["html_tag"].append(m.span())
    for m in re.finditer(r"^\s*\|[^\n]*$", text, re.M):
        scopes["table"].append(m.span())
    return scopes


def masked_text(text, scopes, exclude):
    """Blank out excluded ranges (newlines kept so line numbers survive).

    The mask char must be neutral — not a space (would fake multi-space /
    spacing violations), not Latin/CJK (would fake CJK-Latin spacing
    violations). U+FFFC matches none of the rule character classes.
    """
    if not exclude:
        return text
    chars = list(text)
    for name in exclude:
        for start, end in scopes.get(name, []):
            for i in range(start, end):
                if chars[i] != "\n":
                    chars[i] = "￼"
    return "".join(chars)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def excerpt_at(text, start, end, width=40):
    lo = max(0, start - width)
    hi = min(len(text), end + width)
    return text[lo:hi].replace("\n", "⏎")


# ------------------------------------------------------------------ checks

def run_regex_rule(rule, text, scopes, violations, skipped):
    check = rule["check"]
    if not check.get("python_ok", True):
        skipped.append({"rule_id": rule["id"], "reason": "pattern not compilable in Python"})
        return
    try:
        rx = compile_pattern(check["pattern"], check.get("flags", ""))
    except re.error as e:
        skipped.append({"rule_id": rule["id"], "reason": f"regex error: {e}"})
        return
    view = masked_text(text, scopes, check.get("exclude_scopes"))
    hits = [
        m for m in rx.finditer(view)
        # pure-whitespace matches containing a newline are line-boundary
        # artifacts of source patterns that use \s (typography rules are
        # single-line by nature)
        if not ("\n" in m.group(0) and m.group(0).strip() == "")
    ][:MAX_MATCHES_PER_RULE]
    for m in hits:
        violations.append({
            "rule_id": rule["id"],
            "name": rule["name"],
            "severity": rule.get("severity", "warning"),
            "strength": rule.get("strength", "should"),
            "confidence": check.get("confidence", "exact"),
            "line": line_of(view, m.start()),
            "match": m.group(0)[:80],
            "excerpt": excerpt_at(view, m.start(), m.end()),
            "message": check.get("description", rule["name"]),
            "fix": (rule.get("fix") or {}).get("description") or (rule.get("fix") or {}).get("replacement"),
        })


def run_term_rule(rule, text, scopes, violations):
    term = rule["term"]
    check = rule.get("check", {})
    view = masked_text(text, scopes, check.get("exclude_scopes") or ["code_block", "inline_code", "url", "link_target"])
    flags = 0 if term.get("case_sensitive") else re.IGNORECASE
    patterns = []
    if term.get("match_pattern"):
        patterns.append(term["match_pattern"])
    for wrong in term.get("wrong_variants") or []:
        patterns.append(r"(?<![\w-])" + re.escape(wrong) + r"(?![\w-])")
    for pat in patterns:
        try:
            rx = re.compile(pat, flags)
        except re.error:
            continue
        for m in list(rx.finditer(view))[:MAX_MATCHES_PER_RULE]:
            if m.group(0) == term.get("canonical"):
                continue  # already the canonical form
            violations.append({
                "rule_id": rule["id"],
                "name": rule["name"],
                "severity": rule.get("severity", "warning"),
                "strength": rule.get("strength", "should"),
                "confidence": "heuristic",
                "line": line_of(view, m.start()),
                "match": m.group(0)[:80],
                "excerpt": excerpt_at(view, m.start(), m.end()),
                "message": f"应写作 “{term.get('canonical')}”",
                "fix": term.get("canonical"),
            })


def run_markdownlint(path):
    for cmd in (["markdownlint-cli2", str(path)], ["markdownlint", str(path)]):
        if shutil.which(cmd[0]):
            proc = subprocess.run(cmd, capture_output=True, text=True)
            out = (proc.stdout + proc.stderr).strip()
            issues = [l for l in out.splitlines() if str(path.name) in l]
            return {"tool": cmd[0], "exit": proc.returncode, "issues": issues[:100]}
    return {"tool": None, "exit": None, "issues": [],
            "note": "markdownlint not installed; universal Markdown layer not checked mechanically"}


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("article", nargs="?", help="markdown file to lint")
    ap.add_argument("--genre", help="bundle name, e.g. zh-blog, en-publication")
    ap.add_argument("--bundle", help="explicit path to a compiled rules bundle")
    ap.add_argument("--judgment", action="store_true",
                    help="print judgment (llm) rules for the review agent instead of linting")
    args = ap.parse_args()

    if args.bundle:
        bundle_path = Path(args.bundle)
    elif args.genre:
        bundle_path = SKILL_DIR / "rules" / f"{args.genre}.rules.json"
    else:
        print("error: pass --genre or --bundle", file=sys.stderr)
        return 2
    if not bundle_path.exists():
        print(f"error: bundle not found: {bundle_path}", file=sys.stderr)
        return 2
    bundle = json.loads(bundle_path.read_text())
    rules = bundle["rules"]

    if args.judgment:
        print(f"# Judgment rules — {bundle['bundle']} (apply per-paragraph during review)")
        print(f"# Quote convention: {bundle.get('quote_convention', '')}\n")
        for r in rules:
            if r["check"]["type"] in ("llm", "code"):
                line = f"- [{r['strength']}] {r['id']} — {r['name']}: {r['check'].get('description', '')}"
                print(line)
                ex = r.get("examples") or {}
                for neg in (ex.get("negative") or [])[:1]:
                    print(f"    反例: {str(neg)[:120]}")
        return 0

    if not args.article:
        print("error: article file required for linting", file=sys.stderr)
        return 2
    path = Path(args.article)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text()
    scopes = scope_ranges(text)

    violations, skipped = [], []
    for r in rules:
        ctype = r["check"]["type"]
        if ctype == "regex" and r["check"].get("pattern"):
            run_regex_rule(r, text, scopes, violations, skipped)
        elif ctype == "term" and r.get("term"):
            run_term_rule(r, text, scopes, violations)

    md = run_markdownlint(path)
    violations.sort(key=lambda v: (v["line"], v["rule_id"]))
    report = {
        "file": str(path),
        "bundle": bundle["bundle"],
        "quote_convention": bundle.get("quote_convention"),
        "summary": {
            "violations": len(violations),
            "must": sum(1 for v in violations if v["strength"] == "must"),
            "exact": sum(1 for v in violations if v["confidence"] == "exact"),
            "heuristic": sum(1 for v in violations if v["confidence"] == "heuristic"),
            "markdownlint_issues": len(md["issues"]),
            "rules_executed": sum(1 for r in rules if r["check"]["type"] in ("regex", "term")),
            "rules_skipped": len(skipped),
        },
        "violations": violations,
        "markdownlint": md,
        "skipped_rules": skipped,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if (violations or md["issues"]) else 0


if __name__ == "__main__":
    sys.exit(main())
