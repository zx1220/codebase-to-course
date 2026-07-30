# Module 2: 认识角色们——一个 ECC 里有哪六种「同事」

### Teaching Arc
- **Metaphor:** ECC 是一家「AI 开发公司」,里面有六种角色各司其职:**agents**(专家同事)、**skills**(可复用的 SOP 工作手册)、**commands**(你喊的快捷口令)、**hooks**(自动质检员)、**rules**(公司铁律)、**MCPs**(外线电话,连外部服务)。**不要用「餐厅」。** 这个模块的比喻是「一家公司里的六种同事/岗位」。
- **Opening hook:** 上一节你知道了 ECC 是个「操作系统」。那这个系统里到底住了谁?点开 `agents/` 文件夹,里面有 67 个 `.md` 文件——每一个都是一位「专家同事」的简历。
- **Key insight:** 六种角色不是平行堆叠的,它们是一条「指挥链」:你喊 command → 系统派给 agent → agent 按 skill 干活 → 全程被 hook 盯着 → 大家都守 rule → 需要外部数据时走 MCP。记住这条链,你就知道下次该改哪个文件。
- **"Why should I care?":** 下次你跟 AI 说「它老是忘记写测试」,你就知道该去 `rules/` 加条铁律,而不是干着急。知道角色分工 = 能精准「调试」你的 AI。

### Code Snippets (pre-extracted)

**Snippet A — 一个 agent 长什么样(简历 = YAML 头 + 提示词)**

File: agents/planner.md (lines 1-6)
```yaml
---
name: planner
description: Expert planning specialist for complex features and refactoring. Use PROACTIVELY when users request feature implementation, architectural changes, or complex refactoring.
tools: ["Read", "Grep", "Glob"]
model: opus
---
```

**Snippet B — 一个 command 怎么接你的口令($ARGUMENTS)**

File: commands/code-review.md (lines 1-12)
```markdown
---
description: Code review — local uncommitted changes or GitHub PR (pass PR number/URL for PR mode)
argument-hint: [pr-number | pr-url | blank for local review]
---

# Code Review

**Input**: $ARGUMENTS

If `$ARGUMENTS` contains a PR number, PR URL, or `--pr`:
→ Jump to **PR Review Mode** below.
```

**Snippet C — AGENTS.md 里的角色清单(像公司通讯录)**

File: AGENTS.md (lines 5-7, 13-17 节选)
```markdown
This is a **production-ready AI coding plugin** providing 67 specialized agents,
278 skills, 94 commands, and automated hook workflows.

## Agent Orchestration

Use agents proactively without user prompt:
- Complex feature requests → **planner**
- Code just written/modified → **code-reviewer**
- Bug fix or new feature → **tdd-guide**
- Architectural decision → **architect**
- Security-sensitive code → **security-reviewer**
```

**Snippet D — 六大角色数量统计(用 icon-rows 或 pattern-cards 展示)**

| 角色 | 文件夹 | 数量 | 一句话职责 |
|---|---|---|---|
| agents(专家同事) | `agents/` | 67 | 被派去干一类活的专家 |
| skills(工作手册) | `skills/` | 278 | 可复用的标准操作流程 |
| commands(快捷口令) | `commands/` | 94 | 你一喊就触发的 `/xxx` |
| hooks(自动质检员) | `hooks/` | 多个 | 事件发生时自动检查 |
| rules(公司铁律) | `rules/` | 23 类 | AI 永远要守的规矩 |
| MCPs(外线电话) | `.mcp.json` 等 | 按需 | 连接外部服务 |

### Interactive Elements

- [x] **Group chat animation** — 本模块的 hero visual。模拟「公司内部群聊」:用户在群里喊「帮我审一下这段代码」,然后 system 调度、planner/architect/code-reviewer/security-reviewer 依次发言,展示指挥链。
  - actors(群聊头像首字母 + 颜色): 用户(U)、系统调度(S)、规划师 P(planner,actor-1)、架构师 A(architect,actor-2)、审查员 R(code-reviewer,actor-3)、安全员 Sec(security-reviewer,actor-4)
  - 消息流:用户「帮我加个支付功能」→ 系统「这种复杂活,先派 planner」→ 规划师「我拆成 5 步,第 3 步要改数据库」→ 架构师「数据库改动建议走不可变更新」→ 审查员「代码我看过了,2 处要改」→ 安全员「发现一个密钥写死了,必须删」
- [x] **Code↔English translation** — 用 Snippet A(planner 的 YAML 头)做翻译,讲清 name/description/tools/model 四个字段各干嘛。这是本模块必有的代码翻译。
- [x] **Pattern cards 或 icon-rows** — 用 Snippet D 的六大角色做卡片网格,每张卡一个角色 + 图标 + 一句话。必须做,这是「认识角色」的最直观载体。
- [x] **Quiz** — 3-4 题,场景型:①「想让 AI 永远记得某条规矩,改哪个文件夹?」②「`/code-review` 属于哪种角色?」③调试型「AI 老忘记写测试,该加 agent 还是 rule?为什么」。
- [x] **Callout** — 1-2 个:①「指挥链」洞察(六角色是一条链,不是平的);② MCP 是「外线电话」比喻的 aha。

### Reference Files to Read

- `references/interactive-elements.md` → "Group Chat Animation"、"Code ↔ English Translation Blocks"、"Multiple-Choice Quizzes"、"Pattern/Feature Cards"、"Icon-Label Rows"、"Callout Boxes"
- `references/content-philosophy.md` → 全文
- `references/gotchas.md` → 全文

### Connections

- **Previous module:** 「这是什么」——已建立 ECC = AI 的「操作系统」。本模块打开系统看看里面住了谁。
- **Next module:** 「Skills:教 AI 怎么干活」——本模块只是点名认人,下一模块深入讲最核心的角色(skills)。
- **Tone/style notes:** 偶数模块用浅色背景(见 design-system 的 `--color-surface-warm` 或比奇数模块稍浅的暖色)。中文输出。群聊头像颜色用 `--color-actor-1..4`。给「agent/skill/command/hook/rule/MCP/YAML/orchestration」等词加 tooltip。
