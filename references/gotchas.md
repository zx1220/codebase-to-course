# Build Checklist — Failure Points to Verify

> **When to read this:** During Phase 3 (writing module HTML) and Phase 4 (review). Run through every item before considering a course complete.
>
> This is a checklist, not a teacher. The **why** behind each item lives in `references/content-philosophy.md` — follow the pointers, don't re-derive the rules here.

## Before you write each module

- [ ] **Snippet fidelity.** Code copied verbatim from the codebase — never trimmed, simplified, or "cleaned up." Prefer naturally short snippets (5-10 lines); if a longer block (15-25 lines) carries key engineering wisdom, split it across 2-3 consecutive translation blocks rather than skipping it. *(see content-philosophy › Code ↔ English Translations)*
- [ ] **Fresh metaphor.** Each module's metaphor fits *this specific concept* and is unique across the course. Caught yourself reaching for "restaurant"/"kitchen" a second time? Stop and find a better one. *(see content-philosophy › Metaphors First)*
- [ ] **No walls of text.** Every screen is ≥50% visual. Any list of 3+ items is cards; any sequence is step cards/flow; any code explanation is a translation block — never a paragraph *about* the code. *(see content-philosophy › Show, Don't Tell)*
- [ ] **Quizzes test application, not memory.** No "what does X stand for?" or "which file handles Y?" — every question presents a new scenario and asks the learner to *apply* what they learned. *(see content-philosophy › Quizzes That Test Application)*

## After each module

- [ ] **Tooltips not clipped.** Translation blocks use `overflow: hidden`; tooltips must use `position: fixed` appended to `document.body` (`main.js` already does this). This is the #1 recurring build bug — verify visually.
- [ ] **Aggressive tooltips.** Any term a non-technical friend wouldn't use in casual conversation is tooltip'd on first use per module (REPL, JSON, flag, entry point, PATH, pip, namespace, function, class, module, PR, E2E, software names…). Err heavily toward too many; skip only terms the learner already knows from their own domain.

## After all modules

- [ ] **One module at a time, verified each.** Writing all modules in one pass makes later modules thin and rushed. For complex codebases, this is what the parallel path + module briefs exist to prevent.
- [ ] **Every module has interactivity.** No module is only text + code blocks. Each has at least one of: quiz, data flow animation, group chat, architecture diagram, or drag-and-drop. These aren't decoration — they're how non-technical learners process information.
- [ ] **Coverage check.** The five mandatory interactive elements are all present somewhere in the course: group chat animation, data/message flow animation, code↔English blocks (≥1/module), quizzes (≥1/module), glossary tooltips.

## Hard CSS rules (don't get these wrong)

- [ ] **Scroll-snap is `proximity`, never `mandatory`.** `mandatory` traps users inside long modules.
- [ ] **`.module` uses `min-height: 100dvh` with `100vh` fallback.**
- [ ] **Never inline `<style>` or `<script>` tags** — styling lives in `styles.css`, behavior in `main.js`. Wire up via class names and `data-*` attributes only.
