# armor

A Claude skill for Christian men fighting lust, depression, frustration, fear
and self-destruction. It meets you in the moment you're in and answers with
Scripture, with what pastors you trust have taught, and with one next step you
can take tonight. Named for the armor of God (Ephesians 6:10-18).

> **Status: version 1, being tested.** Setup, the check-in, safety, Scripture,
> From the Pulpit and the next step are built. The six starting pastor
> profiles are drafted and waiting for review; From the Pulpit uses a pastor
> only once his profile is approved. [DESIGN.md](DESIGN.md) has every decision
> made so far.

## What a reply looks like

Every reply has the same parts:

- **Scripture.** The exact King James text, a plain "in today's words" line
  under it, and a link to the same passage in the NKJV:

  > **Psalm 34:18 (KJV)**: "The LORD is nigh unto them that are of a broken
  > heart; and saveth such as be of a contrite spirit."
  > *In today's words:* "The LORD is near to those who have a broken heart, and
  > saves those who are crushed in spirit."
  > [Read in NKJV ↗](https://www.biblegateway.com/passage/?search=Psalm+34%3A18&version=NKJV)

- **From the Pulpit.** What one of your pastors is known for teaching on
  what you're facing, in his spirit but never in his voice, and only from a
  profile you've approved.
- **Next step.** One thing to do in the next hour.

It never shames you, and it never quotes Scripture from memory: every verse
comes from the Bible text bundled with the skill.

## Try it

- `/armor` opens with "What's going on?" The first time, it asks a few setup
  questions first.
- `/armor I'm being tempted right now`
- `/armor I messed up again last night and I feel like garbage`
- `/armor I'm anxious about tomorrow and I can't sleep`
- `/armor setup` changes your answers: your pastors, your church tradition,
  your crisis line, and how armor talks to you.

## Install

### Claude Code

```sh
git clone https://github.com/David-Portillo/armor ~/.claude/skills/armor
```

Start a new Claude Code session and type `/armor`. The first time it looks up a
verse, Claude Code asks permission to run `verse.py`; choose the option that
stops it asking again, so a prompt never interrupts you in a hard moment.

### The Claude app (web, desktop and phone)

1. On a computer with a copy of this repo, build the upload:

   ```sh
   python3 package.py      # writes dist/armor.zip
   ```

2. In Claude, in a browser or the desktop app: make sure code execution is on
   (Settings, under Capabilities), then go to **Customize → Skills → + → Create
   skill → Upload a skill** and choose `dist/armor.zip`.
3. In any chat, including on your phone, type `/armor`.

Rebuild and upload again after any change. Anthropic's help pages don't yet
say whether custom skills work in the iOS and Android apps; we're testing that
now.

### Setup and settings

The first time you type `/armor`, it asks which pastors you trust, your church
tradition, where you live (for the right crisis line) and how it should talk to
you. In Claude Code it saves your answers to `settings.yaml`, and it can draft
a profile for a pastor who isn't in the starting six, for you to approve. Git
ignores your settings and your own profiles, so pulling updates never
overwrites them. `settings.example.yaml` holds the defaults.

The Claude app can't keep anything between chats. To take your answers to
your phone, run setup in Claude Code first, then build and upload the ZIP.
Without that, setup in the app gives you one line to paste into your Claude
profile preferences, where armor finds it in every chat.

## What armor does with what you tell it

armor sends nothing anywhere itself: it makes no network calls, and it
runs only `verse.py`, which reads the Bible text and the pastor profiles bundled
with it. The only things it saves are your setup answers and pastor profiles
you approve, in its own folder. It never writes anything about your
conversations, to memory or anywhere else. (`bible/build.py`, a maintainer
tool that is not part of the skill, downloads the KJV from eBible.org when the
bundled text is rebuilt.)

## If you're in crisis

armor points you to real people and is never a replacement for them. If you're
thinking about ending your life, reach someone tonight:

- US and Canada: call or text **988**
- UK and Ireland: Samaritans, **116 123**
- Australia: Lifeline, **13 11 14**
- Anywhere else: [findahelpline.com](https://findahelpline.com)

If you're in immediate danger, call your local emergency number.

## Sources and rights

- **King James Version.** The text is from [eBible.org](https://ebible.org)
  and is in the public domain in most of the world. In the United Kingdom the
  Authorized (King James) Version is under Crown copyright, administered by
  Cambridge University Press.
- **New King James Version.** © Thomas Nelson. armor links to it on
  BibleGateway and never quotes it.
- **Pastors.** armor summarizes, in its own words, what each pastor is
  publicly known to teach. It is not affiliated with or endorsed by any pastor
  or ministry it names.

## Development

```sh
python3 tests.py          # the lookup, the bundled text and the app package
python3 bible/build.py    # rebuild bible/kjv.txt from eBible.org
python3 verse.py "Psalm 34:18" "Heb 4:15-16"
python3 package.py        # build dist/armor.zip for the Claude app
```

## License

The skill is under the MIT License (see [LICENSE](LICENSE)). The Bible text
keeps the status described above.
