# -*- coding: utf-8 -*-
"""
将《Python 官方教程知识体系学习手册》markdown 解析为 JSON，
供 build_py_html.py 渲染成互动教学型单文件 HTML。

文档结构层级 → 模板层级映射：
    # 第N章 ...        → 模块 (module)
    ## X.Y ...         → 章节 (chapter)
    ### X.Y.Z ...      → 知识点 (point)
    【...】            → 六要素块 (是什么/为什么/怎么用/费曼/典型应用场景/避坑提醒)
    #### 本节配套习题   → 该章节末尾的习题集

答案策略：附录的「习题参考答案」经核对存在多处错位与内容缺失
（如「第1-2章」只给 4 条，而两章实有 6 题；且若干答案明显错误，
例：第1章 Q1 正确答案为 B 蒙提·派森，附录却标 A）。
因此本脚本不依赖附录，而是直接从题面推导正确答案并内置。
"""
import re
import json

SRC = "/Users/zhangxiang/Downloads/Python官方教程知识体系学习手册.md"

with open(SRC, "r", encoding="utf-8") as f:
    raw = f.read()

# ---------- 行内 markdown 渲染 ----------
def render_inline(text):
    text = (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text

# ---------- 块级渲染（含 ```python 围栏代码块，相比 build_course.py 的增强） ----------
def render_block(content_lines):
    html = []
    i = 0
    n = len(content_lines)
    while i < n:
        ln = content_lines[i]
        stripped = ln.strip()

        # 1) 围栏代码块 ```lang ... ```  → <pre><code>
        fence = re.match(r"^```(\w*)\s*$", stripped)
        if fence:
            lang = fence.group(1)
            code_buf = []
            i += 1
            while i < n and content_lines[i].strip() != "```":
                code_buf.append(content_lines[i])
                i += 1
            i += 1  # 跳过收尾 ```
            lang_attr = f' class="language-{lang}"' if lang else ""
            html.append(
                f'<pre><code{lang_attr}>{render_inline(chr(10).join(code_buf))}</code></pre>'
            )
            continue

        if not stripped:
            i += 1
            continue

        # 2) 有序列表  1. / ①
        if re.match(r"^\d+\.\s", stripped) or re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", stripped):
            items = []
            while i < n:
                s = content_lines[i].strip()
                if re.match(r"^\d+\.\s", s) or re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", s):
                    s2 = re.sub(r"^\d+\.\s+", "", s)
                    s2 = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", "", s2)
                    items.append([s2])
                    i += 1
                elif s.startswith("- ") or s.startswith("   "):
                    items[-1].append(s.lstrip(" -"))
                    i += 1
                elif s == "":
                    i += 1
                    break
                else:
                    break
            html.append("<ol>" + "".join(
                "<li>" + render_inline(" ".join(p for p in it if p)) + "</li>" for it in items
            ) + "</ol>")
            continue

        # 3) 无序列表 - x
        if stripped.startswith("- "):
            items = []
            while i < n:
                s = content_lines[i]
                ss = s.strip()
                if ss.startswith("- "):
                    items.append("<li>" + render_inline(ss[2:]) + "</li>")
                    i += 1
                elif s.startswith("   ") and ss:
                    if items:
                        items[-1] = items[-1].rstrip("</li>") + " " + render_inline(ss) + "</li>"
                    i += 1
                elif ss == "":
                    i += 1
                    break
                else:
                    break
            html.append("<ul>" + "".join(items) + "</ul>")
            continue

        # 4) 普通段落
        para = []
        while i < n:
            s = content_lines[i].strip()
            if (s == "" or s.startswith("- ") or s.startswith("```")
                    or re.match(r"^\d+\.\s", s) or re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩]", s)):
                break
            para.append(s)
            i += 1
        if para:
            html.append("<p>" + render_inline(" ".join(para)) + "</p>")
    return "\n".join(html)

# ---------- 三大区切分 ----------
overview_lines, detail_lines = [], []
in_overview = in_detail = False
for ln in raw.split("\n"):
    if ln.strip() == "## 一、知识体系总览":
        in_overview = True
        continue
    if ln.strip() == "## 二、分章节知识详解":
        in_overview = False
        in_detail = True
        continue
    # 附录答案不可靠，遇到即停止收集详情
    if ln.strip() == "# 附录：习题参考答案":
        in_detail = False
        continue
    if in_overview:
        overview_lines.append(ln)
    elif in_detail:
        detail_lines.append(ln)

# ---------- 总览 mermaid 提取 ----------
def extract_mermaid_blocks(text_lines):
    out, prose = [], []
    in_code = code_buf = pending_h = None
    for ln in text_lines:
        if ln.strip().startswith("```mermaid"):
            in_code, code_buf = True, []
            continue
        if in_code and ln.strip() == "```":
            in_code = False
            out.append((pending_h or "知识结构图", "\n".join(code_buf)))
            pending_h = None
            continue
        if in_code:
            code_buf.append(ln)
            continue
        if ln.startswith("### "):
            pending_h = ln[4:].strip()
            continue
        prose.append(ln)
    return out, prose

mermaid_blocks, overview_prose = extract_mermaid_blocks(overview_lines)

# ---------- 知识点详情解析 ----------
# 模块(# 第N章) → 章节(## X.Y) → 知识点(### X.Y.Z)
modules = []
cur_module = cur_chapter = cur_point = None
cur_block_key = None
cur_block_lines = []
in_exercises = False
ex_lines = []

def flush_block():
    global cur_block_key, cur_block_lines
    if cur_point is not None and cur_block_key is not None:
        cur_point["elements"].append({"key": cur_block_key, "html": render_block(cur_block_lines)})
    cur_block_key = None
    cur_block_lines = []

def close_exercises():
    """把当前收集的习题原文挂到所在章节（而非某个知识点）上。"""
    global in_exercises, ex_lines
    if in_exercises and cur_chapter is not None and ex_lines:
        cur_chapter.setdefault("exercises_raw_list", []).append("\n".join(ex_lines))
    in_exercises = False
    ex_lines = []

for ln in detail_lines:
    stripped = ln.strip()
    # 模块 = 章
    m = re.match(r"^# 第(\d+)章\s+(.*)$", stripped)
    if m:
        flush_block()
        close_exercises()
        cur_module = {"num": int(m.group(1)), "title": m.group(2).strip(), "chapters": []}
        modules.append(cur_module)
        cur_chapter = cur_point = None
        continue
    # 章节 = 节
    m = re.match(r"^## (\d+\.\d+)\s+(.*)$", stripped)
    if m and cur_module is not None:
        flush_block()
        close_exercises()
        cur_chapter = {"id": m.group(1), "title": m.group(2).strip(), "points": []}
        cur_module["chapters"].append(cur_chapter)
        cur_point = None
        continue
    # 知识点
    m = re.match(r"^### (\d+\.\d+\.\d+)\s+(.*)$", stripped)
    if m and cur_chapter is not None:
        flush_block()
        close_exercises()
        pid = m.group(1)
        cur_point = {
            "id": pid,
            "title": m.group(2).strip(),
            "chapter_id": cur_chapter["id"],
            "chapter_title": cur_chapter["title"],
            "module_num": cur_module["num"],
            "module_title": cur_module["title"],
            "elements": [],
        }
        cur_chapter["points"].append(cur_point)
        continue
    # 习题标记
    if stripped == "#### 本节配套习题":
        flush_block()
        in_exercises = True
        ex_lines = []
        continue
    # 【】要素块标题
    m = re.match(r"^【([^】]+)】\s*$", stripped)
    if m and cur_point is not None:
        flush_block()
        key = m.group(1).strip().split("|")[0].strip()
        cur_block_key = key
        cur_block_lines = []
        continue
    # 内容行
    if in_exercises:
        ex_lines.append(ln.rstrip())
    elif cur_block_key is not None:
        cur_block_lines.append(ln.rstrip())

flush_block()
close_exercises()

# ---------- 习题解析 ----------
DIFF_COLORS = {
    "基础记忆": "#10b981",
    "进阶理解": "#f59e0b",
    "场景应用": "#ef4444",
    "综合内化": "#8b5cf6",
}

def parse_exercises(raw):
    """把习题原文切成 [{num, diff, qtype, stem, options, extra}]。
    难度标记形如 **【基础记忆】**。"""
    if not raw or not raw.strip():
        return []
    chunks = re.split(r"(?m)^\s*(\d+)\.\s+", raw)
    parts = chunks[1:]
    items = []
    for i in range(0, len(parts), 2):
        num = parts[i]
        body = (parts[i + 1] if i + 1 < len(parts) else "").strip()
        if not body:
            continue
        first, _, rest = body.partition("\n")
        diff = qtype = ""
        stem = first
        dm = re.match(r"^\*\*【([^】]+)】\*\*\s*(.*)$", first)
        if dm:
            diff = dm.group(1).strip()
            stem = dm.group(2).strip()
        # 选项  A. / A. / - A. / A．（兼容有无短横线前缀、全半角句点）
        opts = []
        prose_after = []
        optpat = re.compile(r"^(?:-\s*)?([A-Z])[．\.]\s*(.+)$")
        for ln in rest.split("\n"):
            ls = ln.strip()
            if not ls:
                continue
            om = optpat.match(ls)
            if om:
                opts.append(om.group(1) + ". " + om.group(2))
            else:
                prose_after.append(ls)
        items.append({
            "num": int(num),
            "diff": diff,
            "qtype": qtype,
            "stem": stem,
            "options": opts,
            "extra": "\n".join(prose_after),
        })
    return items

for mod in modules:
    for ch in mod["chapters"]:
        ch["exercises"] = []
        for raw in ch.pop("exercises_raw_list", []):
            ch["exercises"].extend(parse_exercises(raw))

# ---------- 正确答案（由题面推导，不依赖不可靠的附录） ----------
# key = (章号, 题号) → 正确选项字母
CORRECT = {
    (1, 1): "B", (1, 2): "C", (1, 3): "B",
    (2, 1): "C", (2, 2): "A", (2, 3): "B",
    (3, 1): "B", (3, 2): "C", (3, 3): "D",
    (4, 1): "B", (4, 2): "B", (4, 3): "B",
    (5, 1): "B", (5, 2): "C", (5, 3): "D",
    (6, 1): "A", (6, 2): "D", (6, 3): "B",
    (7, 1): "C", (7, 2): "C", (7, 3): "B",
    (8, 1): "B", (8, 2): "C", (8, 3): "B",
    (9, 1): "A", (9, 2): "D", (9, 3): "B",
    (10, 1): "A", (10, 2): "B", (10, 3): "B",
    (11, 1): "B", (11, 2): "C", (11, 3): "C",
    (12, 1): "A", (12, 2): "C", (12, 3): "C",
    # 第 13/14/15 章未配习题；第16章(附录)下的习题块覆盖 shebang/浮点等主题
    (16, 1): "B", (16, 2): "B", (16, 3): "D",
}

def answer_for(module_num, ex):
    """选择题返回「正确答案 + 该选项文本」，综合题返回开放性提示。"""
    if ex["options"]:
        letter = CORRECT.get((module_num, ex["num"]))
        if letter:
            # 选项形如 "A. xxx"
            for o in ex["options"]:
                if o.startswith(letter + "."):
                    txt = o[len(letter) + 2:].strip()
                    return f"参考答案：<strong>{letter}</strong>。{txt}"
            return f"参考答案：<strong>{letter}</strong>"
        return ""
    # 综合内化（开放题）
    return ("参考答案：<strong>开放题</strong>（合理即可）。要点：紧扣本节核心概念，"
            "结合示例说明原理与最佳实践，避免泛泛而谈。")

# 把答案挂到章节（与习题同级），并改写为按题号的 dict，供模板读取
for mod in modules:
    for ch in mod["chapters"]:
        ans = {}
        for ex in ch["exercises"]:
            a = answer_for(mod["num"], ex)
            if a:
                ans[str(ex["num"])] = a
        ch["answers"] = ans

# ---------- 统计 ----------
total_points = sum(len(ch["points"]) for mod in modules for ch in mod["chapters"])
total_ex = sum(len(ch["exercises"]) for mod in modules for ch in mod["chapters"])

print(f"模块(章): {len(modules)} | 章节(节): {sum(len(m['chapters']) for m in modules)} "
      f"| 知识点: {total_points} | 习题: {total_ex}")

data = {
    "title": "Python 官方教程知识体系学习手册",
    "subtitle": "Python 3 中文教程 · 知识体系学习手册",
    "overview_prose": render_block(overview_prose),
    "mermaid": [{"title": t, "code": c} for t, c in mermaid_blocks],
    "modules": modules,
    "stats": {
        "modules": len(modules),
        "chapters": sum(len(m["chapters"]) for m in modules),
        "points": total_points,
        "exercises": total_ex,
    },
}

with open("/tmp/py_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("解析完成，数据已写入 /tmp/py_data.json")
