#!/usr/bin/env python3
"""Rebuild bible/kjv.txt from eBible.org's King James Version (public domain).

    python3 bible/build.py

The skill quotes verses only from this file, never from model memory, so the
wording a struggling man reads is always exact. Re-run only to pick up a
corrected eBible.org release; the text almost never changes.

Only the KJV is bundled: the NKJV, which the skill links every reference to,
is its modernization (same Greek text, every verse in the same place), and the
skill puts a plain modern rendering under each KJV quote (see DESIGN.md).

What the build changes, and why. Every step is checked, and kjv.txt is only
replaced once all checks pass, so a bad download never corrupts the text.

- Keeps the 66-book Protestant canon. eBible.org's file also carries the
  deuterocanonical books; the canon is taken from verse.py's book table so it
  is defined in one place.
- Drops the [brackets] marking words the translators supplied (italics in
  print) and the ¶ paragraph marks. The supplied words stay, as in print.
- Moves the 116 psalm titles out of verse 1 onto their own verse-0 line
  ("PSA 51:0 To the chief Musician, ..."). eBible.org's verse-per-line file
  prepends each title to verse 1, so Psalm 51:1 would otherwise be quoted as
  starting "To the chief Musician". In print the title stands above verse 1,
  unnumbered, in both the KJV and the NKJV. Where each title ends is taken
  from eBible.org's USFM edition, which marks titles explicitly.
"""
import io
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Importing verse.py would otherwise leave a __pycache__ folder in the skill,
# which would then need an ignore rule outside this folder.
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent))
from verse import BOOKS  # noqa: E402

BASE = "https://ebible.org/Scriptures/eng-kjv"
OUT = HERE / "kjv.txt"
EXPECTED_VERSES = 31102  # in the KJV's 66 books
EXPECTED_TITLES = 116    # psalms with a title


def fail(msg):
    sys.exit(f"build failed, {OUT.name} left as it was: {msg}")


def download(fmt):
    req = urllib.request.Request(f"{BASE}_{fmt}.zip", headers={"User-Agent": "armor-bible-build/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return zipfile.ZipFile(io.BytesIO(r.read()))


def plain(usfm):
    """USFM title text to plain words: drop |strong="..." attributes, then the
    closing markers (\\w*, \\add*, \\nd*), then the opening ones with the space
    that belongs to them."""
    s = re.sub(r"\|[^\\]*", "", usfm)
    s = re.sub(r"\\\+?[a-z]+\*", "", s)
    s = re.sub(r"\\\+?[a-z]+ ", "", s)
    return re.sub(r"\s+", " ", s).strip()


def psalm_titles():
    z = download("usfm")
    name = next(n for n in z.namelist() if n.endswith("PSAeng-kjv.usfm"))
    chapter, titles = 0, {}
    for line in z.read(name).decode("utf-8").splitlines():
        if m := re.match(r"\\c (\d+)", line):
            chapter = int(m[1])
        elif line.startswith("\\d "):
            titles[chapter] = plain(line[3:])
    return titles


def main():
    canon = [code for code, _, _ in BOOKS]
    vpl = download("vpl").read("eng-kjv_vpl.txt").decode("utf-8")
    titles = psalm_titles()

    out, seen_books, unmatched = [], [], dict(titles)
    for line in vpl.splitlines():
        code = line.split(" ", 1)[0]
        if code not in canon:
            continue
        line = re.sub(r"¶ *", "", line.replace("[", "").replace("]", ""))
        ref, _, text = line.partition(" ")[2].partition(" ")
        if code == "PSA" and ref.endswith(":1"):
            chapter = int(ref.split(":")[0])
            title = titles.get(chapter)
            if title and text.startswith(title):
                out.append(f"PSA {chapter}:0 {title}")
                text = text[len(title):].lstrip()
                del unmatched[chapter]
        if not text:
            fail(f"{code} {ref} has no text")
        out.append(f"{code} {ref} {text}")
        if not seen_books or seen_books[-1] != code:
            seen_books.append(code)

    verses = sum(1 for line in out if not re.match(r"\S+ \d+:0 ", line))
    if seen_books != canon:
        fail(f"books differ from verse.py's table: {sorted(set(canon) ^ set(seen_books))}")
    if verses != EXPECTED_VERSES:
        fail(f"{verses} verses, expected {EXPECTED_VERSES}")
    if len(titles) != EXPECTED_TITLES or unmatched:
        fail(f"{len(titles)} psalm titles, expected {EXPECTED_TITLES}; "
             f"not found at the start of verse 1: {sorted(unmatched)}")
    if any(c in line for line in out for c in "[]¶"):
        fail("bracket or paragraph marks left in the text")

    tmp = OUT.with_suffix(".tmp")
    tmp.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.replace(tmp, OUT)
    print(f"wrote {OUT} ({verses} verses, {len(titles)} psalm titles, 66 books)")


if __name__ == "__main__":
    main()
