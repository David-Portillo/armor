#!/usr/bin/env python3
"""Checks for armor: the verse lookup, the bundled KJV, setup and the pastor
profiles, the app ZIP, and what Anthropic's plugin directory requires.

    python3 tests.py

These run the scripts the way the skill and its users do (a subprocess, JSON
on stdout, a real ZIP), so they test the contracts the skill relies on, not
just the functions.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skills" / "armor"
APP_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def look(*args, skill=SKILL):
    p = subprocess.run([sys.executable, str(skill / "verse.py"), *args], capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


def texts(result):
    return [text for _, text in result["verses"]]


class Lookup(unittest.TestCase):
    def test_exact_text_and_nkjv_link(self):
        code, out = look("Psalm 34:18")
        self.assertEqual(code, 0)
        r = out["results"][0]
        self.assertEqual(r["ref"], "Psalm 34:18")
        self.assertEqual(texts(r), ["The LORD is nigh unto them that are of a broken heart; "
                                    "and saveth such as be of a contrite spirit."])
        self.assertEqual(r["nkjv_url"],
                         "https://www.biblegateway.com/passage/?search=Psalm+34%3A18&version=NKJV")

    def test_psalm_title_is_not_part_of_verse_one(self):
        r = look("Psalm 51:1")[1]["results"][0]
        self.assertTrue(texts(r)[0].startswith("Have mercy upon me, O God"))
        self.assertTrue(r["titles"]["51"].startswith("To the chief Musician"))

    def test_untitled_passages_have_no_titles_key(self):
        self.assertNotIn("titles", look("John 3:16")[1]["results"][0])

    def test_whole_chapter(self):
        r = look("Psalm 23")[1]["results"][0]
        self.assertEqual(len(r["verses"]), 6)
        self.assertEqual(texts(r)[0], "The LORD is my shepherd; I shall not want.")

    def test_lists_and_ranges(self):
        r = look("Romans 8:28,38-39")[1]["results"][0]
        self.assertEqual([v for v, _ in r["verses"]], ["8:28", "8:38", "8:39"])

    def test_range_across_chapters(self):
        r = look("Ps 34:22-35:1")[1]["results"][0]
        self.assertEqual([v for v, _ in r["verses"]], ["34:22", "35:1"])

    def test_several_books_in_one_call(self):
        code, out = look("Gen 1:1", "Psalm 23:1", "Rev 22:21")
        self.assertEqual(code, 0)
        self.assertEqual([r["ref"] for r in out["results"]], ["Genesis 1:1", "Psalm 23:1", "Revelation 22:21"])

    def test_single_chapter_book_without_chapter(self):
        r = look("Jude 24-25")[1]["results"][0]
        self.assertEqual(r["ref"], "Jude 1:24-25")
        self.assertEqual(len(r["verses"]), 2)

    def test_partial_verse_reads_whole_verse(self):
        self.assertEqual(look("Gal 5:16b")[1]["results"][0]["ref"], "Galatians 5:16")

    def test_settings_come_with_the_lookup(self):
        code, out = look("--settings", "Psalm 34:18")
        self.assertEqual(code, 0)
        name = "settings.yaml" if (SKILL / "settings.yaml").exists() else "settings.example.yaml"
        self.assertEqual(out["settings_file"], name)
        self.assertEqual(out["settings"], (SKILL / name).read_text(encoding="utf-8"))
        self.assertEqual(out["results"][0]["ref"], "Psalm 34:18")

    def test_settings_alone(self):
        code, out = look("--settings")
        self.assertEqual(code, 0)
        self.assertEqual(out["results"], [])
        self.assertIn("tone:", out["settings"])

    def test_book_spellings(self):
        cases = {
            "1 Jn 1:9": "1 John", "First John 1:9": "1 John", "1st John 1:9": "1 John",
            "I John 1:9": "1 John", "III John 2": "3 John", "Phil 4:13": "Philippians",
            "Phillipians 4:13": "Philippians", "Phlm 6": "Philemon", "Is 41:10": "Isaiah",
            "Isaiah 41:10": "Isaiah", "Song of Songs 8:6": "Song of Solomon", "Ps. 23:1": "Psalm",
            "1 Cor 10:13": "1 Corinthians", "Jas 1:12": "James", "Rev 21:4": "Revelation",
        }
        for ref, book in cases.items():
            with self.subTest(ref=ref):
                code, out = look(ref)
                self.assertEqual(code, 0, out["errors"])
                self.assertTrue(out["results"][0]["ref"].startswith(book + " "), out["results"][0]["ref"])


class Errors(unittest.TestCase):
    def test_bad_references_are_errors_not_guesses(self):
        for ref in ["Jo 3:16", "Tobit 1:1", "Psalm 151", "John 3:99", "John 3:16-4", "hello"]:
            with self.subTest(ref=ref):
                code, out = look(ref)
                self.assertEqual(code, 1)
                self.assertEqual(out["results"], [])
                self.assertEqual(len(out["errors"]), 1)

    def test_one_bad_reference_keeps_the_good_ones(self):
        code, out = look("Psalm 34:18", "Tobit 1:1", "John 3:16")
        self.assertEqual(code, 1)
        self.assertEqual([r["ref"] for r in out["results"]], ["Psalm 34:18", "John 3:16"])
        self.assertEqual(len(out["errors"]), 1)

    def test_translation_cannot_reach_outside_bible_dir(self):
        code, out = look("--translation", "../verse", "Psalm 1:1")
        self.assertEqual(code, 1)
        self.assertEqual(out["results"], [])


class BundledText(unittest.TestCase):
    """The build checks these too; repeating them catches a hand-edited file."""

    @classmethod
    def setUpClass(cls):
        cls.files = sorted((SKILL / "bible" / "kjv").glob("*.txt"))
        cls.lines = [line for f in cls.files for line in f.read_text(encoding="utf-8").splitlines()]

    def test_counts(self):
        titles = [line for line in self.lines if re.match(r"PSA \d+:0 ", line)]
        self.assertEqual(len(self.files), 66)
        self.assertEqual(len(titles), 116)
        self.assertEqual(len(self.lines) - len(titles), 31102)

    def test_each_book_file_holds_only_its_book(self):
        for f in self.files:
            codes = {line.split(" ", 1)[0] for line in f.read_text(encoding="utf-8").splitlines()}
            self.assertEqual(codes, {f.stem}, f.name)

    def test_clean(self):
        for line in self.lines:
            self.assertRegex(line, r"^[1-3A-Z]{3} \d+:\d+ \S")
            self.assertFalse(set("[]¶") & set(line), line)


class SetupAndPastors(unittest.TestCase):
    """Run in a scratch copy of the skill, so the real settings and the review
    state of the real profiles never matter."""

    ANSWERS = {"tradition": "Baptist", "crisis_region": "US", "pastors": ["Charles Spurgeon"],
               "tone": {"listen_or_act": "ask", "call_out": "ask", "length": "short",
                        "voice": "friend-and-mentor", "delivery": "gentle", "after_a_fall": "grace-first"}}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "armor"
        shutil.copytree(SKILL, self.dir, ignore=shutil.ignore_patterns(
            "__pycache__", "settings.yaml", "my-pastors", ".DS_Store"))

    def tearDown(self):
        self.tmp.cleanup()

    def run_verse(self, *args):
        return look(*args, skill=self.dir)

    def set_reviewed(self, file, reviewed):
        f = self.dir / file
        f.write_text(re.sub(r"reviewed: \w+", f"reviewed: {str(reviewed).lower()}", f.read_text()))

    def test_first_run_until_setup_saves(self):
        self.assertTrue(self.run_verse("--settings")[1]["first_run"])
        code, saved = self.run_verse("--save-settings", json.dumps(self.ANSWERS))
        self.assertEqual(code, 0, saved)
        self.assertTrue(saved["line"].startswith("armor settings: tradition Baptist; crisis line US; "
                                                 "pastors Charles Spurgeon;"))
        out = self.run_verse("--settings")[1]
        self.assertFalse(out["first_run"])
        self.assertEqual(out["settings_file"], "settings.yaml")
        self.assertIn('- "Charles Spurgeon"', out["settings"])

    def test_bad_answers_are_refused_and_nothing_is_saved(self):
        bad = dict(self.ANSWERS, crisis_region="Mars", tone=dict(self.ANSWERS["tone"], voice="robot"))
        code, out = self.run_verse("--save-settings", json.dumps(bad))
        self.assertEqual(code, 1)
        self.assertIn("crisis_region", out["errors"][0])
        self.assertIn("tone.voice", out["errors"][0])
        self.assertFalse((self.dir / "settings.yaml").exists())

    def test_profiles_are_listed_with_their_review_state(self):
        self.set_reviewed("pastors/charles-spurgeon.md", True)
        self.set_reviewed("pastors/david-wilkerson.md", False)
        listed = {p["name"]: p for p in self.run_verse("--settings")[1]["profiles"]}
        self.assertTrue(listed["Charles Spurgeon"]["reviewed"])
        self.assertFalse(listed["David Wilkerson"]["reviewed"])
        self.assertEqual(len(listed), 6)
        # The first lookup carries each reviewed profile's text, so From the
        # Pulpit is ready from the first reply; a draft's text stays out.
        self.assertIn("Fainting Fits", listed["Charles Spurgeon"]["profile"])
        self.assertNotIn("profile", listed["David Wilkerson"])

    def test_unreviewed_profile_never_reaches_from_the_pulpit(self):
        self.set_reviewed("pastors/david-wilkerson.md", False)
        code, out = self.run_verse("--pastor", "David Wilkerson", "Psalm 34:18")
        self.assertEqual(code, 1)
        self.assertEqual(out["pastors"], [])
        self.assertIn("hasn't been reviewed", out["errors"][0])
        self.assertEqual(len(out["results"]), 1)  # the verses still come back

    def test_reviewed_profile_is_returned_by_full_or_partial_name(self):
        self.set_reviewed("pastors/charles-spurgeon.md", True)
        for name in ["Charles Spurgeon", "spurgeon"]:
            code, out = self.run_verse("--pastor", name)
            self.assertEqual(code, 0, out)
            self.assertEqual(out["pastors"][0]["name"], "Charles Spurgeon")
            self.assertFalse(out["pastors"][0]["living"])
            self.assertIn("Fainting Fits", out["pastors"][0]["profile"])

    def test_setup_fetches_every_chosen_profile_in_one_call(self):
        # Setup shows each chosen pastor's profile for approval, one at a time.
        for f in ["charles-spurgeon.md", "david-wilkerson.md", "tony-evans.md"]:
            self.set_reviewed(f"pastors/{f}", True)
        code, out = self.run_verse("--pastor", "Spurgeon", "--pastor", "Wilkerson", "--pastor", "Tony Evans")
        self.assertEqual(code, 0, out)
        self.assertEqual([p["name"] for p in out["pastors"]],
                         ["Charles Spurgeon", "David Wilkerson", "Tony Evans"])

    def test_at_least_one_pastor_is_required(self):
        # Every response includes From the Pulpit.
        code, out = self.run_verse("--save-settings", json.dumps(dict(self.ANSWERS, pastors=[])))
        self.assertEqual(code, 1)
        self.assertIn("at least one", out["errors"][0])
        self.assertFalse((self.dir / "settings.yaml").exists())

    def test_a_users_own_pastor_profile_is_read(self):
        (self.dir / "my-pastors").mkdir()
        (self.dir / "my-pastors" / "paul-washer.md").write_text(
            "---\nname: Paul Washer\nliving: true\nreviewed: true\nspeaks_to: repentance\n---\n# Paul Washer\n")
        self.assertIn("Paul Washer", [p["name"] for p in self.run_verse("--settings")[1]["profiles"]])
        self.assertEqual(self.run_verse("--pastor", "Paul Washer")[1]["pastors"][0]["name"], "Paul Washer")


class SkillText(unittest.TestCase):
    """One SKILL.md serves Claude Code, Cowork and the app's chat."""

    @classmethod
    def setUpClass(cls):
        cls.md = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_frontmatter_the_app_accepts(self):
        front = self.md.split("---\n")[1]
        keys = {line.split(":", 1)[0] for line in front.splitlines() if line and not line[0].isspace()}
        self.assertLessEqual(keys, APP_KEYS)
        self.assertIn("name: armor", front.splitlines())

    def test_from_the_pulpit_in_every_reply(self):
        self.assertIn("One short paragraph in every response, and a shorter one in every other\n"
                      "reply about what he's going through", self.md)
        self.assertNotIn("leave this section out", self.md)
        self.assertNotIn("no devotional", self.md)

    def test_setup_asks_one_question_at_a_time(self):
        # On the phone, setup first sent several questions at once.
        text = " ".join(self.md.split())
        self.assertIn("one question per message, numbered", text)
        self.assertIn("Never put two questions in one message.", text)
        setup = text[text.index("## Setup"):text.index("Save it all in one call.")]
        self.assertEqual(re.findall(r" (\d)\. ", setup), [str(n) for n in range(1, 10)])

    def test_safety_still_comes_first_in_crisis_replies(self):
        self.assertIn("What\n  keeps him safe always comes first, and From the Pulpit follows", self.md)
        self.assertIn("then, last, ask him directly", self.md)

    def test_placeholder_only_in_commands(self):
        # Claude Code and Cowork replace every occurrence of the placeholder,
        # so in prose it would turn into a path and garble the sentence.
        for m in re.finditer(r"\$\{CLAUDE_SKILL_DIR\}", self.md):
            self.assertEqual(self.md[m.end():m.end() + len("/verse.py")], "/verse.py",
                             self.md[max(0, m.start() - 40):m.end() + 20])

    def test_chat_fallback_finds_verse_py_by_itself(self):
        """In chat the placeholder isn't filled in, so SKILL.md has Claude find
        the script. On the phone the app kept the plugin under
        ~/.claude/plugins/synced/<account>/ in its sandbox; a scratch folder
        stands in for that ~/.claude here."""
        expr = re.search(r'`("\$\(find ~/\.claude /mnt /home [^`]*\)")`', self.md)
        self.assertIsNotNone(expr, "no chat fallback find expression in SKILL.md")
        with tempfile.TemporaryDirectory() as home:
            claude = Path(home) / ".claude"
            shutil.copytree(SKILL, claude / "plugins" / "synced" / "account_id" / "armor" / "skills" / "armor",
                            ignore=shutil.ignore_patterns("settings.yaml", "my-pastors"))
            cmd = "python3 " + expr[1].replace("~/.claude", str(claude)) + ' --settings "Psalm 34:18"'
            p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue(json.loads(p.stdout)["results"][0]["verses"][0][1].startswith("The LORD is nigh"))


