# Module 3: Skills——教 AI 怎么干活的可复用「工作手册」

### Teaching Arc
- **Metaphor:** 一个 skill 是一本「可复用的 SOP 工作手册」——就像连锁咖啡店的饮品制作手册:不管哪个店员(哪个 AI 会话)来,只要翻开「拿铁」这一页,按步骤做,出来的拿铁都一个样。没有手册,每个店员全凭感觉,质量忽好忽坏——这正是「裸 AI」的问题。**不要用「餐厅」整体比喻,这里用「连锁店 SOP 手册」聚焦在「可复用」这点上。**
- **Opening hook:** 你有没有发现:同一段需求,这次让 AI 写得很好,下次它又忘了?问题不在 AI 记性差,在于没人把「正确做法」写成手册。ECC 的 278 个 skills 就是干这个的。
- **Key insight:** 一个 skill = 一个文件夹 + 一个 `SKILL.md`。它告诉 AI「**什么时候**用(When to use)、**按什么步骤**用(Steps)、**长什么样**的代码算对(Patterns)」。最厉害的是 TDD skill——它强制 AI「先写测试、看到测试失败、再写代码」,把 AI 的「凭感觉」变成「有证据」。
- **"Why should I care?":** 学会 skill 的结构,你就能自己写一本手册丢给 AI,让它每次都按你的标准干活。这是 vibe coder 最该掌握的「指挥 AI」的高级技巧。

### Code Snippets (pre-extracted)

**Snippet A — skill 的「身份证」(YAML 头)**

File: skills/tdd-workflow/SKILL.md (lines 1-8)
```yaml
---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage including unit, integration, and E2E tests.
argument-hint: <path/to/*.plan.md>
metadata:
  origin: ECC
---
```

**Snippet B — TDD 的「铁律:先写测试」(这是最能体现 skill 价值的一句)**

File: skills/tdd-workflow/SKILL.md (lines 43-44, 152-157 节选合并)
```markdown
### 1. Tests BEFORE Code
ALWAYS write tests first, then implement code to make tests pass.

### Step 3: Run Tests (They Should Fail)
<test>
# Tests should fail - we haven't implemented yet

This step is mandatory and is the RED gate for all production changes.
```

**Snippet C — RED / GREEN 两道关卡(TDD 的灵魂,用 step-cards 展示)**

File: skills/tdd-workflow/SKILL.md (Step 3-5 精简)
```
🔴 RED 关卡:先写一个测试,运行,它必须失败(因为功能还没写)
   → 证明「这个测试真的在测那个功能」,不是假测试

🟢 GREEN 关卡:写最少的代码让测试通过
   → 再运行同一个测试,它必须变绿(通过)

♻️ REFACTOR:在测试保持绿色的前提下,优化代码
```

**Snippet D — skill 文件夹结构(用 visual file tree 展示)**

```
skills/
  tdd-workflow/
    SKILL.md          ← 手册正文:什么时候用 + 步骤 + 代码模板
  django-tdd/
    SKILL.md          ← Django 专用的 TDD 手册
  laravel-tdd/
    SKILL.md          ← Laravel 专用的 TDD 手册
  ... (共 278 个)
```

### Interactive Elements

- [x] **Code↔English translation** — 用 Snippet A(skill 的 YAML 头)做翻译,讲 name/description/argument-hint/origin。这是本模块必有代码翻译。
- [x] **Numbered step cards** — 用 Snippet C 把 RED/GREEN/REFACTOR 做成三张步骤卡,🔴🟢♻️ 配色。这是本模块的 hero visual(把 TDD 的精髓一眼讲清)。
- [x] **Group chat animation 或 data flow** — 演示「无 skill 的 AI」vs「有 TDD skill 的 AI」对比。建议做一段简短的群聊或双栏对比:左边裸 AI 直接写代码(容易出 bug),右边 TDD AI 先说「等等,我先写测试」→ 测试红了 → 写代码 → 测试绿了。如果用群聊:actors = 你(U)、裸 AI(N)、TDD-AI(T)。可选——若步骤卡够强,这个可省,优先保证前面两个元素。
- [x] **Quiz** — 3-4 题场景型:①「想让 AI 每次改完代码都跑测试,该用 skill 还是 hook?」(区分 skill=按步骤干活 vs hook=自动触发)②「TDD 里 RED 关卡为什么测试必须先失败?」③给你一个场景判断该用哪个现成 skill。
- [x] **Callout** — 1-2 个:①「RED/GREEN 是给 AI 上『证据』」的洞察——AI 不再凭感觉说『搞定了』,必须拿测试结果当证据;②「手册 = 可复用」的 aha。

### Reference Files to Read

- `references/interactive-elements.md` → "Code ↔ English Translation Blocks"、"Numbered Step Cards"、"Multiple-Choice Quizzes"、"Visual File Tree"、"Callout Boxes"、"Group Chat Animation"(如做对比)
- `references/content-philosophy.md` → 全文
- `references/gotchas.md` → 全文

### Connections

- **Previous module:** 「认识角色们」——本模块深入六大角色里最重要的 skills。
- **Next module:** 「Hooks:给 AI 装上自动刹车」——skill 是「AI 主动按手册干」,下一模块讲 hook「不管 AI 想不想,事件一发生就自动检查」。两者形成对比:skill=主动遵循,hook=被动强制。
- **Tone/style notes:** 奇数模块用 `var(--color-bg-warm)` 背景。中文输出。RED 用红/暖色,GREEN 用绿。给「skill/SOP/TDD/RED/GREEN/refactor/coverage/unit test」等词加 tooltip。
