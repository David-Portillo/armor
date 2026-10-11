#!/usr/bin/env python3
"""Verse lookup for the /armor skill.

The skill must never quote Scripture from model memory: a misplaced word in a
verse read by a man who is struggling undermines everything else it says. Every
quote, and every verse retold in passing, goes through this script. It reads
the bundled public-domain text in bible/<translation>/<BOOK>.txt: one file per
book, one verse per line ("PSA 51:1 text"), with each psalm title on its own
verse-0 line (see tools/build_bible.py in the repository).

    verse.py "Psalm 34:18" "Heb 4:15-16" "1 John 1:9" "Romans 8:28,38-39" "Psalm 23"
    verse.py --settings "Psalm 34:18"      # first reply: settings too
    verse.py --settings                    # settings alone
    verse.py --pastor "Charles Spurgeon" "Psalm 42:11"
    verse.py --pastor "Charles Spurgeon" --pastor "David Wilkerson"   # setup
    verse.py --save-settings '{"tradition": "Baptist", ...}'

Pass every reference a reply needs in one call. Each call is a tool round trip
for the skill, which costs far more time than the lookup itself. The other
options ride along on that same call, so the skill never has to read files or
work out where its folder is. (In the Claude app it guessed wrong once and the
whole step failed.)

--settings adds the user's settings (settings.yaml, else the defaults in
settings.example.yaml) as "settings_file" and "settings"; "first_run", true
until setup has saved a settings.yaml; and "profiles", every pastor profile
with its name, tense and whether it has been reviewed, plus the text of each
reviewed one. From the Pulpit is in every reply from the first one on, so the
profiles come with that first lookup instead of costing another round.

--pastor adds pastors' profiles as "pastors"; repeat it for several, as setup
does when it shows each chosen pastor's profile for the user's approval. Only
a profile marked reviewed is returned: From the Pulpit says what a real man
taught, so no draft reaches it.

--save-settings checks the answers from setup and writes settings.yaml. It
also prints them as one "line". In the Claude app's chat every conversation
gets a fresh copy of the skill, so a saved file doesn't last; SKILL.md tells
Claude how to recognize that and hand the line to the user for their Claude
profile preferences instead. This script can't tell where it is running.

Prints one line of JSON:

    {"translation": "KJV", "errors": [],
     "results": [{"ref": "Psalm 51:1-2", "nkjv_url": "https://...",
                  "titles": {"51": "To the chief Musician, ..."},
                  "verses": [["51:1", "Have mercy upon me, O God, ..."], ...]}]}

"titles" appears only for psalms that have one. It is the heading above the
psalm, never part of verse 1, but it is good context to retell (Psalm 142 was
prayed "in the cave"). The NKJV is copyrighted, so it is linked, not quoted.

Exits 1 if any reference could not be resolved. The other results are still
good; for the failed one the skill gives the reference and link without
quoting text.
"""
import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (code in the text file, display name, extra aliases). The display name and
# the code are always accepted too, and ordinals are normalized before lookup
# ("First John", "1st John", "I John" all become "1John"). Anything else falls
# back to an unambiguous prefix match.
BOOKS = [
    ("GEN", "Genesis", ["gn"]),
    ("EXO", "Exodus", ["ex", "exod"]),
    ("LEV", "Leviticus", ["lv"]),
    ("NUM", "Numbers", ["nm", "nb"]),
    ("DEU", "Deuteronomy", ["dt", "deut"]),
    ("JOS", "Joshua", ["josh", "jsh"]),
    ("JDG", "Judges", ["judg", "jdgs", "jg"]),
    ("RUT", "Ruth", ["rth", "ru"]),
    ("1SA", "1 Samuel", ["1sam", "1sm"]),
    ("2SA", "2 Samuel", ["2sam", "2sm"]),
    ("1KI", "1 Kings", ["1kgs", "1kg"]),
    ("2KI", "2 Kings", ["2kgs", "2kg"]),
    ("1CH", "1 Chronicles", ["1chr", "1chron"]),
    ("2CH", "2 Chronicles", ["2chr", "2chron"]),
    ("EZR", "Ezra", []),
    ("NEH", "Nehemiah", []),
    ("EST", "Esther", ["esth"]),
    ("JOB", "Job", ["jb"]),
    ("PSA", "Psalms", ["ps", "psalm", "pss", "psm"]),
    ("PRO", "Proverbs", ["prov", "prv", "pr"]),
    ("ECC", "Ecclesiastes", ["eccl", "eccles", "qoh"]),
    ("SOL", "Song of Solomon", ["song", "songs", "songofsongs", "sos", "canticles"]),
    ("ISA", "Isaiah", ["is"]),
    ("JER", "Jeremiah", ["jr"]),
    ("LAM", "Lamentations", []),
    ("EZE", "Ezekiel", ["ezek", "ezk"]),
    ("DAN", "Daniel", ["dn"]),
    ("HOS", "Hosea", []),
    ("JOE", "Joel", ["jl"]),
    ("AMO", "Amos", []),
    ("OBA", "Obadiah", ["obad"]),
    ("JON", "Jonah", ["jnh"]),
    ("MIC", "Micah", []),
    ("NAH", "Nahum", []),
    ("HAB", "Habakkuk", []),
    ("ZEP", "Zephaniah", ["zeph"]),
    ("HAG", "Haggai", []),
    ("ZEC", "Zechariah", ["zech"]),
    ("MAL", "Malachi", []),
    ("MAT", "Matthew", ["mt", "matt"]),
    ("MAR", "Mark", ["mk", "mrk"]),
    ("LUK", "Luke", ["lk"]),
    ("JOH", "John", ["jn", "jhn"]),
    ("ACT", "Acts", []),
    ("ROM", "Romans", ["rm"]),
    ("1CO", "1 Corinthians", ["1cor"]),
    ("2CO", "2 Corinthians", ["2cor"]),
    ("GAL", "Galatians", []),
    ("EPH", "Ephesians", []),
    ("PHI", "Philippians", ["phil", "php", "pp", "phillipians", "philipians"]),
    ("COL", "Colossians", []),
    ("1TH", "1 Thessalonians", ["1thess"]),
    ("2TH", "2 Thessalonians", ["2thess"]),
    ("1TI", "1 Timothy", ["1tim"]),
    ("2TI", "2 Timothy", ["2tim"]),
    ("TIT", "Titus", []),
    ("PHM", "Philemon", ["phlm", "philem"]),
    ("HEB", "Hebrews", []),
    ("JAM", "James", ["jas", "jm"]),
    ("1PE", "1 Peter", ["1pet", "1pt"]),
    ("2PE", "2 Peter", ["2pet", "2pt"]),
    ("1JO", "1 John", ["1jn", "1jhn"]),
    ("2JO", "2 John", ["2jn", "2jhn"]),
    ("3JO", "3 John", ["3jn", "3jhn"]),
    ("JUD", "Jude", ["jd"]),
    ("REV", "Revelation", ["rv", "revelations", "apocalypse"]),
]
DISPLAY = {code: name for code, name, _ in BOOKS}
SINGLE_CHAPTER = {"OBA", "PHM", "2JO", "3JO", "JUD"}

