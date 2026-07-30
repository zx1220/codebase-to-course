# -*- coding: utf-8 -*-
"""
将 build_py_course.py 解析好的 /tmp/py_data.json 渲染成
互动教学型单文件 HTML：project/py-course/index.html
"""
import json
import os
import subprocess
import html as html_mod

OUT = "/Users/zhangxiang/github/codebase-to-course/project/py-course/index.html"

with open("/tmp/py_data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

def esc(s):
    return html_mod.escape(str(s), quote=True)

def slug(pid):
    return f"kp-{pid}"

ELEMENT_META = [
    ("是什么", "def", "是什么 · 核心定义", "📘"),
    ("为什么", "why", "为什么 · 底层逻辑", "🧠"),
    ("怎么用", "how", "怎么用 · 落地方法", "🛠️"),
    ("费曼通俗解释", "feynman", "费曼通俗解释", "💡"),
    ("典型应用场景", "scene", "典型应用场景", "🎯"),
    ("避坑提醒", "pitfall", "避坑提醒", "⚠️"),
]

DIFF_COLORS = {
    "基础记忆": "#10b981",
    "进阶理解": "#f59e0b",
    "场景应用": "#ef4444",
    "综合内化": "#8b5cf6",
}

# ---------- 知识点 ----------
def render_point(pt):
    aid = slug(pt["id"])
    ordered = {e["key"]: e for e in pt["elements"]}
    elem_html = []
    for key, cls, label, icon in ELEMENT_META:
        e = ordered.get(key)
        if not e:
            continue
        elem_html.append(f"""
    <div class="elem elem-{cls}">
      <div class="elem-head"><span class="elem-icon">{icon}</span><span class="elem-label">{label}</span></div>
      <div class="elem-body">{e['html']}</div>
    </div>""")
    return f"""
  <section class="kp" id="{aid}" data-module="{pt['module_num']}" data-title="{esc(pt['title'])}">
    <div class="kp-anchor"><a href="#{aid}" class="anchor-link">#</a></div>
    <div class="kp-tag">知识点 {esc(pt['id'])} · 第{pt['module_num']}章</div>
    <h3 class="kp-title">{esc(pt['title'])}</h3>
    <div class="kp-meta">所属：{esc(pt['chapter_title'])}</div>
    <div class="elems">{''.join(elem_html)}</div>
  </section>"""

# ---------- 习题（章节级） ----------
def render_exercises(ch):
    exs = ch.get("exercises", [])
    if not exs:
        return ""
    cid = ch["id"]
    blocks = []
    for ex in exs:
        qid = f"ch-{cid}-q{ex['num']}"
        diff_color = DIFF_COLORS.get(ex["diff"], "#64748b")
        opts_html = ""
        if ex["options"]:
            opts_html = '<div class="ex-opts">' + "".join(
                f'<div class="ex-opt">{esc(o)}</div>' for o in ex["options"]
            ) + "</div>"
        extra_html = ""
        if ex["extra"]:
            extra_html = f'<div class="ex-extra">{esc(ex["extra"])}</div>'
        qtype_html = f'<span class="ex-qtype">{esc(ex["qtype"])}</span>' if ex["qtype"] else ""

        ans = ch.get("answers", {}).get(str(ex["num"]), "")
        ans_html = ""
        if ans:
            ans_html = f"""
        <button class="ex-toggle" data-target="{qid}-ans" data-opened="false">查看答案 →</button>
        <div class="ex-ans" id="{qid}-ans" hidden>{ans}</div>"""
        else:
            ans_html = '<div class="ex-ans-empty">（本节解析待补充）</div>'

        blocks.append(f"""
      <div class="ex" id="{qid}">
        <div class="ex-qhead">
          <span class="ex-num">第 {ex['num']} 题</span>
          <span class="ex-diff" style="background:{diff_color}">{esc(ex['diff'])}</span>
          {qtype_html}
        </div>
        <div class="ex-stem">{esc(ex['stem'])}</div>
        {opts_html}
        {extra_html}
        {ans_html}
      </div>""")

    return f"""
    <div class="exercises">
      <div class="exercises-head">📝 本章配套习题（{len(exs)} 题）</div>
      {''.join(blocks)}
    </div>"""

# ---------- 章节 ----------
def render_chapter(ch):
    pts = "".join(render_point(pt) for pt in ch["points"])
    ex_html = render_exercises(ch)
    return f"""
    <div class="chapter" id="ch-{esc(ch['id'])}">
      <h2 class="chapter-title"><span class="chapter-id">{esc(ch['id'])}</span>{esc(ch['title'])}</h2>
      {pts}
      {ex_html}
    </div>"""

# ---------- 模块（= 章） ----------
def render_module(mod):
    chs = "".join(render_chapter(ch) for ch in mod["chapters"])
    pt_count = sum(len(ch["points"]) for ch in mod["chapters"])
    return f"""
  <div class="module" id="mod-{mod['num']}">
    <header class="module-header">
      <div class="module-badge">第 {mod['num']} 章</div>
      <h2 class="module-title">{esc(mod['title'])}</h2>
      <div class="module-count">{pt_count} 个知识点</div>
    </header>
    {chs}
  </div>"""

# ---------- 侧边栏 ----------
def render_sidebar():
    items = []
    for mod in DATA["modules"]:
        children = []
        for ch in mod["chapters"]:
            sub = "".join(
                f'<li><a href="#{slug(pt["id"])}" class="nav-point">{esc(pt["id"])} {esc(pt["title"])}</a></li>'
                for pt in ch["points"]
            )
            children.append(f"""
          <li>
            <a href="#ch-{esc(ch['id'])}" class="nav-chapter">{esc(ch['id'])} {esc(ch['title'])}</a>
            <ul class="nav-sub">{sub}</ul>
          </li>""")
        items.append(f"""
      <li class="nav-module">
        <a href="#mod-{mod['num']}" class="nav-module-link"><span class="nav-mod-num">{mod['num']}</span>{esc(mod['title'])}</a>
        <ul class="nav-chapters">{''.join(children)}</ul>
      </li>""")
    return f'<ul class="nav-tree">{"".join(items)}</ul>'

# ---------- 概览 ----------
def render_overview():
    prose = DATA["overview_prose"]
    mermaid_html = ""
    for m in DATA["mermaid"]:
        mermaid_html += f"""
    <div class="mermaid-block">
      <h3 class="mermaid-title">{esc(m['title'])}</h3>
      <div class="mermaid">{esc(m['code'])}</div>
    </div>"""
    return f"""
    <div class="overview prose-block">
      <h2>核心内容概览</h2>
      {prose}
      {mermaid_html}
    </div>"""

# ---------- 组装 ----------
stats = DATA["stats"]
sidebar = render_sidebar()
overview = render_overview()
modules_html = "".join(render_module(m) for m in DATA["modules"])

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(DATA['title'])} · 互动课程</title>
<style>
:root{{
  --bg:#f7f8fb; --surface:#ffffff; --surface-2:#f1f3f9; --border:#e3e6ee;
  --text:#1a1f36; --text-2:#5b6478; --text-3:#8a93a6;
  --primary:#3776ab; --primary-2:#4a90c8; --primary-soft:#eaf2f9;
  --accent:#ffd43b;
  --shadow:0 1px 3px rgba(20,25,50,.06),0 1px 2px rgba(20,25,50,.04);
  --shadow-lg:0 10px 40px -10px rgba(20,25,50,.15);
  --radius:14px;
  --c-def:#3776ab; --c-why:#0891b2; --c-how:#7c3aed; --c-feynman:#d97706;
  --c-scene:#059669; --c-pitfall:#dc2626;
  --c-def-bg:#eaf2f9; --c-why-bg:#ecfeff; --c-how-bg:#f5f3ff;
  --c-feynman-bg:#fffbeb; --c-scene-bg:#ecfdf5; --c-pitfall-bg:#fef2f2;
  --code-bg:#1e1e2e; --code-text:#e6e9f2;
  --sidebar-w:300px;
}}
[data-theme="dark"]{{
  --bg:#0f1117; --surface:#181b24; --surface-2:#1f2330; --border:#2a2f3d;
  --text:#e6e9f2; --text-2:#a0a8bd; --text-3:#6b7488;
  --primary:#5b9bd5; --primary-2:#7fb3de; --primary-soft:#1e2a38;
  --shadow:0 1px 3px rgba(0,0,0,.3);
  --shadow-lg:0 10px 40px -10px rgba(0,0,0,.5);
  --c-def-bg:#1a2a3a; --c-why-bg:#0c2a33; --c-how-bg:#221638;
  --c-feynman-bg:#3a2a0c; --c-scene-bg:#0a2e22; --c-pitfall-bg:#330e0e;
  --code-bg:#0d0d18;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:90px}}
body{{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--text);line-height:1.75;font-size:16px;
  -webkit-font-smoothing:antialiased;
}}
a{{color:inherit;text-decoration:none}}
code{{background:var(--surface-2);padding:2px 6px;border-radius:4px;font-size:.9em;font-family:"SF Mono",Consolas,"Courier New",monospace;color:var(--primary)}}
pre{{background:var(--code-bg);color:var(--code-text);padding:16px 18px;border-radius:10px;overflow-x:auto;margin:10px 0;font-size:13.5px;line-height:1.6;font-family:"SF Mono",Consolas,"Courier New",monospace}}
pre code{{background:none;padding:0;color:inherit;font-size:inherit}}
[data-theme="dark"] pre{{border:1px solid var(--border)}}

/* 顶部进度条 */
.progress-bar{{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,var(--primary),var(--accent));width:0;z-index:1000;transition:width .1s}}

