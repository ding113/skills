#!/usr/bin/env python3
"""Compile the article-writing skill's per-genre rule bundles.

Sources live in drafts/ (the rule "source code"); output goes to
skills/in-progress/article-writing/rules/. The skill package ships only the
compiled bundles — this script stays in the repo so bundles can be
recompiled whenever drafts/ changes.

Two source schemas are normalized into one:
  - gate model  (drafts/审校工作规范.rules.json): judgment-oriented, gates
    with type regex/code/nlp/llm. code/nlp carry no executable payload, so
    anything non-regex executes as "llm" (agent judgment); the original
    gate type is preserved for traceability.
  - lint model  (drafts/04-写作规范/_extracted/*.rules.json): regex/term
    checks with auto-fix hints, lang tags, severity.

Usage: python3 scripts/compile-article-rules.py
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DRAFTS = REPO / "drafts"
EXTRACTED = DRAFTS / "04-写作规范" / "_extracted"
OUT = REPO / "skills" / "in-progress" / "article-writing" / "rules"

SHENJIAO = DRAFTS / "审校工作规范.rules.json"

# 审校 categories that are language-independent editorial judgment
# (fact-checking, style consistency). The rest (grammar, punctuation,
# numbers) encode zh-specific mechanics and stay out of en bundles.
SHENJIAO_UNIVERSAL_CATS = ("事实核对", "内容审校/体例一致审校")

# ---------------------------------------------------------------- house rules

HOUSE_ZH_CORNER = {
    "id": "HOUSE-zh-quote-corner",
    "name": "家规:正文统一直角引号「」(嵌套『』)",
    "category": ["标点符号", "引号"],
    "layer": "house",
    "strength": "must",
    "severity": "error",
    "check": {
        "type": "regex",
        "pattern": "[“”‘’]",
        "flags": "g",
        "exclude_scopes": ["code_block", "inline_code", "url", "link_target", "frontmatter", "html_tag"],
        "description": "中文博客/技术文档正文出现弯引号（应改为「」/『』）",
        "confidence": "exact",
    },
    "fix": {"auto": False, "description": "主引号改「」，引号内再引用改『』"},
    "examples": {
        "positive": ["他说：「先跑通再谈优雅。」", "所谓「幂等」，指的是重复执行结果不变。"],
        "negative": ["他说：“先跑通再谈优雅。”"],
    },
    "source": {"file": "house", "id": "grilling-2026-07-15#Q6"},
    "notes": "覆盖 GB/T 弯引号建议与 zhtech 弯引号规则；引语、术语、强调一律「」。",
    "replaces": [
        "TW-sspai-punct-cjk-quote-corner",
        "TW-zhcopy-style-corner-quotes",
        "TW-zhtech-punct-straight-quotes",
    ],
}

HOUSE_ZH_ASCII_QUOTE = {
    "id": "HOUSE-zh-no-ascii-quote",
    "name": "家规:中文正文禁用 ASCII 直引号",
    "category": ["标点符号", "引号"],
    "layer": "house",
    "strength": "must",
    "severity": "warning",
    "check": {
        "type": "regex",
        "pattern": "[一-鿿][\"']|[\"'][一-鿿]",
        "flags": "g",
        "exclude_scopes": ["code_block", "inline_code", "url", "link_target", "frontmatter", "html_tag"],
        "description": "紧邻汉字的 ASCII 直引号（应改为「」）",
        "confidence": "heuristic",
    },
    "examples": {
        "positive": ["配置里的 \"debug\" 字段保持原样（代码语境）"],
        "negative": ["他说:\"没问题\"就走了"],
    },
    "source": {"file": "house", "id": "grilling-2026-07-15#Q6"},
}

HOUSE_ZH_PUB_GBT = {
    "id": "HOUSE-zh-pub-gbt-quotes",
    "name": "家规:出版物严格 GB/T 15834 弯引号“”,禁用直角引号",
    "category": ["标点符号", "引号"],
    "layer": "house",
    "strength": "must",
    "severity": "error",
    "check": {
        "type": "regex",
        "pattern": "[「」『』]",
        "flags": "g",
        "exclude_scopes": ["code_block", "inline_code", "url", "link_target", "frontmatter", "html_tag"],
        "description": "出版物正文出现直角引号（国标要求全角弯引号“”‘’）",
        "confidence": "exact",
    },
    "fix": {"auto": True, "description": "「」→“”，『』→‘’"},
    "examples": {
        "positive": ["他说：“先跑通再谈优雅。”"],
        "negative": ["他说：「先跑通再谈优雅。」"],
    },
    "source": {"file": "house", "id": "grilling-2026-07-15#Q6"},
    "notes": "出版物不叠加技术文章排版习惯，标点严格随国标。",
}

HOUSE_EN_CURLY = {
    "id": "HOUSE-en-curly-quotes",
    "name": "House rule: prose uses curly quotes, not straight",
    "category": ["punctuation", "quotes"],
    "layer": "house",
    "strength": "must",
    "severity": "warning",
    "check": {
        "type": "regex",
        "pattern": "[A-Za-z,.;:!?)\\]]\\s*\"[A-Za-z(]|[A-Za-z]\\s\"|\"\\s[A-Za-z]",
        "flags": "g",
        "exclude_scopes": ["code_block", "inline_code", "url", "link_target", "frontmatter", "html_tag"],
        "description": "Straight double quote in prose (use “ ”; apostrophes use ’)",
        "confidence": "heuristic",
    },
    "source": {"file": "house", "id": "grilling-2026-07-15#Q7"},
    "notes": (
        "Unifies the Apple-vs-MDN conflict: Apple and the newsletter corpus "
        "mandate curly quotes; MDN mandates straight. House rule: curly across "
        "all three en genres, so the two MDN curly→straight rules are excluded."
    ),
    "replaces": [
        "TW-mdnen-punct-curly-double-quote",
        "TW-mdnen-punct-curly-single-quote",
        "TW-mdnzh-punct-curly-double-quotes",
        "TW-mdnzh-punct-curly-apostrophe",
    ],
}

HOUSE_EN_APOSTROPHE = {
    "id": "HOUSE-en-curly-apostrophe",
    "name": "House rule: curly apostrophe ’ in prose contractions/possessives",
    "category": ["punctuation", "quotes"],
    "layer": "house",
    "strength": "should",
    "severity": "warning",
    "check": {
        "type": "regex",
        "pattern": "[A-Za-z]'(?=[a-z])",
        "flags": "g",
        "exclude_scopes": ["code_block", "inline_code", "url", "link_target", "frontmatter", "html_tag"],
        "description": "Straight apostrophe in prose (use ’, e.g. don’t / Erik’s)",
        "confidence": "heuristic",
    },
    "fix": {"auto": True, "description": "' → ’"},
    "source": {"file": "house", "id": "grilling-2026-07-15#Q7 (newsletter corpus convention)"},
}

HOUSE_EN_SINGLE_SPACE = {
    "id": "HOUSE-en-single-space-after-period",
    "name": "House rule: single space after sentence period",
    "category": ["punctuation", "spacing"],
    "layer": "house",
    "strength": "must",
    "severity": "error",
    "check": {
        "type": "regex",
        "pattern": "[.!?][”’\"']?  +[A-Z“\"]",
        "flags": "g",
        "exclude_scopes": ["code_block", "inline_code", "table"],
        "description": "Two or more spaces after end-of-sentence punctuation",
        "confidence": "exact",
    },
    "fix": {"auto": True, "description": "collapse to one space"},
    "source": {"file": "house", "id": "grilling-2026-07-15#Q7 (newsletter corpus convention)"},
}

HOUSE_EN_OXFORD = {
    "id": "HOUSE-en-oxford-comma",
    "name": "House rule: use the Oxford comma in lists of three or more",
    "category": ["punctuation", "comma"],
    "layer": "house",
    "strength": "should",
    "severity": "suggestion",
    "check": {
        "type": "regex",
        "pattern": ", (?:[\\w’']+ ){1,3}(?:and|or) [\\w’']+",
        "flags": "g",
        "exclude_scopes": ["code_block", "inline_code", "heading"],
        "description": "Possible missing serial comma before and/or (verify it is a 3+ item list)",
        "confidence": "heuristic",
    },
    "source": {"file": "house", "id": "grilling-2026-07-15#Q7 (newsletter corpus convention)"},
}

# ------------------------------------------------------------- bundle configs
# Each lint-source entry: (filename-stem, lang-filter, include-types or None,
# extra predicate name). Types: punctuation/spacing/style/terminology.

BUNDLES = {
    "zh-blog": {
        "language": "zh",
        "genre": "blog",
        "shenjiao": "all",
        "lint": [
            ("zhcopy", {"zh", "both"}, None),
            ("sspai", {"zh", "both"}, None),
            ("zhtech", {"zh", "both"}, {"punctuation", "spacing"}),
        ],
        "house": [HOUSE_ZH_CORNER, HOUSE_ZH_ASCII_QUOTE],
        "quote_convention": "直角引号「」为主引号，嵌套用『』；禁用弯引号与 ASCII 直引号（代码除外）。",
    },
    "zh-techdoc": {
        "language": "zh",
        "genre": "techdoc",
        "shenjiao": "all",
        "lint": [
            ("zhtech", {"zh", "both"}, None),
            ("mdnzh", {"zh", "both"}, None),
            ("zhcopy", {"zh", "both"}, None),
            ("sspai", {"zh", "both"}, None),
        ],
        "house": [HOUSE_ZH_CORNER, HOUSE_ZH_ASCII_QUOTE],
        "quote_convention": "直角引号「」为主引号，嵌套用『』；禁用弯引号与 ASCII 直引号（代码除外）。",
    },
    "zh-publication": {
        "language": "zh",
        "genre": "publication",
        "shenjiao": "all",
        "lint": [],
        "house": [HOUSE_ZH_PUB_GBT],
        "quote_convention": "严格 GB/T 15834：全角弯引号“”‘’；禁用直角引号。",
    },
    "en-blog": {
        "language": "en",
        "genre": "blog",
        "shenjiao": "universal",
        "lint": [
            ("msbias", {"en", "both"}, None),
        ],
        "house": [HOUSE_EN_CURLY, HOUSE_EN_APOSTROPHE, HOUSE_EN_SINGLE_SPACE, HOUSE_EN_OXFORD],
        "quote_convention": "Curly quotes “ ” ‘ ’ in prose; straight quotes only inside code.",
    },
    "en-techdoc": {
        "language": "en",
        "genre": "techdoc",
        "shenjiao": "universal",
        "lint": [
            ("apple", {"en", "both"}, None),
            ("redhat", {"en", "both"}, None),
            ("mdnen", {"en", "both"}, None),
            ("mdnzh", {"en"}, None),
            ("mstop10", {"en", "both"}, None),
            ("msbias", {"en", "both"}, None),
            ("msabout", {"en", "both"}, None),
            ("msglobal", {"en", "both"}, None),
        ],
        "house": [HOUSE_EN_CURLY, HOUSE_EN_APOSTROPHE, HOUSE_EN_SINGLE_SPACE, HOUSE_EN_OXFORD],
        "quote_convention": "Curly quotes “ ” ‘ ’ in prose; straight quotes only inside code.",
    },
    "en-publication": {
        "language": "en",
        "genre": "publication",
        "shenjiao": "universal",
        "lint": [
            ("apple", {"en", "both"}, {"punctuation", "spacing", "style"}),
            ("redhat", {"en", "both"}, {"punctuation", "spacing", "style"}),
            ("mdnen", {"en", "both"}, {"punctuation", "spacing", "style"}),
            ("mdnzh", {"en"}, {"punctuation", "spacing", "style"}),
            ("msbias", {"en", "both"}, None),
        ],
        "house": [HOUSE_EN_CURLY, HOUSE_EN_APOSTROPHE, HOUSE_EN_SINGLE_SPACE, HOUSE_EN_OXFORD],
        "quote_convention": "Curly quotes “ ” ‘ ’ in prose; straight quotes only inside code.",
        "notes": "Publication methodology is inherited from the zh publication system (审校工作规范); vendor terminology rules are excluded as too product-specific for general publications (bias-free terminology kept).",
    },
}

# Doc-tooling rules that make no sense for prose articles in any genre.
GLOBAL_EXCLUDE = {
    "TW-zhtech-style-filename-lowercase-hyphen",  # source-file naming, not prose
}

# Upstream pattern bugs fixed at compile time (found in iteration-1 evals).
PATTERN_OVERRIDES = {
    # source pattern '[ ]*(——)[ ]*' matches every ——; the rule is about
    # spaces AROUND the dash, so require at least one space.
    "TW-zhtech-punct-dash-no-space": "[ ]+——|——[ ]+",
}

# Rules whose regex needs sentence-level context to be trusted: a hit is a
# review prompt, not an auto-fix (e.g. 全角逗号 between Latin tokens is
# correct inside a Chinese sentence: "480 ms，Redis 命中率…").
CONFIDENCE_OVERRIDES = {
    "TW-zhcopy-punct-english-halfwidth": "heuristic",
}


def trim_examples(rule_src, cap=2):
    ex = rule_src.get("examples")
    if isinstance(ex, dict):
        pos, neg = ex.get("positive") or [], ex.get("negative") or []
    else:
        pos = rule_src.get("positive_examples") or []
        neg = rule_src.get("negative_examples") or []
    if isinstance(pos, str):
        pos = [pos]
    if isinstance(neg, str):
        neg = [neg]
    out = {}
    if pos:
        out["positive"] = pos[:cap]
    if neg:
        out["negative"] = neg[:cap]
    return out or None


def python_ok(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def norm_lint_rule(r, src_file, layer="genre"):
    check = dict(r.get("check") or {})
    ctype = check.get("type", "llm")
    if ctype not in ("regex", "code", "llm"):
        ctype = "llm"
    if r.get("term"):
        ctype = "term"
    sev = r.get("severity", "warning")
    out = {
        "id": r["id"],
        "name": r["name"],
        "category": [r.get("type", "style")] + ([r["category"]] if isinstance(r.get("category"), str) else (r.get("category") or [])),
        "layer": layer,
        "strength": "must" if sev == "error" else "should",
        "severity": sev,
        "check": {
            "type": ctype,
            "description": check.get("description", r["name"]),
        },
        "source": {"file": src_file, "id": r["id"], "doc": r.get("source_doc")},
    }
    if check.get("pattern"):
        pattern = PATTERN_OVERRIDES.get(r["id"], check["pattern"])
        out["check"]["pattern"] = pattern
        out["check"]["flags"] = check.get("flags", "")
        out["check"]["python_ok"] = python_ok(pattern)
    if r["id"] in CONFIDENCE_OVERRIDES:
        out["check"]["confidence"] = CONFIDENCE_OVERRIDES[r["id"]]
    if check.get("exclude_scopes"):
        out["check"]["exclude_scopes"] = check["exclude_scopes"]
    if r.get("term"):
        out["term"] = r["term"]
    if r.get("fix"):
        out["fix"] = r["fix"]
    ex = trim_examples(r)
    if ex:
        out["examples"] = ex
    if r.get("notes"):
        out["notes"] = r["notes"]
    if r.get("source_text"):
        out["source_text"] = r["source_text"][:160]
    return out


def norm_shenjiao_rule(r):
    gates = r.get("gates") or {}
    neg = gates.get("negative") or []
    pos = gates.get("positive") or []
    regex_gate = next((g for g in neg if g.get("type") == "regex" and g.get("pattern")), None)
    all_gates = neg + pos
    orig_types = sorted({g.get("type") for g in all_gates if g.get("type")})
    desc_parts = [g["description"] for g in neg if g.get("description")]
    if not desc_parts:
        desc_parts = [g["description"] for g in pos if g.get("description")]
    strength = (r.get("strength") or {}).get("level", "must")
    out = {
        "id": r["id"],
        "name": r["name"],
        "category": r.get("category") or [],
        "layer": "universal",
        "strength": strength,
        "severity": "error" if strength == "must" else "warning",
        "check": {
            "type": "regex" if regex_gate else "llm",
            "description": " / ".join(desc_parts)[:500],
            "original_gate_types": orig_types,
        },
        "source": {"file": "审校工作规范.rules.json", "id": r["id"]},
    }
    if regex_gate:
        out["check"]["pattern"] = regex_gate["pattern"]
        out["check"]["flags"] = regex_gate.get("flags", "")
        out["check"]["confidence"] = regex_gate.get("confidence", "heuristic")
        out["check"]["python_ok"] = python_ok(regex_gate["pattern"])
        # table rows (`| --- |`) and headings are markup, not prose — the
        # 审校 punctuation gates otherwise misfire on separator hyphens
        out["check"]["exclude_scopes"] = ["code_block", "inline_code", "url", "link_target", "table", "heading"]
    ex = trim_examples(r)
    if ex:
        out["examples"] = ex
    if r.get("notes"):
        out["notes"] = r["notes"]
    if r.get("source_text"):
        out["source_text"] = r["source_text"][:160]
    return out


def main():
    shenjiao_rules = json.loads(SHENJIAO.read_text())["rules"]
    lint_cache = {
        p.stem.replace(".rules", ""): json.loads(p.read_text())["rules"]
        for p in EXTRACTED.glob("*.rules.json")
    }

    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    for bname, cfg in BUNDLES.items():
        rules = []
        replaced = {rid for hr in cfg["house"] for rid in hr.get("replaces", [])}

        # 1. house layer first (highest precedence, review agent sees it on top)
        for hr in cfg["house"]:
            hr = json.loads(json.dumps(hr))  # copy; bundles must not share state
            if hr["check"].get("pattern"):
                hr["check"]["python_ok"] = python_ok(hr["check"]["pattern"])
            rules.append(hr)

        # 2. universal layer: 审校工作规范
        for r in shenjiao_rules:
            cat = "/".join(r.get("category") or [])
            if cfg["shenjiao"] == "all" or cat.startswith(SHENJIAO_UNIVERSAL_CATS):
                rules.append(norm_shenjiao_rule(r))

        # 3. genre layer: lint sources with lang/type filters
        seen_patterns = {}
        for stem, langs, types in cfg["lint"]:
            for r in lint_cache[stem]:
                if r["id"] in replaced or r["id"] in GLOBAL_EXCLUDE:
                    continue
                if r.get("lang") not in langs:
                    continue
                if types and r.get("type") not in types:
                    continue
                nr = norm_lint_rule(r, f"{stem}.rules.json")
                pat = nr["check"].get("pattern")
                if pat and pat in seen_patterns:
                    seen_patterns[pat].setdefault("also_from", []).append(nr["source"])
                    continue
                if pat:
                    seen_patterns[pat] = nr
                rules.append(nr)

        counts = {
            "total": len(rules),
            "regex": sum(1 for r in rules if r["check"]["type"] == "regex"),
            "term": sum(1 for r in rules if r["check"]["type"] == "term"),
            "llm": sum(1 for r in rules if r["check"]["type"] in ("llm", "code")),
            "must": sum(1 for r in rules if r["strength"] == "must"),
        }
        bundle = {
            "bundle": bname,
            "language": cfg["language"],
            "genre": cfg["genre"],
            "version": "1.0.0",
            "compiled_by": "scripts/compile-article-rules.py",
            "layering": "house > genre > universal; markdownlint applies to all genres at runtime",
            "quote_convention": cfg["quote_convention"],
            "sources": ["审校工作规范.rules.json"] + [f"{s}.rules.json" for s, _, _ in cfg["lint"]] + ["house"],
            "counts": counts,
        }
        if cfg.get("notes"):
            bundle["notes"] = cfg["notes"]
        bundle["rules"] = rules
        path = OUT / f"{bname}.rules.json"
        path.write_text(json.dumps(bundle, ensure_ascii=False, indent=1) + "\n")
        bad = [r["id"] for r in rules if r["check"].get("pattern") and not r["check"].get("python_ok")]
        summary.append((bname, counts, path.stat().st_size // 1024, bad))

    for bname, counts, kb, bad in summary:
        print(f"{bname:16} total={counts['total']:3}  regex={counts['regex']:3}  term={counts['term']:3}  llm={counts['llm']:3}  must={counts['must']:3}  {kb}KB")
        if bad:
            print(f"{'':16} non-python-compilable patterns: {bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
