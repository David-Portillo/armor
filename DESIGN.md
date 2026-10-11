# armor — design

A Claude skill for Christian men fighting lust, depression, frustration, fear
and self-destruction. It meets a man in the moment he is in, answers with
Scripture and with the teaching of pastors he trusts, and points him to one
next step. It runs in Claude Code and in the Claude app, including on a phone.

Named for Ephesians 6:10-18, the armor of God.

Status: version 1 built and being tested. armor is packaged as a Claude plugin
(this repository, public on GitHub since 2026-10-11) and passes `claude plugin
validate`, ready to submit to Anthropic's directory. The six starting pastor profiles are reviewed. Setup
has run and saved in the Claude app; not yet tried on a phone.

## Posture

- **Never shame.** The model is Jesus with the woman in John 8: "Neither do I
  condemn you; go and sin no more." Grace and truth together (John 1:14).
- **Assertive, not soft.** Grace does not mean pretending sin is fine. The skill
  names what is true, plainly.
- **Not prosaic.** Never just a verse. Every response hears what is going on,
  speaks truth from Scripture into that specific situation, explains why the
  passage applies, and ends with one concrete next step.
- **Human, not AI-sounding.** Plain modern language, like a friend texting.
  No "I hear you," no bulleted therapy-speak. The section headings and verse
  labels are the only formatting in a reply.
- **Honest about sources.** Never invents a verse's wording or a pastor's view.
- **Spiritual encouragement, not therapy.** armor isn't counseling or medical
  advice and never presents itself as either. Anthropic's usage policy treats
  assessing or treating a mental health condition as high-risk, needing a
  licensed professional in the loop; armor points to real people instead.

## Self-contained

armor stands alone, in its own repository. It uses no other skill's files,
scripts or settings, never mentions another skill, and changes nothing outside
its own folder. The one exception is the permission a user grants in their own
Claude Code settings the first time it runs (see Speed).

## Where it runs

armor is a Claude plugin. The repository root holds `.claude-plugin/plugin.json`
and a `marketplace.json` (so it can be installed straight from the
repository), and the skill itself is `skills/armor/`. That one folder serves
every place:

- **Claude Code**, on a computer: installed as a plugin, or the skill folder
  linked into `~/.claude/skills/armor` while working on it.
- **The Claude app**, on the web and the phone: from Anthropic's directory once
  it is listed, or uploaded as a custom skill (`package.py` builds the ZIP).
  Anthropic's help center says custom skills work on every plan with code
  execution on, while directory plugins are for paid plans. Neither page
  mentions iOS or Android, so the phone is tested before relying on it.

The phone matters most: the hard moments are often late at night, away from
the computer. What that requires:

- Plain Agent Skills format: Python's standard library only, no network at
  runtime, no paths outside the skill folder, nothing tied to one operating
  system.
- One SKILL.md for every surface, using only the frontmatter keys the app
  accepts (`name`, `description`, `license`, `compatibility`, `metadata`,
  `allowed-tools`); any other key fails an upload.
- Claude Code and Cowork fill in the skill-folder placeholder
  (CLAUDE_SKILL_DIR) with the skill's folder; the app's chat doesn't, and copies the folder into its sandbox
  instead. SKILL.md has Claude tell which it is in from whether the path got
  filled in, and in chat find `verse.py` itself. (In the first app test Claude
  guessed `/mnt/skills/plugins/armor` and the step failed.) The placeholder
  appears only in commands, because Claude Code replaces every occurrence,
  prose included.
- The app's chat keeps nothing between chats; every chat starts with a fresh
  copy of the skill. The same signal tells Claude that setup's answers won't
  last, so it hands him one line, "armor settings: ...", in a copy box, to
  paste into Claude's Settings under "What personal preferences should Claude
  consider in responses?", which armor reads in every chat. (An earlier
  version marked the uploaded copy with a file; a plugin can't carry such a
  marker, so the placeholder became the one signal.) A man who runs setup in
  Claude Code and then builds his own ZIP carries his answers inside it, with
  nothing to paste.
