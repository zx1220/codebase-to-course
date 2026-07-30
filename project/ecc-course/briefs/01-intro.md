# Module 1: 这是什么——给 AI 编程工具装一个「操作系统」

### Teaching Arc
- **Metaphor:** ECC 是「AI 编程工具的操作系统」。就像手机出厂时只是块屏幕,装上 iOS/安卓(操作系统)之后才有了打电话、拍照、装 App 的能力——你用的 Claude Code、Cursor、Codex 也是「裸机」,ECC 就是给它们装上的一整套系统:联系人(agents)、技能(skills)、快捷指令(commands)、自动检查(hooks)。**绝不使用「餐厅」比喻。** 这个模块的核心比喻是「操作系统 + 裸机/裸 AI」。
- **Opening hook:** 你每天对 Claude Code 说「帮我做个功能」,它写得时好时坏。但同样一句话,为什么有的人能让 AI 写出生产级代码、你却常被坑?差别不在 AI,在「操作系统」。
- **Key insight:** ECC 不是一个能跑起来的 App,而是一堆「写给 AI 看的说明书」——3300 多个文件,绝大部分是 Markdown。它教 AI 怎么规划、怎么测试、怎么查安全问题。理解了这一点,你就理解了整个项目。
- **"Why should I care?":** 因为你也是用 AI 写代码的人(vibe coder)。搞懂 ECC,你就能看懂「让 AI 变靠谱」的全部套路,自己也能搭一套。

### Code Snippets (pre-extracted)

**Snippet A — SOUL.md(整个项目的「身份证」)**

File: SOUL.md (全文,极短)
```markdown
# Soul

## Core Identity
Everything Claude Code (ECC) is a production-ready AI coding plugin with 30 specialized agents, 135 skills, 60 commands, and automated hook workflows for software development.

## Core Principles
1. **Agent-First** — route work to the right specialist as early as possible.
2. **Test-Driven** — write or refresh tests before trusting implementation changes.
3. **Security-First** — validate inputs, protect secrets, and keep safe defaults.
4. **Immutability** — prefer explicit state transitions over mutation.
5. **Plan Before Execute** — complex changes should be broken into deliberate phases.
```

**Snippet B — 文件类型统计(证明「这是个文档项目,不是 App」)**

```
2495 个 .md 文件     ← 给 AI 看的说明书(占绝大多数)
 405 个 .js 文件     ← 安装和钩子的运行时代码
  62 个 .py 文件     ← 仪表盘 ecc_dashboard.py
  13 个 .hook 文件   ← 钩子配置
共 3322 个文件
```

**Snippet C — RULES.md 里的「铁律」(给 AI 立规矩)**

File: RULES.md (节选)
```markdown
## Must Always
- Delegate to specialized agents for domain tasks.
- Write tests before implementation and verify critical paths.
- Validate inputs and keep security checks intact.

## Must Never
- Include sensitive data such as API keys, tokens, secrets.
- Submit untested changes.
- Bypass security checks or validation hooks.
```

### Interactive Elements

- [x] **Code↔English translation** — 用 Snippet A(SOUL.md)做一段翻译,左 Markdown 右中文逐行解释。这是本模块的核心教学元素。
- [x] **Data flow animation** — 演示「用户一句话 → 装了 ECC 的 Claude Code → 自动触发规划/测试/安全检查 → 产出可靠代码」的接力过程。这是本模块的 hero visual(主视觉)。
  - actors: 用户、Claude Code(装了 ECC)、planner(规划专家)、tdd-guide(测试专家)、security-reviewer(安全专家)、代码成果
  - 6 个 flow-actor,步骤见下方补充说明
- [x] **Quiz** — 3 题,场景型:测「ECC 到底是给谁用的/它由什么组成/为什么文档占绝大多数」。
- [x] **Callout** — 2 个:①「写给 AI 看的说明书」这个反直觉洞察;②「操作系统」比喻的 aha 时刻。

### Reference Files to Read

- `references/interactive-elements.md` → "Code ↔ English Translation Blocks"、"Message Flow / Data Flow Animation"、"Multiple-Choice Quizzes"、"Callout Boxes"、"Numbered Step Cards"、"Icon-Label Rows"
- `references/content-philosophy.md` → 全文(内容规则)
- `references/gotchas.md` → 全文(检查清单)

### Connections

- **Previous module:** 无(这是第一模块)。
- **Next module:** 「认识角色们」——本模块只点出 ECC 是个操作系统,下一模块把里面的「联系人/技能/快捷指令」六大角色挨个介绍。
- **Tone/style notes:** 课程主色 = vermillion(朱红)。模块交替背景:奇数模块用 `var(--color-bg-warm)`。中文输出,代码保留原文。给「操作系统」「Markdown」「vibe coder」「agent」等词加 tooltip。语气像聪明的朋友讲解,不是教授说教。
