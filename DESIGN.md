# armor — design

A Claude skill for Christian men fighting lust, depression, frustration, fear
and self-destruction. It meets a man in the moment he is in, answers with
Scripture and with the teaching of pastors he trusts, and points him to one
next step. It runs in Claude Code and in the Claude app, including on a phone.

Named for Ephesians 6:10-18, the armor of God.

Status: version 1 built and being tested: SKILL.md (check-in, safety,
Scripture, next step), the verse lookup and the packaging for the app. Not
built yet: the pastor profiles (From the Pulpit) and the first-run setup. Not
yet tried on a phone.

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

## Self-contained

armor stands alone, in its own repository. It uses no other skill's files,
scripts or settings, never mentions another skill, and changes nothing outside
its own folder. The one exception is the permission a user grants in their own
Claude Code settings the first time it runs (see Speed).

## Where it runs

The same folder serves two places:

- **Claude Code**, on a computer: linked into `~/.claude/skills/armor`.
- **The Claude app**, on the web and the phone: uploaded as a custom skill, a
  ZIP of the folder added under Customize > Skills. Anthropic's help center
  says custom skills work on every plan, Free included, with code execution
  turned on. It doesn't mention iOS or Android, so the first upload is tested
  on the phone before relying on it.

The phone matters most: the hard moments are often late at night, away from
the computer. What that requires:

- Plain Agent Skills format: Python's standard library only, no network at
  runtime, no paths outside the folder, nothing tied to one operating system.
  The Bible text and lookup zip to 1.33 MB.
- The app accepts only `name`, `description`, `license`, `compatibility`,
  `metadata` and `allowed-tools` in SKILL.md's frontmatter; any other key
  fails the upload. Claude Code-only features (such as
  `disable-model-invocation`, `${CLAUDE_SKILL_DIR}` and `!` command blocks)
  therefore stay out of the app copy. `package.py` builds the app ZIP
  (`dist/armor.zip`) from this folder: it strips those, leaves out the
  development files (DESIGN.md, README, tests, the build scripts), and keeps
  the user's settings.
- The app doesn't tell Claude where the skill's folder is. In the first test
  it guessed `/mnt/skills/plugins/armor`, failed, and had to search before it
  could answer. So nothing depends on knowing the folder: in the app copy each
  `verse.py` command finds the script itself (under `/mnt`, or under
  `~/.claude/skills` for synced copies), and `verse.py --settings` returns the
  settings.
- Skills uploaded to the account also sync into Claude Code, as
  `anthropic-skills:armor` under `~/.claude/skills/synced/`. On a computer
  where the repo is linked, typing `/armor` runs the linked copy.
- Settings live in the skill folder, because an uploaded skill has no home
  directory to save to. `settings.example.yaml` holds the defaults; a user's
  own `settings.yaml` overrides it and is kept out of git. After a change the
  ZIP is rebuilt and uploaded again.

## Starting the skill

Only `/armor` starts it. Claude never starts it on its own, even when a man
mentions struggling in an unrelated conversation.

- Claude Code: `disable-model-invocation: true`, so Claude never loads the
  skill by itself, and typing `/armor` does.
- The app doesn't accept that setting, and there Claude picks skills from
  their descriptions. So the description itself says to use the skill only
  when a message starts with `/armor`. That is strong guidance rather than a
  lock; test it on the phone.

## Session flow

1. **Check-in.** Open question first; the list is only a fallback.

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
   the tab or app, change rooms, lights on), then asks. If the settings say
   "depends on the day," it also asks whether he wants to be heard or helped.
3. **Response** in clearly separated sections:
   - **Scripture**: the passage in the KJV, a plain "in today's words" line
     under it, and an NKJV link (see Sources).
   - **From the Pulpit**: what a pastor from the configured list teaches on
     this struggle (see Sources). Comes once the profiles are reviewed;
     version 1 leaves it out.
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

Length: about what the first dry run produced. Two short passages, each with
two or three sentences on why it applies; a paragraph from the pastor; one
next step; one gentle question. Anything beyond that waits for "want more?"

Moments map to response shapes. For example, "tempted right now" is short and
urgent, and getting away from it comes first, in the follow-up reply. "After a
fall" gives
grace first, then the plan, if the settings ask for that order.

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
- **Yes, or anything close to it.** No devotional. Short replies, and stay
  with him:
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
  folder kept in git and pushed to a server, for one).
- It never claims the conversation is unsaved. Claude Code keeps a local
  transcript of every session (under `~/.claude/projects/`), the app keeps
  its chat history, and messages go to Anthropic to be answered under the
  account's normal data settings. The skill says so plainly if asked.

## Speed

