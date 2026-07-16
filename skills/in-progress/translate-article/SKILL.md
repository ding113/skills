---
name: translate-article
description: Translate articles, blog posts, docs, and web pages between Chinese and English to publication quality — glossary built before translating, meaning-over-syntax rendering with zero translationese, Markdown/links/code kept byte-identical, then a source-fidelity diff and a target-language-only polish pass with mechanical lint. Use whenever the user wants prose translated, localized, or made bilingual (翻译、翻译文章、译成中文、译成英文、中译英、英译中、双语对照), even if they just drop a file or URL and say 翻译一下. NOT for subtitle files (translate-subtitle), and NOT for writing or substantively rewriting original content (article-writing).
---

# Translate Article

A translation pipeline with article-writing's review discipline behind it. The
standard is 神形兼备: the translation reads as if the source author had written
the article in the target language — same argument, same voice, no translation
residue. The user sees one deliverable: a clean file containing only the
translation.

## Assets

| Path | What it is | When to use |
|---|---|---|
| `scripts/check_invariants.py` | Diffs source vs translation: code blocks, inline code, URLs, images, heading structure, footnotes, number survival | Review phase, final gate |

If the article-writing skill is installed alongside this one (try
`../article-writing/scripts/lint.py`, then
`~/.claude/skills/article-writing/scripts/lint.py`), its lint provides the
mechanical target-language check (`--genre <lang>-<register>`). Without it,
apply the translationese checklist below by hand — the pipeline degrades, it
doesn't break.

## Step 0 — Direction, register, output

- **Direction**: explicit user choice wins. Otherwise translate into the
  language the user is speaking to you in.
- **Register**: mirror the source — `blog`, `techdoc`, or `publication`. This
  picks the lint bundle and the quote convention (「」 for zh blog/techdoc,
  GB/T “” for zh publication, curly quotes for en). The translator never
  upgrades or downgrades the register; the source author owns it.
- **Output**: user-specified path wins; otherwise
  `<source-name>.<target-lang>.md` next to the source. Bilingual
  (paragraph-interleaved: source paragraph, then its translation) only when
  asked.
- No checkpoint. Translation has no positioning decisions for the user to
  veto — if direction or register is genuinely undecidable, ask once, then run
  unattended to the finished file.

## Phase 1 — Read everything, then fix the terminology

Translate nothing yet. Read the whole article first: the argument's spine, the
audience, running metaphors, jokes that pay off later, terms that recur. A
sentence translated before you know why it exists is the root cause of most
translation errors — 理解优先 is the first principle, not a slogan.

Then build a working glossary before the first translated sentence, because
retrofitting consistency later never fully works:

- **Stays in English** (zh target): product names, model names, brands, code
  identifiers, established acronyms — "Cursor"、"Gemini-2.5-pro-exp"、"API"
  embed naturally inside the Chinese sentence, never transliterated or
  translated.
- **Recurring terms**: one rendering each. A user-provided glossary is
  binding. Otherwise use 通行译法 — official docs, Wikipedia, established
  community usage; don't coin a rendering when a settled one exists. For a
  term with no settled translation, give the original in parentheses at first
  occurrence, then use your rendering consistently.
- **Region matters**: UK vs US idiom, 大陆 vs 台湾 terminology (视频/影片、
  软件/软体) — pick the variant matching the audience and stay in it.

## Phase 2 — Translate by meaning

Work paragraph by paragraph, not sentence by sentence — the paragraph is the
smallest unit that carries intent. For each:

1. **Understand why it's here** — what it does to the reader (sets up, pays
   off, concedes, pivots). If your translation reads illogical, emotionally
   off, or unlike anything a native speaker would say, the diagnosis is almost
   always that you misread the source, not that you phrased it badly. Research
   what you don't understand (surrounding text, referenced docs, cultural
   background) instead of translating the surface. If genuinely unresolvable,
   mark it and move on — never fabricate a confident rendering.
2. **Say it the way the target language says it** — reorganize sentence
   structure freely as long as meaning survives; supply what the target
   language grammatically needs but the source omits; prefer the natural,
   common expression over the structurally faithful one. Idioms, slang, memes,
   and puns translate by their real meaning and force, not their words; when a
   pun can't keep both layers, keep the one the argument needs, and only then
   consider a translator's note (≤40 字, rare).
3. **Keep the voice** — hedges, irony, enthusiasm, dryness. A wry aside that
   becomes a flat statement is a translation error even if every word is
   "correct". Subtext carries through word order, 把/被 constructions,
   sentence breaks, and omission — not through the source's syntax.

