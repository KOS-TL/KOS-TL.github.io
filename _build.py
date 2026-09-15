# -*- coding: utf-8 -*-
"""Build the KOS-TL public site from the v13 manifesto and monograph."""
from __future__ import print_function

import html
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(r"D:/kos.github.io")
SRC = Path(r"D:/re-Palantir/doc")
ZH_MD = SRC / "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519b_\u6a84\u6587.md"
EN_MD = ROOT / "manifesto-en.md"
BOOK_MD = SRC / "\u5411\u53ef\u4fe1\u8f6f\u4ef6\u65f6\u4ee3\u8fdb\u519b-\u5168\u4e66\u6e90\u6587\u4ef6v13.md"
FIGS = SRC / "figs"
CSS = (ROOT / "assets" / "site.css").read_text(encoding="utf-8")

FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,700;1,9..144,500&family=Noto+Serif+SC:wght@400;500;600;700;900&family=Syne:wght@700;800&display=swap" rel="stylesheet"/>
"""
ICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect fill='%238c1c13' width='64' height='64' rx='4'/%3E"
    "%3Ctext x='32' y='44' text-anchor='middle' font-size='32' fill='%23f4ead5' "
    "font-family='serif'%3E\u547d%3C/text%3E%3C/svg%3E"
)

STATS_ZH = """
<div class="stats">
  <div class="stat"><b>15.48 \u4e07\u4ebf</b><span>2025 \u5e74\u8f6f\u4ef6\u4e1a\u52a1\u6536\u5165 \u00b7 \u540c\u6bd4 +13.2%</span></div>
  <div class="stat"><b>1.39%</b><span>\u57fa\u7840\u8f6f\u4ef6 2,146 \u4ebf\u5143</span></div>
  <div class="stat"><b>1.44%</b><span>\u4fe1\u606f\u5b89\u5168 2,235 \u4ebf\u5143</span></div>
</div>
"""
STATS_EN = """
<div class="stats">
  <div class="stat"><b>\u00a515.48 tn</b><span>2025 software business revenue \u00b7 +13.2% YoY</span></div>
  <div class="stat"><b>1.39%</b><span>Foundational software \u00b7 \u00a5214.6 bn</span></div>
  <div class="stat"><b>1.44%</b><span>Information security \u00b7 \u00a5223.5 bn</span></div>
