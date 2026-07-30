# Module 3: 一次请求的旅程 · 中间件流水线

### Teaching Arc
- **Metaphor:** 「机场安检+流水线」。一条请求到达 RSSHub，就像一个旅客进机场：先过安检门（access-control 查你有没有钥匙）、再过登机牌扫描（cache 查缓存里有没有现成结果）、走到对应登机口（路由匹配找到 handler）、handler 干完活回来，还要经过行李打包区（parameter 中间件做美化处理）、最后贴标签出港（template 渲染成 RSS）。每一道关都是一个「中间件」，按固定顺序排队。
- **Opening hook:** 上一模块我们看到了 handler 的真面目——它只返回一个数据对象。但请求不是直接「咣当」掉进 handler 的。它要排队过一道道「关卡」，这些关卡叫「中间件」。理解这道流水线，你才真正理解 RSSHub 怎么运转。
- **Key insight:** RSSHub 用一串「中间件 (middleware)」按固定顺序处理每个请求：有的在前门把守（访问控制）、有的查缓存省事、有的在 handler 之后给数据做美化和加工。handler 只是流水线上「最核心那一站」。这个「洋葱模型」——请求一层层穿进去、响应一层层穿出来——是几乎所有现代 Web 框架的核心思想。
- **"Why should I care?":** 出问题的时候，80% 的 bug 都在这条流水线上：「为什么我的订阅源报 403？」「为什么加了 ?limit=10 没效果？」「为什么第一次慢第二次快？」理解中间件顺序，你就能精准定位问题在哪一站。跟 AI 排错时，你能说「请在缓存中间件之前/之后加日志」，而不是干瞪眼。

### Code Snippets (pre-extracted) — 逐字复制

**Snippet A — 中间件注册顺序（RSSHub 的「流水线总图」）**
File: lib/app-bootstrap.tsx (lines 28-47，教学用，说明性注释为辅助)
```
app 上的中间件按下面这个固定顺序排队（请求依次穿过）：

  trimTrailingSlash  → 去掉 URL 末尾多余的斜杠
  compress           → 压缩响应，省流量
  logger             → 打印日志
  trace              → 链路追踪（调试用）
  honeybadger/sentry → 错误上报（出 bug 自动报警）
  accessControl      → 【关卡1】查访问密钥，没钥匙就 403
  debug              → 统计调试信息
  template           → 【关卡】在 handler 之后渲染输出
  header             → 设置响应头、ETag
  antiHotlink        → 防图片盗链
  parameter          → 【关卡】美化数据、支持 ?filter ?limit 等
  cache              → 【关卡2】查缓存，没缓存才放行去 handler

然后才路由匹配 → 跑 handler
```
（这是说明性展示，原文来自 app-bootstrap.tsx 第 28-47 行的连续 app.use(...) 调用，这里把每个中间件作用翻译出来做成教学。）

**Snippet B — handler 返回的对象怎么被「接住」**
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
（上一模块见过，这里强调：handler 把这个对象「往回扔」，然后缓存中间件把它存起来、parameter 中间件美化它、template 中间件把它变成 RSS。）

**Snippet C — 缓存中间件的核心逻辑（「省事关卡」怎么工作）**
File: lib/middleware/cache.ts (lines 21-27)
```ts
    const requestPath = ctx.req.path;
    const format = `:${ctx.req.query('format') || 'rss'}`;
    const limit = ctx.req.query('limit') ? `:${ctx.req.query('limit')}` : '';
    const key = 'rsshub:koa-redis-cache:' + h64ToString(requestPath + format + limit);
    const controlKey = 'rsshub:path-requested:' + h64ToString(requestPath + format + limit);
```

**Snippet D — 缓存命中就直接返回，跳过 handler**
File: lib/middleware/cache.ts (lines 54-60)
```ts
    if (value) {
        ctx.status(200);
        ctx.header('RSSHub-Cache-Status', 'HIT');
        ctx.set('data', JSON.parse(value));
        await next();
        return;
    }
```

### Interactive Elements

