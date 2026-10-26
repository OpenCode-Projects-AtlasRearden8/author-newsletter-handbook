#!/usr/bin/env python3
"""Static site generator for The Reader Newsletter Handbook.

Standard library only -- no installs, no network access. It turns the
Markdown manual in docs/ (and the copy-paste templates in templates/)
into a small offline website: a landing page, one polished page per
chapter and template with sidebar navigation and prev/next pagers, plus
CSV copies of the issue calendar, so the whole handbook works offline
and from file://.

Usage:
  python3 scripts/build.py              build the site into site/
  python3 scripts/build.py --out DIR    build somewhere else
  python3 scripts/build.py --check      lint the Markdown corpus and exit
  python3 scripts/build.py --serve      build, then preview on localhost
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TEMPLATES = ROOT / "templates"
ASSETS = Path(__file__).resolve().parent / "assets"
SITE = ROOT / "site"

BOOK_TITLE = "The Reader Newsletter Handbook"
CHAPTER_COUNT = 9  # chapters 01..09 carry the manual's numbering; 00 is front matter

# Sidebar labels and sections, keyed by the *stripped* stem
# ("04-welcome-sequence" -> "welcome-sequence"). Pages without an entry
# fall back to their document title and a default section.
MANIFEST = {
    "start-here": ("Start Here", "The handbook"),
    "why-newsletters": ("Why a Newsletter", "The handbook"),
    "choose-a-provider": ("Pick Your Provider", "The handbook"),
    "setup-in-one-sitting": ("Setup in One Sitting", "The handbook"),
    "welcome-sequence": ("Welcome Sequence", "The handbook"),
    "subject-lines": ("Subject Lines", "The handbook"),
    "ai-drafting": ("Draft With AI, Sound Like You", "The handbook"),
    "send-cadence": ("Send Without Dread", "The handbook"),
    "growing-ethically": ("Growing Ethically", "The handbook"),
    "archiving-issues": ("Archive Your Issues", "The handbook"),
    "glossary": ("Glossary", "Reference"),
    "troubleshooting": ("Troubleshooting", "Reference"),
    # Templates live in templates/ (no numeric prefix). Their site pages
    # out_name to the same stem: issue-template.md -> issue-template.html
    "welcome-sequence-template": ("Welcome Sequence (copy-paste)", "Templates"),
    "issue-template": ("Issue Template", "Templates"),
    "subject-line-cheatsheet": ("Subject-Line Cheat Sheet", "Templates"),
    "signup-form-copy": ("Signup Form Copy", "Templates"),
    "issue-calendar": ("Issue Calendar", "Templates"),
}


def h(text: str) -> str:
    """Escape text for safe HTML interpolation."""
    return html.escape(text, quote=False)


def plain_text(md: str) -> str:
    """Markdown text -> plain text (links collapse to their label)."""
    md = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)
    md = md.replace("**", "").replace("`", "")
    md = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", md)
    return md


def slug(text: str) -> str:
    """Turn a heading into an anchor id: ASCII, lowercase, hyphenated."""
    text = plain_text(text)
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text or "section"


def split_stem(stem: str) -> tuple[int | None, str]:
    """'04-welcome-sequence' -> (4, 'welcome-sequence').

    Leading digits are ordering/chapter numbers only. Files without a
    numeric prefix return (None, stem).
    """
    m = re.match(r"^(\d+)[-_](.+)$", stem)
    if m:
        return int(m.group(1)), m.group(2)
    return None, stem


def out_name(stem: str) -> str:
    """Site filename for a source stem: '04-welcome-sequence' ->
    'welcome-sequence.html'."""
    _, short = split_stem(stem)
    return f"{short}.html"


def rewire_link(url: str) -> str:
    """Rewrite internal .md link targets so the site stays browsable.

    Matches on the basename: '10-glossary.md' -> 'glossary.html',
    '10-glossary.md#open-rates' -> 'glossary.html#open-rates',
    '../templates/issue-template.md' -> 'issue-template.html'.
    Links outside the handbook (http, https, mailto) and non-.md files
    (like the calendar CSV) pass through untouched.
    """
    if url.startswith(("http://", "https://", "mailto:", "#")):
        return url
    base, frag = url.partition("#")[0], url.partition("#")[2]
    if base.endswith(".md"):
        base = out_name(Path(base).stem)
    return base + ((f"#{frag}") if frag else "")


def inline(text: str) -> str:
    """Inline Markdown -> inline HTML (escape first, then decorate)."""
    text = h(text)
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{h(rewire_link(m.group(2)))}">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


HR_RE = re.compile(r"\s*(---+|\*\*\*+)\s*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
OL_RE = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
UL_RE = re.compile(r"^(\s*)[-*]\s+(.*)$")
TASK_RE = re.compile(r"^(\s*)[-*]\s+\[([ xX])\]\s+(.*)$")


def is_list_marker(line: str) -> bool:
    return bool(OL_RE.match(line) or UL_RE.match(line))


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip())


def convert_markdown(text: str) -> str:
    """Handbook Markdown -> HTML.

    Supported: headings, paragraphs, fenced code blocks, blockquotes,
    ordered/unordered lists with one level of nesting, task checkboxes,
    pipe tables and horizontal rules. Lists are contiguous blocks (no
    blank lines inside); wrapped item text arrives on indented lines.
    Fenced code passes through verbatim (escaped).
    """
    code_blocks: list[str] = []

    def stash(match: "re.Match[str]") -> str:
        code_blocks.append(match.group(2).rstrip("\n"))
        return f"\x02{len(code_blocks) - 1}\x03"

    text = re.sub(r"```([\w+-]*)\n(.*?)```", stash, text, flags=re.S)

    lines = text.splitlines()
    out: list[str] = []
    para: list[str] = []
    quote: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []

    def flush_quote() -> None:
        nonlocal quote
        if not quote:
            return
        body: list[str] = []
        chunk: list[str] = []
        for line in quote:
            if line:
                chunk.append(line)
            elif chunk:
                body.append(f"<p>{inline(' '.join(chunk))}</p>")
                chunk = []
        if chunk:
            body.append(f"<p>{inline(' '.join(chunk))}</p>")
        out.append("<blockquote>" + "".join(body) + "</blockquote>")
        quote = []

    def close_blocks() -> None:
        flush_para()
        flush_quote()

    def render_list(block: list[str]) -> str:
        """Render one contiguous list block (no blank lines inside)."""
        parts: list[str] = []
        cur_tag: str | None = None
        i = 0
        while i < len(block):
            line = block[i]
            mo = OL_RE.match(line)
            mt = TASK_RE.match(line) if mo is None else None
            mu = UL_RE.match(line) if mo is None and mt is None else None
            if not (mo or mt or mu):
                i += 1  # continuation garbage at layer start: skip defensively
                continue
            box = ""
            checked = False
            if mo:
                kind, text_, cls = "ol", mo.group(2), ""
            elif mt:
                checked = mt.group(2).lower() == "x"
                kind, text_, cls = "ul", mt.group(3), "task done" if checked else "task"
            else:
                kind, text_, cls = "ul", mu.group(2), ""

            if cur_tag is not None and kind != cur_tag:
                parts.append(f"</{cur_tag}>")
                cur_tag = None
            if cur_tag is None:
                parts.append(f"<{kind}>")
                cur_tag = kind

            indent = indent_of(line)
            text_parts = [text_]
            nested_parts: list[str] = []
            j = i + 1
            while j < len(block):
                b = block[j]
                base_ind = indent_of(b)
                if base_ind <= indent:
                    break
                if is_list_marker(b):
                    # One nested layer: consume everything deeper than us.
                    k = j
                    while k < len(block) and indent_of(block[k]) > indent:
                        k += 1
                    nested_parts.append(render_list(block[j:k]))
                    j = k
                    continue
                text_parts.append(b.strip())
                j += 1
            i = j
            cls_attr = f' class="{cls}"' if cls else ""
            content = inline(" ".join(text_parts)) + "".join(nested_parts)
            if checked:
                content = '<input type="checkbox" checked disabled>' + " " + content
            elif cls == "task":
                content = '<input type="checkbox" disabled>' + " " + content
            parts.append(f"<li{cls_attr}>{content}</li>")
        if cur_tag is not None:
            parts.append(f"</{cur_tag}>")
        return "\n".join(parts)

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        if HR_RE.fullmatch(line):
            close_blocks()
            out.append("<hr>")
            i += 1
            continue

        # A stashed fenced block occupies its own line: emit verbatim.
        if re.fullmatch(r"\s*\x02\d+\x03\s*", line):
            close_blocks()
            out.append(line.strip())
            i += 1
            continue

        m = HEADING_RE.match(line)
        if m:
            close_blocks()
            level, title = len(m.group(1)), m.group(2)
            tag = {1: "h1", 2: "h2", 3: "h3"}.get(level, "h4")
            out.append(f'<{tag} id="{slug(title)}">{inline(title)}</{tag}>')
            i += 1
            continue

        if line.startswith(">"):
            flush_para()
            quote.append(line.lstrip("> ").strip())
            i += 1
            continue
        flush_quote()

        if is_list_marker(line):
            flush_para()
            block: list[str] = []
            j = i
            while j < n:
                ln = lines[j]
                if (
                    not ln.strip()
                    or ln.startswith((">", "#"))
                    or re.match(r"^\s*\|", ln)
                    or HR_RE.fullmatch(ln)
                    or re.fullmatch(r"\s*\x02\d+\x03\s*", ln)
                ):
                    break
                block.append(ln)
                j += 1
            out.append(render_list(block))
            i = j
            continue

        m = re.match(r"^\s*\|.+\|\s*$", line)
        if m and i + 1 < n and re.match(r"^\s*\|[-: |]+\|\s*$", lines[i + 1]):
            close_blocks()
            header = [c.strip() for c in m.group(0).strip().strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < n and re.match(r"^\s*\|.+\|\s*$", lines[i]):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                cells += [""] * (len(header) - len(cells))
                rows.append(cells[: len(header)])
                i += 1
            parts = ["<table><thead><tr>"]
            parts += [f"<th>{inline(c)}</th>" for c in header]
            parts.append("</tr></thead><tbody>")
            for row in rows:
                parts.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            parts.append("</tbody></table>")
            out.append("".join(parts))
            continue

        if not line.strip():
            close_blocks()
            i += 1
            continue

        # Paragraph lines join (wrapped lines arrive as-is).
        para.append(line.strip())
        i += 1

    close_blocks()

    html_out = "\n".join(out)
    for idx, code in enumerate(code_blocks):
        html_out = html_out.replace(
            f"\x02{idx}\x03", f"<pre><code>{h(code)}</code></pre>"
        )
    return html_out


def page_title(md_text: str) -> str:
    m = re.search(r"^#\s+(.+?)\s*$", md_text, flags=re.M)
    return m.group(1).strip() if m else "Untitled"


def summary(md_text: str) -> str:
    """First plain paragraph after the H1 (meta/TOC blurb).

    Skips exactly one level of structure: headings, quotes, tables,
    lists, rules and fences are ignored until real prose is found.
    """
    buf: list[str] = []
    started = False
    for line in md_text.splitlines():
        if not started:
            if re.match(r"^#\s", line):
                started = True
            continue
        if not line.strip():
            if buf:
                break
            continue
        if re.match(r"^(#|>|\s*\||\s+[-*]\s|\s+\d+[.)]\s|\s*(---+|\*\*\*+)\s*$|\x02)", line):
            continue
        buf.append(line.strip())
    text = plain_text(" ".join(buf))
    if not text:
        return ""
    return text if len(text) <= 160 else text[:157].rstrip() + "..."


def lint_docs(pairs: list[tuple[str, str]], known_files: set[str] | None = None) -> list[str]:
    """Static checks over the whole Markdown corpus.

    pairs is a list of (stem, markdown text) covering every page that
    will be online; stems should be *stripped* ('04-welcome-sequence'
    -> 'welcome-sequence'). known_files holds non-Markdown targets
    internal links may point at (e.g. the calendar CSV). Returns
    human-readable problems; an empty list is healthy.
    """
    known_files = known_files or set()
    problems: list[str] = []
    anchors: dict[str, set[str]] = {}

    for stem, text in pairs:
        if not re.search(r"^#\s+\S", text, flags=re.M):
            problems.append(f"{stem}: no '# ' title heading for the page")
        for flag in ("TODO", "FIXME", "XXX"):
            if re.search(rf"\b{flag}\b", text):
                problems.append(f"{stem}: placeholder note '{flag}' left in the text")
        seen: set[str] = set()
        for line in text.splitlines():
            m = HEADING_RE.match(line)
            if not m or m.group(1) == "#":
                continue
            sid = slug(m.group(2))
            if sid in seen:
                problems.append(
                    f"{stem}: duplicate heading '{plain_text(m.group(2)).strip()}'"
                )
            seen.add(sid)
        anchors[stem] = seen

    for stem, text in pairs:
        for label, url in re.findall(r"\[([^\]]+)\]\(([^)\s]+)\)", text):
            if not label.strip():
                problems.append(f"{stem}: link with an empty label ({url})")
                continue
            if url.startswith(("http://", "https://", "mailto:")):
                continue
            base, frag = url.partition("#")[0], url.partition("#")[2]
            if base.endswith(".md"):
                target = split_stem(Path(base).stem)[1]
                if target not in anchors:
                    problems.append(f"{stem}: link target does not exist ({url})")
                    continue
                if frag and frag not in anchors[target]:
                    problems.append(f"{stem}: anchor not found ({url})")
                continue
            if not base and frag:
                if frag not in anchors.get(stem, set()):
                    problems.append(f"{stem}: anchor not found (#{frag})")
                continue
            if Path(base).name in known_files:
                continue
            problems.append(f"{stem}: internal link should point at a .md file ({url})")

    return problems


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<a class="skip-link" href="#content">Skip to content</a>
<header class="site-header">
  <a class="brand" href="index.html">{brand}</a>
  <span class="tagline">published by Asdale Dynamics, LLC</span>
</header>
<div class="layout">
  <nav class="sidebar" aria-label="Chapters and templates">
    {nav}
    <p class="sidebar-note">Local-first: build once, read offline forever. No tracking, no accounts.</p>
  </nav>
  <main id="content">
    <article>
      <p class="kicker">{kicker}</p>
{content}
    </article>
    <nav class="pager" aria-label="Previous and next page">
      {prev}
      {next}
    </nav>
  </main>
</div>
<footer class="page-footer">
  {brand} &middot; by Asdale Dynamics, LLC &middot; MIT licensed
  &middot; works offline, opens from a USB stick
</footer>
</body>
</html>
"""


