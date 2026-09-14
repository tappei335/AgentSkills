"""Exercise portable builds, destination isolation, and launcher selection."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_skills import build


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def run_command(self, *args, ok=True):
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def sync(self, profile, home, *extra, ok=True):
        return self.run_command("bash", "scripts/sync_skills.sh", "--agent", "codex",
                                "--profile", profile, "--codex-home", str(home), *extra, ok=ok)

    def test_all_builds_are_portable_and_model_neutral_without_profile(self):
        for profile in (None, "gpt-6", "gpt-5.6"):
            output = self.work / (profile or "common")
            build(output, profile)
            self.run_command(sys.executable, "scripts/validate_skills.py", "--root", str(output))
            self.assertEqual({p.parent.name for p in (output / "skills").glob("*/SKILL.md")},
                             {p.parent.name for p in (ROOT / "codex").glob("*/SKILL.md")})
            for path in (output / "skills").rglob("*.md"):
                self.assertNotIn("../../policies/", path.read_text())
            policy = (output / "skills/team-dev/references/model-policy.md").read_text()
            self.assertEqual("gpt-6-astra" in policy, profile == "gpt-6")
            self.assertEqual("gpt-5.6-sol" in policy, profile == "gpt-5.6")
            if profile is None:
                self.assertNotIn("gpt-", policy)

    def test_existing_build_is_preserved(self):
        output = self.work / "build"
        output.mkdir()
        (output / "mine").write_text("keep")
        with self.assertRaises(ValueError):
            build(output, "gpt-6")
        self.assertEqual((output / "mine").read_text(), "keep")

    def test_shared_guidance_loads_before_workflow_only_in_selected_profile(self):
        guidance = (ROOT / "variants/gpt-6/_shared/instructions.md").read_bytes()
        for profile in (None, "gpt-6", "gpt-5.6"):
            output = self.work / (profile or "common")
            build(output, profile)
            for skill in (output / "skills").iterdir():
                shared = skill / "references/model-profile.md"
                self.assertEqual(shared.exists(), profile == "gpt-6")
                text = (skill / "SKILL.md").read_text()
                if profile == "gpt-6":
                    self.assertEqual(shared.read_bytes(), guidance)
                    self.assertLess(text.index("Read [profile guidance]"), text.index("\n# "))
                else:
                    self.assertNotIn("references/model-profile.md", text)
                self.assertFalse(any(p.name == "evidence.md" for p in skill.rglob("*")))

    def test_shared_guidance_requires_evidence(self):
        root = self.work / "source"
        for name in ("codex", "profiles", "policies", "variants"):
            shutil.copytree(ROOT / name, root / name)
        (root / "variants/gpt-6/_shared/evidence.md").unlink()
        with self.assertRaises(ValueError):
            build(self.work / "invalid", "gpt-6", root)
        self.assertFalse((self.work / "invalid").exists())

    def test_sync_isolated_idempotent_and_dry_run_has_no_destination_writes(self):
        first, second = self.work / "six home", self.work / "five home"
        self.sync("gpt-6", first, "--dry-run")
        self.assertFalse(first.exists())
        self.sync("gpt-6", first)
        self.sync("gpt-5.6", second)
        snapshot = {str(p.relative_to(first)): p.read_bytes() for p in first.rglob("*") if p.is_file()}
        self.sync("gpt-5.6", first, ok=False)
        self.sync("gpt-6", first)
        self.assertEqual(snapshot, {str(p.relative_to(first)): p.read_bytes() for p in first.rglob("*") if p.is_file()})
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(first)
        result = subprocess.run(
            ["bash", "scripts/sync_skills.sh", "--agent", "codex", "--profile", "gpt-6",
             "--codex-home", str(first)], cwd=ROOT, env=environment, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((second / "agent-skills-profile.json").read_text())["name"], "gpt-5.6")
        result = self.run_command(sys.executable, "scripts/codex_profile.py", "gpt-6",
                                  "--codex-home", str(first), "--dry-run", "--", "exec", "literal $HOME `text`")
        launch = json.loads(result.stdout)
        self.assertEqual(launch["codex_home"], str(first))
        self.assertIn('model="gpt-6-astra"', launch["command"])
        self.assertEqual(launch["command"][-1], "literal $HOME `text`")
        self.run_command(sys.executable, "scripts/codex_profile.py", "gpt-5.6",
                         "--codex-home", str(first), "--dry-run", ok=False)

    def test_profile_refuses_shared_home_and_unmanaged_skills(self):
        self.sync("gpt-6", Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))), "--dry-run", ok=False)
        home = self.work / "existing"
        (home / "skills/mine").mkdir(parents=True)
        self.sync("gpt-6", home, ok=False)
        self.assertTrue((home / "skills/mine").exists())

    def test_common_sync_preserves_unrelated_skills_and_refuses_profile_home(self):
        home = self.work / "common"
        (home / "skills/mine").mkdir(parents=True)
        (home / "skills/mine/keep").write_text("keep")
        self.run_command("bash", "scripts/sync_skills.sh", "--agent", "codex", "--codex-home", str(home))
        self.assertEqual((home / "skills/mine/keep").read_text(), "keep")
        self.assertIn("references/model-policy.md", (home / "skills/github-pr-review/SKILL.md").read_text())
        self.assertFalse((home / "agent-skills-profile.json").exists())
        profile_home = self.work / "profile"
        self.sync("gpt-6", profile_home)
        self.run_command("bash", "scripts/sync_skills.sh", "--agent", "codex", "--codex-home", str(profile_home), ok=False)

    def test_variants_require_evidence_and_only_affect_selected_profile(self):
        root = self.work / "source"
        for name in ("codex", "profiles", "policies", "variants"):
            shutil.copytree(ROOT / name, root / name)
        variant = root / "variants/gpt-6/team-dev"
        variant.mkdir()
        (variant / "instructions.md").write_text("Apply the measured adjustment.\n")
        with self.assertRaises(ValueError):
            build(self.work / "missing-evidence", "gpt-6", root)
        (variant / "evidence.md").write_text("Fixture task and measured outcome.\n")
        for profile in ("gpt-6", "gpt-5.6"):
            output = self.work / profile
            build(output, profile, root)
            self.assertEqual((output / "skills/team-dev/references/model-variant.md").exists(), profile == "gpt-6")
        (variant / "instructions.md").write_text("[broken](missing.md)\n")
        with self.assertRaises(ValueError):
            build(self.work / "broken-link", "gpt-6", root)
        self.assertFalse((self.work / "broken-link").exists())


if __name__ == "__main__":
    unittest.main()
