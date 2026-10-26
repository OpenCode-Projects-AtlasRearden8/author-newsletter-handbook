# STATUS

Project: The Reader Newsletter Handbook
Owner: Asdale Dynamics, LLC
State: complete and verified (October 2026)

## What was built

A beginner-facing manual for starting a reader newsletter from zero with
free tools, plus the tooling that turns it into an offline static site.

- **docs/** (12 Markdown files: front matter + 9 numbered chapters + 2
  reference pages):
  - `00-start-here.md` — front matter: audience, conventions, 5-minute
    quick start, and a "one hour to live" path.
  1. Why a Newsletter (inbox-vs-feed comparison table, the honest
     counter-case)
  2. Picking a Free Provider (Honestly) — free tier comparison table
     (MailerLite, Kit, Beehiiv, Substack, Buttondown, and why not
     Mailchimp), the "exit door" test, a decision path, last-reviewed
     dates in the labeling discipline of free-author-marketing-kit
  3. Make It Official in One Sitting — 90-minute setup checklist,
     SPF/DKIM/DMARC in plain English, the test-send ring, expectations
     for the first weeks
  4. The Welcome Sequence — four-email arc, when and why, what to write
  5. Subject Lines That Get Opened — five rules, preheader pairs,
     formulas with worked examples, honestly sized testing
  6. Drafting With AI Without Sounding Canned — the five-step loop,
     banned-phrase table, what AI is good for here, honesty/privacy/
     copyright-brain hard rules, a worked micro-example
  7. Send Without Dread — tiny promise, four-pass pipeline table,
     scheduling for day jobs, dread defusing, three-month rescue plan
  8. Growing Your List Ethically — never list, honest channels, list
     hygiene, small-list morale
  9. Archive Your Issues as Local Files — folder layout, monthly
     20-minute ritual, Markdown mirrors, provider-change drill
  10. Glossary (plain-English definitions)
  11. Troubleshooting (symptom-first)

  All in-text "chapter N" references follow the filename numbering, and
  every cross-reference was checked by the doc linter and by hand.
- **templates/** (5 Markdown files + 1 CSV): copy-paste welcome sequence
  (4 emails), issue template with the minimum-lovable-issue checklist,
  25-line subject cheat sheet, signup form copy, issue calendar page +
  a filled-in `issue-calendar.csv` (12 issues, 8 columns).
- **scripts/build.py**: standard-library-only static site generator —
  zero dependencies, zero network. Landing page + 17 content pages with
  sidebar navigation, prev/next pagers, chapter kickers ("Chapter 3 of
  9"), embedded light/dark/print stylesheet, plus CSV copies. CLI flags:
  `--out DIR`, `--check` (docs lint), `--serve`, `--port`.
- **scripts/assets/style.css**: one embedded stylesheet, no external
  requests; prefers-color-scheme dark mode; print styles.
- **tests/test_build.py**: 57 tests covering the Markdown converter
  (headings/anchors, inline markers, link rewriting by basename, tables,
  task lists, wrapped continuation, fenced-code escaping), the doc
  linter (missing targets, bad anchors, non-.md links, duplicate
  headings, missing titles, placeholder notes), the site builder
  (fixture and repo modes, kickers, tag balancing of every built page,
  reproducible builds, source-directory refusal, lint-blocked and
  manifest-blocked repo builds), the CLI (`--check` clean and failing,
  build + build-checks, refusal to build into source dirs), repo docs
  health (12 planned chapters, 5 templates + CSV well-formed), and repo
  hygiene (secret-pattern scan, exact MIT license line, README credit,
  root-file whitelist, no external page resources).
- **README.md, LICENSE** (MIT, "Copyright (c) 2026 Asdale Dynamics,
  LLC"), **.gitignore**.

The README pairs the handbook with the sibling project
free-author-marketing-kit (and backup-basics-handbook and the
writing-handbook family) and credits Asdale Dynamics, LLC.

## How to run it

```bash
python3 scripts/build.py            # build the site into site/
python3 scripts/build.py --check    # lint docs (links, anchors, structure)
python3 scripts/build.py --serve    # build + preview on localhost
python3 -m unittest discover -s tests  # run the test suite
```

Then open `site/index.html` in a browser — no server needed; pages embed
their stylesheet and make no external requests, so the site works
offline and from file://.

## Verification results (run in this folder)

- `python3 --version` → Python 3.13.5
- `python3 scripts/build.py --check` → "Docs check: clean (links,
  anchors, titles, placeholders)."
- `python3 scripts/build.py` → "Built 19 files into site/" (index + 12
  docs + 4 template pages + issue-calendar.csv) and "Build checks
  passed: pages built, links resolve, nothing unresolved."
- HTML tag-balance check over every generated page (html.parser,
  included in the test suite) → 0 problems
- `python3 -m unittest discover -s tests` → 57 tests, OK (0 failures,
  0 errors)
- Reproducible-build test: two consecutive builds produce identical
  output manifests
- Secret-pattern scan (API keys, tokens, private-key blocks) across
  docs/scripts/tests/README/LICENSE → 0 matches
- Content pass: chapters hand-read for broken sentences and typos after
  initial drafting; reader-voice consistent with the house style
  ("explained like a friend would")

## Fix-ups applied in this pass

- First-pass drafts produced several garbled sentences ("physicalpostal",
  "tentatives grow into keepers", a broken AI-chapter paragraph, a
  stray row in the subject cheat sheet); each was caught, corrected, and
  the docs lint + tests re-run afterward.
- Converter bugs found by its own tests and fixed: table separator rows
  containing inner pipes were not recognized as tables; task-checkbox
  markup was escaped instead of emitted; fenced code kept a trailing
  newline before `</code>`; slugs did not collapse repeated hyphens;
  `summary()` aborted on structural lines instead of skipping them.
- Builder bug found by tests: `build_site` leaked the repository's own
  templates/manifest into arbitrary docs-folder builds; template and
  manifest handling are now scoped to repo docs, and repo-mode builds
  run the doc lint as a preflight (bad docs block the build).
- CLI `--check` printed its report to stdout; moved to stderr so failing
  lint is scriptable.

## Known gaps

- Provider free-tier figures (chapter 2) are accurate to the October
  2026 review but are recheck-date material: MailerLite/Kit/Beehiiv/
  Substack pricing pages should be re-read before relying on any
  number. The handbook itself says this on the page.
- `--serve` is implemented but not covered by an automated test (a live
  server in unit tests would be flaky); it is exercised manually.
- No dark/high-contrast screenshot verification: styles are simple and
  validated by construction, but rendering was reviewed only in headless
  tag-balance terms, not visually on real browsers/devices.
- The welcome-sequence and AI-chapter content is opinion-bearing by
  design; reader outcomes will vary and the manual does not promise
  growth numbers.
