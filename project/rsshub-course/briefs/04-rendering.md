# Module 4: 数据变 RSS · 渲染输出的魔法

### Teaching Arc
- **Metaphor:** 「同一个菜，三种摆盘」。handler 给你端上来的是一盘「半成品」（一个数据对象 `{ title, link, description, item }`）。但阅读器们口味不同：有的只吃 RSS，有的爱吃 Atom，有的要 JSON。template 这一站就像一个会三种摆盘手艺的厨师——同一锅菜，根据你 URL 里 `?format=` 写的口味，摆成三种不同的样子端上桌。菜还是那道菜，装盘不同。
- **Opening hook:** 前面模块你看到的 handler，自始至终只返回一个数据对象，从不碰 XML。那这个数据对象是怎么「变成」阅读器能认的 RSS 的？秘密在流水线最后一站——一个叫 template 的中间件。而且它不止会一种摆盘。
- **Key insight:** RSSHub 用一个 `?format=` 查询参数决定输出哪种格式：默认 RSS（XML），`?format=atom` 出 Atom，`?format=json` 出 JSON Feed。渲染用的不是传统的「字符串拼接」，而是 JSX——把 RSS 标签当成组件来写，像搭积木一样拼出 XML。一套数据，多套外观，按需切换。
- **"Why should I care?":** ① 当你看到订阅源返回的不是 XML 而是别的格式，你就知道是 `?format=` 在起作用——不用慌。② 「同数据多视图」是软件设计里超重要的思想（MVC 里的 V），理解它你能跟 AI 更好地讨论「把数据和展示分开」。③ 知道 JSX 不只能写网页还能写 XML/配置文件，扩展你对「模板」的想象。

### Code Snippets (pre-extracted) — 逐字复制

**Snippet A — 根据 format 切换输出格式（template 中间件核心）**
File: lib/middleware/template.tsx (lines 118-129，教学用，注释为辅助说明)
```tsx
    switch (outputType) {
        case 'ums':
        case 'rss3':
            return ctx.json(rss3(result));
        case 'json':
            ctx.header('Content-Type', 'application/feed+json; charset=UTF-8');
            return ctx.body(json(result));
        case 'atom':
            return ctx.render(<Atom data={result} />);
        default:
            return ctx.render(<RSS data={result} />);
    }
```
（switch 根据用户传的 ?format= 决定走哪个分支。default 是 RSS。注意同一个 `result` 数据对象，被喂给不同的渲染函数/组件。）

**Snippet B — RSS 是用 JSX 写出来的（把 XML 当组件搭）**
File: lib/views/rss.tsx (lines 5-17)
```tsx
const RSS: FC<{ data: Data }> = ({ data }) => {
    const hasItunes = data.itunes_author || data.itunes_category || (data.item && data.item.some((i) => i.itunes_item_image || i.itunes_duration));
    const hasMedia = data.item?.some((i) => i.media);
    const isTelegramLink = data.link?.startsWith('https://t.me/s/');

    return (
        <rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes={hasItunes ? 'http://www.itunes.com/dtds/podcast-1.0.dtd' : undefined} xmlns:media={hasMedia ? 'http://search.yahoo.com/mrss/' : undefined} version="2.0">
            <channel>
                <title>{data.title || 'RSSHub'}</title>
                <link>{data.link || 'https://docs.rsshub.app'}</link>
```

**Snippet C — 数据对象的 item 数组变成 XML 里的 item 标签**
File: lib/views/rss.tsx (lines 38-50)
```tsx
                {data.item?.map((item) => (
                    <item>
                        <title>{item.title}</title>
                        <description>{item.description}</description>
                        <link>{item.link}</link>
                        <guid isPermaLink="false">{item.guid || item.link || item.title}</guid>
                        {item.pubDate && <pubDate>{item.pubDate}</pubDate>}
                        {item.author && <author>{item.author}</author>}
                        {item.image && <enclosure url={item.image} type="image/jpeg" />}
```

