# -*- coding: utf-8 -*-
"""
将《破局者》知识手册 markdown 转换为互动教学型单文件 HTML 课程。
"""
import re
import json
import os

SRC = "/Users/zhangxiang/Downloads/破局者.txt"
OUT = "/Users/zhangxiang/github/codebase-to-course/破局者-课程.html"

# ---------- 读取 ----------
with open(SRC, "r", encoding="utf-8") as f:
    raw = f.read()

# 去掉开头的 ```markdown 围栏（文档前几行有）
lines = raw.split("\n")
# 找到正文起点
start = 0
for i, ln in enumerate(lines):
    if ln.strip().startswith("# 破局者"):
        start = i
        break
lines = lines[start:]

def render_inline(text):
    """渲染行内 markdown：粗体、行内代码"""
    # 转义
    text = (text.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;"))
    # 粗体 **x**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # 行内代码 `x`
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text

def render_block(content_lines):
    """把内容块（已去除【】标记行）渲染成 HTML。处理列表与段落。"""
    html = []
    i = 0
    n = len(content_lines)
    while i < n:
        ln = content_lines[i]
        stripped = ln.strip()
        if not stripped:
            i += 1
            continue
        # 有序列表  1. / ① 等
        if re.match(r"^\d+\.\s", stripped) or re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", stripped):
            items = []
            while i < n:
                s = content_lines[i].strip()
                if re.match(r"^\d+\.\s", s) or re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", s):
                    # 取掉前缀
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
        # 无序列表 - x
        if stripped.startswith("- "):
            items = []
            while i < n:
                s = content_lines[i]
                ss = s.strip()
                if ss.startswith("- "):
                    items.append("<li>" + render_inline(ss[2:]) + "</li>")
                    i += 1
                elif s.startswith("   ") and ss:
                    # 嵌套续行，并入上一个
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
        # 普通段落（合并连续非空非列表行）
        para = []
        while i < n:
            s = content_lines[i].strip()
            if s == "" or s.startswith("- ") or re.match(r"^\d+\.\s", s) or re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩]", s):
                break
            para.append(s)
            i += 1
        if para:
            html.append("<p>" + render_inline(" ".join(para)) + "</p>")
    return "\n".join(html)

# ---------- 切分大块 ----------
# 把文档按行扫描，识别：总览、模块、章节、知识点、习题、答案
# 先提取总览区（## 一、 到 ## 二、之前）
overview_lines = []
in_overview = False
in_detail = False
answer_lines = []
collect_answer = False
detail_lines = []

for ln in lines:
    if ln.strip() == "## 一、知识体系总览":
        in_overview = True
        continue
    if ln.strip() == "## 二、分章节知识详解":
        in_overview = False
        in_detail = True
        continue
    if ln.strip() == "## 三、答案与解析全集":
        in_detail = False
        collect_answer = True
        continue
    if in_overview:
        overview_lines.append(ln)
    elif in_detail:
        detail_lines.append(ln)
    elif collect_answer:
        answer_lines.append(ln)

# ---------- 解析总览：提取 mermaid 块 ----------
def extract_mermaid_blocks(text_lines):
    """返回 [(title, mermaid_code)] 列表 + 剩余文本"""
    out = []
    buf = []
    in_code = False
    code_buf = []
    title = None
    prose = []
    pending_h = None
    for ln in text_lines:
        if ln.strip().startswith("```mermaid"):
            in_code = True
            code_buf = []
            continue
        if in_code and ln.strip() == "```":
            in_code = False
            out.append((pending_h or "图", "\n".join(code_buf)))
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

# ---------- 解析知识点详情 ----------
# 模块(# 一级模块N ...) -> 章节(## X.Y ...) -> 知识点(### X.Y.Z ...)
modules = []   # {title, chapters:[{title, points:[...]}]}
cur_module = None
cur_chapter = None
cur_point = None
cur_block_key = None   # 当前【】块的key
cur_block_lines = []
in_exercises = False
ex_lines = []

def flush_block():
    global cur_block_key, cur_block_lines
    if cur_point is not None and cur_block_key is not None:
        cur_point["elements"].append({
            "key": cur_block_key,
            "html": render_block(cur_block_lines),
        })
    cur_block_key = None
    cur_block_lines = []

ELEMENT_LABELS = {
    "是什么": ("是什么 · 核心定义", "def", "①"),
    "为什么": ("为什么 · 底层逻辑", "why", "②"),
    "怎么用": ("怎么用 · 落地方法", "how", "③"),
    "费曼通俗解释": ("费曼通俗解释", "feynman", "④"),
    "典型应用场景": ("典型应用场景", "scene", "⑤"),
    "避坑提醒": ("避坑提醒", "pitfall", "⑥"),
}

