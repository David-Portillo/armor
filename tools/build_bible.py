#!/usr/bin/env python3
"""Rebuild the bundled King James Version from eBible.org (public domain).

    python3 tools/build_bible.py

Writes skills/armor/bible/kjv/<BOOK>.txt, one file per book (GEN.txt ...
REV.txt), each line "PSA 51:1 text". The skill puts every verse into today's
words from these files, never from model memory, so what a struggling man reads
always rests on the exact text. Re-run only to pick up a corrected eBible.org
release; the text almost never changes. This is a maintainer tool: the skill
itself never downloads anything.

Only the KJV is bundled: the NKJV, which the skill links every reference to,
is its modernization (same Greek text, every verse in the same place), and the
skill shows each verse in plain modern words made from the KJV (see DESIGN.md).

What the build changes, and why. Every step is checked, and the bundled text is
only replaced once all checks pass, so a bad download never corrupts it.

- One file per book. Anthropic's plugin directory holds any file over 256 KiB
  for a manual review, and the whole Bible is 4.4 MB; split by book, the
  largest, Psalms, is about 249 KiB. verse.py then reads only the books a
  lookup needs.
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
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "armor"
OUT = SKILL / "bible" / "kjv"
# Importing verse.py would otherwise leave a __pycache__ folder in the skill.
sys.dont_write_bytecode = True
sys.path.insert(0, str(SKILL))
from verse import BOOKS  # noqa: E402

BASE = "https://ebible.org/Scriptures/eng-kjv"
EXPECTED_VERSES = 31102  # in the KJV's 66 books
EXPECTED_TITLES = 116    # psalms with a title
MAX_FILE = 256 * 1024    # larger files are held for a manual directory review


def fail(msg):
    sys.exit(f"build failed, the bundled text was left as it was: {msg}")


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

    books, unmatched = {}, dict(titles)
    for line in vpl.splitlines():
        code = line.split(" ", 1)[0]
        if code not in canon:
            continue
        line = re.sub(r"¶ *", "", line.replace("[", "").replace("]", ""))
        ref, _, text = line.partition(" ")[2].partition(" ")
        out = books.setdefault(code, [])
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

    lines = [line for code in canon for line in books.get(code, [])]
    verses = sum(1 for line in lines if not re.match(r"\S+ \d+:0 ", line))
    if list(books) != canon:
        fail(f"books differ from verse.py's table: {sorted(set(canon) ^ set(books))}")
    if verses != EXPECTED_VERSES:
        fail(f"{verses} verses, expected {EXPECTED_VERSES}")
    if len(titles) != EXPECTED_TITLES or unmatched:
        fail(f"{len(titles)} psalm titles, expected {EXPECTED_TITLES}; "
             f"not found at the start of verse 1: {sorted(unmatched)}")
    if any(c in line for line in lines for c in "[]¶"):
        fail("bracket or paragraph marks left in the text")
    texts = {code: "\n".join(books[code]) + "\n" for code in canon}
    too_big = [c for c, t in texts.items() if len(t.encode("utf-8")) >= MAX_FILE]
    if too_big:
        fail(f"over {MAX_FILE // 1024} KiB, which the plugin directory holds for review: {too_big}")

    # Write the new books beside the old ones, then swap the folders.
    tmp, old = OUT.with_name("kjv.tmp"), OUT.with_name("kjv.old")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    for code, text in texts.items():
        (tmp / f"{code}.txt").write_text(text, encoding="utf-8")
    shutil.rmtree(old, ignore_errors=True)
    if OUT.exists():
        os.replace(OUT, old)
    os.replace(tmp, OUT)
    shutil.rmtree(old, ignore_errors=True)
    largest = max(texts, key=lambda c: len(texts[c].encode("utf-8")))
    print(f"wrote {OUT} ({verses} verses, {len(titles)} psalm titles, 66 books; "
          f"largest {largest} at {len(texts[largest].encode('utf-8')) / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