- Settings live in the skill folder. `settings.example.yaml` holds the
  defaults; a user's own `settings.yaml`, written by setup, overrides it and is
  kept out of git, as are the profiles he adds in `my-pastors/`.
- Skills uploaded to the account also sync into Claude Code, as
  `anthropic-skills:armor`. On a computer where the repo is linked, typing
  `/armor` runs the linked copy.
- Every file stays under 256 KiB, the size above which the directory holds a
  file for a manual review, so the Bible is split into one file per book.

## Starting the skill

Only `/armor` starts it. Claude should never start it on its own, even when a
man mentions struggling in an unrelated conversation.

Claude Code's `disable-model-invocation` would make that a hard rule there,
but the app refuses that key, and a plugin uses one SKILL.md everywhere. So
the description does the job on every surface: use the skill only when a
message starts with `/armor`. That is strong guidance rather than a lock
(decided when armor became a plugin). In Claude Code a plugin's skill may show
as `/armor:armor`.

## Session flow

1. **Setup or check-in.** The first time a man types plain `/armor` (no
   settings of his own yet), setup comes first (see Setup questions), then
   the check-in; `/armor setup` runs it again anytime. A man who came with
   something hard is never made to wait on setup: armor helps first with the
   defaults and offers setup once at the end. The check-in itself is an open
   question first; the list is only a fallback.

   > What's going on?
   >
   > Or if it's easier, pick one:
   > - Getting tempted right now
   > - I messed up and I feel like garbage
   > - I'm down and can't shake it
   > - I'm angry, fed up
   > - Anxious about something
   > - I've been hurting myself, or thinking about it
   > - Nothing urgent, I just want some time in the Word

   If his `/armor` message already says what's going on, that answers the
   check-in: the menu isn't shown, and the follow-up still comes.
2. **One follow-up, always**, before the response, even when he asks for
   encouragement straight away; only Safety comes before it. (In the first app
   test the skill skipped it when he was tempted right now.) It is shaped by
   the moment (what happened, how long, what set it off). If he's tempted
   right now, that reply opens by telling him to get away from it first (close
   the tab or app, change rooms, lights on). It carries a short From the
   Pulpit, and the question comes last. If the settings say "depends on the
   day," it also asks whether he wants to be heard or helped.