def chapter_kicker(stem: str, section: str, number: int | None) -> str:
    if section == "Templates":
        return "Copy-paste template"
    if section == "Reference":
        return "Reference"
    if number == 0:
        return "Front matter - read this first"
    if number is not None:
        return f"Chapter {number} of {CHAPTER_COUNT}"
    return ""


def page_html(page: dict, pages: list[dict], css: str) -> str:
    idx = next(i for i, p in enumerate(pages) if p["href"] == page["href"] and p["title"] == page["title"])
    prev_page = pages[idx - 1] if idx > 0 else None
    next_page = pages[idx + 1] if idx + 1 < len(pages) else None

    groups: list[str] = []
    for p in pages:
        if p["section"] not in groups:
            groups.append(p["section"])
    nav_items: list[str] = []
    for group in groups:
        nav_items.append(f'<li><span class="nav-label">{h(group)}</span></li>')
        for p in pages:
            if p["section"] != group:
                continue
            active = ' class="active"' if p is page else ""
            nav_items.append(
                f'<li><a{active} href="{p["href"]}">{h(p["label"])}</a></li>'
            )
    nav = '<ul class="nav">' + "".join(nav_items) + "</ul>"

    prev_html = ""
    if prev_page:
        prev_html = (
            f'<a class="prev" href="{prev_page["href"]}">'
            f'<span class="dir">Previous</span>{h(prev_page["label"])}</a>'
        )
    next_html = ""
    if next_page:
        next_html = (
            f'<a class="next" href="{next_page["href"]}">'
            f'<span class="dir">Next</span>{h(next_page["label"])}</a>'
        )

    return TEMPLATE.format(
        title=f'{h(page["title"])} - {BOOK_TITLE}',
        description=h(page["summary"]) or h(BOOK_TITLE),
        brand=h(BOOK_TITLE),
        kicker=h(chapter_kicker(page["stem"], page["section"], page["number"])),
        css=css,
        nav=nav,
        content=page["html"],
        prev=prev_html,
        next=next_html,
    )


