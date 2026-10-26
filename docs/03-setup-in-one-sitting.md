# Make It Official in One Sitting

>You voted for a provider in chapter 2. Chapter 3 is the signing-up
>sitting: every finicky one-time setting, done once, in about 90 minutes,
>so you never have to think about them again.

Time estimate: **90 minutes total** as a first sitting, coffee nearby. Do
not draft your first issue in this sitting. Setup and drafting are
different muscles, and mixing them is how setup never finishes.

> Everything in this chapter is free. The two settings that often want
> money elsewhere (custom domains, advanced design templates) are either
> worked around for free here or simply not needed yet.

## Before you start, have these ready

- The name of your newsletter (tentative names
  grow into keepers, so do not spend an hour on this).
- A **physical mailing address** to put in the footer. Legal anti-spam
  rules (like CAN-SPAM in the US) require a real physical postal address on
  commercial email. Your own street address works; many authors use a city,
  state zip on its own, a PO box, or their LLC's address. Never lie.
- The **default reply-to email** you actually read. Newsletters generate
  replies into a week's worth of conversations; one real inbox works.
- A domain you control *if* you have one (book site, blog). If not: skip
  the optional custom-domain section; it is a paid feature at most
  providers and genuinely fine to postpone.

## The 90-minute checklist

- [ ] Create the account on your provider (10 min)
  - Use an email you check; confirm their verification email immediately.
  - Expect a human review at MailerLite-style providers (a day, sometimes
    longer on weekends). This is normal spam defense,
    not suspicion of you specifically.
- [ ] Set the From name and reply-to (10 min)
  - From name: your real name. People open mail from people, not brands.
  - Reply-to: an inbox you will genuinely read within a week. Replies are
    chapter 8's cheapest growth tool.
- [ ] Choose double opt-in if offered (5 min) -- see chapter 2's note; on
  unless your country gives you a reason not to.
- [ ] Do the account-verification paperwork providers now require (15 min)
  - Google and Yahoo (thanks to their 2024 bulk-sender rules) expect
    real senders to prove domain ownership via three DNS records:
    **SPF, DKIM, and DMARC**. Glossary names them; the provider's setup
    screen walks you through them one at a time.
  - Using the provider's own free sending domain still asks you to verify your email;
    custom domains need the DNS entries pasted at your registrar.
- [ ] Set up your signup form or landing page (20 min)
  - Use the [signup form copy template](../templates/signup-form-copy.md).
  - Say plainly what people get and how often: "one email a month, book
    news and AI tools in plain English, zero spam, unsubscribe anytime."
  - Turn on is the relevant checkboxes: consent, GDPR if it is offered.
- [ ] Write and switch on welcome email #1 (20 min)
  - Copy from the [welcome sequence template](../templates/welcome-sequence-template.md).
  - Set it to send immediately when someone subscribes.
- [ ] The test send ring (10 min)
  - Subscribe with two of your own addresses (different domains if you
    have them): one personal, one "old laptop" address.
  - Check: the form works, the double-opt-in email arrives, the
    confirmation lands you on the list, the welcome email arrives, the
    footer link unsubscribe works (then unsubscribe from the second
    address and confirm the list shows the change).
- [ ] Export drill (10 min)
  - Export your subscribers as CSV from the provider now -- with four
    rows, of which three are you and one is your cat's test persona. This
    proves chapter 9's archive ritual can work before it matters.

Done sitting. Classic beginner mistake avoided: do not yet design a logo.

## The DNS words, in one plain table

You will meet these letters during verification. The table is all most
authors ever need; no one learns email infrastructure out of love.

| Term   | In plain English                                                                                          | What you do                            |
| ------ | ------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| SPF    | A public note listing which computers are allowed to send email **as you**                                | Paste provider-provided TXT record once |
| DKIM   | A wax seal -- the provider signs outgoing mail so receivers can check it was not forged in transit        | Provider handles it once you verify    |
| DMARC  | A rule for email receivers: how strictly to treat mail *claiming* to be you, and where to send reports    | Optional-ish; providers help set it    |
| Bounce | A sending attempt that failed (bad address, full inbox)                                                  | Automatic; watch the weekly report      |

Why diligence here: since 2024, Google and Yahoo enforce these for anyone
sending bulk email, including "bulk" meaning your 47 subscribers. Doing it
one time means skipping the spam folder for most of your readers forever.

## Expectations for the first weeks

- Your first sends typically land 60-90 minutes later than you are used to
  consumer email. Slow relay queues are normal and boring. Do not resend.
- The "open rate" numbers on a 12-person list are basically noise; judge
  deliverability on placement and bounces, not opens, for the first month.
- One hot topic: gmail putting you in **Promotions**. That is Gmail
  sorting, not spam foldering; readers still see you. Hide from it by
  being worth pulling into Primary (chapters 4-7 all help, especially
  replies).

## The two things to never do in a setup sitting

1. **Import a purchased list.** Chapter 8 explains why this is the one
   true cardinal sin of newsletters, but the practical sentence is: it
   wrecks your sender reputation on day one, and the provider may ban the
   account before you send a single real issue.
2. **Delay the export drill.** The exit-door test from chapter 2 only
   counts if you have actually done it. Ten minutes now makes chapter 9 a
   ritual rather than a rescue.

Next: [The Welcome Sequence](04-welcome-sequence.md). When you have sent
issue #1, chapter 9 takes over; before that, chapter 7's calendar keeps
you honest.
