# The Reader Newsletter Handbook

A $0-budget manual for starting a reader newsletter from zero -- with
free tools only, catches stated plainly, and a build that works offline.
Why newsletters beat social feeds, picking a provider honestly, welcome
sequences, subject lines, drafting with AI without sounding canned,
sending monthly without dread, growing ethically, and archiving every
issue to your own hard drive.

Built with warmth, tested locally, and hosted nowhere: this is a
**local-first site**. Run one build command and open `site/index.html` in
your browser -- everything works, forever, offline. No accounts, no
tracking, no affiliate links, no secrets.

> Part of the Asdale Dynamics free tools collection. Written in the same
> spirit as everything else Dylan Asdale makes: explained like a friend
> would, step by step, never condescending.

## What's inside

| File | What it covers |
|---|---|
| [`docs/00-start-here.md`](docs/00-start-here.md) | Front matter: who this is for, a 5-minute quick start, conventions |
| [`docs/01-why-newsletters.md`](docs/01-why-newsletters.md) | Chapter 1 -- why an inbox beats a feed, with the honest counter-case |
| [`docs/02-choose-a-provider.md`](docs/02-choose-a-provider.md) | Chapter 2 -- free tiers compared honestly (MailerLite, Kit, Substack, Buttondown, Beehiiv, and why not Mailchimp), plus "the exit door" test |
| [`docs/03-setup-in-one-sitting.md`](docs/03-setup-in-one-sitting.md) | Chapter 3 -- the 90-minute setup checklist, SPF/DKIM/DMARC in plain English, first test sends |
| [`docs/04-welcome-sequence.md`](docs/04-welcome-sequence.md) | Chapter 4 -- the four-email welcome sequence that greets subscribers forever |
| [`docs/05-subject-lines.md`](docs/05-subject-lines.md) | Chapter 5 -- subject lines and preheaders that get opened, without clickbait |
| [`docs/06-ai-drafting.md`](docs/06-ai-drafting.md) | Chapter 6 -- the five-step AI drafting loop, the banned-phrase list, privacy and honesty rules |
| [`docs/07-send-cadence.md`](docs/07-send-cadence.md) | Chapter 7 -- monthly cadence, a four-pass pipeline, and dread defusing for people with day jobs |
| [`docs/08-growing-ethically.md`](docs/08-growing-ethically.md) | Chapter 8 -- the never list, honest channels, list hygiene, small-list morale |
| [`docs/09-archiving-issues.md`](docs/09-archiving-issues.md) | Chapter 9 -- the 20-minute monthly ritual that saves your list and issues as local files |
| [`docs/10-glossary.md`](docs/10-glossary.md) | Glossary -- every term, in plain English |
| [`docs/11-troubleshooting.md`](docs/11-troubleshooting.md) | Troubleshooting -- spam folders, open-rate crashes, stalled months |
| [`templates/welcome-sequence-template.md`](templates/welcome-sequence-template.md) | Copy-paste welcome sequence (4 emails, bracketed slots) |
| [`templates/issue-template.md`](templates/issue-template.md) | Single-issue skeleton plus the "minimum lovable issue" checklist |
| [`templates/subject-line-cheatsheet.md`](templates/subject-line-cheatsheet.md) | 25 worked subject lines with preheader pairs |
| [`templates/signup-form-copy.md`](templates/signup-form-copy.md) | Signup form, thank-you page, and bio one-liner copy |
| [`templates/issue-calendar.md`](templates/issue-calendar.md) | How to use the calendar (`+` the CSV below) |
| [`templates/issue-calendar.csv`](templates/issue-calendar.csv) | A filled-in 12-issue year: titles, promises, subjects, CTAs |

## How to run it

Requires only Python 3 (standard library -- no installs, no network).

```bash
python3 scripts/build.py            # build the site into site/
python3 scripts/build.py --out DIR  # build somewhere else
python3 scripts/build.py --check    # lint the Markdown (links, anchors, structure)
python3 scripts/build.py --serve    # build, then preview on localhost
```

Then open `site/index.html` in any browser: a landing page, one polished
page per chapter and template with sidebar navigation and prev/next
pagers, and the issue calendar CSV copied alongside. The pages embed
their stylesheet, make no external requests, and open fine from `file://`
or a USB stick.

## Honesty, labeled

The handbook follows the labeling discipline of the sibling project
**free-author-marketing-kit**: every tool recommendation states its
**cost exactly**, its **honest limits** in plain words, and a **last
reviewed** date (this edition: October 2026). Free tiers drift; the
chapters remind you to recheck pricing pages the week you sign up, and
chapter 2's "exit door" test keeps every provider escapable.

## Verify it yourself

```bash
python3 scripts/build.py --check     # docs lint: links, anchors, titles, placeholders
python3 -m unittest discover -s tests  # 57 tests: converter, lint, build, CLI, hygiene
```

The test suite covers the Markdown converter (headings, tables, task
lists, inline styles, link rewriting, escaping), the doc linter, the site
builder (fixture and repo modes, reproducible builds, tag balance), the
CLI, and repo hygiene (secret-pattern scan, the exact MIT license line,
README credit, and a root-file whitelist). Markdown, Python, CSV, CSS,
and HTML only -- no build tools to install.

## Pairings

- **free-author-marketing-kit** -- the wider $0 marketing kit; this
  handbook's chapters 2 and 8 go deeper on the newsletter slice of it.
- **backup-basics-handbook** -- chapter 9's archive folder wants backups;
  that handbook covers them kindly.
- **writers-ai-companion-manual** and **prompt-writing-handbook** --
  chapter 6's AI drafting loop meets these on the writing-toolshelf.
- Other books, guides, and tools from **Asdale Dynamics, LLC**, including
  *The Massive AI Manual* and the hub site dylanasdale.github.io.

## License

MIT -- see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
You may copy, adapt, and share this material freely, including
commercially, with attribution.