</div>
"""

JS = r"""
<script>
  const btn = document.getElementById("tocBtn");
  const mask = document.getElementById("mask");
  const skip = document.getElementById("skip");
  const brandSub = document.getElementById("brandSub");
  const copy = {
    zh: {
      title: "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519b \u2014\u2014 \u628a\u8f6f\u4ef6\u7ed1\u56de\u53ef\u68c0\u9a8c\u7684\u6258\u4ed8",
      brand: "\u4f7f\u547d\u8f6f\u4ef6\u6a84\u6587",
      toc: "\u76ee\u5f55",
      skip: "\u8df3\u5230\u6b63\u6587",
      skipHref: "#main",
      m: "\u6a84\u6587", b: "\u4e13\u8457"
    },
    en: {
      title: "Advance into the Age of Mission-bound Software",
      brand: "Manifesto",
      toc: "Contents",
      skip: "Skip to content",
      skipHref: "#main-en",
      m: "Manifesto", b: "Monograph"
    }
  };
  let io;
  function setOpen(open) {
    document.body.classList.toggle("toc-open", open);
    if (mask) mask.hidden = !open;
  }
  if (btn) btn.addEventListener("click", () => setOpen(!document.body.classList.contains("toc-open")));
  if (mask) mask.addEventListener("click", () => setOpen(false));
  document.querySelectorAll(".toc").forEach((toc) => {
    toc.addEventListener("click", (e) => {
      if (e.target.tagName === "A") setOpen(false);
    });
  });
  function bindToc(lang) {
    if (io) io.disconnect();
    const toc = document.querySelector('.toc[data-lang="' + lang + '"]') || document.querySelector(".toc");
    if (!toc) return;
    const links = [...toc.querySelectorAll("a")];
    const sections = links.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
    io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = "#" + entry.target.id;
        links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === id));
      });
    }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });
    sections.forEach((el) => io.observe(el));
  }
  function mapHash(lang) {
    const raw = (location.hash || "").replace(/^#/, "");
    if (!raw) return;
    const id = lang === "en" ? (raw.startsWith("en-") ? raw : "en-" + raw) : raw.replace(/^en-/, "");
    const el = document.getElementById(id);
    if (el) history.replaceState(null, "", "#" + id);
  }
  function setLang(lang) {
    lang = lang === "en" ? "en" : "zh";
    document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
    document.querySelectorAll("[data-lang]").forEach((el) => {
      el.classList.toggle("pane-off", el.getAttribute("data-lang") !== lang);
    });
    document.querySelectorAll("[data-set-lang]").forEach((b) => {
      b.setAttribute("aria-pressed", b.getAttribute("data-set-lang") === lang ? "true" : "false");
    });
    const t = copy[lang];
    if (!t) { bindToc("zh"); return; }
    document.title = t.title;
    if (brandSub) brandSub.textContent = t.brand;
    if (btn) btn.textContent = t.toc;
    if (skip) { skip.textContent = t.skip; skip.setAttribute("href", t.skipHref); }
    const nm = document.getElementById("navManifesto");
    const nb = document.getElementById("navBook");
    if (nm) nm.textContent = t.m;
    if (nb) nb.textContent = t.b;
    const url = new URL(location.href);
    url.searchParams.set("lang", lang);
    history.replaceState(null, "", url.pathname + url.search + url.hash);
    try { localStorage.setItem("kos-lang", lang); } catch (e) {}
    mapHash(lang);
    bindToc(lang);
  }
  document.querySelectorAll("[data-set-lang]").forEach((b) => {
    b.addEventListener("click", () => setLang(b.getAttribute("data-set-lang")));
  });
  if (document.querySelector("[data-set-lang]")) {
    const params = new URLSearchParams(location.search);
    const start = params.get("lang") || (function () {
      try { return localStorage.getItem("kos-lang"); } catch (e) { return null; }
    }()) || "zh";
    setLang(start);
  } else {
    bindToc("zh");
  }
</script>
"""


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def parse_manifesto(md_text):
    lines = md_text.replace("\r\n", "\n").split("\n")
    meta = {"title": "", "sub": "", "kicker2": "", "author": "", "date": "", "note": ""}
    blocks = []
    buf = []
    started = False

    def flush():
        if buf:
            blocks.append(("p", "\n".join(buf).strip()))
            buf.clear()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not started:
            if line.startswith("# ") and not line.startswith("## "):
                meta["title"] = line[2:].strip()
            elif line.startswith("## "):
                meta["sub"] = line[3:].strip()
            elif line.startswith("> "):
                meta["note"] = line[2:].strip()
            elif line.startswith("\u5173\u4e8e") or line.startswith("A manifesto"):
                meta["kicker2"] = line.strip()
            elif line in ("\u9648\u9e4f", "Chen Peng"):
                meta["author"] = line.strip()
            elif "\u4e8c\u3007\u4e8c\u516d\u5e74" in line or line.startswith("September"):
                meta["date"] = line.strip()
            elif line.strip() == "":
                pass
            i += 1
            if meta["note"] and (i >= len(lines) or lines[i].strip() == "" or not lines[i].startswith(">")):
                started = True
            continue
        if line.startswith("## "):
            flush()
            blocks.append(("h2", line[3:].strip()))
        elif not line.strip():
            flush()
        else:
            buf.append(line)
        i += 1
    flush()
    return meta, blocks


def roman(n):
    table = [
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = []
    for v, s in [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


def render_blocks(blocks, lang, id_prefix=""):
    out = []
    toc = []
    n = 0
    stats_done = False
    coda = False
    for kind, text in blocks:
        if kind == "h2":
            n += 1
            is_coda = text.startswith("\u7ed3\u8bed") or text.startswith("Coda")
            hid = ("%s%s" % (id_prefix, "coda" if is_coda else "s%d" % n))
            if is_coda:
                coda = True
                out.append('<section class="close" id="%s">' % hid)
                label = "CODA"
            else:
                label = "%02d" % n
            out.append('<h2 class="sec" id="%s"><small>%s</small>%s</h2>' % (
                hid if not is_coda else hid, label, inline(text)))
            toc.append((hid, text, False))
            continue
        if "\u2261" in text:
            out.append('<div class="formula"><div class="lbl">%s</div><p>%s</p></div>' % (
                "CORE" if text.startswith("\u6838\u5fc3") or text.startswith("Core") else "MISSION-BOUND SOFTWARE",
                inline(text),
            ))
            continue
        if text.strip() in (
            "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519b\u3002",
            "Advance into the age of mission-bound software.",
        ):
            out.append('<p class="final">%s</p>' % inline(text))
            if coda:
                out.append("</section>")
            continue
        cls = ""
        if not out or (out and "lede" not in "".join(out[-3:]) and n == 0 and kind == "p"):
            # first body para after hero handled by caller
            pass
        html_p = "<p>%s</p>" % inline(text)
        if (
            "\u6ca1\u6709\u53ef\u4fe1\uff0c\u6258\u4ed8\u662f\u7a7a\u8bdd" in text
            or "Without trustworthiness, a charge is empty talk" in text
        ):
            html_p += '<blockquote class="pull">%s</blockquote>' % inline(
                "\u6ca1\u6709\u53ef\u4fe1\uff0c\u6258\u4ed8\u662f\u7a7a\u8bdd\uff1b\u6ca1\u6709\u6258\u4ed8\uff0c\u53ef\u4fe1\u662f\u624b\u6bb5\u3002"
                if lang == "zh"
                else "Without trustworthiness, a charge is empty talk; without a charge, trustworthiness is a means."
            )
        out.append(html_p)
        if not stats_done and n == 2:
            out.append(STATS_ZH if lang == "zh" else STATS_EN)
            stats_done = True
    if coda and "</section>" not in "".join(out[-3:]):
        out.append("</section>")
    return "\n".join(out), toc


def toc_html(toc, lang):
    title = "\u76ee\u5f55" if lang == "zh" else "Contents"
    items = []
    for hid, text, is_h2 in toc:
        items.append('<a href="#%s"%s>%s</a>' % (hid, ' class="h2"' if is_h2 else "", html.escape(text)))
    return '<nav class="toc" data-lang="%s" aria-label="%s"><h2>%s</h2>%s</nav>' % (
        lang, title, title, "\n".join(items),
    )


def nav_bar(prefix, current, show_lang=True):
    m_href = prefix + "index.html" if prefix else "./"
    b_href = prefix + "book/"
    lang = ""
    if show_lang:
        lang = """
      <div class="lang" role="group" aria-label="Language / \u8bed\u8a00">
        <button type="button" data-set-lang="zh" aria-pressed="true">\u4e2d\u6587</button>
        <button type="button" data-set-lang="en" aria-pressed="false">EN</button>
      </div>"""
    return """
  <header class="topbar">
    <a class="brand" href="%s">
      <b>KOS-TL</b>
      <span id="brandSub">%s</span>
    </a>
    <nav>
      %s
      <button class="toc-btn" type="button" id="tocBtn">\u76ee\u5f55</button>
      <a id="navManifesto" href="%s"%s>\u6a84\u6587</a>
      <a id="navBook" href="%s"%s>\u4e13\u8457</a>
      <a href="https://github.com/KOS-TL">GitHub</a>
    </nav>
  </header>
""" % (
        m_href,
        "\u4f7f\u547d\u8f6f\u4ef6\u6a84\u6587" if current == "manifesto" else "\u4f7f\u547d\u8f6f\u4ef6\u4e13\u8457",
        lang,
        m_href, ' aria-current="page"' if current == "manifesto" else "",
        b_href, ' aria-current="page"' if current == "book" else "",
    )


def shell(title, desc, body_class, body, extra_js=True):
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>%s</title>
  <meta name="description" content="%s"/>
  <meta name="author" content="\u9648\u9e4f"/>
  <meta property="og:title" content="%s"/>
  <meta property="og:description" content="%s"/>
  <meta property="og:type" content="article"/>
  <link rel="icon" href="%s"/>
  %s
  <style>
%s
  </style>
</head>
<body%s>
%s
</body>
</html>
""" % (
        html.escape(title), html.escape(desc), html.escape(title), html.escape(desc),
        ICON, FONTS, CSS, body_class, body + (JS if extra_js else ""),
    )


def hero(meta, seal, lede, lang):
    return """
      <header class="hero">
        <p class="kicker">MANIFESTO \u00b7 \u6a84\u6587</p>
        <h1>%s</h1>
        <p class="sub">%s</p>
        <p class="kicker2">%s</p>
        <p class="byline">
          <span class="who">%s</span>
          <span>%s</span>
          <a href="mailto:chenpeng_buaa@163.com">chenpeng_buaa@163.com</a>
        </p>
        <div class="seal" aria-hidden="true">%s</div>
        <p class="note">%s</p>
        <p class="lede">%s</p>
      </header>
""" % (
        inline(meta["title"]), inline(meta["sub"]), inline(meta["kicker2"]),
        inline(meta["author"] or ("\u9648\u9e4f" if lang == "zh" else "Chen Peng")),
        inline(meta["date"]),
        seal, inline(meta["note"]), inline(lede),
    )


def build_manifesto():
    zh_meta, zh_blocks = parse_manifesto(ZH_MD.read_text(encoding="utf-8"))
    en_meta, en_blocks = parse_manifesto(EN_MD.read_text(encoding="utf-8"))
    zh_lede = ""
    en_lede = ""
    if zh_blocks and zh_blocks[0][0] == "p":
        zh_lede = zh_blocks[0][1]
        zh_blocks = zh_blocks[1:]
    if en_blocks and en_blocks[0][0] == "p":
        en_lede = en_blocks[0][1]
        en_blocks = en_blocks[1:]
    zh_body, zh_toc = render_blocks(zh_blocks, "zh")
    en_body, en_toc = render_blocks(en_blocks, "en", "en-")
    zh_toc = [("intro", "\u5f00\u7bc7", False)] + zh_toc
    en_toc = [("en-intro", "Prologue", False)] + en_toc
    # give intro id to lede's following? first remaining is already sections.
    # Put id=intro on hero via extra wrap - skip, point intro to first para by adding id on hero
    article_zh = (
        '<article id="main" data-lang="zh">'
        + hero(zh_meta, "\u547d", zh_lede, "zh").replace('<header class="hero">', '<header class="hero" id="intro">')
        + zh_body
        + """
      <footer class="site">
        <span>\u4f5c\u8005\u3000\u9648\u9e4f\u3000\u00b7\u3000<a href="mailto:chenpeng_buaa@163.com">chenpeng_buaa@163.com</a></span>
        <span>KOS-TL \u00b7 Knowledge Operating System \u2014 Type Logic</span>
      </footer>
    </article>"""
    )
    article_en = (
        '<article id="main-en" class="pane-off" data-lang="en">'
        + hero(en_meta, "\u547d", en_lede, "en").replace('<header class="hero">', '<header class="hero" id="en-intro">')
        + en_body
        + """
      <footer class="site">
        <span>Author: Chen Peng \u00b7 <a href="mailto:chenpeng_buaa@163.com">chenpeng_buaa@163.com</a></span>
        <span>KOS-TL \u00b7 Knowledge Operating System \u2014 Type Logic</span>
      </footer>
    </article>"""
    )
    body = """
  <a class="skip" id="skip" href="#main">\u8df3\u5230\u6b63\u6587</a>
  <div class="mask" id="mask" hidden></div>
  %s
  <div class="layout" id="top">
    %s
    %s
    %s
    %s
  </div>
""" % (
        nav_bar("", "manifesto", True),
        toc_html(zh_toc, "zh"),
        toc_html(en_toc, "en").replace('<nav class="toc"', '<nav class="toc pane-off"'),
        article_zh,
        article_en,
    )
    html_doc = shell(
        "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519b \u2014\u2014 \u628a\u8f6f\u4ef6\u7ed1\u56de\u53ef\u68c0\u9a8c\u7684\u6258\u4ed8",
        "\u8f6f\u4ef6\u4e0d\u4ec5\u8981\u80fd\u591f\u8fd0\u884c\uff0c\u66f4\u5fc5\u987b\u627f\u62c5\u4f7f\u547d\u3002KOS-TL \u4f7f\u547d\u8f6f\u4ef6\u6a84\u6587\u4e0e\u4e13\u8457\u7b2cv13\u7a3f\u3002",
        "",
        body,
    )
    (ROOT / "index.html").write_text(html_doc, encoding="utf-8")
    nested = ROOT / "kos.github.io"
    nested.mkdir(exist_ok=True)
    shutil.copy2(ROOT / "index.html", nested / "index.html")
    (nested / "book").mkdir(exist_ok=True)
    (nested / "book" / "index.html").write_text(
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"/>'
        '<meta http-equiv="refresh" content="0;url=/book/"/>'
        '<link rel="canonical" href="https://kos-tl.github.io/book/"/>'
        "<title>\u4e13\u8457</title></head><body>"
        '<p><a href="/book/">\u6253\u5f00\u4e13\u8457\u300a\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519b\u300b</a></p>'
        "<script>location.replace('/book/'+location.hash)</script>"
        "</body></html>",
        encoding="utf-8",
    )
    (nested / "files").mkdir(exist_ok=True)
    (nested / "files" / "index.html").write_text(
        '<!DOCTYPE html><html><head><meta charset="utf-8"/>'
        '<meta http-equiv="refresh" content="0;url=/files/"/>'
        "</head><body><a href=\"/files/\">files</a></body></html>",
        encoding="utf-8",
    )


def slugify(n, text):
    return "p%d" % n


def convert_book():
    raw = BOOK_MD.read_text(encoding="utf-8")
    raw = re.sub(r"^# .+\n## .+\n", "", raw, count=1)
    raw = raw.replace("\n---\n", "\n\n<hr>\n\n")
    md = markdown.Markdown(
        extensions=["tables", "footnotes", "sane_lists"],
        output_format="html5",
    )
    body = md.convert(raw)
    n = 0
    toc = []

    def head_sub(m):
        nonlocal n
        level = m.group(1)
        inner = m.group(2)
        text = re.sub(r"<[^>]+>", "", inner).strip()
        n += 1
        hid = slugify(n, text)
        skip = (
            text.startswith("\u7248\u6743")
            or text.startswith(">")
            or text.startswith("\u628a\u8f6f\u4ef6\u7ed1\u56de")
            or len(text) > 60
        )
        if level == "1" and not skip:
            toc.append((hid, text, False))
        return '<h%s id="%s">%s</h%s>' % (level, hid, inner, level)

    body = re.sub(r"<h([1-6])(?:\s[^>]*)?>(.*?)</h\1>", head_sub, body, flags=re.S)

    def fig_sub(m):
        alt, src = m.group(1), m.group(2).replace("figs/", "")
        return (
            '<figure class="fig"><img alt="%s" src="figs/%s"/>'
            "<figcaption>%s</figcaption></figure>" % (alt, src, alt)
        )

    body = re.sub(r"</?figure[^>]*>", "", body)
    body = re.sub(r"<figcaption>.*?</figcaption>", "", body)
    body = re.sub(
        r'<img alt="([^"]*)" src="(?:figs/)?([^"]+)"[^>]*>',
        fig_sub,
        body,
    )
    body = re.sub(r"<p>\s*(<figure[\s\S]*?</figure>)\s*</p>", r"\1", body)
    body = re.sub(r"</figure>\s*</p>", "</figure>", body)
    body = re.sub(r"<p>\s*<figure", "<figure", body)
    dest_figs = ROOT / "book" / "figs"
    dest_figs.mkdir(parents=True, exist_ok=True)
    used = set(re.findall(r'src="figs/([^"]+)"', body))
    for name in used:
        src = FIGS / name
        if src.exists():
            shutil.copy2(src, dest_figs / name)
    toc_nav = toc_html(toc, "zh")
    article = """<article id="main">
      <header class="hero" id="top">
        <p class="kicker">MONOGRAPH · 专著 v13</p>
        <h1>向软件使命时代进军</h1>
        <p class="sub">把软件绑回可检验的托付</p>
        <p class="byline">
          <span class="who">陈鹏</span>
          <span>第13稿 · 二〇二六年九月</span>
          <a href="mailto:chenpeng_buaa@163.com">chenpeng_buaa@163.com</a>
        </p>
        <div class="seal" aria-hidden="true">命</div>
        <p class="note">知识操作系统是架构主张，不是已经交付的操作系统。使命软件工程学是体系主张，不是已经形成的学科。正文与插图按第13稿网页重排，便于阅读。</p>
      </header>
      %s
      <footer class="site">
        <span>作者　陈鹏　·　<a href="mailto:chenpeng_buaa@163.com">chenpeng_buaa@163.com</a></span>
        <span>KOS-TL · 第13稿 · 2026年9月</span>
      </footer>
    </article>""" % body
    page = """
  <a class="skip" id="skip" href="#main">跳到正文</a>
  <div class="mask" id="mask" hidden></div>
  %s
  <div class="layout" id="layout">
    %s
    %s
  </div>
""" % (nav_bar("../", "book", False), toc_nav, article)
    html_doc = shell(
        "向软件使命时代进军（第13稿）",
        "把软件绑回可检验的托付。陈鹏著，第13稿。",
        ' class="book"',
        page,
    )
    (ROOT / "book" / "index.html").write_text(html_doc, encoding="utf-8")


def copy_files():
    dest = ROOT / "files"
    dest.mkdir(exist_ok=True)
    m = SRC / "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519b.docx"
    b = SRC / "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519bv13.docx"
    if not m.exists() or not b.exists():
        raise SystemExit("missing docx: %s %s" % (m.exists(), b.exists()))
    shutil.copy2(m, dest / "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519b.docx")
    shutil.copy2(b, dest / "\u5411\u8f6f\u4ef6\u4f7f\u547d\u65f6\u4ee3\u8fdb\u519bv13.docx")
    shutil.copy2(m, dest / "manifesto.docx")
    shutil.copy2(b, dest / "book-v13.docx")
    (dest / "index.html").write_text(
        """<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"/><title>下载</title>
<meta http-equiv="refresh" content="0;url=../"/>
</head><body>
<p><a href="../">返回</a></p>
</body></html>
""",
        encoding="utf-8",
    )
    shutil.copy2(ZH_MD, ROOT / "manifesto.md")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")


def write_readme():
    (ROOT / "README.md").write_text(
        """# 向软件使命时代进军

KOS-TL 公开阅读站点。檄文与专著第13稿。

- 檄文：https://kos-tl.github.io/
- 专著：https://kos-tl.github.io/book/

兼容路径：https://kos-tl.github.io/kos.github.io/

知识操作系统是架构主张，不是已经交付的操作系统。使命软件工程学是体系主张，不是已经形成的学科。
""",
        encoding="utf-8",
    )


def main():
    copy_files()
    build_manifesto()
    convert_book()
    write_readme()
    idx = ROOT / "index.html"
    book = ROOT / "book" / "index.html"
    figs = list((ROOT / "book" / "figs").glob("*.png"))
    files = list((ROOT / "files").glob("*.docx"))
    log = ROOT / "_build_log.txt"
    log.write_text(
        "index=%s\nbook=%s\nfigs=%d bytes=%d\nfiles=%s\n"
        % (
            idx.stat().st_size,
            book.stat().st_size,
            len(figs),
            sum(f.stat().st_size for f in figs),
            ", ".join("%s:%d" % (f.name, f.stat().st_size) for f in files),
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
