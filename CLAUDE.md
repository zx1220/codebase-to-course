# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 这个仓库是什么

这是一个 **Claude Code skill**，不是可运行的应用。"源码"是 `SKILL.md` 加上 `references/` 下的规范文档。skill 被触发时，从任意代码库生成一份自包含的交互式单页 HTML 课程。`project/` 目录存放 **课程看板**（所有已建课程的 dashboard）和若干 **已建好的示例课程**——它们是产物，不是待编辑的源码。

仓库里**没有包管理器、构建工具链、测试套件、linter**。一切只是纯 HTML/CSS/JS 加两个 bash 脚本。

## 常用命令

```bash
# 构建一门课程：把各部分组装成 index.html，并自动刷新看板。
cd project/<course-name> && bash build.sh

# 只重建看板 dashboard（project/index.html），不动任何课程。
cd project && bash build-gallery.sh
```

`build.sh` 是唯一的构建步骤，它组装完课程后会自动调用 `build-gallery.sh`，所以基本不用手动跑看板脚本。查看结果时直接用浏览器打开生成的 `index.html`——没有 dev server。

## 架构：课程的两条构建路径

仓库里的课程有两种完全不同的来源，看课程目录里有什么文件就能区分。

### 路径 A：五文件组装模型（SKILL.md 的标准流程）

**逐字复制契约（不可违反）。** 每门课程目录由 `references/` 里的五个文件组装而成。其中四个必须**逐字节复制**，绝不重新生成或编辑：

- `styles.css` → `<course>/styles.css`
- `main.js` → `<course>/main.js`
- `_footer.html` → `<course>/_footer.html`
- `build.sh` → `<course>/build.sh`

只有 `_base.html` 允许定制，且只有两处替换：两处 `COURSE_TITLE` 字符串，和四个 `ACCENT_*` CSS 占位符（从 `references/_base.html` 注释块里选一套配色）。其余内容（`NAV_DOTS`、`<html>`/`<head>`/`<body>` 外壳）一律不动。

**组装模型。** 一门课程就是一组 HTML 片段目录：

```text
project/<course-name>/
  _base.html        ← <head>/导航外壳（开放式，没有闭合标签）
  modules/*.html    ← 唯一手写的内容：每个文件是一个裸的
                      <section class="module" id="module-N">…</section> 块，
                      不含 <html>/<head>/<body>/<style>/<script> 标签
  _footer.html      ← 闭合外壳
  index.html        ← 绝不手写；由 build.sh 生成
```

`build.sh` 实际上就是 `cat _base.html modules/*.html _footer.html > index.html`。模块顺序就是 `modules/` 目录的 shell glob 顺序，因此每个文件名的 `0N-` 数字前缀（`01-intro.html`、`02-actors.html`…）**就是**课程序列。前缀数字必须与 section 的 `id="module-N"` 一致（如 `01-*` → `module-1`）。

**导航点（nav dots）是生成的，绝不手写。** `main.js` 在加载时扫描 `.module` section 自动构建导航点条，所以导航永远不会和模块漂移。只在需要更短 tooltip 时给 `<section>` 加 `data-nav-title="short"`。

### 路径 B：Python 一次性生成器（根目录的 build_*.py）

仓库根目录有 4 个 Python 脚本：`build_course.py`/`build_html.py` 生成 `project/pojv-course/`，`build_py_course.py`/`build_py_html.py` 生成 `project/py-course/`。它们把特定的中文知识手册 markdown 解析成 JSON 再渲染成**单文件** `index.html`，产物目录里只有这一个文件，**不遵循**五文件模型。

这 4 个脚本是**历史一次性生成器**：源文件路径硬编码为原作者机器上的绝对路径（`/Users/zhangxiang/Downloads/...`），在本机不可重跑。不要模仿它们建新课程——新课程一律走路径 A；改这两个课程的内容意味着改脚本后重跑（在原机器上），或直接放弃。脚本末尾和 `build.sh` 一样会自动刷新看板（刷新失败非致命）。

**看板对两类课程都兼容。** `build-gallery.sh` 扫描 `project/*/index.html` 时，模块计数兼容两种标记：路径 A 课程用 `data-target="module-N"`，路径 B 课程用 `id="mod-N"`。

## SKILL.md 内部的两条写作路径（一个设计决策）

- **Sequential（顺序）**——简单代码库（单一入口、≤5 个模块）。先在工作笔记里给每个模块草拟一行 mini-brief，然后逐个写模块。
- **Parallel（并行）**——复杂代码库（全栈/多服务、6+ 个模块）。**Phase 2.5** 给每个模块写完整 brief 到 `<course>/briefs/0N-slug.md`（模板：`references/module-brief-template.md`），对照 Phase 1 的提取清单做强制覆盖检查，然后按每批 3 个分派给子 agent 写模块。brief 里预先摘好了代码片段，写作 agent 完全不需要读代码库。

两条路径里只有模块 HTML 不同；五个 reference 文件的复制方式完全一样。

## 生成课程内容的硬规则

- **所有课程内容是中文**——标题、正文、按钮、tooltip、测验文本，以及代码↔翻译块的"大白话"侧。代码片段本身保留原文。（`SKILL.md` 顶部明文规定。）
- **每门课程必须包含全部六个骨干元素**：至少一个群聊动画、至少一个消息/数据流动画、每模块一个代码↔英文翻译块、每模块一个测验、每模块每个技术术语首次出现时加术语表 tooltip、每模块结尾一张**康奈尔总结卡**（测验之后的收官屏：线索栏 + 遮盖笔记自测 + 费曼挑战 + 大白话总结，模式见 `references/interactive-elements.md`）。
- **每门课程先定义唯一可检验的学习成果**（「学完你能做到___」，展示在模块 1 开头的 callout）；每个模块头部用 `.module-subtitle` 前缀标注「⏱ 约 N 分钟」（一个番茄钟 15–25 分钟，超 30 分钟应拆分）。方法论详见 `references/content-philosophy.md` › The Learning Methodology。
- **代码片段从目标代码库逐字复制**，带文件路径 + 行号——绝不简化或改写。
- `references/` 文件**在到达相应阶段时才懒加载读取**，不要一开始全读（`SKILL.md` › Reference Files 列明了哪个阶段读哪个文件）。这是有意的上下文管理。

## 构建注意事项

- **没有课程清单要维护。** 看板（`project/index.html`）由 `build-gallery.sh` 扫描 `project/*/index.html` 生成——不存在 `courses.json` 之类的注册表需要同步。新增课程 = 构建它；dashboard 自动收录。
- **`build-gallery.sh` 是可移植的。** 它会先探测 `stat` 的风格（GNU `stat -c` vs BSD/macOS `stat -f`），所以在 Linux 和 macOS 上日期都正确。每门课程的 `build.sh` 末尾自动调用它；看板刷新失败是非致命的（课程自身的 `index.html` 仍然已构建）。
- **`SKILL.md` 中的路径相对于仓库根目录**（即持有 `SKILL.md` 的目录），因此这个 skill 不受 checkout 位置影响。
