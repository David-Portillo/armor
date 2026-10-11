#!/usr/bin/env python3
"""Build dist/armor.zip, the copy of armor to upload to the Claude app.

    python3 package.py

Then, in Claude in a browser or the desktop app: Customize > Skills > + >
Create skill > Upload a skill, and choose dist/armor.zip. Re-run and upload
again after any change, including a change to settings.yaml.

Why the app gets its own copy: the app accepts only a few SKILL.md frontmatter
keys and fails the upload on any other, and it doesn't fill in Claude Code's
${CLAUDE_SKILL_DIR}. So this copy:

- keeps only the frontmatter keys the app accepts. Claude Code's
  disable-model-invocation and allowed-tools stay behind: in the app the
  description itself limits the skill to /armor, and code runs without asking;
- turns each `python3 ${CLAUDE_SKILL_DIR}/verse.py` command into one that finds
  verse.py by itself (see LOOKUP). SKILL.md may use ${CLAUDE_SKILL_DIR} only in
  those commands, so nothing else depends on knowing the folder;
- carries only what the skill needs when it runs: SKILL.md, verse.py, the KJV
  text, the settings, the pastor profiles (bundled and the user's own), and the
  license. The design notes, README, tests and build scripts stay out;
- adds an empty .app-copy marker, so verse.py knows nothing it saves will last.

Run setup in Claude Code before packaging: the ZIP carries settings.yaml and
any approved profiles in my-pastors/, which is how your answers reach your
phone.
"""
import argparse
import os
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "armor"  # the app requires the folder in the ZIP to match the skill name
APP_KEYS = {"name", "description", "license", "compatibility", "metadata"}

# The app doesn't tell Claude where the skill's folder is. Left to guess, it
# tried /mnt/skills/plugins/armor, failed, and had to search before it could
# answer. So each command finds verse.py itself: /mnt is where the app keeps
# skills, and ~/.claude/skills is where Claude Code keeps the copies it syncs
# from the account. Both searches take milliseconds.
LOOKUP = "python3 \"$(find /mnt ~/.claude/skills -path '*/armor/verse.py' -print -quit 2>/dev/null)\""
NOTE = ("In this copy, each `verse.py` command finds the script by itself. If one "
        "ever says it can't open the file, locate it with "
        "`find / -path '*/armor/verse.py' -print -quit 2>/dev/null` and run that "
        "path instead.\n\n")


def fail(msg):
    sys.exit(f"package failed: {msg}")


def app_skill_md():
    text = (HERE / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail("SKILL.md has no frontmatter")
    kept, key = [], None
    for line in m[1].splitlines():
        if line and not line[0].isspace():  # a new top-level key
            key = line.split(":", 1)[0].strip()
        if key in APP_KEYS:
            kept.append(line)
    body = text[m.end():].replace("python3 ${CLAUDE_SKILL_DIR}/verse.py", LOOKUP)
    if "${CLAUDE_SKILL_DIR}" in body:
        fail("SKILL.md uses ${CLAUDE_SKILL_DIR} outside a verse.py command; the app can't resolve it")
    body, n = re.subn(r"^(# .*\n\n)", lambda h: h[1] + NOTE, body, count=1, flags=re.M)
    if not n:
        fail("SKILL.md body has no top-level heading to put the note under")
    out = "---\n" + "\n".join(kept) + "\n---\n" + body

    keys = {line.split(":", 1)[0] for line in kept if line and not line[0].isspace()}
    if f"name: {NAME}" not in kept:
        fail(f"frontmatter name must be '{NAME}' to match the folder in the ZIP")
    if "description" not in keys:
        fail("frontmatter has no description")
    if "${CLAUDE_" in out or re.search(r"!`", out):
        fail("a Claude Code-only feature is left in the app copy")
    return out


def files():
    yield "SKILL.md", app_skill_md().encode("utf-8")
    for rel in ["verse.py", "bible/kjv.txt", "LICENSE"]:
        yield rel, (HERE / rel).read_bytes()
    settings = HERE / "settings.yaml"
    if not settings.exists():
        settings = HERE / "settings.example.yaml"
    yield settings.name, settings.read_bytes()
    # Bundled profiles and the user's own; verse.py reads both folders.
    for folder in ("pastors", "my-pastors"):
        d = HERE / folder
        for p in sorted(d.glob("*.md")) if d.is_dir() else []:
            yield f"{folder}/{p.name}", p.read_bytes()
    # Tells verse.py it is the app copy, where nothing written is kept
    # between chats, so setup hands over its answers instead of saving them.
    yield ".app-copy", b""


def main():
    p = argparse.ArgumentParser(description="Build the ZIP to upload to the Claude app.")
    p.add_argument("--out", type=Path, default=HERE / "dist" / f"{NAME}.zip")
    out = p.parse_args().out

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    names = []
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, data in files():
            z.writestr(f"{NAME}/{rel}", data)
            names.append(rel)
    os.replace(tmp, out)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB): {', '.join(names)}")


if __name__ == "__main__":
    main()