A man who is tempted right now cannot wait on a slow reply. The lookup itself
takes about 55 ms; what costs seconds is each tool round trip and each token
the model reads. So:

- The check-in needs no tool calls.
- Settings come with the first lookup (`verse.py --settings`), once per
  conversation.
- Every reference in a reply is looked up in one `verse.py` call: one tool
  call per reply, run as written, with nothing chained onto it. (In the first
  app test Claude built a long chained command to read files, which failed.)
  When From the Pulpit is built, the chosen pastor's profile should come
  through the same call.
- SKILL.md stays short. Setup, the moment guide and the pastor profiles live
  in separate files, read only when needed.
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

`bible/kjv.txt`: the 66 books (31,102 verses; deuterocanon left out), public
domain from eBible.org, rebuilt by `python3 bible/build.py`. One verse per
line; each psalm title on its own verse-0 line. The build:

- strips the [brackets] marking translators' supplied words and the ¶
  paragraph marks (the supplied words stay);
- moves the psalm titles out of verse 1, where eBible.org's verse-per-line
  file puts them (Psalm 51:1 had read "To the chief Musician, ... Have mercy
  upon me"), using eBible.org's USFM edition to find where each title ends;
- checks the book list, the verse count, that all 116 titles were found, and
  that no marks remain, and replaces the file only if every check passes.

`verse.py "Psalm 34:18" "Heb 4:15-16"` prints one line of compact JSON: for
each reference, the verses with their numbers, the NKJV link, and the psalm
title when there is one. One bad reference is reported in `errors` (exit 1)
without losing the others. It reads only the books asked for. `python3
tests.py` checks the lookup, the bundled text and the app package.

### From the Pulpit

- A summary of what a pastor teaches on the struggle, with his name and the
  Bible references he leans on. No sermon links and no web searching.
- Each pastor has a profile, `pastors/<name>.md`, holding what he is actually
  known for: recurring themes, the passages he leans on, his voice, and the
  struggles he speaks to most strongly.
- For this section the skill steps back from its own voice: it picks the
  pastor whose profile best fits the struggle, reads that profile, and writes
  what he teaches in his spirit, in the third person ("Wilkerson taught
  that..."). Never first person; that would put words in a real man's mouth.
- Profiles are files, not separate agents. A subagent per pastor would start
  cold and take too long for someone who is tempted right now.
- Only teaching the pastor is actually known for. If no profile fits, or the
  model is not confident about a view, it picks another pastor rather than
  inventing one. No made-up direct quotes.
- Adding a pastor means adding a profile. Setup can draft one for a new name;
  the user reviews it before it is used.
- A profile records whether the pastor is still living, so the skill uses the
  right tense ("Wilkerson taught" against "Evans teaches").

Starting profiles and where each is strongest:

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
skill folder overrides them (see Where it runs). Until the first-run setup is
built, a user copies the example and edits it. The defaults:

```yaml
translation: KJV            # the only bundled text for now
modern_rendering: true      # "in today's words" line under each quote
nkjv_link: true
tradition: Baptist          # e.g. Baptist, Reformed, Pentecostal, non-denominational
crisis_region: US           # US, CA, UK, IE, AU, or other
pastors:                    # each needs a profile in pastors/
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

Tradition, translation, pastors, then the tone questions. Each question has
one short line saying why it is asked, so the user knows what they are
choosing:

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

- **Voice.** For many men, hearing the Word and sermons helps more than
  reading it. Explore reading replies aloud in a way that also works on the
  phone; check first what the Claude app's own voice features already do.
- **Per-moment tone overrides**, e.g. firmer when tempted, gentler when down.
- **Testing.** Realistic scenarios (11pm and tempted, a heavy morning, after a
  fall) to check tone, accuracy and safety before sharing. First test,
  2026-10-11, in the app on a computer: `/armor` started the skill and the menu
  was skipped as designed; the folder guess, the skipped follow-up and the
  too-literal rendering were fixed afterwards. Still to test: the phone.
- **What `tradition` changes.** Nothing is defined yet. For a Baptist, one
  clear effect: a fall never puts his salvation in doubt (eternal security),
  which shapes every "after a fall" reply.
- **Pastor profiles.** Draft the six starting profiles for review, then put
  From the Pulpit back into SKILL.md.
- **First-run setup.** Ask the setup questions and write `settings.yaml`.
- **Going public.** The repo stays private until version 1 has been tested on
  a phone. The license is MIT, chosen so anyone can reuse armor freely,
  accepting that others may also sell it or change it.

## Set aside

Considered and decided against, so they aren't proposed again:

- A fast path for "tempted right now" that skips the follow-up question.
- Asking the safety question a second time when it goes unanswered.
