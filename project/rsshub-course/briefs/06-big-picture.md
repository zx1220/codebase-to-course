# Module 6: 全景回顾 · 一张图看懂 RSSHub

### Teaching Arc
- **Metaphor:** 「城市交通总览图」。前面五个模块我们像在逛城市的各个街区（翻译官、路由文件、中间件流水线、渲染、缓存）。这个模块我们坐直升机升空，看整座城市的全景：请求像一辆车，从城外（阅读器）进城，过收费站（访问控制）、经停调度中心（缓存）、开到对应的工厂（路由+handler）取货、再到包装车间（parameter）贴标、最后到发货口（template 渲染）出城。一张图把所有模块串起来。
- **Opening hook:** 恭喜你走完了 RSSHub 的每个核心部分。现在我们把它们拼起来——你会看到，前面学的每一块都不是孤立的，它们组成了一条精密的流水线。这一张图，就是 RSSHub 的全部灵魂。
- **Key insight:** RSSHub 的优雅在于「约定优于配置」和「关注点分离」：用文件系统约定（文件夹=网站、文件=源）组织 1600+ 个源；让 handler 只管抓数据，把缓存、美化、渲染全交给中间件。这种「让简单的部分保持简单，让复杂的部分各司其职」的设计，是它能在社区维护下长成庞然大物却不崩溃的根本原因。
- **"Why should I care?":** ① 拥有完整的架构视野后，你跟 AI 讨论任何「抓取+转换+服务」类项目都能胸有成竹。② 你能判断 AI 给你的架构是不是「干净分层」——如果它把抓取、缓存、渲染全揉在一个函数里，你能指出问题。③ 这套设计思想（插件化约定、中间件流水线、单飞缓存）可以迁移到你自己的项目里。

### Code Snippets (pre-ex extracted) — 复习用，无需新长代码

**Snippet A — 一条请求的完整旅程（教学串讲图，文字版）**
```
阅读器请求 /bilibili/user/dynamic/2267573?format=json
   │
   ▼  ┌─ accessControl：查 ACCESS_KEY（模块3）
流水线 ├─ cache：查缓存，命中就返回；没命中去抓（模块3、5）
      ├─ 路由匹配：找到 lib/routes/bilibili/dynamic.ts（模块2）
      ├─ handler：调 B站 API，返回数据对象（模块2）
      ├─ parameter：美化数据、支持 ?filter ?limit（模块3）
      └─ template：按 ?format=json 渲染成 JSON Feed（模块4）
   │
   ▼
阅读器收到 JSON 格式的订阅内容
```

**Snippet B — handler 返回的数据对象（贯穿全课程的核心，复用）**
File: lib/routes/bilibili/article.ts (lines 81-87)
```ts
    return {
        title,
        link,
        description,
        item,
    };
}
```

**Snippet C — RSSHub 设计哲学三句话（教学提炼）**
```
1. 约定优于配置：文件夹=网站，文件=源。1600+ 源靠这个约定组织。
2. 关注点分离：handler 只抓数据，缓存/美化/渲染交给中间件。
3. 用聪明的工程保护自己：单飞缓存防惊群，原子操作防竞态。
```

### Interactive Elements

- [x] **Interactive Architecture Diagram** — 本模块的 hero visual，也是全课程的总图。用 arch-diagram 展示 RSSHub 完整架构，分几个 zone：
  - zone「外部」：阅读器、目标网站(B站等)
  - zone「RSSHub 入口」：Hono 服务器、accessControl
  - zone「中间件流水线」：cache、parameter、template（每个做成可点 arch-component，点击显示职责）
  - zone「路由」：routes 文件夹、namespace + route 约定
  - zone「输出」：RSS / Atom / JSON 三种格式
  - 每个 arch-component 带 data-desc，onclick 显示说明。这是全课程的「知识地图」，要让学习者点着每个块就能想起对应模块。
- [x] **Drag-and-drop matching** — 「把概念放回它属于的模块」。chips: handler、namespace.ts、?format=、claim 占位、accessControl。zones(正确): handler→「路由模块·抓数据」、namespace.ts→「路由模块·网站身份证」、?format=→「渲染模块·选输出格式」、claim→「缓存模块·防惊群」、accessControl→「流水线·查密钥」。
- [x] **Code↔English translation** — 用 Snippet B 做最后的复习：左边这个贯穿全课程的对象，右边用一段话总结「就是这个小对象，把整个 RSSHub 串起来——handler 造它、缓存存它、parameter 美化它、template 渲染它」。
- [x] **Pattern cards (设计哲学)** — 3 张卡：① 约定优于配置 ② 关注点分离 ③ 用聪明工程保护自己。每张一句话 + 一个「你能怎么用」的提示（帮学习者迁移到自己项目）。
- [x] **Quiz (综合应用)** — 3-4 题，全课程综合：
  - Q1（架构决策，综合）：你想做一个「把多个天气预报网站汇总成统一 API」的服务。借鉴 RSSHub，你会怎么组织代码？正确：每个天气网站一个文件夹(约定)，每个源一个文件只管抓数据(handler)，缓存/输出交给公共中间件(分离)。
  - Q2（debugging，综合）：用户报「订阅源突然全是旧内容」。你会依次检查哪里？正确选项给出合理的排查顺序：先看缓存是否太久没刷新、再看 handler 是否抓取失败、再看目标网站是否改版。
  - Q3（AI 协作）：你让 AI 写一个新源，它返回的代码里 handler 直接拼接 RSS XML。基于你学到的，问题在哪？正确：handler 应只返回数据对象，渲染是 template 的事（关注点分离）。
  - Q4（术语，可选）：「惊群效应」指的是什么？正确：缓存失效时所有请求同时涌向后端。
- [x] **Callout (callout-accent)** — 结尾的「aha!」：好架构的本质是「让简单的部分保持简单，让复杂的部分各司其职」。RSSHub 能靠社区维护 1600+ 源，靠的就是这个。
- [x] **结尾鼓励段**（非交互）：用 2-3 句话告诉学习者——你现在拥有了读、理解、指挥这类项目的能力。遇到类似抓取/转换/服务类项目，你心里已经有图了。

### Reference Files to Read
- `references/interactive-elements.md` → "Interactive Architecture Diagram", "Drag-and-Drop Matching", "Code ↔ English Translation Blocks", "Pattern/Feature Cards", "Multiple-Choice Quizzes", "Callout Boxes", "Glossary Tooltips"
- `references/content-philosophy.md` → 全部
- `references/gotchas.md` → 全部

### Connections
- **Previous module:** 模块 5「缓存与防护」——单飞缓存。
- **Next module:** 无（最后一模块）。这是收尾，要把前 5 个模块融会贯通。
- **Tone/style notes:** 强调色 teal。模块 6 是奇数模块，用 `--color-bg-warm`。arch-diagram 是核心，要做精致，把全课程的 actor 都放进去。结尾要有「学完了」的成就感和可迁移的收获。务必 tooltip：约定优于配置、关注点分离、架构、中间件、插件化 等术语。语气可以是总结性的、略带鼓励。
