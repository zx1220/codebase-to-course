# Module 5: 聪明的缓存与防护 · 不被自己打垮

### Teaching Arc
- **Metaphor:** 「编辑部唯一的跑腿记者 + 候客休息区」。想象 RSSHub 是个编辑部，只有一个跑腿记者（handler）负责去 B站 抢新闻。如果一万个人同时要看同一条新闻，记者不可能跑一万趟——于是前台（cache 中间件）做了两件事：① 把抢回来的新闻复印一份存着（缓存），后来的人直接拿复印件；② 如果有人正在催这条新闻，其他人先去「候客休息区」等着（单飞机制 single-flight），记者抢回来后大家共享，绝不让记者重复跑同一趟。
- **Opening hook:** RSSHub 是个公开服务，一个热门源（比如某个大 V 的微博）可能被成千上万个阅读器订阅。如果每个阅读器来一次，RSSHub 就去微博抓一次——微博分分钟把 RSSHub 封号。它是怎么做到既不重复抓、又不让请求互相打架的？答案是两个非常聪明的工程：缓存 + 单飞。
- **Key insight:** RSSHub 的缓存不只是「存一份省事」这么简单。它用一个叫 `claim`（占位）的原子操作解决了一个棘手问题：当缓存没命中时，只让「第一个」请求去抓数据，其他并发请求原地等待，抓完大家一起用。这叫「单飞 (single-flight)」/「请求合并」，是高并发系统的看家本领，防止「惊群效应」。
- **"Why should I care?":** ① 这是整个项目最值得学的工程思想之一——「用锁/占位防止重复劳动」，你做任何会被并发调用的东西都用得上。② 排错时如果你看到「RequestInProgressError / 503 正在抓取请稍后」，你就知道是单飞机制在起作用，不是 bug。③ 跟 AI 讨论性能时你能说出「single-flight / 请求合并 / 防惊群」这些精确词，AI 才会给你对的方案。

### Code Snippets (pre-extracted) — 逐字复制

**Snippet A — 缓存未命中时，抢着「占位」当唯一抓取者**
File: lib/middleware/cache.ts (lines 27-33)
```ts
    let value = await cacheModule.globalCache.get(key);

    // Doesn't hit the cache? Try to become the fetcher and let others know!
    let isRequesting = false;
    if (!value) {
        isRequesting = !(await cacheModule.globalCache.claim(controlKey, config.cache.requestTimeout));
    }
```

**Snippet B — 其他请求原地等待，不重复抓**
File: lib/middleware/cache.ts (lines 35-52)
```ts
    if (isRequesting) {
        let retryTimes = process.env.NODE_ENV === 'test' ? 1 : 10;
        let bypass = false;
        while (retryTimes > 0) {
            // eslint-disable-next-line no-await-in-loop
            await new Promise((resolve) => setTimeout(resolve, process.env.NODE_ENV === 'test' ? 3000 : 6000));
            // eslint-disable-next-line no-await-in-loop
            if ((await cacheModule.globalCache.get(controlKey)) !== '1') {
                bypass = true;
                break;
            }
            retryTimes--;
        }
        if (!bypass) {
            throw new RequestInProgressError('This path is currently fetching, please come back later!');
        }
        value = await cacheModule.globalCache.get(key);
    }
```

**Snippet C — claim 用一段 Redis 原子脚本实现（防止两个人同时抢到）**
File: lib/utils/cache/index.ts (lines 63-69)
```ts
            globalCache.claim = async (key, maxAge) => {
                if (!key || !cacheModule.status.available || !redisClient) {
                    return true;
                }
                const result = await redisClient.eval("if redis.call('GET', KEYS[1]) == '1' then return 0 end redis.call('SET', KEYS[1], '1', 'EX', ARGV[1]) return 1", 1, key, maxAge);
                return result === 1;
            };
```

**Snippet D — 抓完存起来，5 分钟内的请求都吃缓存**
File: lib/middleware/cache.ts (lines 78-84)
```ts
    const data: Data = ctx.get('data');
    if (ctx.res.headers.get('Cache-Control') !== 'no-cache' && data) {
        data.lastBuildDate = new Date().toUTCString();
        ctx.set('data', data);
        const body = JSON.stringify(data);
        await cacheModule.globalCache.set(key, body, config.cache.routeExpire);
    }
```
（config.cache.routeExpire 默认 300 秒 = 5 分钟）

### Interactive Elements

