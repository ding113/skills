---
name: translate-subtitle
description: Translate subtitle files (SRT, VTT, ASS) between Chinese and English, preserving timestamps, numbering, and styling while respecting line-length and reading-speed conventions. Use when the user wants subtitles or captions translated or proofread.
---

> **Draft** — scope agreed, behavior not yet written. Do not rely on this skill yet.

The planned shape:

1. **Parse the container** — recognize the format (SRT / VTT / ASS); cue IDs, timestamps, and styling tags stay byte-identical.
2. **Translate for the ear** — subtitles are spoken register: colloquial, compact, faithful to intent over literal wording.
3. **Fit the constraints** — line length and reading-speed limits per language convention; split or condense lines rather than overflow.
4. **Keep context in view** — translate with neighboring cues visible so pronouns, jokes, and running references stay coherent.
5. **QC pass** — re-emit the file, confirm it still parses, and check cue count and timing are unchanged.