/* 顶栏 */
.topbar{{
  position:sticky;top:0;z-index:100;background:rgba(255,255,255,.85);
  backdrop-filter:saturate(180%) blur(12px);
  border-bottom:1px solid var(--border);padding:14px 24px;
  display:flex;align-items:center;gap:16px;
}}
[data-theme="dark"] .topbar{{background:rgba(15,17,23,.85)}}
.topbar-logo{{display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px;flex-shrink:0}}
.topbar-logo .logo-mark{{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--primary),#ffd43b);display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:800}}
.topbar-search{{flex:1;max-width:420px;position:relative}}
.topbar-search input{{
  width:100%;padding:9px 14px 9px 38px;border:1px solid var(--border);border-radius:10px;
  background:var(--surface);color:var(--text);font-size:14px;transition:.2s;
}}
.topbar-search input:focus{{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-soft)}}
.topbar-search .search-icon{{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--text-3)}}
.topbar-actions{{display:flex;gap:8px;align-items:center;margin-left:auto}}
.icon-btn{{
  width:38px;height:38px;border:1px solid var(--border);background:var(--surface);border-radius:10px;
  cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--text-2);
  font-size:18px;transition:.2s;
}}
.icon-btn:hover{{border-color:var(--primary);color:var(--primary)}}
.menu-btn{{display:none}}