ORDINALS = {"1st": "1", "first": "1", "i": "1",
            "2nd": "2", "second": "2", "ii": "2",
            "3rd": "3", "third": "3", "iii": "3"}
ORDINAL = re.compile(r"^\s*(1st|first|iii|ii|i|2nd|second|3rd|third)\s+", re.I)


def norm(s):
    return re.sub(r"[\s.]", "", s.lower())


ALIASES = {norm(a): code for code, name, extra in BOOKS for a in [code, name, *extra]}


def find_book(raw):
    key = norm(ORDINAL.sub(lambda m: ORDINALS[m[1].lower()], raw))
    if key in ALIASES:
        return ALIASES[key]
    # "Phi" alone could mean Philippians or Philemon, so a prefix only counts
    # when it points at exactly one book.
    hits = {code for alias, code in ALIASES.items() if alias.startswith(key)}
    return hits.pop() if len(hits) == 1 else None


# Book, chapter, then an optional verse spec: "34", "34:18", "34:18-20",
# "8:28,38-39", "34:18-35:2". The book may start with a digit or an ordinal.
# Sermon-style partial verses ("5:16b") are read as the whole verse.
REF = re.compile(r"^\s*(\d?\s*[A-Za-z][A-Za-z .]*?)\s*(\d+)(?::([\d,\-\s:abc]+))?\s*$")
BARE = re.compile(r"^\s*(\d?\s*[A-Za-z][A-Za-z .]*?)\s*(\d[\d,\-\sabc]*)$")


def parse(ref):
    """Reference text -> (code, chapter, spec or None). No Bible text needed,
    so every book can be known before the file is read."""
    ref = ref.replace("–", "-").replace("—", "-")
    # One-chapter books are cited without a chapter ("Jude 24-25"), so there
    # the numbers are verses: rewrite to "Jude 1:24-25" before parsing.
    bare = BARE.match(ref)
    if bare and ":" not in ref and find_book(bare[1]) in SINGLE_CHAPTER:
        ref = f"{bare[1]} 1:{bare[2]}"
    m = REF.match(ref)
    if not m:
        raise ValueError(f"could not read reference '{ref}'")
    code = find_book(m[1])
    if not code:
        raise ValueError(f"unknown or ambiguous book in '{ref}'")
    spec = re.sub(r"[abc\s]", "", m[3]) if m[3] else None
    return code, int(m[2]), spec


