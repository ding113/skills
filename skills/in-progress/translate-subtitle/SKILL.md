---
name: translate-subtitle
description: Translate subtitle files (SRT, VTT, ASS/SSA) between Chinese and English like a professional subtitler — timestamps, cue ids, and styling tags stay byte-identical; names and terms unified before the first line; lines fit subtitle form (≤25 汉字 per line, ≤5–7 字/秒); subtitle punctuation conventions (no 。，, 「」 quotes, 「…」) enforced by a bundled rule set plus lint script; bilingual subtitles on request. Use whenever the user wants subtitles or captions translated, localized, proofread, or made bilingual (翻译字幕、字幕文件、SRT/VTT/ASS、双语字幕、字幕校对), even if they just drop a subtitle file and say 翻译. NOT for prose articles or docs (translate-article).
---

# Translate Subtitle

Professional subtitle translation, not per-line machine translation. Five
priorities govern every trade-off, in this order: **意思准确、逻辑成立、情绪正确、
中文自然、字幕可读性**. When a constraint below conflicts with another, these
five decide. The deliverable is one file: the translated subtitles, nothing
else.

## Assets

| Path | What it is | When to use |
|---|---|---|
| `rules/subtitle-zh.rules.json` | 36-rule bundle for zh-target subtitles (source_text verbatim from the 翻译原则 prompt; regex/code/nlp/llm gates, must/should strengths) | Consumed by the lint script; `--judgment` prints the llm rules for review |
| `scripts/lint.py` | Parses SRT/VTT/ASS, diffs structure against the source file, runs the bundle's mechanical rules (punctuation, line length, reading speed, consistency) | QC phase, final gate |

## Step 0 — Parse the container, fix what may not change

Detect the format (SRT / VTT / ASS). Everything that is not translatable
payload text is **byte-identical** in the output:

- SRT: cue numbers and timestamp lines.
- VTT: header block, cue ids, timestamps, cue settings, NOTE/STYLE blocks.
- ASS: everything outside `Dialogue:` text — script info, styles, the
  Dialogue prefix fields (Layer/Start/End/Style/Name/Margins/Effect) — plus,
  inside the text, `{\...}` override tags and `\N` line breaks.

Timing is fixed: cues are never merged, split, or retimed. When the natural
translation doesn't fit a cue, condense the wording — cut weak modifiers, drop
what the picture already shows — never overflow, never touch the clock. (The
source's cue segmentation already encodes shot changes and speaker turns;
your job is what goes inside each cue.)

Gather context before translating: title, synopsis, episode/franchise, any
info the user supplied. Don't interrogate the user — infer, and mark what
resists inference (Step 5).

## Step 1 — 名词统一, before the first line

Sweep the whole file for 人名、地名、组织名、术语、专有名词 and recurring
catchphrases (角色口头禅、名场面台词). Then:

- A user-provided glossary is binding — follow it even where you'd choose
  differently.
- Without one, research: official material, 原作设定, Wikipedia, 通行译法.
  Don't invent a rendering when an established one exists.
- One name, one rendering, the whole file. Same for fixed lines: a callback,
  flashback, or re-quoted 名场面 repeats its first rendering **exactly** —
  the audience's recognition depends on it.
- Mind regional norms in the source: UK vs US spelling and idiom, dialect,
  era-specific slang — understand by region, don't generalize.

Keep the glossary; it's part of delivery (series need it for the next
episode).

## Step 2 — Understand, then translate

For every line, first answer: **why does this line exist here?** Scene, who's
talking to whom, their state, the surrounding cues, the plot beat, the works'
setting. Translate with neighboring cues in view — pronouns, running jokes,
and setups/payoffs live across cue boundaries. Self-check: if a rendering
reads illogical, emotionally wrong, mismatched with what's on screen, or
unlike anything a native speaker would say, you almost certainly misread the
source — go back to the source, not the phrasing.

- **Spoken register**: subtitles are speech. Write what the character would
  say in the target language — colloquial, compact, in-character — not
  written prose. Slang, memes, puns, accents, and cultural references
  translate by their real meaning and force, never their surface words.
- **Tone survives**: 犹豫、欲言又止、愤怒、调侃、无奈、坚定、冷淡、幽默、讽刺
  all carry into the translation. A deadpan joke rendered as a flat statement
  is an error even if every word is "correct". Subtext rides on 把/被 句式、
  断句、留白、语序 — not on the source's grammar.
- **Puns and multi-layer lines**: keep the effect if possible; if not, keep
  the layer the plot needs. A short note (≤40 字) is the last resort, not a
  habit.
- **zh diction**: Chinese word order and logic, never the source's; no
  的字堆叠; no 进行/对于/关于 bookishness (on-screen notices exempt); few
  啊/哈/哦/哎 — the voice track already carries the emotion.
- Never fabricate a confident rendering for something you couldn't confirm —
  mark it (Step 5) instead.

## Step 3 — Subtitle form (zh target)

- **One core message per line**; ≤25 汉字 per line; target ≤5 字/秒, hard
  ceiling 7 字/秒. Reading speed beats completeness of words: viewers who
  can't finish the line got nothing.
- **Punctuation**: no 。 or ，inside dialogue lines — rhythm comes from line
  breaks, not commas. Quotes are 「」 (nested 『』). Ellipsis is 「…」, never
  `...` or `···`. Use ? and ! sparingly; when combined, 「?!」 in that order.
  On-screen text (notices, signs, messages) keeps normal punctuation.
- **On-screen text** cues start with 「（」.
- **Stutter**: obvious stammering may use 「…」; light hesitation stays
  unmarked — the audio already carries it.
- **en target**: conventions flip — ~42 characters per line, ≤17 CPS,
  standard English punctuation and sentence case; the zh-specific rules above
  don't apply (the bundle and lint's mechanical checks are zh-only).

## Step 4 — Bilingual subtitles (only when asked)

Format 「原文。译文」 or 「译文。原文」 — the 。 as separator is the one
deliberate exception to the no-。 rule. Keep both sides visually balanced;
condense whichever side runs long. Pass `--bilingual` to the lint so the
separator isn't flagged.

## Step 5 — QC (the review loop)

1. **Mechanical**: `python3 scripts/lint.py OUT --source IN`
   (add `--target en` / `--bilingual` when applicable). Structure errors and
   `exact`-confidence hits are fixes, not suggestions; `heuristic` hits get
   individually inspected (they flag exempt contexts by design — screen text,
   bilingual separators, emotionally-needed 语气词).
2. **Judgment**: `python3 scripts/lint.py --judgment` prints the bundle's
   llm-gate rules. Apply them cue by cue while reading the translation
   **alone, without the source** — the closest a reviewer gets to watching
   without the original audio. Logic holds? Emotion right? Sounds like
   speech? Any line that fails gets flagged with why.
3. **Rewrite loop**: re-translate flagged cues from the source meaning (not
   word-patched), then re-run both passes on the changes. At most **2 rewrite
   rounds**; a clean pass ends the loop early.

## Delivery

- Re-emit the file; the lint's structure check is the proof that cue count,
  timing, ids, and styling are untouched.
- The file contains subtitles and nothing else — no 翻译说明, no analysis, no
  commentary (unless the user asked for them).
- Anything unconfirmable is marked in place as 「※ 此处含义待确认」 rather
  than papered over; list those cues in the conversation with what would
  resolve them.
- Hand over the glossary in the conversation when the work established one
  worth reusing.

No process narration. The subtitles speak for themselves.