/* 布局 */
.layout{{display:flex;max-width:1400px;margin:0 auto;gap:0;align-items:flex-start}}
.sidebar{{
  width:var(--sidebar-w);flex-shrink:0;position:sticky;top:67px;height:calc(100vh - 67px);
  overflow-y:auto;padding:24px 16px 24px 24px;border-right:1px solid var(--border);
}}
.sidebar::-webkit-scrollbar{{width:6px}}
.sidebar::-webkit-scrollbar-thumb{{background:var(--border);border-radius:3px}}
.nav-tree{{list-style:none}}
.nav-module{{margin-bottom:6px}}
.nav-module-link{{
  display:flex;align-items:center;gap:8px;padding:9px 10px;border-radius:8px;font-weight:600;
  font-size:14px;color:var(--text);transition:.15s;cursor:pointer;
}}
.nav-module-link:hover{{background:var(--surface-2)}}
.nav-module-link.active{{background:var(--primary-soft);color:var(--primary)}}
.nav-mod-num{{
  width:22px;height:22px;border-radius:6px;background:var(--primary);color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;
}}
.nav-module-link.active .nav-mod-num{{background:var(--primary-2)}}
.nav-chapters{{list-style:none;padding-left:14px;max-height:0;overflow:hidden;transition:max-height .3s ease}}
.nav-module.open .nav-chapters{{max-height:3000px}}
.nav-chapter{{
  display:block;padding:6px 10px;border-radius:6px;font-size:13px;color:var(--text-2);
  transition:.15s;font-weight:500;
}}
.nav-chapter:hover{{color:var(--primary);background:var(--surface-2)}}
.nav-sub{{list-style:none;padding-left:12px;border-left:1.5px solid var(--border);margin:4px 0 6px 10px}}
.nav-point{{
  display:block;padding:5px 10px;border-radius:6px;font-size:12.5px;color:var(--text-3);
  transition:.15s;line-height:1.4;
}}
.nav-point:hover{{color:var(--primary);background:var(--surface-2)}}
.nav-point.active{{color:var(--primary);font-weight:600;background:var(--primary-soft)}}

