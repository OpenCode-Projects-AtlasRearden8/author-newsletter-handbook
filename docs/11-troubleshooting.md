# Troubleshooting

> Symptoms first, causes second, fixes third. If your problem is not
> here, the [glossary](10-glossary.md) may at least hand you the right
> word to search for.

## "The email is going to spam"

The classic, and it almost always has an identified culprit:

1. **Chapter 3's authentication is missing or half-done.** Re-run the
   SPF/DKIM/DMARC checklist in your provider's settings; this is the
   most common cause by far for brand-new senders.
2. **Your test address was new to your list.** Deliverability warm-up is
   real: new providers and new senders take a few weeks of steady,
   low-complaint volume to earn a reputation. Send small, on schedule,
   and let the age work.
3. **Someone on the list reported you as spam** -- check if your
   provider shows complaint feedback. A small list with a handful of
   wrong-permission signups can trigger this; prune and re-permission
   honestly (chapter 8).
4. **You imported contacts you did not earn.** The one true cardinal
   sin. Export what is recoverable, start clean with only people who
   asked.

Diagnosis helper: send to a fresh webmail address (Outlook, a spare
Gmail) and a work address if available. Whether it *only* misses one
inbox tells you which filter conversation to have.

## "Open rate crashed this month"

In order of celebrity:

1. **One huge send went to a different slice** than usual (compare the
   send counts in your provider's report).
2. **A big provider (Apple, Gmail) privacy change inflated the old
   baseline** -- your earlier months were flattered; the trend line is
   the truth, single points lie.
3. **The subject line was mushy** (chapter 5's four questions, applied
   honestly).
4. **The list went stale** -- chapter 8's hygiene session was skipped
   two or three launches running; cleanup time.

Reminder from chapter 3: per-sends, deliverability and reply counts are
truer indicators than opens; privacy features grade opens dishonestly.

## "Gmail puts me in the Promotions tab"

That is Gmail being Gmail, not spam. Readers still receive you; the fix
that matters is being worth dragging into Primary -- consistent cadence
(chapter 7), real From name (chapter 3), and welcome email #4's polite
ask to star you (chapter 4). It takes weeks and reader behavior, and it
does not always happen; life goes on because letters get read from both
corners.

## "I have 11 subscribers and it feels embarrassing"

Chapter 8 addressed the data; here is the practical reframe. At 11
readers, your job is writing and one honest invite per month, not
analytics. The metric worth tracking at this size: replies. One reply to
issue #3. Then confirm at 100 readers, then at 1,000 -- with the truth
that a reliable 100-reader newsletter is a better asset than a
five-year-old abandoned 3,000-subscriber shell.

## "I missed a month (or three)"

Not fatal, not novel, and chapter 7's three-month rescue plan is the
playbook. Short version: send the "I owe you one" restart issue with
your single best link, re-commit to the small promise, and put three
*outline* passes (not sends) on the calendar this week.

## "The provider changed their free terms"

Real and recurring; the free-tier table in chapter 2 carries its own recheck date for
exactly this. Sequence: read what changed (subscriber caps, send limits,
feature moves), decide whether the plan still fits chapters 4/6/7's
needs, and if not, chapter 9's exit drill makes moving cheap: CSV out,
welcome sequence re-created from your local template copy, back catalog
imported, test-send ring, done. The whole design of this handbook is to
make provider exits boring.

## "The signup form works but nobody fills it"

1. **The form copy probably sells vagueness** ("Subscribe to my
   updates" asks nothing). Fix with more clear and more specific copy
   from [the signup form template](../templates/signup-form-copy.md):
   what arrives, how often, what a reader gets in the first week.
2. **The link is in the wrong place.** Chapter 8's back-matter and
   profile rule; measure whether readers meet the form *without*
   hunting.
3. **You are not yet being useful in public** -- one good, findable
   public artifact per month (an issue, a post linked to a real
   question) is the honest funnel the form hangs from.

## "The issue looks different in different inboxes"

Inherent to email, not a bug: dark mode, tiny screens, images-off
settings, and client differences make every email render slightly
differently forever. Two habits absorb it: send test emails to your own
odd addresses (chapter 3's ring), and design plain-first (chapter 4's
welcome rule extends to issues: if it reads well as plain text, the
fancy layout is a bonus, not a requirement).

## "I hit a wall and just dread opening the provider dashboard"

That is chapter 7's subject spelled in symptoms, and its medicine is the
timeboxing and one-person rule; the note here is the escape valve: the
whole flow is local-first by design. You can write in your own editor
(the [issue template](../templates/issue-template.md)), keep stats in a
text file, store issues in [the archive](09-archiving-issues.md), and
only touch the provider twice a month: send day and the 20-minute
ritual. Dread shrinks when the dashboard becomes a tollbooth instead of
a desk.
