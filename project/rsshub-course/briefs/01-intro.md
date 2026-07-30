# Module 1: 这是什么？万物皆可 RSS

### Teaching Arc
- **Metaphor:** "翻译官/翻译社"。RSSHub 是一个「网站翻译官」——你喜欢的网站（B站、微博、GitHub、推特）只说自己的「方言」（JSON API、网页），而你的 RSS 阅读器只听得懂一种「世界语」（RSS）。RSSHub 就是中间那个同声传译：你把一个 B站地址递给它，它替你去问 B站要数据，翻译成 RSS 这种统一格式，再交还给你的阅读器。
- **Opening hook:** 你可能已经用 RSS 阅读器订阅过博客。但你有没有想过——为什么 B站、微博、推特这些你天天刷的网站，偏偏不能直接订阅？因为你需要一个「中间人」帮你去抓、去翻译。这个中间人就是 RSSHub。
- **Key insight:** RSSHub 的存在意义只有一个：把「不提供 RSS 的网站」变成「能订阅的 RSS 源」。它是一个跑在服务器上的翻译/抓取服务，url 里写什么网站，它就去抓什么网站。
- **"Why should I care?":** 理解了这个「翻译官」定位，你就理解了整个项目的架构——它必然由三部分组成：① 接收你的请求（入口）、② 替你去目标网站抓数据（抓取+翻译）、③ 把结果包成 RSS 还给你（输出）。后面所有模块都在拆解这三步。这个心智模型能帮你在跟 AI 协作时说清楚「我要做一个类似 RSSHub 的抓取翻译服务」。

### Code Snippets (pre-extracted)

**Snippet A — 一条真实的 RSSHub URL 长什么样**
（这是教学用的概念展示，不是文件代码）
```
https://rsshub.app/bilibili/user/dynamic/2267573
              ─┬────  ────┬────  ────┬──  ───┬───
               │         │          │       │
          服务器地址   命名空间(网站)  路径   参数(用户ID)
```
解读：把这段地址粘进任何 RSS 阅读器，就能在阅读器里刷到这个 B站 UP 主的最新动态。RSSHub 把 B站的数据翻译成了 RSS。

**Snippet B — RSSHub 是用什么技术搭的（来自 package.json 关键依赖，节选概念）**
File: package.json （关键部分，教学说明用）
```
框架: Hono          ← 一个轻量、快速的 Web 框架（类似 Express）
运行时: Node.js     ← 服务端 JavaScript 运行环境
语言: TypeScript    ← 带类型的 JavaScript
构建: tsdown        ← 打包工具
HTTP 客户端: ofetch  ← 用来「替你去别的网站抓数据」
解析: cheerio       ← 用来「读网页」，像 jQuery 一样提取内容
浏览器自动化: Playwright ← 用来对付需要真正打开浏览器才能抓的网站
默认端口: 1200
```

**Snippet C — 项目对外口号（README 标题，原文）**
File: README.md
```
RSSHub · 万物皆可 RSS
The world's largest RSS network.
```

### Interactive Elements

- [x] **Code↔English translation** — 用 Snippet A（URL 拆解）。把那条 URL 的 5 个部分做成 translation block：左边是带标注的 URL，右边逐段中文解释每一段含义。
- [x] **数据流动画 (Data flow animation)** — 这是本模块的 hero visual，也是全课程必须的 Message Flow 之一。3 个 actor：① 你的 RSS 阅读器、② RSSHub 服务器、③ 目标网站(B站)。
  - 步骤：
    1. highlight actor-1：「你的阅读器发出订阅请求」
    2. packet from 1→2：「RSSHub 收到 /bilibili/user/dynamic/2267573」
    3. highlight actor-2：「RSSHub 知道：这是要抓 B站 UP 主动态」
    4. packet from 2→3：「RSSHub 替你去访问 B站 API」
    5. packet from 3→2：「B站 返回原始数据(JSON)」
    6. highlight actor-2：「RSSHub 把数据翻译成 RSS 格式」
    7. packet from 2→1：「返回标准 RSS 给你的阅读器」
  - 注意：label 里绝对不要用单引号/撇号，用中文引号「」。
- [x] **Pattern/Feature cards** — 用卡片展示「RSSHub 能做什么 / 为什么特别」：① 1600+ 个网站源、② 一个 URL 就能订阅、③ 自带缓存省流量、④ 可自己部署。4 张卡片。
- [x] **Quiz (scenario)** — 3 题，放在模块末尾。
  - Q1（概念理解）：你想订阅某个 B站 UP 主，但 B站 没有 RSS。最该用什么工具？选项：A 让浏览器装插件刷新 B、用 RSSHub 生成一个该 UP 主的 RSS 源（正确）C 写个脚本每天抓 B站 D 放弃，B站不可能订阅。解释：RSSHub 就是专门干这个的翻译官。
  - Q2（架构直觉，tracing）：当你的阅读器请求 /bilibili/... 时，RSSHub 实际上会做什么？选项里正确的是「替你去访问 B站，再把结果翻译成 RSS 返回」。
  - Q3（AI 协作场景）：你想让 AI 帮你做一个「把某网站变成可订阅源」的服务。你会怎么描述需求？正确选项强调「抓取目标网站 + 翻译成统一格式(RSS) + 提供一个 URL 入口」三要素。
- [x] **Callout (callout-accent)** — 一个「aha!」：解释为什么这个三段式（入口→抓取翻译→输出）会成为后面所有模块的主线。

### Reference Files to Read
- `references/interactive-elements.md` → "Code ↔ English Translation Blocks", "Message Flow / Data Flow Animation", "Pattern/Feature Cards", "Multiple-Choice Quizzes", "Callout Boxes", "Glossary Tooltips", "Numbered Step Cards"
- `references/content-philosophy.md` → 全部（尤其 metaphor、visual density、tooltip 规则）
- `references/gotchas.md` → 全部

### Connections
- **Previous module:** 无（这是第一模块）
- **Next module:** 模块 2「路由文件」——将打开 RSSHub 最核心的东西：那个 1600+ 网站源是怎么用「一个文件夹 = 一个网站，一个文件 = 一条订阅源」的约定组织起来的。本模块结尾要埋下这个钩子：「RSSHub 怎么知道 /bilibili/... 对应哪段抓取代码？答案藏在它的『路由文件』里。」
- **Tone/style notes:** 强调色为 teal(#2A7B9B)。模块编号格式「01」。整体口语化，像聪明朋友讲解。Actor 颜色：阅读器用 actor-2(teal)、RSSHub 用 actor-1(保留语义但本模块可自定义)、B站用 actor-4(金)。务必给每个技术术语加 tooltip：RSS、API、JSON、框架、运行时、TypeScript、端口、HTTP、Web 框架、阅读器 等。正文用中文，URL/代码保留原文。
