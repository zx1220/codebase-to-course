# Module 2: 一条订阅源的诞生 · 路由文件解剖

### Teaching Arc
- **Metaphor:** 「外卖菜单 + 后厨配方」。RSSHub 里的每个「路由文件」就像一家餐厅菜单上的一道菜：菜单上写着这道菜叫什么、长什么样（URL 路径），后厨配方（handler 函数）写着怎么做——去哪个菜市场买菜（调 B站 API）、怎么切怎么炒（解析数据）、最后装盘（返回一个数据对象）。`lib/routes/bilibili/` 这个文件夹就是「B站这家餐厅」，里面 50 多个 `.ts` 文件就是 50 多道菜。
- **Opening hook:** 上一模块我们看到 `/bilibili/user/dynamic/2267573` 这条地址能订阅一个 B站 UP 主。但你有没有想过：RSSHub 是怎么知道「遇到 bilibili 就去调 B站、遇到 weibo 就去调微博」的？答案藏在一种叫「路由文件」的东西里——它就是 RSSHub 的灵魂。
- **Key insight:** RSSHub 用一个极简约定组织了 1600+ 个网站源：**一个文件夹 = 一个网站（namespace），一个 .ts 文件 = 一条订阅源（route）**。每个路由文件干两件事：① 用 `path` 声明「我负责哪种 URL」，② 用 `handler` 函数实现「怎么抓、怎么解析、返回什么」。这就是它整个插件式架构的全部。
- **"Why should I care?":** 看懂路由文件 = 看懂 RSSHub 80% 的代码。以后你想「给某个还没收录的网站加一个源」，或者想跟 AI 说「帮我仿照这个结构写一个抓取器」，你都能精确描述：需要一个 path、一个 handler、返回 `{ title, link, description, item }`。你还能判断 AI 给你的代码对不对——如果它没按这个结构写，那就是错的。

### Code Snippets (pre-extracted) — 全部逐字复制，禁止修改

**Snippet A — 一个 namespace（文件夹的「身份证」）**
File: lib/routes/bilibili/namespace.ts (lines 1-7)
```ts
import type { Namespace } from '@/types';

export const namespace: Namespace = {
    name: '哔哩哔哩 bilibili',
    url: 'www.bilibili.com',
    lang: 'zh-CN',
};
```

**Snippet B — 一个完整的路由文件（B站图文，最干净的范例）**
File: lib/routes/bilibili/article.ts (lines 10-31 — 路由声明部分)
```ts
export const route: Route = {
    path: '/user/article/:uid',
    categories: ['social-media'],
    example: '/bilibili/user/article/334958638',
    parameters: { uid: '用户 id, 可在 UP 主主页中找到' },
    features: {
        requireConfig: false,
        requirePuppeteer: false,
        antiCrawler: false,
        supportBT: false,
        supportPodcast: false,
        supportScihub: false,
    },
    radar: [
        {
            source: ['space.bilibili.com/:uid'],
        },
    ],
    name: 'UP 主图文',
    maintainers: ['lengthmin', 'Qixingchen', 'hyoban'],
    handler,
};
```

