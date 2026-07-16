---
name: article-writing
description: Write publication-quality articles in Simplified Chinese or English across three genres — blog posts, technical documentation, and publications — from raw unstructured material (experiment reports, data, scattered notes, voice-memo fragments) or by reviewing and rewriting an existing draft. Runs a full pipeline - discovery brief, genre-aware drafting, mechanical lint plus editorial review against per-genre rule bundles, web fact-checking, and rewrite loops until zero findings. Use whenever the user wants an article, blog post, doc page, or book/course-grade piece written, rewritten, polished, de-AI-flavored, or proofread to a publication standard (写文章、写博客、技术文档、出版物、润色、审校), even if they just dump raw material and say "write this up". NOT for pure translation (translate-article) or academic papers (paper-writing).
---

# Article Writing

A rule-driven pipeline that turns raw material into a finished article, or puts
an existing draft through publication-grade review. Everything mechanical is
enforced by compiled rule bundles + a lint script; everything editorial follows
distilled methodology and genre profiles. The user sees exactly one checkpoint
(the brief) and one deliverable (a clean article file) — never the intermediate
review process.

## Assets

| Path | What it is | When to read |
|---|---|---|
| `references/methodology.md` | Cross-genre writing methodology (认知交付, titling/Slogan, openings, persona, rhetoric, golden lines, speech-to-prose) | Discovery + drafting |
| `references/profile-<lang>-<genre>.md` | Genre voice: persona modes, structure, sentence patterns, paragraph templates, AI-tell checklist | Drafting + review |
| `rules/<lang>-<genre>.rules.json` | Compiled rule bundle (house > genre > universal layers) | Consumed by scripts, not read wholesale |
| `scripts/lint.py` | Mechanical checker: regex/term rules + markdownlint | Review phase, final gate |

`<lang>-<genre>` is one of: `zh-blog`, `zh-techdoc`, `zh-publication`,
`en-blog`, `en-techdoc`, `en-publication`.

Bundles are compiled artifacts — never edit them by hand. They are recompiled
from the repo's `drafts/` sources via `scripts/compile-article-rules.py`
(repo-only; not shipped with the skill).

## Step 0 — Determine entry point, genre, and language

Infer from the request and material; the user's explicit choice always wins.

- **Genre**: `blog` (personal/team posts, newsletters, opinion + experience
  pieces), `techdoc` (docs, guides, READMEs, how-tos, reference pages),
  `publication` (book chapters, course scripts, magazine-grade essays — the
  highest rigor: national-standard punctuation, publication-level
  fact-checking). When genuinely ambiguous, default to blog and say so in the
  brief — the user corrects it at the checkpoint.
- **Language**: the language the article should be *written in*, not the
  language of the request.
- **Entry point**:
  - *Raw material* (reports, data, notes, fragments) → full pipeline, Phase 1.
  - *Existing draft to polish/review/de-AI-flavor* → the draft already embodies
    discovery and drafting; skip to Phase 3 (or Phase 2 first when the user
    asks for substantive rewriting). Only return to Phase 1 if the user asks to
    reposition the piece.

## Phase 1 — Discovery (发掘)

Read `references/methodology.md` (发掘阶段 sections). Work the raw material
into a **brief**:

1. **Cognitive delivery** (认知交付): the reader's starting point, the ending
   point, and what of the reader's prior assumption gets broken and replaced.
   This is the article's reason to exist — if you cannot state it, the article
   is not ready to be written.
2. **Thinking model + narrative model** (KM163): the former makes the piece
   deep, the latter makes it land.
3. **Slogan + title**: slogan per the four dimensions; title carries suspense;
   for blogs pair title × subtitle as hook × promise.
4. **Narrative angle and stance**: whose side the narrator stands on, which
   persona mode (see the genre profile).
5. **导读与简介**: the layered intro — what the reader will get, in their
   language, not the author's.
6. Genre, language, and output path (user-specified path wins; otherwise
   `<title>.md` in the current working directory).

**Checkpoint (the only one):** present the brief to the user and wait for
confirmation. Everything after this runs unattended to the finished file, so
the brief must carry every decision the user might want to veto. If the user
already approved these points explicitly in the request, don't re-ask.

## Phase 2 — Drafting (内容构造)