- [x] **数据流动画 (Message Flow / Data Flow animation)** — 本模块 hero visual，全课程必须的 flow animation 之一。4 个 actor 排成一行：
  - actor-1: 阅读器(请求)、actor-2: accessControl(关卡)、actor-3: cache(缓存)、actor-4: handler(路由)。
  - 步骤（带缓存命中的完整旅程）：
    1. highlight actor-1：「阅读器请求 /bilibili/...」
    2. packet 1→2：「请求进入 RSSHub」
    3. highlight actor-2：「accessControl 检查访问密钥」
    4. packet 2→3：「钥匙对，放行 → 进入缓存关卡」
    5. highlight actor-3：「cache 查：这个地址之前抓过吗？」
    6. （分支：缓存命中）packet 3→1：「命中！直接返回旧结果，跳过 handler」（用一个 label 说明）
    7. （分支：缓存未命中）packet 3→4：「未命中 → 放行去 handler 抓新数据」
    8. highlight actor-4：「handler 调 B站 API、解析、返回数据」
    9. packet 4→3：「数据回到缓存，被存起来」
    10. packet 3→1：「最终返回给阅读器」
  - 注意 label 不能含单引号；用中文引号。actor id 用 flow-actor-1..4。
- [x] **Code↔English translation** — 用 Snippet C + D 组合成一段，讲「缓存关卡」：左边代码，右边解释：① 把「地址+格式+数量」拼成一个唯一的钥匙；② 用 xxhash 把长钥匙压短（注释里工程师特意提醒了这点）；③ 命中就标 HIT 直接返回，连 handler 都不跑。强调工程小心思。
- [x] **Numbered Step Cards** — 用 5 张步骤卡展示「一次请求经过的关卡顺序」：① 访问控制查密钥 ② 缓存查有没有现成的 ③ 路由匹配找到 handler ④ handler 抓数据 ⑤ parameter/template 美化并渲染输出。每张卡一句话。
- [x] **Pattern cards** — 4 张「中间件典型代表」卡：accessControl(守门员)、cache(省钱大师)、parameter(美颜滤镜)、template(翻译成 RSS)。每张一句话职责。
- [x] **Quiz (scenario + debugging)** — 3 题：
  - Q1（debugging）：你部署的 RSSHub 设了 ACCESS_KEY，结果阅读器订阅报 403 错误。最可能卡在哪一站？正确：accessControl（访问控制中间件）。
  - Q2（概念）：同一个订阅源，第一次打开很慢，第二次很快。为什么？正确：cache 中间件第一次没命中要去抓，第二次命中直接返回。
  - Q3（architecture）：为什么 handler 只返回数据对象、不自己生成 RSS？正确：因为 template 中间件在后面统一负责渲染，抓取和输出分开（承接上一模块）。
- [x] **Callout (callout-accent)** — 「洋葱模型」：请求一层层穿进去、响应一层层穿出来。这是 Express/Koa/Hono 等几乎所有现代 Web 框架的核心思想。一个通用大智慧。

### Reference Files to Read
- `references/interactive-elements.md` → "Message Flow / Data Flow Animation", "Code ↔ English Translation Blocks", "Numbered Step Cards", "Pattern/Feature Cards", "Multiple-Choice Quizzes", "Callout Boxes", "Glossary Tooltips"
- `references/content-philosophy.md` → 全部
- `references/gotchas.md` → 全部

### Connections
- **Previous module:** 模块 2「路由文件」——看到了 handler 的真面目（返回数据对象）。
- **Next module:** 模块 4「渲染输出」——聚焦流水线的最后一站：那个数据对象是怎么变成 RSS/Atom/JSON 三种格式的。本模块结尾埋钩子：「请求走完整条流水线，最后拿到一个数据对象。但它还不是 RSS——谁负责把它『翻译』成阅读器认得的样子？下模块看 template 这一站。」
- **Tone/style notes:** 强调色 teal。模块 3 是偶数模块，用 `--color-bg`。务必 tooltip：middleware、中间件、HTTP 状态码、403、cache、缓存、Redis、ETag、洋葱模型、Web 框架 等。flow animation 的 data-steps 用 JSON，label 内禁用单引号。
