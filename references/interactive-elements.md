# Interactive Elements Reference

HTML skeletons for every interactive element type used in courses. Pick the elements that best serve each module's teaching goal.

> **CRITICAL — CSS/JS already exist.** All styling lives in `styles.css` and all behavior lives in `main.js` — both copied verbatim into every course directory. **Never inline `<style>` or `<script>` tags.** Just copy the HTML skeletons below using the exact class names and `data-*` attributes. The engines in `main.js` auto-initialize on page load by scanning for the class names and `data-*` attributes described here.

## Table of Contents
1. [Code ↔ English Translation Blocks](#code--english-translation-blocks)
2. [Multiple-Choice Quizzes](#multiple-choice-quizzes)
3. [Drag-and-Drop Matching](#drag-and-drop-matching)
4. [Group Chat Animation](#group-chat-animation)
5. [Message Flow / Data Flow Animation](#message-flow--data-flow-animation)
6. [Interactive Architecture Diagram](#interactive-architecture-diagram)
7. [Layer Toggle Demo](#layer-toggle-demo)
8. ["Spot the Bug" Challenge](#spot-the-bug-challenge)
9. [Scenario Quiz](#scenario-quiz)
10. [Callout Boxes](#callout-boxes)
11. [Pattern/Feature Cards](#patternfeature-cards)
12. [Flow Diagrams](#flow-diagrams)
13. [Permission/Config Badges](#permissionconfig-badges)
14. [Glossary Tooltips](#glossary-tooltips)
15. [Visual File Tree](#visual-file-tree)
16. [Icon-Label Rows](#icon-label-rows)
17. [Numbered Step Cards](#numbered-step-cards)

---

## Code ↔ English Translation Blocks

The most important teaching element. Shows real code from the project on the left and a plain English translation on the right, line by line.

**HTML:**
```html
<div class="translation-block animate-in">
  <div class="translation-code">
    <span class="translation-label">CODE</span>
    <pre><code>
<span class="code-line"><span class="code-keyword">const</span> response = <span class="code-keyword">await</span> <span class="code-function">fetch</span>(url, {</span>
<span class="code-line">  <span class="code-property">method</span>: <span class="code-string">'POST'</span>,</span>
<span class="code-line">  <span class="code-property">headers</span>: { <span class="code-string">'Authorization'</span>: apiKey }</span>
<span class="code-line">});</span>
    </code></pre>
  </div>
  <div class="translation-english">
    <span class="translation-label">PLAIN ENGLISH</span>
    <div class="translation-lines">
      <p class="tl">Send a request to the URL and wait for a response...</p>
      <p class="tl">We're sending data (POST), not just asking for it (GET)...</p>
      <p class="tl">Include our API key so the server knows who we are...</p>
      <p class="tl">End of the request setup.</p>
    </div>
  </div>
</div>
```

**Rules:**
- Each English line should correspond to 1-2 code lines
- Use conversational language, not technical jargon
- Highlight the "why" not just the "what" — e.g., "Include our API key so the server knows who we are" not "Set the Authorization header"
- Syntax highlighting classes: `.code-keyword`, `.code-string`, `.code-function`, `.code-comment`, `.code-number`, `.code-property`, `.code-operator`, `.code-tag`, `.code-attr`, `.code-value`

---

## Multiple-Choice Quizzes

For testing understanding with instant feedback. Each question has options, one correct answer, and per-question explanations.

**Wiring:** `main.js` exposes `window.selectOption(btn)`, `window.checkQuiz(containerId)`, and `window.resetQuiz(containerId)`. Call them via `onclick`. Per-question explanations go in `data-explanation-right` and `data-explanation-wrong` on the `.quiz-question-block`.

**HTML:**
```html
<div class="quiz-container" id="quiz-module3">
  <div class="quiz-question-block"
       data-correct="option-b"
       data-explanation-right="Exactly — because X is responsible for Y in this architecture."
       data-explanation-wrong="Not quite. Think about where Y lives in the codebase...">
    <h3 class="quiz-question">Question text here?</h3>
    <div class="quiz-options">
      <button class="quiz-option" data-value="option-a" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>Answer A</span>
      </button>
      <button class="quiz-option" data-value="option-b" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>Answer B (correct)</span>
      </button>
      <button class="quiz-option" data-value="option-c" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>Answer C</span>
      </button>
    </div>
    <div class="quiz-feedback"></div>
  </div>

  <button class="quiz-check-btn" onclick="checkQuiz('quiz-module3')">Check Answers</button>
  <button class="quiz-reset-btn" onclick="resetQuiz('quiz-module3')">Try Again</button>
</div>
```

---

## Drag-and-Drop Matching

For matching concepts to descriptions. Supports both mouse (HTML5 Drag API) and touch.

**Wiring:** `main.js` auto-initializes every `.dnd-container` on page load. `window.checkDnD(containerId)` and `window.resetDnD(containerId)` are called via `onclick` — **pass the container's `id`** (not a bare call).

**HTML:**
```html
<div class="dnd-container" id="dnd-module3">
  <div class="dnd-chips">
    <div class="dnd-chip" draggable="true" data-answer="actor-a">Actor A</div>
    <div class="dnd-chip" draggable="true" data-answer="actor-b">Actor B</div>
    <div class="dnd-chip" draggable="true" data-answer="actor-c">Actor C</div>
  </div>
  <div class="dnd-zones">
    <div class="dnd-zone" data-correct="actor-a">
      <p class="dnd-zone-label">Description for Actor A</p>
      <div class="dnd-zone-target">Drop here</div>
    </div>
    <!-- more zones -->
  </div>
  <button onclick="checkDnD('dnd-module3')">Check Matches</button>
  <button onclick="resetDnD('dnd-module3')">Reset</button>
</div>
```

> **Common bug:** forgetting to pass the container `id` — `onclick="checkDnD()"` (no arg) silently fails because `main.js` needs the id to locate the container. Always write `checkDnD('dnd-<id>')` and `resetDnD('dnd-<id>')`, and give the `.dnd-container` a matching `id`.

---

## Group Chat Animation

iMessage/WeChat-style chat showing components "talking" to each other. Messages appear one by one with typing indicators.

**Wiring:** `main.js` auto-initializes every `.chat-window` on page load. Give each chat window a unique `id`. Control buttons need these classes: `.chat-next-btn`, `.chat-all-btn`, `.chat-reset-btn`. The typing indicator avatar element should have `id="{chatWindowId}-typing-avatar"` or simply be the first `.chat-avatar` inside `.chat-typing`.

**HTML:**
```html
<div class="chat-window" id="chat-module2">
  <div class="chat-messages">
    <div class="chat-message" data-msg="0" data-sender="actor-a" style="display:none">
      <div class="chat-avatar" style="background: var(--color-actor-1)">A</div>
      <div class="chat-bubble">
        <span class="chat-sender" style="color: var(--color-actor-1)">Actor A</span>
        <p>Hey Background, I need the data for this item.</p>
      </div>
    </div>
    <!-- more messages... -->
  </div>

  <div class="chat-typing" id="chat-typing" style="display:none">
    <div class="chat-avatar" id="typing-avatar">?</div>
    <div class="chat-typing-dots">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  </div>

  <div class="chat-controls">
    <button class="btn chat-next-btn">Next Message</button>
    <button class="btn chat-all-btn">Play All</button>
    <button class="btn chat-reset-btn">Replay</button>
    <span class="chat-progress"></span>
  </div>
</div>
```

---

## Message Flow / Data Flow Animation

Step-by-step visualization of data moving between components. User clicks "Next Step" to advance.

**Wiring:** `main.js` auto-initializes every `.flow-animation` on page load. Pass steps as JSON in `data-steps`. Each step object: `{ highlight: "flow-actor-id", label: "description", packet: true, from: "actor-id-suffix", to: "actor-id-suffix" }`. Actor element IDs must be `flow-actor-1`, `flow-actor-2`, etc. Control buttons need classes `.flow-next-btn` and `.flow-reset-btn`.

> **⚠️ Single quotes in step labels will break parsing.** The `data-steps` attribute is delimited by single quotes (`data-steps='[...]'`), so any single quote inside a label (e.g. `"the user's request"`) will terminate the attribute early and cause `JSON.parse` to fail silently — the entire animation will stop working. Either avoid apostrophes in labels, replace them with `&apos;`, or rewrite the attribute using double-quote delimiters with escaped inner quotes (`data-steps="[{\"label\":\"...\"}]"`).

**HTML:**
```html
<div class="flow-animation" data-steps='[
  {"highlight":"flow-actor-1","label":"User clicks the button"},
  {"highlight":"flow-actor-1","label":"Frontend sends request","packet":true,"from":"actor-1","to":"actor-2"},
  {"highlight":"flow-actor-2","label":"Backend calls the database","packet":true,"from":"actor-2","to":"actor-3"}
]'>
  <div class="flow-actors">
    <div class="flow-actor" id="flow-actor-1">
      <div class="flow-actor-icon">A</div>
      <span>Actor 1</span>
    </div>
    <div class="flow-actor" id="flow-actor-2">
      <div class="flow-actor-icon">B</div>
      <span>Actor 2</span>
    </div>
    <div class="flow-actor" id="flow-actor-3">
      <div class="flow-actor-icon">C</div>
      <span>Actor 3</span>
    </div>
  </div>

  <div class="flow-packet" id="flow-packet"></div>

  <div class="flow-step-label" id="flow-label">Click "Next Step" to begin</div>

  <div class="flow-controls">
    <button class="btn flow-next-btn">Next Step</button>
    <button class="btn flow-reset-btn">Restart</button>
    <span class="flow-progress"></span>
  </div>
</div>
```

---

## Interactive Architecture Diagram

Full-system diagram where hovering/clicking a component shows a description tooltip.

**Wiring:** `main.js` binds click handlers to every `.arch-component` on page load.

**HTML:**
```html
<div class="arch-diagram">
  <div class="arch-zone arch-zone-browser">
    <h4 class="arch-zone-label">Browser</h4>
    <div class="arch-component" data-desc="Injects UI into the web page, reads DOM, captures user actions">
      <div class="arch-icon">📄</div>
      <span>Component A</span>
    </div>
    <!-- more components -->
  </div>
  <div class="arch-zone arch-zone-external">
    <h4 class="arch-zone-label">External Services</h4>
    <!-- API cards -->
  </div>
  <div class="arch-description" id="arch-desc">Click any component to learn what it does</div>
</div>
```

---

## Layer Toggle Demo

Shows how different layers (e.g., HTML/CSS/JS, or data/logic/UI) build on each other. Three tabs switch between views.

**Wiring:** `window.showLayer(layerId, btn)` — call via `onclick`, passing the target layer id and `this`.

**HTML:**
```html
<div class="layer-demo">
  <div class="layer-tabs">
    <button class="layer-tab active" onclick="showLayer('html', this)">HTML</button>
    <button class="layer-tab" onclick="showLayer('css', this)">+ CSS</button>
    <button class="layer-tab" onclick="showLayer('js', this)">+ JS</button>
  </div>
  <div class="layer-viewport">
    <div class="layer" id="layer-html" style="display:block">
      <!-- Raw unstyled version -->
    </div>
    <div class="layer" id="layer-css" style="display:none">
      <!-- Styled version -->
    </div>
    <div class="layer" id="layer-js" style="display:none">
      <!-- Interactive version -->
    </div>
  </div>
  <p class="layer-description" id="layer-desc">This is the raw HTML...</p>
</div>
```

---

## "Spot the Bug" Challenge

Show code with a deliberate bug. User clicks the buggy line. Reveal explains the issue.

**Wiring:** `window.checkBugLine(el, isCorrect)` — call via `onclick`. Put the explanation in `data-explanation` on the correct line and optional `data-hint` on wrong lines.

**HTML:**
```html
<div class="bug-challenge">
  <h3>Find the bug in this code:</h3>
  <div class="bug-code">
    <div class="bug-line" data-line="1" onclick="checkBugLine(this, false)">
      <span class="line-num">1</span>
      <code>chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {</code>
    </div>
    <div class="bug-line" data-line="2" onclick="checkBugLine(this, false)">
      <span class="line-num">2</span>
      <code>  if (msg.action === 'fetchData') {</code>
    </div>
    <div class="bug-line bug-target" data-line="3" onclick="checkBugLine(this, true)"
         data-explanation="The listener uses an async operation (fetch) but doesn't return true. Chrome closes the message channel before the response can be sent. Fix: add return true; at the end.">
      <span class="line-num">3</span>
      <code>    fetch(url).then(r => r.json()).then(data => sendResponse(data));</code>
    </div>
    <div class="bug-line" data-line="4" onclick="checkBugLine(this, false)">
      <span class="line-num">4</span>
      <code>  }</code>
    </div>
    <div class="bug-line" data-line="5" onclick="checkBugLine(this, false)">
      <span class="line-num">5</span>
      <code>});</code>
    </div>
  </div>
  <div class="bug-feedback" id="bug-feedback"></div>
</div>
```

---

## Scenario Quiz

"What would a senior engineer do?" — situational questions with explanations.

Same HTML/JS pattern as Multiple-Choice Quizzes, but with longer scenario descriptions and more detailed explanations. Wrap each question in a scenario context block:

```html
<div class="scenario-block">
  <div class="scenario-context">
    <span class="scenario-label">Scenario</span>
    <p>Your app processes a 3-hour podcast transcript. The API has a 16,000 token limit. What do you do?</p>
  </div>
  <!-- quiz-question-block here (same pattern as Multiple-Choice Quizzes) -->
</div>
```

---

## Callout Boxes

"Aha!" moments — universal CS insights. Max 2 per module.

**Variants:**
- `callout-accent`: vermillion left border, light accent background (for CS insights)
- `callout-info`: teal left border, light info background (for "good to know")
- `callout-warning`: red left border, light error background (for common mistakes)

```html
<div class="callout callout-accent">
  <div class="callout-icon">💡</div>
  <div class="callout-content">
    <strong class="callout-title">Key Insight</strong>
    <p>This pattern — splitting responsibilities into focused roles — is one of the most important ideas in software engineering. Engineers call it "separation of concerns."</p>
  </div>
</div>
```

---

## Pattern/Feature Cards

Grid of cards highlighting engineering patterns, tech stack components, or key concepts. Use an inline `border-top` color to tie each card to its actor color.

```html
<div class="pattern-cards">
  <div class="pattern-card" style="border-top: 3px solid var(--color-actor-1)">
    <div class="pattern-icon" style="background: var(--color-actor-1)">🔄</div>
    <h4 class="pattern-title">Caching</h4>
    <p class="pattern-desc">Store results to avoid redundant work — like keeping leftovers instead of cooking a new meal every time.</p>
  </div>
  <!-- more cards -->
</div>
```

---

## Flow Diagrams

Static horizontal flow (no animation). Arrows rotate to `↓` on mobile via CSS transform.

```html
<div class="flow-steps">
  <div class="flow-step">
    <div class="flow-step-num">1</div>
    <p>User clicks button</p>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-num">2</div>
    <p>Component A detects click</p>
  </div>
  <div class="flow-arrow">→</div>
  <!-- more steps -->
</div>
```

---

## Permission/Config Badges

For annotating config files, permissions, or settings as a visual list.

```html
<div class="badge-list">
  <div class="badge-item">
    <code class="badge-code">storage</code>
    <span class="badge-desc">Save data between sessions (like browser bookmarks)</span>
  </div>
  <div class="badge-item">
    <code class="badge-code">activeTab</code>
    <span class="badge-desc">Access the currently open tab (only when the user clicks)</span>
  </div>
</div>
```

---

## Glossary Tooltips

The most important accessibility feature for non-technical learners. Any technical term in the course text should be wrapped in a tooltip that shows a plain-English definition on hover (desktop) or tap (mobile). The learner never has to leave the page or Google anything.

**Wiring:** `main.js` auto-binds hover/click handlers to every `.term` on page load. Tooltips use `position: fixed` and are appended to `document.body` (never clipped by ancestor `overflow: hidden`). Just provide the definition in `data-definition`.

**HTML — mark up terms inline:**
```html
<p>The extension uses a
  <span class="term" data-definition="A service worker is a background script that runs independently of the web page — like a behind-the-scenes assistant that's always on, even when you're not looking at the page.">service worker</span>
  to handle API calls.
</p>
```

**Rules:**
- Mark up EVERY technical term on first use in each module (API, DOM, callback, async, endpoint, middleware, etc.)
- Keep definitions to 1-2 sentences max, in everyday language
- Use a metaphor in the definition when it helps — e.g., "A **callback** is like leaving your phone number at a restaurant so they can call you when your table is ready"
- Don't mark the same term twice within the same screen — only on first appearance per module
- The dashed underline should be subtle enough not to distract but visible enough that curious learners discover it

---

## Visual File Tree

Use instead of paragraphs listing "this folder does X, that folder does Y." Much easier to scan.

```html
<div class="file-tree">
  <div class="ft-folder open">
    <span class="ft-name">app/</span>
    <span class="ft-desc">Pages and API routes</span>
    <div class="ft-children">
      <div class="ft-folder">
        <span class="ft-name">api/</span>
        <span class="ft-desc">Backend endpoints the frontend calls</span>
      </div>
      <div class="ft-file">
        <span class="ft-name">layout.tsx</span>
        <span class="ft-desc">The shell that wraps every page</span>
      </div>
    </div>
  </div>
  <div class="ft-folder">
    <span class="ft-name">components/</span>
    <span class="ft-desc">Reusable UI building blocks</span>
  </div>
  <div class="ft-folder">
    <span class="ft-name">lib/</span>
    <span class="ft-desc">Shared logic and utilities</span>
  </div>
</div>
```

---

## Icon-Label Rows

For listing components, features, or concepts visually. Replaces bullet-point paragraphs.

```html
<div class="icon-rows">
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-1)">🖥️</div>
    <div>
      <strong>Frontend (Next.js)</strong>
      <p>What the user sees and interacts with</p>
    </div>
  </div>
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-2)">⚡</div>
    <div>
      <strong>API Routes</strong>
      <p>Backend logic that runs on the server</p>
    </div>
  </div>
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-3)">🗄️</div>
    <div>
      <strong>Database (Supabase)</strong>
      <p>Where all the data is stored permanently</p>
    </div>
  </div>
</div>
```

---

## Numbered Step Cards

For sequences that would otherwise be a numbered paragraph list. Visual, scannable, and each step stands alone.

```html
<div class="step-cards">
  <div class="step-card">
    <div class="step-num">1</div>
    <div class="step-body">
      <strong>User pastes a YouTube URL</strong>
      <p>The frontend captures the URL and extracts the video ID</p>
    </div>
  </div>
  <div class="step-card">
    <div class="step-num">2</div>
    <div class="step-body">
      <strong>API fetches the transcript</strong>
      <p>A server-side route calls an external service to get the video's text</p>
    </div>
  </div>
  <div class="step-card">
    <div class="step-num">3</div>
    <div class="step-body">
      <strong>AI analyzes the content</strong>
      <p>The transcript is sent to an AI model that extracts key moments</p>
    </div>
  </div>
</div>
```