def index_html(pages: list[dict], css: str) -> str:
    def card(p: dict) -> str:
        num = f'<span class="num">{p["number"]}</span>' if p["number"] else ""
        blurb = f"<p>{h(p['summary'])}</p>" if p["summary"] else ""
        return f'<a class="card" href="{p["href"]}">{num}<span class="card-label">{h(p["label"])}</span>{blurb}</a>'

    def card_grid(items: list[dict]) -> str:
        return f'<div class="cards">\n' + "\n".join(card(p) for p in items) + "\n</div>"

    handbook = [p for p in pages if p["section"] == "The handbook"]
    reference = [p for p in pages if p["section"] == "Reference"]
    templates = [p for p in pages if p["section"] == "Templates"]

    sections = (
        '<section><h2>The manual</h2>'
        '<p class="intro">Nine short chapters. Read in order, or in borrowed minutes.</p>'
        f"{card_grid(handbook)}</section>"
    )
    if reference:
        sections += (
            '<section><h2>Reference</h2>'
            '<p class="intro">Come back when something needs looking up.</p>'
            f"{card_grid(reference)}</section>"
        )
    if templates:
        sections += (
            '<section><h2>Templates</h2>'
            '<p class="intro">Copy, paste, personalize, send.</p>'
            f"{card_grid(templates)}</section>"
        )

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A free-tools manual for starting a reader newsletter from zero, explained like a friend would: plain English, step by step, never condescending.">
<title>{h(BOOK_TITLE)}</title>
<style>
{css}
</style>
</head>
<body>
<a class="skip-link" href="#content">Skip to content</a>
<header class="site-header">
  <a class="brand" href="index.html">{h(BOOK_TITLE)}</a>
  <span class="tagline">published by Asdale Dynamics, LLC</span>
