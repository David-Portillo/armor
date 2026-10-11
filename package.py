#!/usr/bin/env python3
"""Build dist/armor.zip, the skill folder to upload to the Claude app yourself.

    python3 package.py

Then, in Claude in a browser or the desktop app: Customize > Skills > + >
Create skill > Upload a skill, and choose dist/armor.zip. Re-run and upload
again after any change, including a change to your settings.

This is for using armor before it's listed in Anthropic's directory, or with
settings of your own. The ZIP is the skill folder, skills/armor, as it is:
SKILL.md, verse.py, the KJV, the settings and the pastor profiles, including
your settings.yaml and the profiles you added in my-pastors/ if you ran setup
in Claude Code. The app wants the folder as the ZIP's single top-level entry,
named like the skill.

The same SKILL.md serves Claude Code, Cowork and the app, so nothing is
rewritten here. This only checks that the frontmatter uses keys the app
accepts, because the app fails the whole upload on any other key.
"""
import argparse
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "armor"
SKILL = ROOT / "skills" / NAME
APP_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
JUNK = {".DS_Store", "Thumbs.db", "__pycache__"}


def fail(msg):
    sys.exit(f"package failed: {msg}")


def check_frontmatter():
    m = re.match(r"---\n(.*?)\n---\n", (SKILL / "SKILL.md").read_text(encoding="utf-8"), re.S)
    if not m:
        fail("SKILL.md has no frontmatter")
    lines = m[1].splitlines()
    keys = {line.split(":", 1)[0] for line in lines if line and not line[0].isspace()}
    if keys - APP_KEYS:
        fail(f"frontmatter keys the app would refuse: {', '.join(sorted(keys - APP_KEYS))}")
    if f"name: {NAME}" not in lines:
        fail(f"frontmatter name must be '{NAME}' to match the folder in the ZIP")


def files():
    for f in sorted(SKILL.rglob("*")):
        rel = f.relative_to(SKILL)
        if f.is_file() and not JUNK & set(rel.parts):
            yield rel.as_posix(), f


def main():
    p = argparse.ArgumentParser(description="Build the ZIP to upload to the Claude app.")
    p.add_argument("--out", type=Path, default=ROOT / "dist" / f"{NAME}.zip")
    out = p.parse_args().out
    check_frontmatter()

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    count = 0
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, f in files():
            z.write(f, f"{NAME}/{rel}")
            count += 1
    os.replace(tmp, out)
    mine = [n for n in ("settings.yaml", "my-pastors") if (SKILL / n).exists()]
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB, {count} files"
          + (f", with your {' and '.join(mine)}" if mine else ", default settings") + ")")


if __name__ == "__main__":
    main()