**Snippet D — 三种格式的对照（教学示意）**
```
同一个 handler 返回的数据对象：
  { title: "某UP主的动态", item: [ {title:"新视频", link:"..."} ] }

?format=rss  (默认)        →  RSS 2.0 的 XML：<rss><channel><item>...
?format=atom               →  Atom 的 XML：<feed><entry>...
?format=json               →  JSON Feed：{ "version":"...", "items":[...] }
```

### Interactive Elements

- [x] **Layer Toggle Demo** — 本模块 hero visual，超合适。三个 tab：① RSS、② Atom、③ JSON。每个 tab 展示「同一个数据对象被渲染成什么样」。让学习者点 tab 切换，直观看到「同数据多视图」。
  - layer-rss：展示一段精简的 RSS XML（`<rss><channel><title>...</title><item>...</item></channel></rss>`）
  - layer-atom：展示一段 Atom XML（`<feed><entry>...</entry></feed>`）
  - layer-json：展示一段 JSON Feed（`{"version":"...","items":[...]}`）
  - 描述文字：点每个 tab 说明「这都是同一个数据对象变的，只是摆盘不同」。
- [x] **Code↔English translation** — 用 Snippet A：左边 switch 代码，右边逐行中文解释：`outputType` 是用户在 URL 里写的 `?format=`；走不同分支；RSS 是默认；强调「同一个 result 喂给不同渲染器」。
- [x] **Code↔English translation** — 用 Snippet B + C 合并讲：左边 JSX 代码，右边解释：RSS 居然是用 JSX 组件写出来的；`data.item.map` 把数组里每条内容变成一个 `<item>` 标签；这是「把 XML 当成可以拼搭的积木」。
- [x] **Pattern cards** — 3 张「三种格式」卡：RSS（最通用、默认）、Atom（更现代、Google 推的）、JSON Feed（给程序读的、不是 XML）。每张一句话特点。
- [x] **Quiz (scenario + architecture)** — 3 题：
  - Q1（tracing/应用）：你的程序想用代码解析某个 RSSHub 源，XML 太麻烦。你该在 URL 后面加什么？正确：`?format=json`，拿到 JSON 程序更好处理。
  - Q2（概念）：为什么 RSSHub 把 handler 和渲染（template）分开？正确：一套抓取代码能同时支持多种输出格式，改格式不用改 handler（关注点分离，承接前模块）。
  - Q3（应用/debugging）：你访问源看到的是 XML，朋友访问同一个源看到的是 JSON。为什么？正确：因为 URL 里的 `?format=` 参数不同，决定走哪个渲染分支。
- [x] **Callout (callout-accent)** — 「模型-视图」思想：数据（M）和展示（V）分开。这是从桌面软件到 Web 到现在所有界面设计的通用大智慧。RSSHub 的 handler=模型，template=视图。

### Reference Files to Read
- `references/interactive-elements.md` → "Layer Toggle Demo", "Code ↔ English Translation Blocks", "Pattern/Feature Cards", "Multiple-Choice Quizzes", "Callout Boxes", "Glossary Tooltips"
- `references/content-philosophy.md` → 全部
- `references/gotchas.md` → 全部

### Connections
- **Previous module:** 模块 3「请求的旅程」——请求走完流水线，最后拿到数据对象。
- **Next module:** 模块 5「缓存与防护」——回到中间件，深入看 RSSHub 最聪明的两个工程：缓存（怎么防止被同一请求打爆）和访问控制（怎么保护自己的服务）。本模块结尾：「输出搞定了。但还有一个大问题——如果一万个阅读器同时订阅同一个源，RSSHub 难道要跑去 B站 抓一万次吗？下模块看它怎么用缓存聪明化解。」
- **Tone/style notes:** 强调色 teal。模块 4 是奇数模块，用 `--color-bg-warm`。务必 tooltip：XML、RSS、Atom、JSON、JSX、组件、查询参数、Content-Type、MVC/模型-视图 等。Layer toggle 的 JS 用 main.js 里的 showLayer（如果 main.js 没有自动初始化 layer，写作 agent 需要在 module 末尾用一小段 inline onclick 调 window.showLayer；showLayer 在 interactive-elements.md 里有定义说明）。若 showLayer 不可用，用按钮 onclick 切换 layer div 的 display。