</header>
<main id="content" class="landing">
  <div class="hero">
    <p class="kicker">A $0-budget, local-first manual</p>
    <h1>Your readers' inboxes beat any feed.</h1>
    <p class="lede">Start a reader newsletter from zero with honest free tools:
    picking a provider, a welcome sequence, subject lines, drafting with AI
    without sounding canned, sending on a schedule that fits a real life,
    growing without list-spamming, and keeping an archive on your own hard
    drive. Explained like a friend would.</p>
  </div>
  <section>
    <h2>Start here if you only have an hour</h2>
    <ol class="quickstart">
      <li><a href="start-here.html">Read Start Here</a> (5 minutes)</li>
      <li><a href="why-newsletters.html">Skim Why a Newsletter</a> plus our pick for you in <a href="choose-a-provider.html">Pick Your Provider</a> (10 minutes)</li>
      <li><a href="welcome-sequence-template.html">Copy welcome email #1</a> from the template (15 minutes)</li>
      <li><a href="setup-in-one-sitting.html">Put the signup link everywhere readers already find you</a> (10 minutes)</li>
    </ol>
  </section>
  {sections}
  <p class="pairing">This handbook pairs with the sibling project
  <strong>free-author-marketing-kit</strong> (a wider $0 author marketing
  kit) and with books, guides, and tools from
  <strong>Asdale Dynamics, LLC</strong>. MIT licensed: copy, adapt, and
  share freely.</p>