for ln in detail_lines:
    s = ln.rstrip()
    stripped = s.strip()
    # 模块
    m = re.match(r"^# 一级模块(\d+)\s+(.*)$", stripped)
    if m:
        flush_block()
        if in_exercises and cur_point is not None:
            cur_point["exercises_raw"] = "\n".join(ex_lines)
        in_exercises = False
        cur_module = {"num": int(m.group(1)), "title": m.group(2).strip(), "chapters": []}
        modules.append(cur_module)
        cur_chapter = None
        cur_point = None
        continue
    # 章节
    m = re.match(r"^## (\d+\.\d+)\s+(.*)$", stripped)
    if m and cur_module is not None:
        flush_block()
        if in_exercises and cur_point is not None:
            cur_point["exercises_raw"] = "\n".join(ex_lines)
        in_exercises = False
        cur_chapter = {"id": m.group(1), "title": m.group(2).strip(), "points": []}
        cur_module["chapters"].append(cur_chapter)
        cur_point = None
        continue
    # 知识点
    m = re.match(r"^### (\d+\.\d+\.\d+)\s+(.*)$", stripped)
    if m and cur_chapter is not None:
        flush_block()
        if in_exercises and cur_point is not None:
            cur_point["exercises_raw"] = "\n".join(ex_lines)
        in_exercises = False
        pid = m.group(1)
        title = m.group(2).strip()
        cur_point = {
            "id": pid,
            "title": title,
            "chapter_id": cur_chapter["id"],
            "chapter_title": cur_chapter["title"],
            "module_num": cur_module["num"],
            "module_title": cur_module["title"],
            "elements": [],
            "exercises_raw": "",
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
        raw_key = m.group(1).strip()
        # 形如 "是什么 | 核心定义"
        key = raw_key.split("|")[0].strip()
        if key in ELEMENT_LABELS:
            cur_block_key = key
            cur_block_lines = []
        else:
            cur_block_key = raw_key
            cur_block_lines = []
        continue
    # 普通内容行
    if in_exercises:
        ex_lines.append(s)
    elif cur_block_key is not None:
        cur_block_lines.append(s)

# 收尾
flush_block()
if in_exercises and cur_point is not None:
    cur_point["exercises_raw"] = "\n".join(ex_lines)

# ---------- 解析习题 ----------
def parse_exercises(raw):
    """把习题原文切成 [{diff, type, stem, options:[A...], kind}]"""
    if not raw.strip():
        return []
    items = []
    # 按题号切分（行首 数字.）
    chunks = re.split(r"(?m)^\s*(\d+)\.\s+", raw)
    # chunks: [前置, '1', 题干, '2', 题干, ...]
    parts = chunks[1:]
    for i in range(0, len(parts), 2):
        num = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        # 找到下一个题号前的全部内容
        body = body.strip()
        if not body:
            continue
        # 第一行可能含难度层级·题型
        first, _, rest = body.partition("\n")
        diff = ""
        qtype = ""
        stem = first
        mm = re.match(r"^（([^）]+)）(.*)$", first)
        if mm:
            tag = mm.group(1)
            diff = tag.split("·")[0].strip()
            if "·" in tag:
                qtype = tag.split("·", 1)[1].strip()
            stem = mm.group(2).strip()
        # 提取选项 A. B. ...
        opts = []
        optpat = re.compile(r"^([A-Z])．?\.?\s*(.+)$")
        cur_opt = None
        prose_after = []
        for ln in rest.split("\n"):
            ls = ln.strip()
            if not ls:
                continue
            om = optpat.match(ls)
            if om:
                opts.append(om.group(1) + ". " + om.group(2))
                cur_opt = om.group(1)
            else:
                # 题干补充或场景描述
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
        for pt in ch["points"]:
            pt["exercises"] = parse_exercises(pt["exercises_raw"])

# ---------- 解析答案 ----------
answers = {}   # {point_id: {num: html}}
cur_kp = None
cur_ans = {}
cur_qnum = None
cur_qbuf = []

def flush_ans():
    global cur_qnum, cur_qbuf
    if cur_kp and cur_qnum:
        cur_ans[cur_qnum] = render_block(cur_qbuf)
    cur_qnum = None
    cur_qbuf = []

for ln in answer_lines:
    stripped = ln.strip()
    m = re.match(r"^#{2,5}\s*知识点\s*([\d\.]+)\s*习题解析", stripped)
    if m:
        flush_ans()
        if cur_kp and cur_ans:
            answers[cur_kp] = cur_ans
        cur_kp = m.group(1).strip().rstrip(".")
        cur_ans = {}
        continue
    m = re.match(r"^#{2,5}\s*模块\s*(\d+)\s*习题解析", stripped)
    if m:
        flush_ans()
        if cur_kp and cur_ans:
            answers[cur_kp] = cur_ans
        cur_kp = None
        cur_ans = {}
        continue
    if cur_kp is None:
        continue
    m = re.match(r"^(\d+)\.\s*\*\*参考答案\*\*[：:]?\s*(.*)$", stripped)
    if m:
        flush_ans()
        cur_qnum = int(m.group(1))
        rest = m.group(2).strip()
        cur_qbuf = []
        if rest:
            cur_qbuf.append("**参考答案**：" + rest)
        continue
    if cur_qnum is not None:
        cur_qbuf.append(ln)
flush_ans()
if cur_kp and cur_ans:
    answers[cur_kp] = cur_ans

# 把答案挂到知识点
for mod in modules:
    for ch in mod["chapters"]:
        for pt in ch["points"]:
            pt["answers"] = answers.get(pt["id"], {})

# ---------- 统计 ----------
total_points = sum(len(ch["points"]) for mod in modules for ch in mod["chapters"])
total_ex = sum(len(pt["exercises"]) for mod in modules for ch in mod["chapters"] for pt in ch["points"])
total_ans = sum(len(pt["answers"]) for mod in modules for ch in mod["chapters"] for pt in ch["points"])
print(f"模块: {len(modules)} | 知识点: {total_points} | 习题: {total_ex} | 已有解析: {total_ans}")

data = {
    "title": "破局者：企业内生性增长破局方法论",
    "subtitle": "知识体系学习手册",
    "overview_prose": render_block(overview_prose),
    "mermaid": [{"title": t, "code": c} for t, c in mermaid_blocks],
    "modules": modules,
    "stats": {
        "modules": len(modules),
        "points": total_points,
        "exercises": total_ex,
        "answers": total_ans,
    },
}

with open("/tmp/pojv_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("解析完成，数据已写入 /tmp/pojv_data.json")
