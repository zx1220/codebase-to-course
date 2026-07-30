# Module 4: Hooks——给 AI 装上「自动刹车」的隐形质检员

### Teaching Arc
- **Metaphor:** hook 是汽车上的「自动安全系统」——你不用每次都想着「系安全带」「别超速」,车自己会在关键时刻提醒/限制你。skill 是 AI「主动愿意遵守」的手册,但 hook 是「不管 AI 想不想,事件一发生就强制触发」的自动闸。**这是本模块核心比喻:自动刹车/安全系统,不是餐厅。** 关键对比要讲透:skill 靠 AI 自觉,hook 是被动强制。
- **Opening hook:** 上一节 TDD skill 写得再好,也架不住 AI 偶尔「偷懒跳过」。但如果装一个 hook:「每次 AI 想提交代码前,先自动跑一遍测试,跑不过就拦住」——它就一次都跳不掉。这就是 hook 的威力。
- **Key insight:** hook = 「**在某个事件发生时,自动执行一段检查**」。ECC 用的核心事件有六种(PreToolUse 工具用之前、PostToolUse 工具用之后、Stop AI 停下时等)。一个 hook 配置 = 一个 matcher(匹配什么情况)+ 一段 command(执行什么检查)。理解 matcher + command 这两个零件,你就能看懂所有 hook。
- **"Why should I care?":** hook 是把「希望 AI 永远做的事」从「靠它自觉」升级成「物理上拦不住」的唯一手段。这是 vibe coder 对付「AI 老犯同样错误」的终极武器。

### Code Snippets (pre-extracted)

**Snippet A — 一个最小 hook:运行长命令前提醒开 tmux**

File: the-shortform-guide.md (lines 53-67) — 一个真实可读的最小 hook
```json
{
  "PreToolUse": [
    {
      "matcher": "tool == \"Bash\" && tool_input.command matches \"(npm|pnpm|yarn|cargo|pytest)\"",
      "hooks": [
        {
          "type": "command",
          "command": "if [ -z \"$TMUX\" ]; then echo '[Hook] Consider tmux for session persistence' >&2; fi"
        }
      ]
    }
  ]
}
```

**Snippet B — ECC 实际用的六种 hook 事件(用 step-cards 或 badge 展示)**

```
PreToolUse     ← AI 用某个工具之前(拦/提醒)
PostToolUse    ← AI 用完工具之后(格式化/反馈)
UserPromptSubmit ← 你按下回车那一刻
Stop           ← AI 回答完毕停下来时
PreCompact     ← 上下文被压缩之前
Notification   ← 需要你授权时
```

**Snippet C — 真实的「写 .md 文件前先拦截」hook(展示 matcher 的精确性)**

File: the-shortform-guide.md (lines 346-358) 节选
```json
{
  "PreToolUse": [
    { "matcher": "npm|pnpm|yarn|cargo|pytest", "hooks": ["tmux reminder"] },
    { "matcher": "Write && .md file", "hooks": ["block unless README/CLAUDE"] },
    { "matcher": "git push", "hooks": ["open editor for review"] }
  ],
  "PostToolUse": [
    { "matcher": "Edit && .ts/.tsx/.js/.jsx", "hooks": ["prettier --write"] }
  ]
}
```

**Snippet D — hook 的「退码哲学」(来自 RULES.md,讲为什么 hook 能拦)**

File: RULES.md (Hook Format 节选)
```markdown
## Hook Format
- Hooks use matcher-driven JSON registration and shell or Node entrypoints.
- Matchers should be specific instead of broad catch-alls.
- Exit `1` only when blocking behavior is intentional; otherwise exit `0`.
```

### Interactive Elements

- [x] **Data flow animation** — 本模块的 hero visual。演示「AI 想直接 git push → 触发 PreToolUse hook → hook 拦截『先 review』→ 打开编辑器 → 通过后才放行」的完整拦截链。
  - actors: AI、PreToolUse(hook 守卫)、git push(目标动作)、编辑器 review
  - 用 4-5 个 flow-actor,关键步骤是「hook 在动作发生前插入一道关卡」
- [x] **Code↔English translation** — 用 Snippet A(最小 tmux hook)做翻译,把 JSON 拆成「PreToolUse = 事件 / matcher = 什么时候 / command = 做什么」三块讲清。这是本模块必有代码翻译。
- [x] **Pattern cards 或 badge list** — 用 Snippet B 把六种事件做成卡片/徽章,每张配图标 + 一句话。
- [x] **Quiz** — 3-4 题场景型:①「想让 AI 每次 commit 前自动跑测试,这是 skill 还是 hook 的活?为什么」②给你一个 matcher,问它会在什么情况下触发 ③debug 型「hook 配了但没触发,最可能哪错了」(matcher 太宽/太窄)。
- [x] **Callout** — 1-2 个:①「skill 靠自觉,hook 靠强制」的核心对比洞察(这是全课最该记住的一句话之一);②「退码 1 = 拦截,退码 0 = 放行」的 aha(讲清 hook 怎么「拦」)。

### Reference Files to Read

- `references/interactive-elements.md` → "Message Flow / Data Flow Animation"、"Code ↔ English Translation Blocks"、"Pattern/Feature Cards"、"Permission/Config Badges"、"Multiple-Choice Quizzes"、"Callout Boxes"
- `references/content-philosophy.md` → 全文
- `references/gotchas.md` → 全文(特别注意:flow-animation 的 data-steps 里**不能有单引号**,否则 JSON 解析失败,整个动画失效——所有 label 文案用中文/双引号,避免撇号)

### Connections

- **Previous module:** 「Skills」——形成鲜明对比:skill 是 AI 主动遵循的手册,hook 是被动强制的闸。本模块开头要回收这个对比。
- **Next module:** 「装一套属于你的 ECC」——讲完两大核心角色(skill/hook),最后一模块讲怎么把这些东西按需装进你的工具,以及为什么同一套 ECC 能跨 Claude Code / Cursor / Codex 通吃。
- **Tone/style notes:** 偶数模块用稍浅暖色背景。中文输出。⚠️ flow-animation 的 `data-steps` label **绝不可含单引号 `'` 或撇号**,用中文标点或 `&apos;`。给「hook/matcher/PreToolUse/PostToolUse/exit code/CLI」等词加 tooltip。