/* 主内容 */
.main{{flex:1;min-width:0;padding:0 40px 80px;max-width:1000px;margin:0 auto}}

/* Hero */
.hero{{padding:56px 0 40px;border-bottom:1px solid var(--border);margin-bottom:8px}}
.hero-eyebrow{{display:inline-block;padding:5px 12px;background:var(--primary-soft);color:var(--primary);border-radius:20px;font-size:13px;font-weight:600;margin-bottom:18px}}
.hero h1{{font-size:38px;font-weight:800;line-height:1.25;letter-spacing:-.5px;margin-bottom:14px;background:linear-gradient(135deg,var(--text),var(--primary));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.hero-sub{{font-size:18px;color:var(--text-2);margin-bottom:24px}}
.hero-stats{{display:flex;gap:32px;flex-wrap:wrap}}
.hero-stat .num{{font-size:28px;font-weight:800;color:var(--primary);line-height:1}}
.hero-stat .lbl{{font-size:13px;color:var(--text-3);margin-top:4px}}

/* 概览 */
.prose-block{{padding:40px 0}}
.prose-block h2{{font-size:26px;font-weight:700;margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid var(--primary);display:inline-block}}
.prose-block p{{margin-bottom:14px;color:var(--text)}}
.mermaid-block{{margin:32px 0;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px;box-shadow:var(--shadow);overflow-x:auto}}
.mermaid-title{{font-size:16px;font-weight:600;margin-bottom:16px;color:var(--text)}}
[data-theme="dark"] .mermaid{{filter:invert(.9) hue-rotate(180deg)}}

/* 模块 */
.module{{padding:36px 0 16px}}
.module-header{{display:flex;align-items:center;gap:16px;margin-bottom:28px;flex-wrap:wrap}}
.module-badge{{padding:6px 14px;background:linear-gradient(135deg,var(--primary),var(--primary-2));color:#fff;border-radius:8px;font-size:13px;font-weight:700}}
.module-title{{font-size:30px;font-weight:800;letter-spacing:-.3px}}
.module-count{{padding:4px 12px;background:var(--surface-2);border-radius:20px;font-size:13px;color:var(--text-2)}}

/* 章节 */
.chapter{{margin-bottom:24px}}
.chapter-title{{display:flex;align-items:center;gap:12px;font-size:22px;font-weight:700;margin:28px 0 18px;padding-bottom:10px;border-bottom:1px solid var(--border)}}
.chapter-id{{font-size:14px;font-weight:600;color:var(--primary);background:var(--primary-soft);padding:3px 10px;border-radius:6px}}

/* 知识点卡片 */
.kp{{
  position:relative;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:28px 30px;margin-bottom:24px;box-shadow:var(--shadow);scroll-margin-top:90px;
  transition:box-shadow .25s,border-color .25s;
}}
.kp:hover{{box-shadow:var(--shadow-lg);border-color:var(--primary)}}
.kp-anchor{{position:absolute;top:14px;right:18px;opacity:0;transition:.2s}}
.kp:hover .kp-anchor{{opacity:1}}
.anchor-link{{color:var(--text-3);font-size:18px}}
.kp-tag{{font-size:12px;color:var(--primary);font-weight:600;letter-spacing:.5px;margin-bottom:6px}}
.kp-title{{font-size:23px;font-weight:700;margin-bottom:6px;letter-spacing:-.2px}}
.kp-meta{{font-size:13px;color:var(--text-3);margin-bottom:20px}}

/* 六要素 */
.elems{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.elem{{border-radius:12px;padding:16px 18px;border:1px solid;transition:.2s}}
.elem:hover{{transform:translateY(-2px)}}
.elem-head{{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-size:14px;font-weight:700}}
.elem-icon{{font-size:16px}}
.elem-body{{font-size:14.5px;color:var(--text)}}
.elem-body p{{margin-bottom:8px}}.elem-body p:last-child{{margin-bottom:0}}
.elem-body ol,.elem-body ul{{padding-left:20px;margin-bottom:8px}}
.elem-body li{{margin-bottom:5px}}
.elem-body strong{{color:var(--text);font-weight:700}}
.elem-def{{background:var(--c-def-bg);border-color:rgba(55,118,171,.25)}}.elem-def .elem-label{{color:var(--c-def)}}
.elem-why{{background:var(--c-why-bg);border-color:rgba(8,145,178,.25)}}.elem-why .elem-label{{color:var(--c-why)}}
.elem-how{{background:var(--c-how-bg);border-color:rgba(124,58,237,.25)}}.elem-how .elem-label{{color:var(--c-how)}}
.elem-feynman{{background:var(--c-feynman-bg);border-color:rgba(217,119,6,.25)}}.elem-feynman .elem-label{{color:var(--c-feynman)}}
.elem-scene{{background:var(--c-scene-bg);border-color:rgba(5,150,105,.25)}}.elem-scene .elem-label{{color:var(--c-scene)}}
.elem-pitfall{{background:var(--c-pitfall-bg);border-color:rgba(220,38,38,.25)}}.elem-pitfall .elem-label{{color:var(--c-pitfall)}}

/* 习题 */
.exercises{{margin-top:20px;border-top:1px dashed var(--border);padding-top:18px}}
.exercises-head{{font-size:15px;font-weight:700;margin-bottom:14px;color:var(--text)}}
.ex{{background:var(--surface-2);border-radius:10px;padding:16px 18px;margin-bottom:12px}}
.ex-qhead{{display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap}}
.ex-num{{font-size:13px;font-weight:700;color:var(--text)}}
.ex-diff{{padding:2px 9px;border-radius:10px;font-size:11px;color:#fff;font-weight:600}}
.ex-qtype{{padding:2px 9px;background:var(--surface);border:1px solid var(--border);border-radius:10px;font-size:11px;color:var(--text-2)}}
.ex-stem{{font-size:15px;font-weight:500;margin-bottom:10px;line-height:1.6}}
.ex-opts{{margin:8px 0;padding-left:8px}}
.ex-opt{{padding:5px 0;font-size:14px;color:var(--text-2)}}
.ex-extra{{font-size:13.5px;color:var(--text-2);background:var(--surface);padding:10px 12px;border-radius:8px;margin-top:8px;line-height:1.6}}
.ex-toggle{{
  margin-top:10px;padding:6px 14px;background:var(--primary);color:#fff;border:none;border-radius:8px;
  font-size:13px;cursor:pointer;font-weight:500;transition:.2s;
}}
.ex-toggle:hover{{background:var(--primary-2)}}
.ex-ans{{margin-top:12px;padding:14px 16px;background:var(--surface);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;font-size:14px;animation:fadein .25s}}
.ex-ans strong{{color:var(--primary)}}
.ex-ans-empty{{margin-top:10px;font-size:13px;color:var(--text-3);font-style:italic}}
@keyframes fadein{{from{{opacity:0;transform:translateY(-6px)}}to{{opacity:1}}}}

/* 高亮（搜索） */
mark.search-hit{{background:#fde68a;color:inherit;padding:0 2px;border-radius:3px}}
[data-theme="dark"] mark.search-hit{{background:#7c5e00;color:#fff}}

/* 回到顶部 */
.totop{{
  position:fixed;bottom:30px;right:30px;width:46px;height:46px;border-radius:50%;
  background:var(--primary);color:#fff;border:none;cursor:pointer;font-size:20px;
  box-shadow:var(--shadow-lg);opacity:0;pointer-events:none;transition:.3s;z-index:90;
  display:flex;align-items:center;justify-content:center;
}}
.totop.show{{opacity:1;pointer-events:auto}}
.totop:hover{{transform:translateY(-3px);background:var(--primary-2)}}

/* 响应式 */
@media(max-width:960px){{
  .elems{{grid-template-columns:1fr}}
  .sidebar{{transform:translateX(-100%);transition:transform .3s;z-index:200;box-shadow:var(--shadow-lg);background:var(--bg)}}
  .sidebar.open{{transform:translateX(0)}}
  .menu-btn{{display:flex}}
  .main{{padding:0 20px 60px}}
  .hero h1{{font-size:28px}}
  .module-title{{font-size:24px}}
  .kp{{padding:22px 18px}}
  .topbar-search{{max-width:200px}}
}}
@media(max-width:560px){{
  .topbar-search{{display:none}}
  .hero{{padding:36px 0 28px}}
  .hero h1{{font-size:24px}}
  .hero-stats{{gap:20px}}
}}
.sidebar-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:150}}
.sidebar-overlay.show{{display:block}}
</style>
</head>
<body data-theme="light">

<div class="progress-bar" id="progressBar"></div>

<header class="topbar">
  <button class="icon-btn menu-btn" id="menuBtn" aria-label="目录">☰</button>
  <div class="topbar-logo">
    <div class="logo-mark">Py</div>
    <span>Python 教程 · 课程</span>
  </div>
  <div class="topbar-search">
    <span class="search-icon">🔍</span>
    <input type="text" id="searchInput" placeholder="搜索知识点 / 关键词…" autocomplete="off">
  </div>
  <div class="topbar-actions">
    <button class="icon-btn" id="themeBtn" title="切换主题" aria-label="切换主题">🌙</button>
    <button class="icon-btn" id="tocBtn" title="目录" aria-label="目录">📖</button>
  </div>
</header>

<div class="sidebar-overlay" id="sidebarOverlay"></div>

<div class="layout">
  <aside class="sidebar" id="sidebar">
    <nav>{sidebar}</nav>
  </aside>

  <main class="main">
    <section class="hero">
      <span class="hero-eyebrow">Python 3.14 中文教程 · 知识体系</span>
      <h1>{esc(DATA['title'])}</h1>
      <p class="hero-sub">{esc(DATA['subtitle'])} · 体系化学习｜快速复盘｜面试准备</p>
      <div class="hero-stats">
        <div class="hero-stat"><div class="num">{stats['modules']}</div><div class="lbl">章节</div></div>
        <div class="hero-stat"><div class="num">{stats['points']}</div><div class="lbl">知识点</div></div>
        <div class="hero-stat"><div class="num">{stats['exercises']}</div><div class="lbl">配套习题</div></div>
        <div class="hero-stat"><div class="num">{len(DATA['mermaid'])}</div><div class="lbl">知识图谱</div></div>
      </div>
    </section>

    {overview}

    {modules_html}
  </main>
</div>

<button class="totop" id="toTop" aria-label="回到顶部">↑</button>

<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
(function(){{
  const body=document.body;
  // 主题
  const themeBtn=document.getElementById('themeBtn');
  const saved=localStorage.getItem('py-theme');
  if(saved){{body.setAttribute('data-theme',saved);themeBtn.textContent=saved==='dark'?'☀️':'🌙';}}
  themeBtn.addEventListener('click',()=>{{
    const cur=body.getAttribute('data-theme')==='dark'?'light':'dark';
    body.setAttribute('data-theme',cur);localStorage.setItem('py-theme',cur);
    themeBtn.textContent=cur==='dark'?'☀️':'🌙';
    if(window.mermaid)mermaid.initialize({{theme:cur==='dark'?'dark':'default'}});
  }});

  // 移动端侧栏
  const sidebar=document.getElementById('sidebar'),overlay=document.getElementById('sidebarOverlay');
  const menuBtn=document.getElementById('menuBtn'),tocBtn=document.getElementById('tocBtn');
  const toggleSidebar=(o)=>{{sidebar.classList.toggle('open',o);overlay.classList.toggle('show',o);}};
  menuBtn.addEventListener('click',()=>toggleSidebar(!sidebar.classList.contains('open')));
  tocBtn.addEventListener('click',()=>toggleSidebar(!sidebar.classList.contains('open')));
  overlay.addEventListener('click',()=>toggleSidebar(false));

  // 模块折叠
  document.querySelectorAll('.nav-module-link').forEach(link=>{{
    link.addEventListener('click',function(e){{
      const mod=this.closest('.nav-module');
      document.querySelectorAll('.nav-module').forEach(m=>{{if(m!==mod)m.classList.remove('open');}});
      mod.classList.toggle('open');
    }});
  }});

  // 进度条
  const progressBar=document.getElementById('progressBar');
  window.addEventListener('scroll',()=>{{
    const h=document.documentElement;
    progressBar.style.width=(h.scrollTop/(h.scrollHeight-h.clientHeight)*100)+'%';
  }});

  // 回到顶部
  const toTop=document.getElementById('toTop');
  window.addEventListener('scroll',()=>toTop.classList.toggle('show',window.scrollY>500));
  toTop.addEventListener('click',()=>window.scrollTo({{top:0,behavior:'smooth'}}));

  // 当前阅读位置高亮
  const kps=document.querySelectorAll('.kp');
  const navPoints=document.querySelectorAll('.nav-point');
  const observer=new IntersectionObserver((entries)=>{{
    entries.forEach(en=>{{
      if(en.isIntersecting){{
        const id=en.target.id;
        navPoints.forEach(n=>n.classList.remove('active'));
        const active=document.querySelector('.nav-point[href="#'+id+'"]');
        if(active)active.classList.add('active');
      }}
    }});
  }},{{rootMargin:'-100px 0px -70% 0px',threshold:0}});
  kps.forEach(kp=>observer.observe(kp));

  // 习题答案展开
  document.querySelectorAll('.ex-toggle').forEach(btn=>{{
    btn.addEventListener('click',function(){{
      const target=document.getElementById(this.dataset.target);
      const opened=this.dataset.opened==='true';
      target.hidden=opened;
      this.dataset.opened=(!opened).toString();
      this.textContent=opened?'查看答案 →':'收起答案 ↑';
    }});
  }});

  // 搜索
  const searchInput=document.getElementById('searchInput');
  const main=document.querySelector('.main');
  let searchTimer;
  const clearHits=()=>main.querySelectorAll('mark.search-hit').forEach(m=>{{
    const p=m.parentNode;p.replaceChild(document.createTextNode(m.textContent),m);p.normalize();
  }});
  const highlight=(node,term)=>{{
    if(node.nodeType===3){{
      const idx=node.nodeValue.toLowerCase().indexOf(term);
      if(idx>=0){{
        const span=document.createElement('mark');span.className='search-hit';
        span.textContent=node.nodeValue.substring(idx,idx+term.length);
        const rest=document.createTextNode(node.nodeValue.substring(idx+term.length));
        node.nodeValue=node.nodeValue.substring(0,idx);
        node.parentNode.insertBefore(span,node.nextSibling);
        node.parentNode.insertBefore(rest,span.nextSibling);
      }}
    }}else if(node.nodeType===1&&node.childNodes&&!['SCRIPT','STYLE','MARK','CODE','PRE'].includes(node.nodeName)){{
      Array.from(node.childNodes).forEach(c=>highlight(c,term));
    }}
  }};
  searchInput.addEventListener('input',function(){{
    clearTimeout(searchTimer);
    searchTimer=setTimeout(()=>{{
      clearHits();
      const term=this.value.trim().toLowerCase();
      if(term.length<2)return;
      highlight(main,term);
      const first=document.querySelector('mark.search-hit');
      if(first)first.scrollIntoView({{behavior:'smooth',block:'center'}});
    }},300);
  }});

  // mermaid
  if(window.mermaid){{
    mermaid.initialize({{startOnLoad:true,theme:'default',securityLevel:'loose'}});
  }}
}})();
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = len(HTML.encode("utf-8")) / 1024
print(f"✅ HTML课程已生成: {OUT}")
print(f"   文件大小: {size_kb:.1f} KB")

# 自动刷新看板，让 project/index.html 收录新课程
GALLERY = os.path.join(os.path.dirname(os.path.dirname(OUT)), "build-gallery.sh")
if os.path.isfile(GALLERY):
    try:
        result = subprocess.run(
            ["bash", GALLERY],
            cwd=os.path.dirname(GALLERY),
            capture_output=True, text=True,
        )
        print(result.stdout.strip())
        if result.returncode != 0:
            print(f"⚠️  看板刷新失败（非致命）：{result.stderr.strip()}")
    except Exception as e:
        print(f"⚠️  看板刷新跳过：{e}")
else:
    print("ℹ️  未找到 build-gallery.sh，跳过看板刷新")