**Snippet C — 同一个文件的 handler 函数（抓取+解析+返回）**
File: lib/routes/bilibili/article.ts (lines 33-87)
```ts
async function handler(ctx) {
    const uid = ctx.req.param('uid');
    const name = await cache.getUsernameFromUID(uid);
    const response = await got({
        method: 'get',
        url: `https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space?host_mid=${uid}`,
        headers: {
            Referer: `https://space.bilibili.com/${uid}/article`,
        },
    });
    const data = response.data.data;
    const title = `${name} 的 bilibili 图文`;
    const link = `https://space.bilibili.com/${uid}/article`;
    const description = `${name} 的 bilibili 图文`;
    const cookie = await cache.getCookie();

    const item = await Promise.all(
        data.items.map(async (item) => {
            const link = 'https:' + item.jump_url;
            const data = await cacheGeneral.tryGet(
                link,
                async () =>
                    (
                        await got({
                            method: 'get',
                            url: link,
                            headers: {
                                Referer: `https://space.bilibili.com/${uid}/article`,
                                Cookie: cookie,
                            },
                        })
                    ).data
            );

            const $ = load(data as string);
            const description = $('.opus-module-content').html();
            const pubDate = $('.opus-module-author__pub__text').text().replace('编辑于 ', '');

            const single = {
                title: item.content,
                link,
                description: description || item.content,
                // 2019年11月11日 08:50
                pubDate: pubDate ? parseDate(pubDate, 'YYYY年MM月DD日 HH:mm') : undefined,
            };
            return single;
        })
    );
    return {
        title,
        link,
        description,
        item,
    };
}
```

**Snippet D — 项目目录结构（教学示意，文件树）**
```
lib/routes/
├── bilibili/              ← 「B站这家餐厅」(namespace)
│   ├── namespace.ts       ← 这家店的身份证
│   ├── article.ts         ← 一道菜：UP主图文
│   ├── dynamic.ts         ← 一道菜：UP主动态
│   ├── video.ts           ← 一道菜：视频
│   └── ...50 多个文件
├── weibo/                 ← 「微博这家餐厅」
│   ├── namespace.ts
│   └── ...
├── github/                ← 「GitHub这家餐厅」
└── ...1600+ 个文件夹
```

### Interactive Elements

- [x] **Code↔English translation** — 必须做两段：
  1. Snippet A（namespace）—— 左边代码，右边逐行中文：解释 `name` 是显示名、`url` 是目标网站、`lang` 是语言。
  2. Snippet C 的「返回对象」部分（最后的 `return { title, link, description, item }`）—— 左边代码，右边解释：handler 不碰 HTTP、不写 XML，只返回一个「纯数据对象」；这是 RSSHub 最关键的设计——抓取逻辑和输出格式彻底分开。`item` 是每一条内容的数组。
- [x] **数据流/组聊动画 (Group chat animation)** — 全课程必须有 Group Chat，放这里最合适。模拟「路由文件被加载时各角色自我介绍」：
  - actors：`route 对象`(route)、`handler 函数`(handler)、`got 工具`(got)、`cheerio 工具`(load)
  - 消息流：
    - route：「我负责 /user/article/:uid 这个地址，谁负责干活？」
    - handler：「我来！我先拿到 uid 参数」
    - route：「需要记住，example 是 /bilibili/user/article/334958638」
    - handler：「got，帮我请求 B站 API」
    - got：「拿到 JSON 了，给你」
    - handler：「load，帮我解析每篇文章的网页」
    - load：「提取到正文和日期了」
    - handler：「好，我把所有内容打包成 {title, link, description, item} 返回，不管 RSS 长什么样」
  - chat window id: `chat-module2`。颜色用 actor-1/2/3/4。
- [x] **Visual File Tree** — 用 Snippet D 做一个可读的文件树，突出「文件夹=网站，文件=订阅源」的约定。比写一大段文字强。
- [x] **Drag-and-drop matching** — 把「路由文件的字段」和「它的作用」配对：
  - chips: `path`、`handler`、`name`、`maintainers`、`example`
  - zones(正确): path→「声明这条源负责哪种 URL 地址」、handler→「实现抓取与解析的函数」、name→「这条源的人话名字」、maintainers→「负责维护这个文件的 GitHub 用户」、example→「一个可直接用的示例地址」
- [x] **Quiz (architecture)** — 3 题：
  - Q1（设计理解）：为什么 RSSHub 让 handler 只返回数据对象，而不让它直接生成 RSS XML？正确选项强调「分离关注点：抓取逻辑和输出格式解耦，一套抓取代码能同时输出 RSS/Atom/JSON」。
  - Q2（debugging 场景）：你给 AI 一个新网站让它写 RSSHub 源，AI 返回的代码里 handler 直接 `ctx.body('<rss>...')` 输出 XML。哪里不对？正确：应该返回 `{title,link,description,item}` 对象，不该自己拼 XML。
  - Q3（tracing）：B站图文 handler 里的 `got({...})` 这一步，实际发生了什么？正确：「RSSHub 代替你，用 HTTP 去访问 B站 的接口拿数据」。
- [x] **Callout (callout-accent)** — 强调「分离关注点 (separation of concerns)」这个通用软件工程大智慧：handler 只管「拿数据」，RSS 长什么样由别人管。这是 5000+ 路由文件能共用一套渲染引擎的根本原因。

### Reference Files to Read
- `references/interactive-elements.md` → "Code ↔ English Translation Blocks", "Group Chat Animation", "Drag-and-Drop Matching", "Visual File Tree", "Multiple-Choice Quizzes", "Callout Boxes", "Glossary Tooltips"
- `references/content-philosophy.md` → 全部
- `references/gotchas.md` → 全部

### Connections
- **Previous module:** 模块 1「这是什么」——建立了「RSSHub = 翻译官，入口→抓取翻译→输出」的心智模型。
- **Next module:** 模块 3「请求的旅程」——把镜头拉到「一次完整请求」：从你的阅读器发请求，到中间件一道道处理，到最终被某个 handler 接住。本模块结尾要承接：「你已经看到了 handler 长什么样——但请求是怎么一路走到 handler 的？中间又经过了哪些『关卡』？下模块揭晓。」
- **Tone/style notes:** 强调色 teal。这模块是全课程最核心，要重点用力。务必给术语加 tooltip：namespace、route、handler、参数、API、JSON、HTTP、cookie、cheerio、CSS 选择器、Promise、异步 等。代码逐字复制，`white-space: pre-wrap` 会自动换行。模块 2 是奇数模块，用 `--color-bg-warm` 背景。
