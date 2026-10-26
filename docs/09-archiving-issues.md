# Archive Your Issues (Local Files)

> Last reviewed: October 2026. This chapter is the handbook practicing
> what it preaches: these docs live as plain Markdown on your computer,
> and this handbook itself is a build-from-local-files project. The
> parallel is the point.

Chapter 9 is short on theory and long on ritual. One premise, stated
plainly: **the provider is a tenant, not a landlord.** Subscriptions,
obsolete tools, corporate pivots, or an accidental click in a
setup screen can all make a newsletter's history vanish. The fix costs
20 minutes a month and a folder on your own computer.

## What you keep, exactly

Three file kinds make up a complete archive:

| What                          | Why it matters                                     | Format to keep                        |
| ----------------------------- | -------------------------------------------------- | ------------------------------------- |
| **The subscriber list (CSV)** | The audience itself -- your years of trust          | CSV export, monthly                   |
| **Every issue you sent**      | Your back catalog; future issues' raw material      | One HTML or PDF per issue, or Markdown mirror |
| **Your writing raw**          | Drafts, swipe file, banned-words list, notes        | Plain text files (Markdown or .txt)   |

Subscriber data note: a subscriber CSV contains personal data -- emails,
sometimes names. Store it where you store your own sensitive documents,
do not paste its contents into any AI tool (chapter 6's rule), and keep
the archive itself out of anything you might publish. The handbook's own
hygiene rules (no personal data in shared folders) apply to you too.

## The folder layout

One folder, boring on purpose. `newsletter-archive/` dedicated purely to
sending data; nothing else lives here:

```text
newsletter-archive/
  subscribers/
    2026-10-subscribers.csv
    2026-11-subscribers.csv
  issues/
    2026-10-first-issue.html
    2026-11-issue-02.md          <- if you keep a text mirror
    2026-11-issue-02.html
  drafts/
    swipe-file.md                <- your own best sentences (chapter 6)
    banned-list.md               <- your personal canned-phrase list
    notes.md                     <- capture pass (chapter 7, pass 1)
```

The naming rule is `YYYY-MM-<slug>`: it sorts itself chronologically,
zero tooling needed, and the month prefix matches the issue calendar.
Use lowercase-hyphen slugs, matching the
[issue calendar](../templates/issue-calendar.md)'s working-title column,
so the archive and the calendar tell one story together.

Why files rather than a clever app: because files survive everything.
Any text editor, any future computer, any backup drive, no subscription.
The boring solution wins here on every axis that matters -- including
the one your future self cares about most: a decade from now, everything
in this folder still opens.

## The monthly ritual (20 minutes, calendar note)

- [ ] Export the subscriber list to `subscribers/YYYY-MM-subscribers.csv`.
- [ ] Save each issue you sent this month:
  - Preferred: your provider's "download as HTML"/"view as page" copy of
    the sent email, saved as a file (keeps the real, delivered look).
  - Plus a Markdown mirror for anything you might rework later into an
    essay, a chapter, or a book draft.
  - PDF (browser print to file) as the "universal" copy when HTML gets
    fussy.
- [ ] Append the month's stats (sends, opens, unsubscribes, replies) to
  one `stats.txt` line -- five numbers, one line, your history.
- [ ] Glance at backups: is this folder inside whichever folder your
  regular backup already covers? The sibling project
  backup-basics-handbook covers the wider subject; here, one line
  matters: **two copies on different drives** beats one clever copy.

21 minutes. Probably 15 by month two. This is the whole chapter.

## Why Markdown mirrors are worth the extra minutes

HTML copies are the faithful record; Markdown mirrors are the *useful*
one. A year of issues as Markdown means:

- Ctrl+F through your own ideas without leaving your editor.
- Reuse without scraping: next year's book chapter may start as issue
  #7's mid-section. (This is how this handbook's own chapters get
  maintainable -- plain text is greppable, diffable, and durable.)
- Provider-independent forever: if you leave any provider in chapter 2's
  table, the archive opens in anything.

## The provider-change drill (rehearsed, not feared)

When you switch providers -- and most working newsletters switch at least
once -- the checklist collapses to: import the latest CSV, re-create the
welcome sequence from your local template copy (chapter 4), paste the
back catalog in as new archived issues or links, re-verify the domain
records (chapter 3's table), and re-run the test-send ring. An afternoon,
not a tragedy. Chapters 3-9 were written so that this paragraph could be
this boring.

## What you do NOT need to archive

- Every open, click, and bounce log (provider statistics dashboards can
  stay fugitive; five numbers in `stats.txt` is your history).
- Unlimited design variants and logo iterations (chapter 3 warned
  against this habit, politely).
- Old drafts past the point of curiosity -- keep cut issues' best lines
  into `swipe-file.md`, then let drafts go.

Next: the [Troubleshooting](11-troubleshooting.md) reference when
something misbehaves, or the [glossary](10-glossary.md) for any word
that got away.