- [x] **数据流动画 (Message Flow / Data Flow animation)** — 本模块 hero visual。用动画演示「惊群 vs 单飞」：3 个 actor：阅读器A、阅读器B、cache 中间件 + handler。
  - 用两个并行的请求展示：A 和 B 同时到达。
  - 步骤：
    1. highlight actor-1 (阅读器A) + actor-2 (阅读器B)：「A 和 B 几乎同时请求同一个源」
    2. packet A→cache、packet B→cache：「都到了缓存关卡」
    3. highlight cache：「缓存没命中。claim 占位——只有一个能当抓取者」
    4. packet cache→handler (A 这条)：「A 的请求抢到了，放行去 handler 抓」
    5. highlight B：「B 没抢到，进入等待循环，每隔几秒查一次」
    6. packet handler→cache：「A 抓完，数据存进缓存」
    7. highlight B：「B 发现缓存有了，直接拿结果」
    8. packet cache→A、packet cache→B：「A 和 B 都拿到结果，handler 只跑了一次」
  - 注意：简化为 3-4 个 actor 即可（阅读器A/B 可用 2 个 actor，cache 和 handler 各 1 个）。label 禁用单引号。
- [x] **Code↔English translation** — 用 Snippet C 讲「claim 的原子性」：左边那段 Redis eval 脚本，右边解释：这段脚本在 Redis 里「一口气」执行——先查这个 key 是不是已经是 1，如果不是就设成 1。因为 Redis 是单线程，中间不可能有人插队，所以「检查 + 设置」是原子不可分割的，保证只有一个请求能抢到。这就是「原子操作」。
- [x] **Code↔English translation** — 用 Snippet A + B 讲「单飞流程」：左边代码，右边解释：缓存没有 → 尝试 claim 占位 → 抢到的去抓、没抢到的进 while 循环等待 → 等到缓存出现就拿、等不到就报「正在抓取请稍后」。
- [x] **Numbered Step Cards** — 5 张卡讲「单飞」时序：① 缓存查不到 ② 抢占位（claim）③ 抢到的去抓数据 ④ 其他人原地轮询等待 ⑤ 抓完共享结果。
- [x] **Group Chat Animation** — 可选补充：模拟 cache 和两个请求的对话（A：「我要数据」B：「我也要」cache：「等会儿，让 A 去抓，抓回来给你们俩」）。如果 flow animation 已经足够清楚，这个可以省略，但全课程至少要有 1 个 group chat（模块 2 已有，所以本模块可省）。
- [x] **Quiz (scenario + debugging)** — 3 题：
  - Q1（概念应用）：一万个阅读器同时请求同一个源，RSSHub 会去目标网站抓几次？正确：1 次（5 分钟内），其余都吃缓存。
  - Q2（debugging）：你订阅源偶尔返回 503，提示「正在抓取请稍后」。这说明什么？正确：不是 bug，是单飞机制——有别的请求正在抓，你这次被安排等待，过会儿重试就好。
  - Q3（architecture）：为什么 claim 必须是「原子操作」？正确：如果不是原子的，两个请求可能同时查到「没人占」然后都去抓，单飞就失效了（经典竞态条件/race condition）。
- [x] **Callout (callout-warning)** — 「惊群效应 (thundering herd)」：高并发系统的经典陷阱——缓存一旦失效，所有请求同时涌向后端。RSSHub 用单飞化解。这是个值得记住的术语。
- [x] **Callout (callout-accent)** — 「原子操作」：要么全做、要么不做，中间不可被打断。这是并发编程的基石概念。

### Reference Files to Read
- `references/interactive-elements.md` → "Message Flow / Data Flow Animation", "Code ↔ English Translation Blocks", "Numbered Step Cards", "Multiple-Choice Quizzes", "Callout Boxes", "Glossary Tooltips"
- `references/content-philosophy.md` → 全部
- `references/gotchas.md` → 全部

### Connections
- **Previous module:** 模块 4「渲染输出」——数据怎么变成 RSS/Atom/JSON。
- **Next module:** 模块 6「全景回顾」——把前五个模块串成一张完整架构图，回顾 RSSHub 的设计哲学。本模块结尾：「缓存和单飞解决了『被用户打垮』的问题。现在你已经看过了入口、路由、流水线、渲染、缓存——下模块我们把它们拼成一张大图。」
- **Tone/style notes:** 强调色 teal。模块 5 是偶数模块，用 `--color-bg`。务必 tooltip：缓存、cache、并发、单飞/single-flight、惊群效应、原子操作、竞态条件/race condition、Redis、TTL、503 等。flow label 禁用单引号。这是全课程技术含量最高的一模块，要把「为什么原子」讲透但用大白话。
