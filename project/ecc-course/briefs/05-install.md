# Module 5: 装一套属于你的 ECC——从「菜单」到「跨工具通吃」

### Teaching Arc
- **Metaphor:** 安装 ECC 像在快餐店点一份「套餐」——你不用把 278 个 skills 全装上(那会把 AI 的「脑子」塞爆)。ECC 给你几份预设套餐(minimal/core/developer/security/full),每份套餐勾选若干「模块」(modules),像点 combo 一样按需取用。**这是「点套餐」比喻,聚焦在「按需、不贪多」。** 第二个核心比喻(跨工具):ECC 的 skill 是「同一份说明书」,不同 AI 工具只是「不同的阅读器」——同一本菜谱,微波炉、烤箱、空气炸锅各按自己的方式读,但菜谱本身不变。
- **Opening hook:** 前四节你见识了 ECC 的本事。但真要装,一个问题立刻冒出来:3300 个文件全塞进去,AI 的上下文窗口(它的工作记忆)会被撑爆,反而变笨。怎么办?答案是「按需点套餐」。
- **Key insight:** 两件事:(1)**安装 = 选 profile(套餐) → 它决定装哪些 module(模块) → module 决定复制哪些文件夹**;(2)**ECC 最厉害的设计是「可移植」——`SKILL.md` 这种纯文本说明书可以在 Claude Code / Cursor / Codex / Gemini 之间几乎不改地复用,因为「写给 AI 看的说明书」本来就是通用的。这就是为什么一个人维护能周更支持 7 个工具。
- **"Why should I care?":** ①别贪多——装太多反而让 AI 变笨(上下文窗口是稀缺资源);②理解了可移植性,你写的一套规矩就能在所有 AI 工具里通用,不用每个工具重学一遍。

### Code Snippets (pre-extracted)

**Snippet A — 五份「套餐」(profiles)——用 pattern cards 或 step-cards 展示**

File: manifests/install-profiles.json (lines 3-40 节选)
```json
{
  "minimal": {
    "description": "Low-context setup with rules, agents, commands, but no hook runtime.",
    "modules": ["rules-core", "agents-core", "commands-core", "platform-configs", "workflow-quality"]
  },
  "core": {
    "description": "Minimal harness baseline with commands, hooks, platform configs.",
    "modules": ["rules-core", "agents-core", "commands-core", "hooks-runtime", "platform-configs", "workflow-quality"]
  },
  "developer": {
    "description": "Default engineering profile for most ECC users.",
    "modules": ["rules-core", "agents-core", "commands-core", "hooks-runtime",
                "platform-configs", "workflow-quality", "framework-language", "database", "orchestration"]
  },
  "full": {
    "description": "Complete ECC install with all classified modules.",
    "modules": ["...23 个模块,全装上..."]
  }
}
```

**Snippet B — 一个 module 长什么样(说明它复制哪些文件夹 + 给哪些工具)**

File: manifests/install-modules.json (lines 3-30 节选)
```json
{
  "id": "rules-core",
  "kind": "rules",
  "description": "Shared and language rules for supported harness targets.",
  "paths": ["rules"],
  "targets": ["claude", "claude-project", "cursor", "codex", "zed",
              "gemini", "hermes", "kimi", "qwen", "openclaw"],
  "defaultInstall": true,
  "cost": "light"
}
```

**Snippet C — 一行命令装上(展示易用性)**

File: install.sh (本质,精简表述)
```bash
# 通过 npm 装运行时,然后选套餐
npx ecc-universal install --profile developer

# 或最小化
npx ecc-universal install --profile minimal
```

**Snippet D — 跨工具可移植的「秘密」(来自架构文档)**

File: docs/architecture/cross-harness.md (lines 24-31 节选)
```markdown
## What Travels Unchanged

`SKILL.md` is the most portable unit.

A good ECC skill should:
- use YAML frontmatter with `name`, `description`, and `origin`
- describe when to use the skill
- keep examples repo-relative or generic
- avoid harness-only command assumptions
```

**Snippet E — 「上下文窗口是稀缺资源」的铁律(来自 shortform guide)**

File: the-shortform-guide.md (lines 144-146)
```markdown
Your 200k context window before compacting might only be 70k with too many tools enabled.
Performance degrades significantly.

Rule of thumb: Have 20-30 MCPs in config, but keep under 10 enabled / under 80 tools active.
```

### Interactive Elements

- [x] **Interactive architecture diagram** — 本模块的 hero visual。画一张「ECC 仓库(skills/rules/hooks)在中间,七种 AI 工具(Claude Code/Cursor/Codex/Gemini/Zed/OpenCode/Hermes)围绕四周」的图,点击任一工具显示「它怎么读取这些文件」。中间高亮「SKILL.md = 最可移植的单位」。
- [x] **Code↔English translation** — 用 Snippet B(一个 module 的 JSON)做翻译,讲清 id/paths/targets/cost 四个字段。这是本模块必有代码翻译。
- [x] **Pattern cards** — 用 Snippet A 把 minimal/core/developer/full 四份套餐做成卡片,每张写「适合谁/装哪些模块/轻重」。再加 Snippet E 的「别贪多」做成一张警示卡。
- [x] **Drag-and-drop(可选,推荐)** — 给几个场景(「我只写前端」「我做安全审计」「我全栈都要」),让学习者把场景拖到对应套餐上。若时间紧可改为 quiz。
- [x] **Quiz** — 3-4 题场景型:①「你是全栈开发,该选哪个 profile?」②「为什么不能把 full 全装上?」(上下文窗口)③「同一个 skill 要在 Cursor 和 Codex 都用,核心靠什么?」(可移植性)。
- [x] **Callout** — 1-2 个:①「上下文窗口 = AI 的工作记忆,装太多 = 让 AI 变笨」的关键洞察(全课最重要的实操教训之一);②「说明书(SKILL.md)是通用的,阅读器(工具)不同」的可移植性 aha。结尾再加一个总结性 callout:回顾全课五大要点。

### Reference Files to Read

- `references/interactive-elements.md` → "Interactive Architecture Diagram"、"Code ↔ English Translation Blocks"、"Pattern/Feature Cards"、"Drag-and-Drop Matching"(如做)、"Multiple-Choice Quizzes"、"Callout Boxes"
- `references/content-philosophy.md` → 全文
- `references/gotchas.md` → 全文

### Connections

- **Previous module:** 「Hooks」——前四节讲完了 ECC 是什么、住着谁、两大核心角色。本模块收尾:怎么把这些好东西装到你的工具里。
- **Next module:** 无(这是最后一模块)。结尾要做全课总结,呼应第一模块「ECC = AI 的操作系统」的比喻,形成闭环。
- **Tone/style notes:** 奇数模块用 `var(--color-bg-warm)`。中文输出。架构图里七种工具用不同 actor 颜色。给「profile/module/context window/便携性/portable/harness/compact」等词加 tooltip。结尾语气要有一点「你现在也能搭一套了」的赋能感。