Read `references/methodology.md` (内容构造 sections) and the matching
`references/profile-<lang>-<genre>.md`. Then write the full draft to the output
file. While drafting:

- Source every concrete detail from the user's material. Where the material is
  thin, mark the claim for the fact-checker rather than padding with
  generalities — invented specifics are the costliest defect this pipeline can
  produce.
- Choose the persona mode per the profile and keep it stable; per-paragraph
  person shifts need a motive (methodology covers when sliding is allowed).
- Rhetoric with restraint: golden lines belong at the three moments the
  methodology names (narrative peaks, concept explanation, examples) — not in
  every paragraph.
- Follow the bundle's quote convention from the start (「」 for zh
  blog/techdoc, GB/T “” for zh publication, curly quotes for en) — writing it
  right is cheaper than fixing it in review.

## Phase 3 — Fact-check + review (parallel)

Spawn two subagents **in the same message** so they run concurrently. If
subagents are unavailable, do the same two jobs yourself, sequentially,
fact-check first.

**Fact-check agent (read-only — it must not edit the file):**
- Input: the draft + the user's raw material.
- Extract every factual claim (people, dates, places, works, numbers,
  attributions, quotes). 凡事实必核，凡数字必核.
- **Source-fidelity pass first**: diff every number, unit, technical term, and
  proper noun in the draft against the user's material, checking the 口径 —
  not just the value. "6,144 Tensor Cores" in the source becoming "6144 个
  CUDA 核心" in the draft, or "billions" becoming 千亿级, are exactly the
  errors this pass exists to catch: each number keeps its original unit,
  qualifier, and referent, or the deviation is flagged as an `error`. External
  verification cannot catch these — only the source diff can.
- Verify each against web search and reliable knowledge. Classify:
  `error` (source found, draft is wrong — include the correction),
  `unverifiable-load-bearing` (no independent source, claim carries weight —
  typically from the user's own material), `ok`.
- Return the classified list. Corrections get applied by the review side;
  unverifiable items go into the delivery report, never into the article.

**Review agent (may edit the file directly):**
1. Run `python3 scripts/lint.py <file> --genre <lang>-<genre>` and fix every
   violation. `exact`-confidence hits are fixes, not suggestions; `heuristic`
   hits need a human-grade look before touching (they flag line boundaries and
   code-adjacent text by design).
2. Run `python3 scripts/lint.py --genre <lang>-<genre> --judgment` and apply
   those rules paragraph by paragraph, together with the profile's AI-tell
   checklist. Small fixes: edit in place. Structural failures (paragraph
   doesn't deliver its cognitive step, tone breaks persona, hook missing):
   don't patch — flag the paragraph for rewrite with one sentence on what's
   wrong and what the paragraph owes the reader.
3. Apply the fact-checker's `error` corrections.
4. Return: violations fixed, paragraphs flagged for rewrite.

## Rewrite loop

If paragraphs were flagged: spawn a rewriter with the methodology + profile +
the flag reasons; it rewrites only the flagged paragraphs in place. Then run
the review again (lint + judgment pass over the changed text).

Convergence: a review pass with zero findings ends the loop early. At most
**2 rewrite rounds** (3 full review passes) — past that, polish is churn; the
final gate closes out whatever remains.

## Final gate

The last action before delivery is always a review-side pass:
- `lint.py` must exit clean: zero violations, or only heuristic hits that were
  individually inspected and dismissed as false positives.
- Structure complete: 标题、简介、导读、引言、正文、结语, plus footnotes when
  sources are cited.
- No metadata anywhere: no frontmatter, no author/date/genre lines, no review
  traces, no HTML comments. The file contains the article and nothing else.
- Filename is the article title (sanitize only what the filesystem forbids).

## Delivery

Tell the user, in the conversation:
1. Where the file is.
2. The fact-check report — only the `unverifiable-load-bearing` items, each
   with one line: the claim, why it couldn't be verified, what the user should
   confirm. If there are none, say the fact-check came back clean.

Nothing else. No process narration, no list of what was fixed, no quality
self-assessment — the article speaks for itself. Sources cited in the article
appear as Markdown footnotes at the end of the file; that is the only
metadata-like content allowed, because it serves the reader.
