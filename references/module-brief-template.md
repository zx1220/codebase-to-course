# Module Brief Template

> **When to read this:** During Phase 2.5 (planning checkpoint) for complex codebases. Fill in one brief per module, save to `course-name/briefs/0N-slug.md`. Each brief gives a parallel agent everything it needs to write one module without reading the codebase or SKILL.md.

---

## Module N: [Title]

### Teaching Arc
- **Metaphor:** [A fresh, specific metaphor unique to this module — follow the rules in `references/content-philosophy.md` › Metaphors First]
- **Opening hook:** [1 sentence that connects to something the learner already knows from using the app]
- **Key insight:** [The one thing the learner should walk away understanding]
- **"Why should I care?":** [How this helps them steer AI / debug / make decisions]
- **Duration:** ~N min (one pomodoro, 15–25 min — if honestly over 30, propose a split)

### Code Snippets (pre-extracted)

Include the actual code the module will use in code↔English translation blocks. Copy-paste from the codebase with file path and line numbers. The writing agent will use these verbatim — it will NOT re-read the codebase.

File: src/example/file.ts (lines 12-24)
[paste actual code here]

File: src/another/file.ts (lines 45-52)
[paste actual code here]

**Snippet length rule (balance readability against fidelity):** Prefer naturally short, punchy snippets (5-10 lines). But when a longer block (15-25 lines) carries key engineering wisdom — error handling, caching, boundary conditions, a clever guard clause — **do not skip it to keep things short.** Instead, mark it for the writing agent to present as 2-3 consecutive translation blocks, each covering a slice with its own explanation. *Cutting an idea out of the codebase to fit a length budget is the #1 cause of important knowledge being silently dropped.*

### Concept Coverage (anti-drop contract)

List every concept this module **must** teach clearly — the actors, data-flow steps, engineering patterns, or tech-stack choices it owns. This is the brief-stage promise that nothing important gets dropped when the writing agent works alone. The writer lands each one; the quiz tests at least the most decision-relevant ones.

- [ ] Concept 1 — [one line: what it is, why it matters]
- [ ] Concept 2 — [one line]
- [ ] …

> Source these from your Phase 1 analysis (the "What to extract" list: actors, user journey, data flows, clever patterns, tech stack & why). If a key idea from the codebase doesn't belong in *any* module's list here, that's a gap to fix before writing — see the course-level coverage check in SKILL.md › Phase 2.5.

### Interactive Elements

Check which elements this module needs. Include enough detail for the writing agent to build them.

- [ ] **Code↔English translation** — which snippet(s) from above
- [ ] **Quiz** — [number] questions, style: [scenario / debugging / architecture / tracing]. Brief description of each question's angle.
- [ ] **Group chat animation** — actors: [list]. Message flow summary: [who says what to whom, in what order]
- [ ] **Data flow animation** — actors: [list]. Steps: [sequence of highlights and packet movements]
- [ ] **Drag-and-drop** — items: [list], targets: [list]
- [ ] **Cornell summary card** (mandatory, final screen) — cue keywords: [3–5 个]; self-ask questions: [2–3 个，应用型]; Feynman topic: [把什么讲给外行听]; stuck points: [2–3 个，各指向哪个 screen]; plain summary: [1–3 句]
- [ ] **Other** — [architecture diagram, layer toggle, pattern cards, etc.]

### Reference Files to Read

List only the sections the writing agent needs — not the whole file.

- `references/interactive-elements.md` → [section names, e.g., "Multiple-Choice Quizzes", "Group Chat Animation"]
- `references/design-system.md` → [only if needed for specific tokens not in the brief]
- `references/content-philosophy.md` → [always include — agent needs content rules]
- `references/gotchas.md` → [always include — agent needs the checklist]

### Connections

- **Previous module:** [Title — what it covered, so this module can build on it]
- **Next module:** [Title — what it will cover, so this module can set it up]
- **Tone/style notes:** [Any course-wide consistency notes: accent color name, actor naming convention, etc.]