BOOK_ORDER = {code: i for i, (code, _, _) in enumerate(BOOKS)}


def load(translation, codes):
    """Read only the books asked about: one small file each."""
    verses, titles, order = {}, {}, []
    for book in sorted(codes, key=BOOK_ORDER.get):
        with open(HERE / "bible" / translation / f"{book}.txt", encoding="utf-8") as f:
            lines = f.read().splitlines()
        for line in lines:
            code, cv, text = line.split(" ", 2)
            c, v = map(int, cv.split(":"))
            if v == 0:
                titles[(code, c)] = text
            else:
                verses[(code, c, v)] = text
                order.append((code, c, v))
    return verses, titles, order


def resolve(code, chapter, spec, verses, titles, order, pos):
    name = "Psalm" if code == "PSA" else DISPLAY[code]
    display = f"{name} {chapter}" + (f":{spec}" if spec else "")
    if (code, chapter, 1) not in verses:
        raise ValueError(f"{name} has no chapter {chapter}")

    keys = []
    if spec is None:  # whole chapter
        keys = [k for k in order if k[0] == code and k[1] == chapter]
    else:
        for part in filter(None, spec.split(",")):
            start, _, end = part.partition("-")
            if not start.isdigit():
                raise ValueError(f"could not read verse part '{part}' in '{display}'")
            if ":" in end:  # crosses into a later chapter: walk the file order
                c, v = end.split(":", 1)
                first, last = (code, chapter, int(start)), (code, int(c), int(v))
                if first not in pos or last not in pos:
                    raise ValueError(f"'{display}' points past the end of a chapter")
                if pos[last] < pos[first]:
                    raise ValueError(f"backwards range in '{display}'")
                keys += order[pos[first]: pos[last] + 1]
                continue
            lo, hi = int(start), int(end or start)
            if hi < lo:
                raise ValueError(f"backwards range in '{display}'")
            for v in range(lo, hi + 1):
                if (code, chapter, v) not in verses:
                    raise ValueError(f"'{display}' points past the end of the chapter")
                keys.append((code, chapter, v))

    result = {
        "ref": display,
        "nkjv_url": "https://www.biblegateway.com/passage/?"
        + urllib.parse.urlencode({"search": display, "version": "NKJV"}),
    }
    heads = {str(c): titles[(code, c)] for c in dict.fromkeys(k[1] for k in keys) if (code, c) in titles}
    if heads:
        result["titles"] = heads
    result["verses"] = [[f"{k[1]}:{k[2]}", verses[k]] for k in keys]
    return result


# Bundled profiles, then the ones a user adds for pastors of their own.
PASTOR_DIRS = ("pastors", "my-pastors")

# The choices setup offers; anything else is refused before it is saved.
REGIONS = ("US", "CA", "UK", "IE", "AU", "other")
TONE = {
    "listen_or_act": ("listen", "act", "ask"),
    "call_out": ("say", "ask"),
    "length": ("short", "long"),
    "voice": ("friend", "mentor", "friend-and-mentor"),
    "delivery": ("gentle", "straight"),
    "after_a_fall": ("grace-first", "plan-first"),
}


def split_frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m[1].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    return meta, text[m.end():]


def profiles():
    """Bundled profiles, then the user's own. A profile of his with the same
    name as a bundled one replaces it: that is how setup keeps his correction
    when he says a starting profile has something wrong."""
    found = {}
    for folder in PASTOR_DIRS:
        d = HERE / folder
        for f in sorted(d.glob("*.md")) if d.is_dir() else []:
            meta, body = split_frontmatter(f.read_text(encoding="utf-8"))
            name = meta.get("name", f.stem)
            found[re.sub(r"[^a-z ]", "", name.lower()).strip()] = {
                "name": name, "living": meta.get("living") == "true",
                "reviewed": meta.get("reviewed") == "true", "speaks_to": meta.get("speaks_to", ""),
                "body": body.strip()}
    return list(found.values())


def find_pastor(name):
    """Match a full name, or any unique part of one ("Spurgeon")."""
    want = re.sub(r"[^a-z ]", "", name.lower()).strip()
    every = profiles()
    exact = [p for p in every if re.sub(r"[^a-z ]", "", p["name"].lower()) == want]
    if exact:
        return exact[0]
    partial = [p for p in every if want and want in re.sub(r"[^a-z ]", "", p["name"].lower())]
    if len(partial) == 1:
        return partial[0]
    raise ValueError(f"no single pastor profile matches '{name}'")


