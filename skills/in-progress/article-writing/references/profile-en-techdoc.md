# Style Profile: English Technical Documentation

Write for a reader mid-task in a second language: “you” plus imperative, simple present, active voice, one idea per sentence.
Front-load everything — keywords in headings, actions at the start of steps, conclusions at the start of paragraphs.
Structure is a contract: overview → prerequisites → numbered steps → explained examples → sparing notes and warnings.

## Voice

Crisp, warm, verb-first. Six moves, each with the reason it works:

- **Bigger ideas, fewer words.** Shorter is always better; every extra word taxes a scanning reader. “If you're ready to purchase Office 365 for your organization, contact your Microsoft account representative.” becomes “Ready to buy? Contact us.”
- **Write like you speak.** Read the text aloud; if it sounds like a machine, rewrite. Replace the error string “Invalid ID” with “You need an ID that looks like this: someone@example.com” — the second tells the reader what to do.
- **Project friendliness.** Use contractions — it’s, you’ll, you’re, we’re, let’s. Stiff uncontracted prose reads as generated boilerplate.
- **Get to the point fast.** Lead with what matters most, front-load keywords for scanning, and make choices and next steps obvious.
- **Start with verbs; revise weak writing.** Cut “you can” when it adds nothing; avoid “there is / there are / there were” openers. “You can access Office apps across your devices, and you get online file storage and sharing.” becomes “Store files online, access them from all your devices, and share them with coworkers.”
- **Be brief.** Give readers just enough to decide and act confidently, then stop.

## Audience: global, non-native, mid-task

Assume the page will be read in many countries, by readers whose primary language isn’t English, often through machine translation — and while the terminal or UI is open. Every rule below exists because it survives translation and interruption:

- Use simple present tense; avoid “will”. “The window opens …”, not “The window will open …” — readers consult docs during the task, not before it, and present tense is the easiest tense to translate.
- Keep sentences under about 40 words, one complete thought each. Split run-ons with periods rather than commas.
- Avoid stacking more than three nouns: “Standard system log management configuration rotates log files every week.” → “Standard configuration of system log management rotates log files every week.” Noun stacks have multiple plausible parses in translation.
- Avoid a noun followed by an -ing verb, which is ambiguous to translate: “The nmap utility scans privileged TCP ports looking for services.” → “The nmap utility scans privileged TCP ports to look for services.”
- Avoid ambiguous “may” and “should” — each carries a double meaning (permission vs. possibility, advice vs. obligation). Write “can” for ability, “might” for possibility, “must” for requirement.
- Cut redundant words: “actually”, “really”, “simply”, “very”; “revert back” → “revert”; “located on” → “on”. “Simply” also insults the reader whose step just failed.
- No idioms, slang, or culture-bound metaphors; they break translation and exclude readers.

## Active voice, and when passive earns its place

Prefer active voice: “Type ... to start Linuxconf”, not “Linuxconf can be started by typing ...”. Active is livelier, shorter, and names who does what. Passive is acceptable in two cases: release-note-style material, and when the acted-on thing is the true topic and belongs at the head of the sentence — “The Developer Center, a site for reference material and other resources, has been introduced to the OpenShift website.” beats the active version because the Developer Center is the news. Decide case by case; consistency beats dogma.

## Structure: which block, when

- **Opening paragraph (before any heading).** Summarize what the page covers and what the reader can do afterward, so they can decide in seconds whether they are on the right page. In guides and tutorials, also state prerequisite knowledge and link the technologies discussed. Aim for one tight paragraph: too short leaves the reader guessing what the feature is; too long buries the page’s purpose under detail that belongs in sections.
- **Abstract formula (what / how / why-and-who), one sentence each:** “The Red Hat Satellite 5.6 API Guide is a full reference for Satellite's XMRPC API. The guide explains each API method and demonstrates examples of data models for input and output. This publication provides a basis for administrators and developers to write custom scripts and to integrate Red Hat Satellite with third-party applications.”
- **Prerequisites.** List required knowledge, access, versions, and installs before the first step — never let a reader discover a missing dependency at step 3.
- **Task steps (procedures).** Numbered, titled, imperative, one action per step. Use numbers only when order matters or steps are referenced elsewhere; otherwise use bullets.
- **Examples.** Every example is a sandwich: a short heading naming the scenario, a lead-in stating what to watch for, the code, then an explanation of the result and how it works. Readers copy examples straight into production code — handle errors, and don’t skimp on details.
- **Notes and warnings.** Escalate deliberately: a Note brings extra information to the reader’s attention; an Important marks information that must not be overlooked; a Warning flags destructive or irreversible consequences. Keep them brief and rare — every admonition you add devalues the others.

## Sentence patterns by function

Reuse the shape; swap the content.

**Overviews and intros**