class Package(unittest.TestCase):
    """The ZIP for uploading the skill to the Claude app yourself (package.py)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.zip_path = Path(cls.tmp.name) / "armor.zip"
        subprocess.run([sys.executable, str(ROOT / "package.py"), "--out", str(cls.zip_path)],
                       check=True, capture_output=True)
        cls.zip = zipfile.ZipFile(cls.zip_path)

    @classmethod
    def tearDownClass(cls):
        cls.zip.close()
        cls.tmp.cleanup()

    def test_one_folder_named_like_the_skill(self):
        self.assertTrue(all(n.startswith("armor/") for n in self.zip.namelist()))

    def test_the_skill_folder_as_it_is(self):
        names = {n.removeprefix("armor/") for n in self.zip.namelist()}
        for needed in ["SKILL.md", "verse.py", "settings.example.yaml", "bible/kjv/PSA.txt"]:
            self.assertIn(needed, names)
        self.assertEqual(sum(n.startswith("bible/kjv/") for n in names), 66)
        self.assertEqual(sum(n.startswith("pastors/") for n in names),
                         len(list((SKILL / "pastors").glob("*.md"))))
        self.assertEqual(self.zip.read("armor/SKILL.md"), (SKILL / "SKILL.md").read_bytes())

    def test_lookup_runs_from_the_unzipped_copy(self):
        with tempfile.TemporaryDirectory() as d:
            self.zip.extractall(d)
            p = subprocess.run([sys.executable, str(Path(d) / "armor" / "verse.py"), "Psalm 34:18"],
                               capture_output=True, text=True, cwd=tempfile.gettempdir())
            self.assertEqual(p.returncode, 0, p.stdout)
            self.assertTrue(json.loads(p.stdout)["results"][0]["verses"][0][1].startswith("The LORD is nigh"))


class Directory(unittest.TestCase):
    """What Anthropic's plugin directory checks before listing armor."""

    def tracked(self):
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True)
        return [ROOT / name for name in out.stdout.splitlines()]

    def test_manifest(self):
        m = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        self.assertRegex(m["name"], r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")
        self.assertRegex(m["version"], r"^\d+\.\d+\.\d+$")
        for key in ["description", "author", "license"]:
            self.assertIn(key, m)

    def test_readme_and_license(self):
        readme = re.sub(r"```.*?```", "", (ROOT / "README.md").read_text(), flags=re.S)
        self.assertGreaterEqual(len(readme.split()), 40)
        self.assertTrue((ROOT / "LICENSE").exists())

    def test_no_file_held_for_review(self):
        # Over 256 KiB, a file is held for a manual review; system files block.
        for f in self.tracked():
            self.assertLess(f.stat().st_size, 256 * 1024, f.name)
            self.assertNotIn(f.name, {".DS_Store", "Thumbs.db", "desktop.ini"})


if __name__ == "__main__":
    unittest.main()
