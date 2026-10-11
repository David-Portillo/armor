#!/usr/bin/env python3
"""Checks for verse.py, the bundled KJV and the app package. Run: python3 tests.py

These run the scripts the way the skill and its users do (a
subprocess, JSON on stdout, a real ZIP), so they test the contracts the skill
relies on, not just the functions.
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

HERE = Path(__file__).resolve().parent


def look(*args):
    p = subprocess.run([sys.executable, str(HERE / "verse.py"), *args], capture_output=True, text=True)
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

    def test_single_chapter_book_without_chapter(self):
        r = look("Jude 24-25")[1]["results"][0]
        self.assertEqual(r["ref"], "Jude 1:24-25")
        self.assertEqual(len(r["verses"]), 2)

    def test_partial_verse_reads_whole_verse(self):
        self.assertEqual(look("Gal 5:16b")[1]["results"][0]["ref"], "Galatians 5:16")

    def test_settings_come_with_the_lookup(self):
        code, out = look("--settings", "Psalm 34:18")
        self.assertEqual(code, 0)
        name = "settings.yaml" if (HERE / "settings.yaml").exists() else "settings.example.yaml"
        self.assertEqual(out["settings_file"], name)
        self.assertEqual(out["settings"], (HERE / name).read_text(encoding="utf-8"))
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
        cls.lines = (HERE / "bible" / "kjv.txt").read_text(encoding="utf-8").splitlines()

    def test_counts(self):
        titles = [line for line in self.lines if re.match(r"PSA \d+:0 ", line)]
        self.assertEqual(len(titles), 116)
        self.assertEqual(len(self.lines) - len(titles), 31102)
        self.assertEqual(len({line.split(" ", 1)[0] for line in self.lines}), 66)

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
        shutil.copytree(HERE, self.dir, ignore=shutil.ignore_patterns(
            ".git", "dist", "__pycache__", "settings.yaml", "my-pastors", ".DS_Store"))

    def tearDown(self):
        self.tmp.cleanup()

    def run_verse(self, *args):
        p = subprocess.run([sys.executable, str(self.dir / "verse.py"), *args], capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def set_reviewed(self, file, reviewed):
        f = self.dir / file
        f.write_text(re.sub(r"reviewed: \w+", f"reviewed: {str(reviewed).lower()}", f.read_text()))

    def test_first_run_until_setup_saves(self):
        code, out = self.run_verse("--settings")
        self.assertTrue(out["first_run"])
        self.assertTrue(out["persistent"])
        code, saved = self.run_verse("--save-settings", json.dumps(self.ANSWERS))
        self.assertEqual(code, 0, saved)
        self.assertTrue(saved["line"].startswith("armor settings: tradition Baptist; crisis line US; "
                                                 "pastors Charles Spurgeon;"))
        code, out = self.run_verse("--settings")
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
        out = self.run_verse("--settings")[1]
        state = {p["name"]: p["reviewed"] for p in out["profiles"]}
        self.assertTrue(state["Charles Spurgeon"])
        self.assertFalse(state["David Wilkerson"])
        self.assertEqual(len(state), 6)

    def test_unreviewed_profile_never_reaches_from_the_pulpit(self):
        self.set_reviewed("pastors/david-wilkerson.md", False)
        code, out = self.run_verse("--pastor", "David Wilkerson", "Psalm 34:18")
        self.assertEqual(code, 1)
        self.assertNotIn("pastor", out)
        self.assertIn("hasn't been reviewed", out["errors"][0])
        self.assertEqual(len(out["results"]), 1)  # the verses still come back

    def test_reviewed_profile_is_returned_by_full_or_partial_name(self):
        self.set_reviewed("pastors/charles-spurgeon.md", True)
        for name in ["Charles Spurgeon", "spurgeon"]:
            code, out = self.run_verse("--pastor", name)
            self.assertEqual(code, 0, out)
            self.assertEqual(out["pastor"]["name"], "Charles Spurgeon")
            self.assertFalse(out["pastor"]["living"])
            self.assertIn("Fainting Fits", out["pastor"]["profile"])

    def test_a_users_own_pastor_profile_is_read(self):
        (self.dir / "my-pastors").mkdir()
        (self.dir / "my-pastors" / "paul-washer.md").write_text(
            "---\nname: Paul Washer\nliving: true\nreviewed: true\nspeaks_to: repentance\n---\n# Paul Washer\n")
        self.assertIn("Paul Washer", [p["name"] for p in self.run_verse("--settings")[1]["profiles"]])
        self.assertEqual(self.run_verse("--pastor", "Paul Washer")[1]["pastor"]["name"], "Paul Washer")

    def test_app_copy_knows_nothing_it_saves_will_last(self):
        (self.dir / ".app-copy").touch()
        self.assertFalse(self.run_verse("--settings")[1]["persistent"])
        self.assertFalse(self.run_verse("--save-settings", json.dumps(self.ANSWERS))[1]["persistent"])


class Package(unittest.TestCase):
    """The ZIP uploaded to the Claude app (see package.py)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.zip_path = Path(cls.tmp.name) / "armor.zip"
        subprocess.run([sys.executable, str(HERE / "package.py"), "--out", str(cls.zip_path)],
                       check=True, capture_output=True)
        cls.zip = zipfile.ZipFile(cls.zip_path)

    @classmethod
    def tearDownClass(cls):
        cls.zip.close()
        cls.tmp.cleanup()

    def test_one_folder_named_like_the_skill(self):
        self.assertTrue(all(n.startswith("armor/") for n in self.zip.namelist()))

    def test_runtime_files_only(self):
        names = {n.removeprefix("armor/") for n in self.zip.namelist()}
        for needed in ["SKILL.md", "verse.py", "bible/kjv.txt", "LICENSE"]:
            self.assertIn(needed, names)
        self.assertTrue({"settings.yaml", "settings.example.yaml"} & names)
        for left_out in ["DESIGN.md", "README.md", "tests.py", "package.py", "bible/build.py"]:
            self.assertNotIn(left_out, names)
        self.assertIn(".app-copy", names)
        self.assertEqual(sum(n.startswith("pastors/") for n in names),
                         len(list((HERE / "pastors").glob("*.md"))))

    def test_frontmatter_the_app_accepts(self):
        md = self.zip.read("armor/SKILL.md").decode("utf-8")
        front = md.split("---\n")[1]
        keys = {line.split(":", 1)[0] for line in front.splitlines() if line and not line[0].isspace()}
        self.assertLessEqual(keys, {"name", "description", "license", "compatibility", "metadata"})
        self.assertIn("name: armor", front.splitlines())
        self.assertNotIn("${CLAUDE_", md)

    def test_app_command_finds_verse_py_by_itself(self):
        """Run the exact command from the app copy, with the package unzipped
        where Claude Code keeps synced account skills (HOME is a temp dir)."""
        md = self.zip.read("armor/SKILL.md").decode("utf-8")
        cmd = re.search(r"`(python3 \"\$\(find [^`]*--settings)`", md)
        self.assertIsNotNone(cmd, "no self-locating --settings command in the app copy")
        with tempfile.TemporaryDirectory() as home:
            synced = Path(home) / ".claude" / "skills" / "synced" / "x"
            synced.mkdir(parents=True)
            self.zip.extractall(synced)
            p = subprocess.run(["bash", "-c", cmd[1] + ' "Psalm 34:18"'], capture_output=True, text=True,
                               cwd=home, env={"HOME": home, "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})
            self.assertEqual(p.returncode, 0, p.stderr)
            out = json.loads(p.stdout)
            self.assertIn("tone:", out["settings"])
            self.assertTrue(out["results"][0]["verses"][0][1].startswith("The LORD is nigh"))

    def test_lookup_runs_from_the_unzipped_copy(self):
        with tempfile.TemporaryDirectory() as d:
            self.zip.extractall(d)
            p = subprocess.run([sys.executable, str(Path(d) / "armor" / "verse.py"), "Psalm 34:18"],
                               capture_output=True, text=True, cwd=tempfile.gettempdir())
            self.assertEqual(p.returncode, 0, p.stdout)
            self.assertTrue(json.loads(p.stdout)["results"][0]["verses"][0][1].startswith("The LORD is nigh"))


if __name__ == "__main__":
    unittest.main()