3. **Response**, every time in the same three sections:
   - **Scripture**: the passage in the KJV, a plain "in today's words" line
     under it, and an NKJV link (see Sources).
   - **From the Pulpit**: what one of the pastors he approved taught on this
     struggle (see Sources). Every response includes it.
   - **Next step**: one thing to do in the next hour, not a program. It is
     something he can do alone (read a psalm aloud, pray, step outside).
     Reaching out to a person is offered as a suggestion, never assumed:
     many men have no one they can explain their situation to, and a step
     that needs a friend he doesn't have reads as one more failure. When it
     fits, offer low-barrier options instead (a pastor at a local church,
     even one he has never met; a men's group; a counselor).
   - **Want more?** End by offering to go deeper (another passage, more from
     the pastor, more to talk through) rather than front-loading it.
4. **Stay in the conversation** if he wants to keep talking; tone can be
   changed at any point ("be gentler", "be straight with me").

From the Pulpit is in every reply about what he's going through, not only
the full response: the follow-up question carries a short one, and the safety
replies carry a sentence or two (decided 2026-10-11: his pastors in every
reply, crisis included). In the safety replies what keeps him safe always
comes first, and the pastor follows, never in its place. Only setup and the
bare check-in, before he has said what's going on, go without it.

Length: about what the first dry run produced. Two short passages, each with
two or three sentences on why it applies; a paragraph from the pastor; one
next step; one gentle question. Anything beyond that waits for "want more?"

Moments map to response shapes. For example, "tempted right now" is short and
urgent, and getting away from it comes first, in the follow-up reply. "After a
fall" gives grace first, then the plan, if the settings ask for that order.

## Safety

The self-harm option, or any sign of it in free text ("giving up on life",
"done with everything", "no point anymore"), comes before everything else: a
direct, caring question about safety, and crisis resources for his region.

The safety step is still the skill speaking, not a hand-off. It carries one
short verse and a word of hope alongside the question, so a man who is hurting
does not feel turned away with only a phone number. The full three-section
response follows once he answers. (Found in the first dry run: a bare safety
check read as "the skill didn't trigger.")

Example:

> I'm really glad you said something. Feeling lost and like you don't belong
> anywhere is heavy, and you're not the first man of God to feel it. Elijah
> sat under a tree and asked God to take his life, and God didn't scold him.
> He fed him, let him sleep, and met him there (1 Kings 19).
>
> **From the Pulpit: Charles Spurgeon**
> Spurgeon knew this darkness himself and wrote about it openly. He taught
> that a heavy spirit is not proof that God has left you.
>
> **Psalm 34:18 (KJV)**: "The LORD is nigh unto them that are of a broken
> heart; and saveth such as be of a contrite spirit."
> *In today's words:* "The LORD is near to those who have a broken heart, and
> saves those who are crushed in spirit."
>
> Can I ask you something straight? When you say giving up on life, have you
> been thinking about ending it, or hurting yourself? If so, even a little,
> call or text 988 tonight. You'll get a real person. Either way, I'm here.
> What's been going on?

What happens next depends on his answer:

- **No.** Continue with the full response for the moment he is in.
- **Yes, or anything close to it.** Short replies, and stay with him. What
  keeps him safe comes first in each; a sentence or two From the Pulpit
  follows, never in its place:
  - Ask whether he is safe right now. If he is in immediate danger: 911, or
    the local emergency number.
  - Urge him to reach a person tonight (the crisis line below), and offer to
    stay in the conversation while he does.
  - Ask him to put distance between himself and anything he could use to hurt
    himself, and to let someone nearby know he is not okay.
  - No shame for having the thoughts. Elijah, Jonah and Job each asked God to
    let them die (1 Kings 19:4, Jonah 4:3, Job 6:8-9), and God met each of
    them there.
  - Never be the one to end the conversation.
- **Hurting himself without wanting to die** (cutting, hitting himself,
  reckless drinking or using): the same care, plus whether a wound needs
  medical attention.

Crisis lines, by the `crisis_region` setting: US and Canada, call or text 988;
UK and Ireland, Samaritans 116 123; Australia, Lifeline 13 11 14; anywhere
else, findahelpline.com.

The skill encourages real people (a pastor, a counselor, an accountability
brother) and never presents itself as a replacement for them.

## Privacy

What a man tells this skill is as private as anything he will ever type.

- The skill writes nothing about the conversation: no memory files, no notes,
  no commits. This overrides any standing instruction to save memory. Memory
  outlives the conversation and can travel further than he expects (a memory
  folder kept in git and pushed to a server, for one). The only things armor
  saves are setup's answers and a pastor profile he has approved.
- It never claims the conversation is unsaved. Claude Code keeps a local
  transcript of every session (under `~/.claude/projects/`), the app keeps
  its chat history, and messages go to Anthropic to be answered under the
  account's normal data settings. The skill says so plainly if asked.

## Speed

A man who is tempted right now cannot wait on a slow reply. The lookup itself
takes about 55 ms; what costs seconds is each tool round trip and each token
the model reads. So:

- Settings come with the first reply's lookup (`verse.py --settings`), once
  per conversation. A plain `/armor` needs that one quick call before the
  check-in, to know whether setup comes first.
- Every reference in a reply is looked up in one `verse.py` call: one tool
  call per reply outside setup, run as written, with nothing chained onto it.
  (In the first app test Claude built a long chained command to read files,
  which failed.) The reviewed pastor profiles (about 9 KB in all) come with
  the first lookup, because From the Pulpit is in every reply from the first
  one on; fetching a profile separately would add a round to the replies
  that can least afford it, the follow-up and the safety step.
- SKILL.md stays short; the pastor profiles live in separate files, returned
  only when needed.
- No permission prompt in a hard moment. In Claude Code, SKILL.md's
  `allowed-tools` covers only the turn that started the skill; the grant
  clears at his next message. So the README tells the user to answer the first
  prompt for `verse.py` with the option that stops Claude Code asking again.
  The app runs code without asking.

## Sources

### Scripture

- **KJV**, the only bundled translation. The NKJV, which the skill links every
  reference to, is a modernization of the KJV, so the two share the same Greek
  text and every verse sits in the same place. The WEB was the first choice
  and was dropped: it reads "Yahweh" for "the LORD", and its Majority Text
  base leaves out verses the NKJV has (Acts 8:37, the longer 1 John 5:7).
  Another public-domain translation can be added later; `translation` stays a
  setting.
- NKJV is copyrighted by Thomas Nelson, so it is linked rather than quoted:
  `https://www.biblegateway.com/passage/?search=<ref>&version=NKJV`.
- Every verse is looked up with `verse.py` before it is quoted. Never quote
  from model memory. If a lookup fails, give the reference and the NKJV link
  without quoted text rather than guess.

Each passage is shown as the exact KJV text, then a modern rendering right
below it, then the NKJV link:

> **Psalm 34:18 (KJV)**: "The LORD is nigh unto them that are of a broken
> heart; and saveth such as be of a contrite spirit."
> *In today's words:* "The LORD is near to those who have a broken heart, and
> saves those who are crushed in spirit."
> [Read in NKJV ↗](https://www.biblegateway.com/passage/?search=Psalm+34%3A18&version=NKJV)

The modern rendering is written by the model, so it is held to strict rules:

- Always labelled ("In today's words"), never presented as Scripture or as a
  translation. The KJV above it is the Word; the rendering only helps read it.
- Natural modern English: modern words, word order and sentences, the way a
  man would say it today. Swapping a few old words is not enough. The first
  app test rendered 1 Corinthians 10:13 as "who will not allow you to be
  tempted above what you are able", still the KJV's sentence; it should read
  like "he won't let you be tempted beyond what you can bear." Watch for words
  whose meaning has shifted: suffer (allow), let (hinder), prevent (go
  before), conversation (conduct), quick (living), meat (food), charity
  (love).
- Adds nothing, drops nothing, and does not interpret. Explaining what the
  verse means belongs in the reflection under it, not in the rendering.
- When unsure what a word means, keep the KJV word.

The NKJV link is there for a modern reading that is an actual translation.

#### Verses mentioned in passing

Outside the Scripture blocks (in the reflection, From the Pulpit, the next
step), verses are retold in today's words without quotation marks, and the
reference is an NKJV link:

> The people closest to him said he'd lost his mind
> ([Mark 3:21](https://www.biblegateway.com/passage/?search=Mark+3%3A21&version=NKJV)).

- Retold, not quoted: reported speech doesn't claim to be the exact words, and
  there is no archaic phrase to stop and translate mid-sentence. Exact KJV
  wording appears only in Scripture blocks.
- Still looked up first. Retelling from memory is how the first dry run said
  Jesus' *family* thought he'd lost his mind; the text says his friends (KJV)
  or his own people (NKJV). `verse.py` supplies both the text to retell and
  the link.
- When the exact words are the point (something worth memorizing), make it a
  full Scripture block instead of retelling it.

#### Psalm titles

116 psalms have a title ("A Prayer when he was in the cave"). In print it
stands above verse 1, unnumbered. The skill never quotes it as part of verse 1,
but may retell it as context, as the dry run did for Psalm 142. `verse.py`
returns it separately, so that retelling is looked up too.

#### The bundled text and the lookup

`skills/armor/bible/kjv/`: the 66 books, one file each (31,102 verses;
deuterocanon left out), public domain from eBible.org, rebuilt by `python3
tools/build_bible.py`. One verse per line; each psalm title on its own verse-0
line. The largest file, Psalms, is about 249 KiB. The build:

- strips the [brackets] marking translators' supplied words and the ¶
  paragraph marks (the supplied words stay);
- moves the psalm titles out of verse 1, where eBible.org's verse-per-line
  file puts them (Psalm 51:1 had read "To the chief Musician, ... Have mercy
  upon me"), using eBible.org's USFM edition to find where each title ends;
- checks the book list, the verse count, that all 116 titles were found, that
  no marks remain and that no file reaches 256 KiB, and replaces the text only
  if every check passes.

`verse.py "Psalm 34:18" "Heb 4:15-16"` prints one line of compact JSON: for
each reference, the verses with their numbers, the NKJV link, and the psalm
title when there is one. One bad reference is reported in `errors` (exit 1)
without losing the others. It reads only the books asked for. `python3
tests.py` checks the lookup, the bundled text, setup, the profiles, the ZIP,
and what the directory checks.

### From the Pulpit

- A summary of what a pastor teaches on the struggle, with his name and the
  Bible references he leans on. No sermon links and no web searching.
- In every reply about what he's going through: a paragraph in the full
  response, two or three sentences in the follow-up question, a sentence or
  two after the safety essentials in a safety reply. armor picks, from the
  pastors he approved, the one who speaks most to his struggle (each profile lists what he `speaks_to`); if
  none speaks to it directly, the one whose teaching comes closest, connected
  honestly. If none of his pastors has a profile it can use, it falls back to
  a reviewed starting pastor and tells him once that `/armor setup` lets him
  choose.
- Each pastor has a profile, `pastors/<name>.md`, holding what he is actually
  known for: recurring themes, the passages he leans on, his voice, and the
  struggles he speaks to most strongly.
- For this section the skill steps back from its own voice: it reads that
  pastor's profile and writes what he teaches in his spirit, in the third
  person ("Wilkerson taught that..."). Never first person; that would put
  words in a real man's mouth.
- Profiles are files, not separate agents. A subagent per pastor would start
  cold and take too long for someone who is tempted right now.
- Only teaching the pastor is actually known for. No made-up direct quotes.
- Two approvals stand between a profile and a reply:
  - The maintainer's: a profile ships with `reviewed: false` until someone
    has checked it against published sources, and `verse.py` never returns an
    unreviewed profile's text, so a draft can't reach a reply even by
    mistake.
  - The user's own: setup shows each pastor he picks, one at a time (who he
    is, what he's known for teaching, what he says to the struggles armor
    meets), and saves only the ones he approves. He needs at least one, since
    every response includes From the Pulpit; `verse.py --save-settings`
    refuses an empty list.
- Adding a pastor means adding a profile. In Claude Code, setup drafts one for
  a new name, shows it to him, and saves it in `my-pastors/` marked reviewed
  only once he approves. In the app nothing can be saved, so he adds the
  pastor from a computer.
- A passage is attributed to a pastor only when his profile lists it under
  passages he preached or wrote on, with how that's known. Where none is
  confirmed, the profile says so, and any passage armor pairs with his
  teaching is presented as armor's own choice.
- A profile records whether the pastor is still living, so the skill uses the
  right tense ("Wilkerson taught" against "Evans teaches").

Starting profiles (drafted and checked against published sources 2026-10-11,
reviewed the same day) and where each is strongest:

| Pastor | Speaks most to |
|---|---|
| Charles Spurgeon | Depression (wrote openly about his own), grace |
| Charles Stanley | Fear, trusting God in hard seasons |
| Voddie Baucham | Biblical manhood, responsibility |
| Tony Evans | Biblical manhood, spiritual warfare |
| John Ramirez | Spiritual warfare, deliverance |
| David Wilkerson | Purity, lust, the power of the cross |

## Configuration

Defaults in `settings.example.yaml`; a user's own `settings.yaml` in the
skill folder overrides them (see Where it runs). Setup writes it with
`verse.py --save-settings`, which refuses any answer outside the choices
below, so a slip in the conversation can't leave a broken file. The
defaults:

```yaml
translation: KJV            # the only bundled text for now
modern_rendering: true      # "in today's words" line under each quote
nkjv_link: true
tradition: Baptist          # e.g. Baptist, Reformed, Pentecostal, non-denominational
crisis_region: US           # US, CA, UK, IE, AU, or other
pastors:                    # at least one, each approved at setup
  - Charles Spurgeon
  - Charles Stanley
  - Voddie Baucham
  - Tony Evans
  - John Ramirez
  - David Wilkerson
tone:
  listen_or_act: ask        # listen | act | ask
  call_out: ask             # say | ask
  length: short             # short | long
  voice: friend-and-mentor  # friend | mentor | friend-and-mentor
  delivery: gentle          # gentle | straight
  after_a_fall: grace-first # grace-first | plan-first
```

### Setup questions

Setup asks these on the first run, or on `/armor setup`: tradition; pastors
(the reviewed starting profiles offered by name, others welcome, then each
chosen pastor's profile shown for approval, one at a time); the crisis-line
region; then the tone questions. Translation isn't asked while the KJV is the
only one bundled. Each tone question has one short line saying why it is
asked, so the user knows what they are choosing:

1. **When you're hurting, should I listen first, or jump to what to do?**
   Some guys need to get it out before they can hear anything.
2. **If I think you're making excuses, should I point it out, or ask you
   something so you see it yourself?**
   Excuses keep us stuck, so I won't ignore them. This is about how I bring it up.
3. **Short replies, or longer ones that explain more?**
   When things are hard, a long message can be too much.
4. **Should I sound like a friend in it with you, or more like an older mentor?**
   This changes how I talk, not what's true.
5. **When something hard needs saying, how should I say it: straight but kind,
   or gently and slowly?**
   I'll always be honest. This is only about how I say it.
6. **After you slip up, what do you need first: to know God hasn't given up on
   you, or a plan for next time?**
   You'll get both. This is just the order.

Honesty is not a setting; only delivery is. An earlier draft asked "Can I be
blunt with you?" and was dropped because bluntness is not the stance the skill
should take with a man who is struggling.

"Ask about it" combined with "gently" means soft, honest questions:
"What do you think was really going on when you picked up the phone?"

## Open

- **Listing in Anthropic's directory.** The plugin passes `claude plugin
  validate`. Next, in the developer portal (claude.ai/directory/manage): Submit
  new, Plugin bundle, this repository, Validate (it works while the repository
  is private, with the Claude GitHub App installed); answer the data-handling
  questions (armor stores no personal data beyond setup's answers, sends
  nothing to any other service, keeps nothing about conversations, and isn't
  meant for people under 18) and the compliance step; submit. (The repository
  is public, as the listing requires.) The name `armor` may be held as
  generic or found taken; the fallback is `armor-of-god`, settled before the
  first publish, since a plugin's name is permanent.
- **Settings after a plugin update.** A plugin installed in Claude Code is
  replaced when it updates, and settings saved in its folder may go with it;
  consider Claude Code's per-plugin data folder.
- **Voice.** For many men, hearing the Word and sermons helps more than
  reading it. Explore reading replies aloud in a way that also works on the
  phone; check first what the Claude app's own voice features already do.
- **Per-moment tone overrides**, e.g. firmer when tempted, gentler when down.
- **Testing.** Realistic scenarios (11pm and tempted, a heavy morning, after a
  fall) to check tone, accuracy and safety before sharing. First test,
  2026-10-11, in the app on a computer: `/armor` started the skill and the menu
  was skipped as designed; the folder guess, the skipped follow-up and the
  too-literal rendering were fixed afterwards. Setup then ran in the app and
  saved; pasting the settings line was the awkward part, so the tester's
  answers were built into his own ZIP. Still to test: the phone.
- **What `tradition` changes.** Nothing is defined yet. For a Baptist, one
  clear effect: a fall never puts his salvation in doubt (eternal security),
  which shapes every "after a fall" reply.
- **License.** MIT, chosen so anyone can reuse armor freely, accepting that
  others may also sell it or change it.

## Set aside

Considered and decided against, so they aren't proposed again:

- A fast path for "tempted right now" that skips the follow-up question.
- Asking the safety question a second time when it goes unanswered.