**zh-specific diction** (en→zh): Chinese word order and Chinese logic, never
the source's; break relative-clause chains into short sentences instead of
stacking 前置定语; avoid 的字堆叠; strip 进行/对于/关于-style padding; drop the
pronouns Chinese doesn't need (English repeats "it/they" every clause;
Chinese doesn't). **Front stance and time comments**: English embeds them
mid-clause (", ironically,", ", frankly,", ", six months in,"); Chinese
states them first — 说来讽刺／坦白讲／早在六个月前 — then delivers the
sentence whole. Reproducing the interruption as ——插入语—— keeps the English
skeleton under Chinese words: the subject gets severed from its predicate,
and the sentence reads translated even when every word is natural. Source
punctuation is not a license to keep the source's sentence shape.
**Em dashes don't survive translation**: English leans on the dash for
pivots, asides, and self-corrections ("Not because it's fashionable — it
isn't — but because…"); carrying those dashes into Chinese produces
dash-studded 翻译腔 even when every clause is idiomatic. Re-express the turn
with Chinese connectives — 相反／况且／但／也就是说／何苦 — and split into
short sentences where the dash was doing the joining. In the translation,
破折号 is reserved for its native zh uses (introducing an explanation) and
appears rarely; a paragraph whose dashes track the source's wasn't re-said
in Chinese — it was transliterated, punctuation and all.

**en-specific diction** (zh→en): add the articles and pronouns English
requires; split topic-comment sentences into subject-verb; resist "very"
inflation for 很/非常 (often zero-translate); render 成语 by meaning, not
image, unless the image is the point.

### Formatting invariants

| Byte-identical | Translated |
|---|---|
| Markdown markers and structure, fenced code blocks, inline code, URLs and link targets, image paths, explicit HTML anchors/ids, footnote ids, frontmatter keys | Prose, headings, list items, table cells, blockquote text, link text, image alt text, prose-valued frontmatter fields (title/description/summary) |

- Code comments stay untranslated — they are part of the code — unless the
  user asks for them.
- Intra-document fragment links (`#section`) get updated to match translated
  headings so they don't silently break; explicit anchors stay and win.
- **Numbers keep their 口径**: value, unit, qualifier, and referent all
  survive — "6,144 Tensor Cores" must not become "6144 个 CUDA 核心",
  "billions" must not become 千亿级. The translator has no license to round,
  convert, or re-denominate.

## Phase 3 — Review (two passes, in parallel)

Spawn both as subagents in the same message; if subagents are unavailable, do
the same two jobs yourself sequentially, fidelity first.

**Fidelity pass (read-only — reports, never edits):** walk source and
translation side by side.

- Every source paragraph accounted for; nothing added the author didn't write.
- Every number, unit, proper noun, quote, and attribution keeps its 口径.
- Glossary applied consistently — same term, same rendering, whole file.
- Run `python3 scripts/check_invariants.py SOURCE TRANSLATION`; every error is
  a defect to hand over, every warning gets individually inspected.
- Output: a list of {location, source text, what drifted}.

**Language pass (may edit the file):** put the source away and read the
translation **alone**, start to finish, as a native reader who has never seen
the original. Anything that makes you reach for the source to understand it is
a finding. Then:

1. If article-writing's lint is available, run it with the matching
   `<target-lang>-<register>` bundle and fix the mechanical hits (punctuation,
   spacing, terminology). Apply only language-surface judgment rules; skip
   content-structure rules (认知交付, titling, 导读) — the source author owns
   structure, the translator owns language.
2. Sweep the translationese checklist:
   - zh: 被动滥用 where Chinese wants active voice; a pronoun in every clause;
     的字堆叠; 进行/对于/关于 padding; 「作为一个 X」 openers; 一个/一种 as
     indefinite-article calques; mid-sentence parentheticals calqued from
     English commas (「主语——说来讽刺——谓语」: front the stance comment and
     rejoin the sentence — an insertion splitting subject from predicate is a
     translation tell even when each word reads fine); em-dash pivots and
     asides inherited from the source (「——它并不时髦——」): re-express with
     相反/况且/但 and resegment — sweep every 「——」 in the draft and treat
     each as guilty until natively motivated; other adverbials left in source
     position; sentences that only parse if the reader mentally
     back-translates them; 「让我们」 for "let's"; 弯引号 or `...` where the
     convention says 「」/…。
   - en: missing articles; comma splices inherited from 逗号 chains;
     topic-comment calques ("This problem, we solved it"); doubled
     intensifiers; 成语 rendered image-for-image into nonsense.
3. Apply the fidelity pass's findings.

## Rewrite loop

Paragraphs flagged by either pass get re-translated from the source meaning —
not patched word-by-word, which produces exactly the translationese this skill
exists to prevent. Then review the changed paragraphs again. At most **2
rewrite rounds**; a pass with zero findings ends the loop early.

## Final gate

- `check_invariants.py` exits clean: zero errors, warnings individually
  inspected and dismissed.
- Mechanical lint (when available) exits clean, or only individually-dismissed
  heuristic hits remain.
- The file contains the translation and nothing else — no preface, no
  translator's commentary, no 「以下是译文」, no metadata. Translator's notes,
  if any survived the 40-字 bar, are footnotes.

## Delivery

Tell the user, in the conversation:

1. Where the file is.
2. Unresolved uncertainties, each one line: the source text, why it resisted
   confirmation, the rendering chosen. If none, say so.
3. The glossary, when the article established terminology the user will
   likely reuse (a series, a product's docs).

No process narration, no list of fixes. The translation speaks for itself.
