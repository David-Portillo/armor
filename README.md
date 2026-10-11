# armor

A Claude skill for Christian men fighting lust, depression, frustration, fear
and self-destruction. It meets you in the moment you're in and answers with
Scripture, with what pastors you trust have taught, and with one next step you
can take tonight. Named for the armor of God (Ephesians 6:10-18).

> **Status: version 1, being tested.** The check-in, safety, Scripture and the
> next step work. From the Pulpit (pastors' teaching) comes next, once each
> pastor's profile has been reviewed. [DESIGN.md](DESIGN.md) has every decision
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

- **From the Pulpit.** What a pastor from your list is known for teaching on
  what you're facing, in his spirit but never in his voice. *(Coming next.)*
- **Next step.** One thing to do in the next hour.

It never shames you, and it never quotes Scripture from memory: every verse
comes from the Bible text bundled with the skill.

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

### Settings

`settings.example.yaml` holds the defaults: tone, pastors, crisis line region.
To change them, copy it to `settings.yaml` and edit the copy. Git ignores
`settings.yaml`, so pulling updates never overwrites it. For the app, rebuild
and upload again.

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