def save_settings(raw):
    try:
        s = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"--save-settings needs JSON: {e}")
    if not isinstance(s, dict):
        raise ValueError("--save-settings needs a JSON object")
    tradition, region, pastors, tone = s.get("tradition"), s.get("crisis_region"), s.get("pastors"), s.get("tone")
    problems = []
    if not isinstance(tradition, str) or not tradition.strip():
        problems.append("tradition must be a name")
    if region not in REGIONS:
        problems.append(f"crisis_region must be one of {', '.join(REGIONS)}")
    # Every response includes From the Pulpit, which needs at least one pastor.
    if not isinstance(pastors, list) or not pastors or not all(isinstance(n, str) and n.strip() for n in pastors):
        problems.append("pastors must list at least one name")
    if not isinstance(tone, dict):
        tone = {}
    for key, choices in TONE.items():
        if tone.get(key) not in choices:
            problems.append(f"tone.{key} must be one of {', '.join(choices)}")
    if problems:
        raise ValueError("; ".join(problems))

    names = [n.strip() for n in pastors]
    text = "\n".join([
        "# Saved by armor's setup. Run /armor setup to change it, or edit it by hand.",
        "translation: KJV",
        "modern_rendering: true",
        "nkjv_link: true",
        f"tradition: {json.dumps(tradition.strip(), ensure_ascii=False)}",
        f"crisis_region: {region}",
        "pastors:",
        *[f"  - {json.dumps(n, ensure_ascii=False)}" for n in names],
        "tone:",
        *[f"  {key}: {tone[key]}" for key in TONE],
    ]) + "\n"
    (HERE / "settings.yaml").write_text(text, encoding="utf-8")
    line = (f"armor settings: tradition {tradition.strip()}; crisis line {region}; "
            f"pastors {', '.join(names)}; " + "; ".join(f"{k} {tone[k]}" for k in TONE))
    return {"saved": "settings.yaml", "line": line}


def main():
    p = argparse.ArgumentParser(description="Look up verses in the bundled Bible text.")
    p.add_argument("refs", nargs="*", help='e.g. "Psalm 34:18" "Heb 4:15-16"')
    p.add_argument("--settings", action="store_true",
                   help="also return the settings, first_run and the pastor profiles")
    p.add_argument("--pastor", metavar="NAME", action="append",
                   help="also return this pastor's reviewed profile; repeat for several")
    p.add_argument("--save-settings", metavar="JSON", help="save the answers from setup to settings.yaml")
    p.add_argument("--translation", default="kjv", help="bundled text to read (default: kjv)")
    args = p.parse_args()

    if args.save_settings is not None:
        try:
            print(json.dumps(save_settings(args.save_settings), ensure_ascii=False))
        except ValueError as e:
            print(json.dumps({"errors": [str(e)]}, ensure_ascii=False))
            sys.exit(1)
        return
    if not args.refs and not args.settings and not args.pastor:
        p.error("give at least one reference, --settings or --pastor")
    out = {"translation": args.translation.upper(), "results": [], "errors": []}

    if args.settings:
        for name in ("settings.yaml", "settings.example.yaml"):
            if (HERE / name).exists():
                out["settings_file"] = name
                out["settings"] = (HERE / name).read_text(encoding="utf-8")
                break
        else:
            out["errors"].append("no settings.yaml or settings.example.yaml next to verse.py")
        out["first_run"] = not (HERE / "settings.yaml").exists()
        # A draft's text stays out, so From the Pulpit can't use it.
        out["profiles"] = [{**{k: v for k, v in pr.items() if k != "body"},
                            **({"profile": pr["body"]} if pr["reviewed"] else {})} for pr in profiles()]

    if args.pastor:
        out["pastors"] = []
        for name in args.pastor:
            try:
                pr = find_pastor(name)
                if not pr["reviewed"]:
                    raise ValueError(f"{pr['name']}'s profile hasn't been reviewed yet, so From the Pulpit can't use it")
                out["pastors"].append({"name": pr["name"], "living": pr["living"], "profile": pr["body"]})
            except ValueError as e:
                out["errors"].append(str(e))

    # The translation name becomes a file path, so it may only name a file
    # in bible/.
    if not re.fullmatch(r"[a-z0-9-]+", args.translation) or \
            not (HERE / "bible" / args.translation).is_dir():
        out["errors"].append(f"no bundled text for translation '{args.translation}'")
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(1)

    parsed = []
    for ref in args.refs:
        try:
            parsed.append(parse(ref))
        except ValueError as e:
            out["errors"].append(str(e))

    verses, titles, order = load(args.translation, {code for code, _, _ in parsed}) if parsed else ({}, {}, [])
    pos = {k: i for i, k in enumerate(order)}
    for code, chapter, spec in parsed:
        try:
            out["results"].append(resolve(code, chapter, spec, verses, titles, order, pos))
        except ValueError as e:
            out["errors"].append(str(e))

    print(json.dumps(out, ensure_ascii=False))
    sys.exit(1 if out["errors"] else 0)


if __name__ == "__main__":
    main()