- “The CanvasRenderingContext2D method strokeText(), part of the Canvas 2D API, strokes (draws the outlines of) the characters of a specified string, anchored at the position indicated by the given X and Y coordinates.” — what it is, which family it belongs to, and what it does, in one sentence.
- “For more details and examples, see the Text section on the Drawing graphics page as well as our main article on the subject, Drawing text.” — close an overview by pointing deeper instead of inlining everything.
- “Save time by creating a document template that includes the styles, formats, and page layouts that you use most often. Then use the template whenever you create a new document.” — benefit first, then the action.

**Steps**

- “Click the Edit button.” — imperative mood; identify the UI element by its label and its type.
- “Press and hold the tile.” — one action, no throat-clearing.
- “Either click Start or press the Windows key to activate the Start menu.” — offer alternatives in a single sentence, not two steps.
- “To access your programs, click Start.” — put the purpose clause first when the goal disambiguates the action.

**Example lead-ins**

- “In the following example, two cascade layers are defined in the CSS, base and special.” — name exactly what the reader should watch for.
- “In the following code example, we animate a circle using CSS transitions.” — say “following”, never “below”: spatial words break screen readers, translations, and reflowed layouts.
- Head the example with its scenario: “Using offset printing”, “Reverting to style in previous layer”.

**Warnings, notes, recommendations**

- Warning, for destructive operations: “alert the reader to potential changes, such as files being removed, and not to perform the operation unless fully aware of the consequences.”
- Important, for easily missed but vital information: it “might not change anything that the user is doing”, but skipping it has a cost — say that cost.
- Recommendations name the recommender: “Red Hat recommends that you generate a service account for each microservice in your project.” — never “It is recommended to generate a service account for each microservice in your project.” Ownerless recommendations dodge accountability and translate poorly.

**Transitions and cross-references**

- “Refer to the Accessibility section later on this page.” — not “the section below”.
- “This concept is explained in the earlier section titled Creating a media query.” — not “the section above”.
- “Learn more about how to order flex items.” — descriptive link text; never “Click here” or “Read this article”, which strand assistive-technology users.

## Headings and lists

- Sentence-style capitalization: “Find a Microsoft partner”, not “Find a Microsoft Partner”. No period or colon at the end of a heading: “Move a tile”, not “Move a tile.”
- Front-load the keyword; make task headings verb-first (“Move a tile”) and example headings gerund-scenario (“Using offset printing”).
- Never place two headings with no intervening text — if you can’t write a meaningful sentence between them, one of the headings is redundant.
- Never use a bare “Introduction” heading; it says nothing and collides in translation memory. The opening paragraph does that job; reserve “Introduction to X” for introducing a product, not a document.
- Bulleted list: unordered, three or more entries. Numbered list: order matters or entries are referenced elsewhere. Definition list: terms, options, parameters — usually better than a table, which earns its keep only when the information truly needs a grid.
- Don’t format a single sentence as a bulleted list; don’t nest more than two levels.

## Inclusive language: principles, not word lists

- Name the action or function, not a metaphor for it: “allowlist” describes what the list does; “whitelist” encodes a good/bad color metaphor. Fixing by principle catches terms no list anticipated.
- Use singular “they”, or better, rewrite to remove pronouns entirely: “A confirmation dialog box that asks the user for permission to use the webcam appears.” — grammatically cleaner and easier to translate than any pronoun choice.
- Avoid violent and ableist idioms (“kill two birds with one stone” → “solve two problems at once”; drop “sanity check”) and superlative job metaphors (“ninja”, “rockstar”, “guru”).
- Avoid spatial and directional references (“above”, “below”, “left”, “right”) — layouts reflow, screen readers linearize, and translations reorder. Refer to sections by title and to examples by what they demonstrate.

## Bad smells: AI-written tech docs (review checklist)

- [ ] “It is recommended …”, “It should be noted that …” — ownerless hedging where a named recommender or plain imperative belongs.
- [ ] Future-tense narration (“this will create …”, “you will see …”) where simple present belongs.
- [ ] “simply”, “just”, “easily”, “seamlessly”, “powerful”, “robust” — marketing adverbs and adjectives inside task prose.
- [ ] Symmetry everywhere: every section exactly three bullets, every bullet a bolded phrase plus colon, every step the same length.
- [ ] An opener that restates the title (“In this article, we will explore …”) instead of saying what the reader will be able to do.
- [ ] Admonition inflation: a Note or Warning on every screen, none of them consequential.
- [ ] Examples with no lead-in and no result explanation; code that ignores errors or uses placeholder values without saying so.
- [ ] Vague links (“click here”, “read more”) and spatial references (“as shown above”).
- [ ] A closing “Conclusion” section that summarizes what was just read instead of pointing to the next task or deeper reference.
- [ ] Uniform sentence length and zero contractions — grammatically perfect, rhythmically dead.

## House rule

Use curly quotes and apostrophes in prose (“ ” ‘ ’); straight quotes belong only in code, commands, file names, and sample output.
