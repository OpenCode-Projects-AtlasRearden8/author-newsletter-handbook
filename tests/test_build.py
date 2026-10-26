"""Tests for The Reader Newsletter Handbook build.

Run with: python3 -m unittest discover -s tests
Standard library only. Covers the Markdown converter, doc lint, the
site builder, the CLI, repo-doc health, reproducibility, and repo
hygiene (secrets, license line, README credit, root file whitelist).
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build as b  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

FIXTURE_A = """\
# Alpha Chapter

Hello world with **bold**, *soft*, and `code here`, plus [glossary link](09-glossary.md#token-plus).

First continues.

- one
- two
  - deep

1. first
2. second

- [ ] todo
- [x] done

> quote line
> second line

| A | B |
| --- | --- |
| 1 | 2 |
| short | |

```bash
echo hi --flag
```

---

See the template [here](../templates/issue-template.md) and the web [site](https://example.com/page).
"""

FIXTURE_B = """\
# Glossary Thing

Some intro bit.

## token plus

Body about tokens.
"""


class ConverterTests(unittest.TestCase):
    def conv(self, doc):
        return b.convert_markdown(doc)

    def test_headings_and_anchors(self):
        html = self.conv("## My Section\nwords")
        self.assertIn('<h2 id="my-section">My Section</h2>', html)

    def test_heading_levels_map(self):
        html = self.conv("#### deep\nbody")
        self.assertIn('<h4 id="deep">deep</h4>', html)

    def test_inline_markers(self):
        html = self.conv("dog **bold** cat *soft* end `x` and `y` tail")
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>soft</em>", html)
        self.assertIn("<code>x</code>", html)
        self.assertNotIn("**", html)

    def test_html_escapes_but_code_is_literal(self):
        html = self.conv("safe <script> tag & `x <b>y</b>` z")
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("<code>x &lt;b&gt;y&lt;/b&gt;</code>", html)
        self.assertNotIn("<script>", html)

    def test_internal_link_rewrite_by_basename(self):
        html = self.conv("see [token](09-glossary.md#token-plus) and [tpl](../templates/issue-template.md)")
        self.assertIn('href="glossary.html#token-plus"', html)
        self.assertIn('href="issue-template.html"', html)

    def test_external_link_kept(self):
        html = self.conv("go [there](https://example.com/a)")
        self.assertIn('href="https://example.com/a"', html)

    def test_csv_and_mailto_untouched(self):
        html = self.conv("cal [cal](issue-calendar.csv) mail [m](mailto:a@b.c)")
        self.assertIn('href="issue-calendar.csv"', html)
        self.assertIn('href="mailto:a@b.c"', html)

    def test_lists_nested_and_ordered(self):
        html = self.conv("- a\n- b\n  - b1\n  - b2\n1. one\n2. two")
        self.assertIn("<ul>\n<li>a</li>\n<li>b<ul>\n<li>b1</li>\n<li>b2</li>\n</ul></li>\n</ul>", html)
        self.assertIn("<ol>\n<li>one</li>\n<li>two</li>\n</ol>", html)

    def test_task_lists(self):
        html = self.conv("- [ ] todo\n- [x] done")
        self.assertIn('<li class="task"><input type="checkbox" disabled> todo</li>', html)
        self.assertIn('<li class="task done"><input type="checkbox" checked disabled> done</li>', html)

    def test_wrapped_list_item_continuation(self):
        html = self.conv("- first item that wraps\n  onto a second indented line\n- next item")
        self.assertIn("<li>first item that wraps onto a second indented line</li>", html)
        self.assertIn("<li>next item</li>", html)

    def test_blockquote_joins_and_hr(self):
        html = self.conv("> one line\n> two line\n\n---\n\nafter")
        self.assertIn("<blockquote><p>one line two line</p></blockquote>", html)
        self.assertIn("<hr>", html)

    def test_table_cells_and_padding(self):
        html = self.conv("| A | B |\n| --- | --- |\n| 1 | 2 |\n| short | |")
        self.assertIn("<th>A</th><th>B</th>", html)
        self.assertIn("<td>1</td><td>2</td>", html)
        self.assertIn("<td>short</td><td></td>", html)

    def test_table_separator_with_inner_pipes(self):
        html = self.conv("| A | B |\n| :--- | ---: |\n| 1 | 2 |")
        self.assertIn("<table>", html)

    def test_code_fence_language_and_protection(self):
        html = self.conv("```bash\nrun --flag `nested`\n```")
        self.assertIn("<pre><code>run --flag `nested`</code></pre>", html)
        self.assertNotIn("\x02", html)

    def test_slug_ascii_and_plain(self):
        self.assertEqual(b.slug("What's Next - 2?"), "whats-next-2")

    def test_plain_text(self):
        self.assertEqual(
            b.plain_text("**Bold** [link](a.md) and `code` rock"),
            "Bold link and code rock",
        )

    def test_doc_title(self):
        self.assertEqual(b.page_title("pre\n# The Title\n"), "The Title")

    def test_out_name_strips_numbering(self):
        self.assertEqual(b.out_name("09-glossary"), "glossary.html")
        self.assertEqual(b.out_name("issue-template"), "issue-template.html")

    def test_full_fixture(self):
        html = self.conv(FIXTURE_A)
        for needle in (
            "<h1",
            "<strong>bold</strong>",
            "<ul>",
            "<ol>",
            '<li class="task done">',
            "<blockquote><p>",
            "<table>",
            "<pre><code>",
            "<hr>",
            'href="glossary.html#token-plus"',
            'href="https://example.com/page"',
        ):
            self.assertIn(needle, html, needle)
        self.assertNotIn("\x02", html)


class LintTests(unittest.TestCase):
    def lint(self, pairs, fragment):
        problems = b.lint_docs(pairs)
        self.assertTrue(
            any(fragment in p for p in problems),
            f"expected problem containing {fragment!r}, got {problems}",
        )

    def test_missing_target(self):
        self.lint([("a", "# A\nsee [x](missing.md)"), ("b", "# B")], "link target does not exist")

    def test_bad_anchor(self):
        self.lint([("a", "# A\nsee [x](b.md#nope)"), ("b", "# B\n\n## real")], "anchor not found")

    def test_non_md_internal_link(self):
        self.lint([("a", "# A\nsee [x](b.txt)")], "internal link should point at a .md file")

    def test_known_csv_file_allowed(self):
        pairs = [("a", "# A\nget [cal](issue-calendar.csv)")]
        self.assertEqual(b.lint_docs(pairs, known_files={"issue-calendar.csv"}), [])

    def test_unknown_file_rejected(self):
        pairs = [("a", "# A\nget [x](other.txt)")]
        self.assertNotEqual(b.lint_docs(pairs, known_files={"issue-calendar.csv"}), [])

    def test_duplicate_heading_flagged(self):
        self.lint([("a", "# A\n\n## x\nstuff\n\n## x")], "duplicate heading")

    def test_missing_title_flagged(self):
        self.lint([("a", "no title at all")], "no '# ' title heading")

    def test_placeholder_note_flagged(self):
        self.lint([("a", "# A\n\nTODO fix this slot")], "placeholder note 'TODO'")

    def test_clean_docs_pass(self):
        pairs = [
            ("a", "# A\nsee [glossary](b.md#token)\n\ntext"),
            ("b", "# B\n\n## token\nbody"),
        ]
        self.assertEqual(b.lint_docs(pairs), [])


class SummaryTests(unittest.TestCase):
    def test_summary_takes_first_paragraph(self):
        md = "# Title\n\nFirst short line here.\n\n- list item\n"
        self.assertEqual(b.summary(md), "First short line here.")

    def test_summary_skips_lists_and_quotes(self):
        md = "# Title\n\n> quote start\n\n| A |\n|---|\n|x|\n\nreal first paragraph."
        self.assertEqual(b.summary(md), "real first paragraph.")

    def test_summary_truncates(self):
        md = "# Title\n\n" + "word " * 100
        out = b.summary(md)
        self.assertTrue(out.endswith("..."))
        self.assertLessEqual(len(out), 160)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="handbook-build-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.docs = self.tmp / "docs"
        self.docs.mkdir()
        (self.docs / "01-alpha.md").write_text(FIXTURE_A, encoding="utf-8")
        (self.docs / "09-glossary.md").write_text(FIXTURE_B, encoding="utf-8")
        self.out = self.tmp / "site"

    def test_build_creates_expected_files(self):
        written = b.build_site(self.docs, self.out)
        names = sorted(p.name for p in written)
        self.assertEqual(
            names,
            sorted(["index.html", "alpha.html", "glossary.html"]),
        )
        for name in names:
            self.assertTrue((self.out / name).is_file())

    def test_index_has_toc_with_titles(self):
        b.build_site(self.docs, self.out)
        index = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn("Glossary Thing", index)
        self.assertIn('href="glossary.html"', index)
        self.assertIn(b.BOOK_TITLE, index)

    def test_chapter_page_has_nav_pager_meta(self):
        b.build_site(self.docs, self.out)
        alpha = (self.out / "alpha.html").read_text(encoding="utf-8")
        self.assertIn('class="pager"', alpha)
        self.assertIn('name="description"', alpha)
        self.assertIn("<table>", alpha)
        self.assertIn("<blockquote>", alpha)

    def test_kicker_chapter_numbering(self):
        b.build_site(self.docs, self.out)
        alpha = (self.out / "alpha.html").read_text(encoding="utf-8")
        self.assertIn("Chapter 1 of 9", alpha)
        gloss = (self.out / "glossary.html").read_text(encoding="utf-8")
        # Non-manifest'd fixture docs default to handbook section.
        self.assertIn("Chapter 9 of 9", gloss)

    def test_anchor_link_in_doc_points_to_existing_heading(self):
        b.build_site(self.docs, self.out)
        alpha = (self.out / "alpha.html").read_text(encoding="utf-8")
        self.assertIn('href="glossary.html#token-plus"', alpha)
        gloss = (self.out / "glossary.html").read_text(encoding="utf-8")
        self.assertIn('id="token-plus"', gloss)

    def test_chapter_kicker_function(self):
        self.assertEqual(
            b.chapter_kicker("why-newsletters", "The handbook", 1),
            "Chapter 1 of 9",
        )
        self.assertEqual(
            b.chapter_kicker("start-here", "The handbook", 0),
            "Front matter - read this first",
        )
        self.assertEqual(b.chapter_kicker("glossary", "Reference", None), "Reference")
        self.assertEqual(
            b.chapter_kicker("issue-template", "Templates", None),
            "Copy-paste template",
        )

    def test_build_refuses_source_directory(self):
        with self.assertRaises(SystemExit):
            b.build_site(self.docs, self.docs)
        self.assertEqual(len(list(self.docs.glob("*.md"))), 2)

    def test_lint_failure_blocks_repo_mode(self):
        (self.docs / "02-bad.md").write_text("# Bad\n[missing](nowhere.md)\n", encoding="utf-8")
        repo = self.tmp / "repo-docs"
        repo.mkdir()
        shutil.copytree(self.docs, repo / "docs")
        templates = repo / "templates"
        templates.mkdir()
        original_docs, original_templates = b.DOCS, b.TEMPLATES
        b.DOCS, b.TEMPLATES = repo / "docs", templates
        try:
            with self.assertRaises(SystemExit):
                b.build_site()
        finally:
            b.DOCS, b.TEMPLATES = original_docs, original_templates

    def test_manifest_mismatch_blocks_repo_mode(self):
        repo = self.tmp / "repo-docs2"
        repo.mkdir()
        shutil.copytree(self.docs, repo / "docs")
        templates = repo / "templates"
        templates.mkdir()
        # Fixture stems are not in the manifest; repo mode must complain.
        original_docs, original_templates, original_site = b.DOCS, b.TEMPLATES, b.SITE
        b.DOCS, b.TEMPLATES, b.SITE = repo / "docs", templates, self.out
        try:
            with self.assertRaises(SystemExit):
                b.build_site()
        finally:
            b.DOCS, b.TEMPLATES, b.SITE = original_docs, original_templates, original_site


class RepoBuildTests(unittest.TestCase):
    """Build the repository's actual docs/templates into a temp dir."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="handbook-repo-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.out = self.tmp / "site"

    def test_repo_build_outputs(self):
        written = b.build_site(docs_dir=b.DOCS, out_dir=self.out, templates_dir=b.TEMPLATES)
        names = {p.name for p in written}
        self.assertIn("index.html", names)
        self.assertIn("issue-calendar.csv", names)
        for stem in ("start-here", "why-newsletters", "choose-a-provider",
                     "setup-in-one-sitting", "welcome-sequence", "subject-lines",
                     "ai-drafting", "send-cadence", "growing-ethically",
                     "archiving-issues", "glossary", "troubleshooting",
                     "welcome-sequence-template", "issue-template",
                     "subject-line-cheatsheet", "signup-form-copy", "issue-calendar"):
            self.assertIn(f"{stem}.html", names)

    def test_repo_pages_are_tag_balanced(self):
        b.build_site(docs_dir=b.DOCS, out_dir=self.out, templates_dir=b.TEMPLATES)

        class Balanced(HTMLParser):
            VOID = {"br", "hr", "img", "input", "meta", "link", "area",
                    "base", "col", "embed", "source", "track", "wbr"}

            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.stack = []
                self.problems = []

            def handle_starttag(self, tag, attrs):
                if tag not in self.VOID:
                    self.stack.append(tag)

            def handle_endtag(self, tag):
                if tag in self.VOID:
                    return
                if self.stack and self.stack[-1] == tag:
                    self.stack.pop()
                else:
                    self.problems.append(tag)

        parser = Balanced()
        for path in sorted(self.out.glob("*.html")):
            parser.stack.clear()
            parser.problems.clear()
            parser.feed(path.read_text(encoding="utf-8"))
            parser.close()
            self.assertFalse(
                parser.problems or parser.stack,
                f"{path.name}: problems={parser.problems[:3]} stack={parser.stack[:5]}",
            )

    def test_repo_build_is_reproducible(self):
        seen = []
        for _ in range(2):
            out = self.tmp / f"site-repeat-{len(seen)}"
            b.build_site(docs_dir=b.DOCS, out_dir=out, templates_dir=b.TEMPLATES)
            seen.append(sorted((p.name, p.stat().st_size) for p in out.iterdir()))
        self.assertEqual(seen[0], seen[1])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="handbook-cli-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.docs = self.tmp / "docs"
        self.docs.mkdir()
        (self.docs / "01-alpha.md").write_text(FIXTURE_A, encoding="utf-8")

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "build.py"), *args],
            capture_output=True,
            text=True,
        )

    def test_cli_check_clean(self):
        result = self.run_cli("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("clean", result.stdout)

    def test_cli_builds_site_and_checks(self):
        out = self.tmp / "out"
        result = self.run_cli("--out", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Built", result.stdout)
        self.assertIn("Build checks passed", result.stdout)
        self.assertTrue((out / "index.html").is_file())

    def test_cli_doc_lint_failure_exits_one(self):
        (b.DOCS / "_scratch_test_doc.md").write_text(
            "# Scratch\n[missing](gone.md)\n", encoding="utf-8"
        )
        try:
            result = self.run_cli("--check")
        finally:
            (b.DOCS / "_scratch_test_doc.md").unlink()
        self.assertEqual(result.returncode, 1)
        self.assertIn("DOC LINT", result.stderr)

    def test_cli_bad_output_directory(self):
        result = self.run_cli("--out", str(b.DOCS))
        self.assertEqual(result.returncode, 1)
        self.assertIn("Refusing", result.stderr)


class RepoDocsTests(unittest.TestCase):

    def test_repo_docs_lint_clean(self):
        docs = sorted(b.lint_repo())
        self.assertEqual(docs, [], f"lint problems: {docs}")

    def test_planned_chapters_present(self):
        stems = {p.stem for p in b.DOCS.glob("*.md")}
        self.assertEqual(
            stems,
            {
                "00-start-here", "01-why-newsletters", "02-choose-a-provider",
                "03-setup-in-one-sitting", "04-welcome-sequence",
                "05-subject-lines", "06-ai-drafting", "07-send-cadence",
                "08-growing-ethically", "09-archiving-issues",
                "10-glossary", "11-troubleshooting",
            },
        )

    def test_template_files_present(self):
        stems = {p.stem for p in b.TEMPLATES.glob("*.md")}
        self.assertEqual(
            stems,
            {"welcome-sequence-template", "issue-template",
             "subject-line-cheatsheet", "signup-form-copy", "issue-calendar"},
        )
        self.assertTrue((b.TEMPLATES / "issue-calendar.csv").is_file())

    def test_calendar_csv_well_formed(self):
        import csv

        with (b.TEMPLATES / "issue-calendar.csv").open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 12)
        for row in rows:
            self.assertEqual(
                set(row), {"week", "issue", "working_title", "one_line_promise",
                           "subject_line_draft", "send_day", "cta", "notes"}
            )
            for value in row.values():
                self.assertIsNotNone(value)

    def test_site_document_root_is_source(self):
        self.assertTrue(b.DOCS.is_dir())
        self.assertTrue(b.TEMPLATES.is_dir())


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"gh[p bou]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)api[_-]?key\s*[=:]\s*['\"][^'\"]{8,}"),
    re.compile(r"(?i)(secret|token)\s*[=:]\s*['\"][^'\"]{16,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

LICENSE_LINE = "Copyright (c) 2026 Asdale Dynamics, LLC"


class RepoHygieneTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = ROOT
        cls.scanned = [
            p
            for p in cls.root.rglob("*")
            if p.is_file()
            and "site" not in p.parts
            and ".git" not in p.parts
            and "__pycache__" not in p.parts
        ]

    def test_no_secrets_anywhere(self):
        for path in self.scanned:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                self.assertIsNone(
                    pattern.search(text),
                    f"possible secret pattern {pattern.pattern} in {path}",
                )

    def test_license_file_exact_copyright(self):
        text = (self.root / "LICENSE").read_text(encoding="utf-8")
        self.assertIn(LICENSE_LINE, text)
        self.assertIn("Permission is hereby granted, free of charge", text)

    def test_readme_credits_the_llc(self):
        text = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", text)
        self.assertIn(LICENSE_LINE, text)

    def test_repo_has_no_unexpected_top_level_files(self):
        allowed = {
            "README.md",
            "LICENSE",
            "STATUS.md",
            ".gitignore",
            ".git",
            "scripts",
            "docs",
            "tests",
            "templates",
            "site",
        }
        extra = {p.name for p in self.root.iterdir()} - allowed
        self.assertEqual(extra, set(), f"unexpected files in repo root: {extra}")

    def test_no_external_resource_requests_in_built_pages(self):
        out = Path(tempfile.mkdtemp(prefix="handbook-hygiene-"))
        try:
            b.build_site(docs_dir=b.DOCS, out_dir=out, templates_dir=b.TEMPLATES)
            for page in out.glob("*.html"):
                text = page.read_text(encoding="utf-8")
                for attr in ("src", "integrity"):
                    self.assertNotIn(f'{attr}="', text, f"{page.name}: unexpected {attr}")
                for url in re.findall(r'(?:href|src)="([^"]+)"', text):
                    if url.startswith("http"):
                        # external references are allowed only as <a> links
                        self.assertTrue(
                            re.search(rf'<a [^>]*href="{re.escape(url)}"', text),
                            f"{page.name}: referenced as a resource: {url}",
                        )
        finally:
            shutil.rmtree(out)


if __name__ == "__main__":
    unittest.main()
