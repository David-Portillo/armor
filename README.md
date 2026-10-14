# armor

A Claude skill for Christian men fighting lust, depression, frustration, fear
and self-destruction. It meets you in the moment you're in and answers with
Scripture, with what pastors you trust have taught, and with one next step you
can take tonight. Named for the armor of God (Ephesians 6:10-18).

armor offers spiritual encouragement. It isn't therapy, counseling or medical
advice, and it always points you to real people for those.

> **Status: version 1, being tested.** [DESIGN.md](DESIGN.md) has every
> decision made so far.

## What a reply looks like

Every reply has the same parts:

- **Scripture.** Each verse in plain words, the way you'd say it today, made
  from the King James text, with a link to the same passage in the NKJV:

  > **Psalm 34:18**
  > *In today's words:* "The LORD is near to those who have a broken heart, and
  > saves those who are crushed in spirit."
  > [Read in NKJV ↗](https://www.biblegateway.com/passage/?search=Psalm+34%3A18&version=NKJV)

- **From the Pulpit.** What each of your pastors is known for teaching on what
  you're facing, every one whose teaching applies, in his spirit but never in
  his voice, drawn only from profiles you approved. If you choose no pastors,
  replies go without it.
- **Next step.** One thing to do in the next hour.

It never shames you, and it never works from memory: every verse is looked up
in the King James text bundled with the skill, and today's words are made from
that text.

## Try it

- `/armor setup` is the place to start: nine quick questions, one at a time.
  The first time you use armor, it starts with setup whatever you type.
- `/armor` opens with "What's going on?"
- `/armor I'm being tempted right now`
- `/armor I messed up again last night and I feel like garbage`
- `/armor I'm anxious about tomorrow and I can't sleep`
- `/armor setup` again any time changes your answers: your pastors, your
  church tradition, your crisis line, and how armor talks to you.

## Setup

The first time you type `/armor`, it asks:

- your church tradition;
- which pastors you trust. It offers six to start (Charles Spurgeon, Charles
  Stanley, Voddie Baucham, Tony Evans, John Ramirez and David Wilkerson),
  shows you each one's profile, and uses only the ones you approve. Name a
  pastor who isn't on the list, and it writes his profile on the spot for you
  to approve the same way, then saves it (in the Claude app, inside your
  settings line);
- whether From the Pulpit gives every one of your pastors whose teaching
  fits, or just the one who fits best;
- where you live, for the right crisis line;
- six short questions on how it should talk to you.

If your first message is about something hard, it helps you first and offers
setup at the end.

## Install

### Claude Code

```sh
/plugin install armor --marketplace David-Portillo/armor
```

Then type `/armor` (as a plugin skill it may show as `/armor:armor`). The
first time it looks up a verse, Claude Code asks permission to run `verse.py`;
choose the option that stops it asking again, so a prompt never interrupts you
in a hard moment.

To work on armor itself, clone the repository and link the skill folder:

```sh
git clone https://github.com/David-Portillo/armor ~/armor
ln -s ~/armor/skills/armor ~/.claude/skills/armor
```

Your answers from setup are saved in `skills/armor/settings.yaml`, and the
profiles you add in `skills/armor/my-pastors/`. Git ignores both, so pulling
updates never overwrites them.

### The Claude app (web, desktop and phone)

1. On a computer with a copy of this repository, build the upload:

   ```sh
   python3 package.py      # writes dist/armor.zip
   ```

2. In Claude, in a browser or the desktop app: make sure code execution is on
   (Settings, under Capabilities), then go to **Customize → Skills → + → Create
   skill → Upload a skill** and choose `dist/armor.zip`.
3. In any chat, including on your phone, type `/armor`.

The app keeps nothing between chats, so there are two ways to keep your setup
answers:

- Run setup in Claude Code first; the ZIP then carries your answers and
  profiles, with nothing to paste.
- Or run setup in the app. It ends with one line in a copy box; paste it into
  Claude's Settings, in the box "What personal preferences should Claude
  consider in responses?", and every new chat picks it up.

Rebuild and upload again after any change.

## What armor does with what you tell it

armor sends nothing anywhere itself: it makes no network calls, and the only
program it runs is `verse.py`, which reads the Bible text and the pastor
profiles bundled with it. The only things it saves are your setup answers and
the pastor profiles you approve, in its own folder. It never writes anything
about your conversations, to memory or anywhere else. (`tools/build_bible.py`,
a maintainer tool that isn't part of the skill, downloads the KJV from
eBible.org when the bundled text is rebuilt.)

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

## Support

Questions, corrections to a pastor's profile, or problems:
[open an issue](https://github.com/David-Portillo/armor/issues).

## Development

```sh
python3 tests.py                  # lookup, Bible text, setup, profiles, package, directory checks
python3 tools/build_bible.py      # rebuild skills/armor/bible/kjv/ from eBible.org
python3 skills/armor/verse.py "Psalm 34:18" "Heb 4:15-16"
python3 package.py                # build dist/armor.zip for the Claude app
claude plugin validate .          # check the plugin and marketplace manifests
```

The plugin is the repository root: `.claude-plugin/` holds the manifest and
the marketplace file, and `skills/armor/` is the skill itself.

## License

The skill is under the MIT License (see [LICENSE](LICENSE)). The Bible text
keeps the status described above.