</main>
<footer class="page-footer">
  {h(BOOK_TITLE)} &middot; by Asdale Dynamics, LLC &middot; MIT licensed
  &middot; works offline, opens from a USB stick
</footer>
</body>
</html>
"""
    return doc


def build_site(
    docs_dir: Path | None = None,
    out_dir: Path | None = None,
    templates_dir: Path | None = None,
) -> list[Path]:
    """Build the site: landing page, one page per doc/template, CSV copies.

    With no arguments this builds the repository (docs/ + templates/,
    manifest-checked and doc-linted). Passing docs_dir builds any docs
    folder standalone; passing templates_dir adds template pages and
    CSV copies to that build. Returns the files written. Refuses to
    build into a source directory.
    """
    repo_docs = docs_dir is None or Path(docs_dir).resolve() == DOCS.resolve()
    repo_templates = templates_dir is None or Path(templates_dir).resolve() == TEMPLATES.resolve()
    repo_mode = repo_docs and repo_templates
    docs_dir = Path(docs_dir) if docs_dir else DOCS
    if templates_dir is not None:
        templates_dir = Path(templates_dir)
    elif repo_docs:
        templates_dir = TEMPLATES
    out_dir = Path(out_dir) if out_dir else SITE

    resolved_out = out_dir.resolve()
    for source in (docs_dir, templates_dir):
        if source and source.exists() and resolved_out == source.resolve():
            raise SystemExit(
                f"Refusing to build the site into {resolved_out} (a source directory)."
            )

    if repo_mode:
        # Preflight: refuse to publish a corpus with doc-lint problems.
        problems = lint_repo()
        if problems:
            print("DOC LINT (build blocked):", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            sys.exit(1)

    md_files = sorted(docs_dir.glob("*.md"))
    tpl_files = sorted(templates_dir.glob("*.md")) if templates_dir else []
    if not md_files and not tpl_files:
        raise SystemExit(f"No markdown found in {docs_dir} (or {templates_dir})")

    css = (ASSETS / "style.css").read_text(encoding="utf-8")
    pages: list[dict] = []

    for path in md_files:
        text = path.read_text(encoding="utf-8")
        number, short = split_stem(path.stem)
        if repo_docs:
            label, section = MANIFEST.get(short, (page_title(text), "The handbook"))
        else:
            label, section = page_title(text), "The handbook"
        pages.append(
            {
                "stem": short,
                "number": number,
                "href": out_name(path.stem),
                "label": label,
                "section": section,
                "title": page_title(text),
                "summary": summary(text),
                "html": convert_markdown(text),
            }
        )
    for path in tpl_files:
        text = path.read_text(encoding="utf-8")
        number, short = split_stem(path.stem)
        if repo_templates:
            label, section = MANIFEST.get(short, (page_title(text), "Templates"))
        else:
            label, section = page_title(text), "Templates"
        pages.append(
            {
                "stem": short,
                "number": None,
                "href": out_name(path.stem),
                "label": label,
                "section": section,
                "title": page_title(text),
                "summary": summary(text),
                "html": convert_markdown(text),
            }
        )

    if repo_mode:
        unknown = [p["stem"] for p in pages if p["stem"] not in MANIFEST]
        if unknown:
            raise SystemExit(f"Pages missing MANIFEST entries: {unknown}")

    rank = {"The handbook": 0, "Reference": 1, "Templates": 2}
    pages.sort(
        key=lambda p: (
            rank.get(p["section"], 3),
            p["number"] if p["number"] is not None else 999,
            p["stem"],
        )
    )

    written: list[Path] = []
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "index.html").write_text(index_html(pages, css), encoding="utf-8")
    written.append(out_dir / "index.html")

    for page in pages:
        path = out_dir / page["href"]
        path.write_text(page_html(page, pages, css), encoding="utf-8")
        written.append(path)

    if templates_dir:
        for csv_path in sorted(templates_dir.glob("*.csv")):
            dest = out_dir / csv_path.name
            shutil.copyfile(csv_path, dest)
            written.append(dest)

    return written


def check_site(written: list[Path], out_dir: Path) -> list[str]:
    """Verify the built site: files exist, internal links resolve, no
    unresolved placeholders, no external page resources."""
    errors: list[str] = []
    missing = [p.name for p in written if not (out_dir / p.name).is_file()]
    if missing:
        errors.append(f"missing outputs: {missing}")

    for path in sorted(out_dir.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        if "\x02" in text or "\x03" in text:
            errors.append(f"{path.name}: unresolved code-block placeholder")
        srcs = re.findall(r'src="([^"]+)"', text)
        if srcs:
            errors.append(f"{path.name}: unexpected src attributes {srcs}")
        for url in re.findall(r'href="([^"]+)"', text):
            if url.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = url.split("#")[0]
            if target and not (out_dir / target).is_file():
                errors.append(f"{path.name}: broken href={url}")
        if path.name != "index.html" and "<h1" not in text:
            errors.append(f"{path.name}: no H1 rendered")

    return errors


def lint_repo() -> list[str]:
    """Lint the repository's own Markdown corpus."""
    pairs: list[tuple[str, str]] = []
    for path in sorted(DOCS.glob("*.md")) + sorted(TEMPLATES.glob("*.md")):
        pairs.append((split_stem(path.stem)[1], path.read_text(encoding="utf-8")))
    csv_names = {p.name for p in TEMPLATES.glob("*.csv")}
    return lint_docs(pairs, known_files=csv_names)


def serve(out_dir: Path, port: int = 8000) -> None:
    import os
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    os.chdir(out_dir)
    server = HTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler)
    print(f"Preview at http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Build The Reader Newsletter Handbook site.")
    parser.add_argument("--out", default=str(SITE), help="output directory (default: site/)")
    parser.add_argument("--check", action="store_true", help="lint the Markdown corpus and exit")
    parser.add_argument("--serve", action="store_true", help="preview the built site on localhost")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.check:
        problems = lint_repo()
        if problems:
            print("DOC LINT:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            sys.exit(1)
        print("Docs check: clean (links, anchors, titles, placeholders).")
        return

    out = Path(args.out)
    written = build_site(out_dir=out)
    print(f"Built {len(written)} files into {out}")

    errors = check_site(written, out)
    if errors:
        print("BUILD CHECK FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("Build checks passed: pages built, links resolve, nothing unresolved.")

    if args.serve:
        serve(out, args.port)


if __name__ == "__main__":
    main()
