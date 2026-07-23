import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import List


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLDER = SKILL_ROOT / "scripts/scaffold_agent_docs.py"


class ManageAgentDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()
        result = self.run_command(
            ["python3", str(SCAFFOLDER), "--repo", str(self.repo)]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.manager = self.repo / "ai/manage-agent-docs.py"

    def run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            command,
            cwd=self.repo if self.repo.exists() else SKILL_ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_manager(self, command: str) -> subprocess.CompletedProcess:
        return self.run_command(["python3", str(self.manager), command])

    def write_root_fragment(self, content: str) -> None:
        (self.repo / "ai/fragments/10-root.md").write_text(
            content, encoding="utf-8"
        )

    def test_source_change_rebuilds_unmodified_outputs(self) -> None:
        self.write_root_fragment("# Rules\n\n- old\n")
        self.assertEqual(self.run_manager("build").returncode, 0)

        self.write_root_fragment("# Rules\n\n- new\n")
        rebuilt = self.run_manager("build")

        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        self.assertIn("- new", (self.repo / "AGENTS.md").read_text())
        self.assertEqual(self.run_manager("check").returncode, 0)

    def test_modified_managed_output_is_preserved_until_migrated(self) -> None:
        self.write_root_fragment("# Rules\n\n- old\n")
        self.assertEqual(self.run_manager("build").returncode, 0)
        agents = self.repo / "AGENTS.md"
        manual_content = "# AGENTS.md\n\n# Rules\n\n- manual\n"
        agents.write_text(manual_content, encoding="utf-8")

        blocked = self.run_manager("build")

        self.assertEqual(blocked.returncode, 1)
        self.assertIn("modified managed documents file: AGENTS.md", blocked.stderr)
        self.assertEqual(agents.read_text(encoding="utf-8"), manual_content)

        self.write_root_fragment("# Rules\n\n- manual\n")
        migrated = self.run_manager("build")
        self.assertEqual(migrated.returncode, 0, migrated.stderr)
        self.assertEqual(self.run_manager("check").returncode, 0)

    def test_active_alternate_configs_block_build_and_check(self) -> None:
        self.write_root_fragment("# Rules\n\n- shared\n")
        self.assertEqual(self.run_manager("build").returncode, 0)
        (self.repo / "AGENTS.override.md").write_text(
            "# Override\n", encoding="utf-8"
        )
        claude_directory = self.repo / ".claude"
        claude_directory.mkdir()
        (claude_directory / "CLAUDE.md").write_text(
            "# Alternate\n", encoding="utf-8"
        )

        checked = self.run_manager("check")
        built = self.run_manager("build")

        self.assertEqual(checked.returncode, 1)
        self.assertEqual(built.returncode, 1)
        for result in (checked, built):
            self.assertIn("AGENTS.override.md", result.stderr)
            self.assertIn(".claude/CLAUDE.md", result.stderr)
            self.assertIn("Safe alternatives:", result.stderr)
            self.assertIn(
                "Preserve .claude/CLAUDE.md as canonical", result.stderr
            )
            self.assertIn(
                "Preserve AGENTS.override.md as canonical", result.stderr
            )

    def test_generated_root_and_dot_claude_documents_are_rejected(self) -> None:
        self.write_root_fragment("# Rules\n\n- shared\n")
        (self.repo / ".claude").mkdir()
        alternate_source = self.repo / "ai/fragments/.claude"
        alternate_source.mkdir()
        (alternate_source / "10-alternate.claude.md").write_text(
            "# Alternate\n", encoding="utf-8"
        )

        built = self.run_manager("build")

        self.assertEqual(built.returncode, 1)
        self.assertIn(".claude/CLAUDE.md", built.stderr)
        self.assertFalse((self.repo / "AGENTS.md").exists())


class ScaffoldAgentDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()

    def run_scaffolder(
        self, *extra_arguments: str
    ) -> subprocess.CompletedProcess:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                "python3",
                str(SCAFFOLDER),
                "--repo",
                str(self.repo),
                *extra_arguments,
            ],
            cwd=SKILL_ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_existing_ai_namespace_reports_safe_alternatives(self) -> None:
        namespace = self.repo / "ai"
        namespace.mkdir()
        (namespace / "__init__.py").write_text("", encoding="utf-8")

        result = self.run_scaffolder()

        self.assertEqual(result.returncode, 1)
        self.assertIn("ai/ is already repository-owned", result.stderr)
        self.assertIn("Safe alternatives:", result.stderr)
        self.assertIn(".agent-docs/", result.stderr)
        self.assertIn("tools/agent-docs/", result.stderr)
        self.assertFalse((namespace / "manage-agent-docs.py").exists())

    def test_installed_scaffold_is_not_reported_as_namespace_conflict(self) -> None:
        installed = self.run_scaffolder()
        checked = self.run_scaffolder("--check")

        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertNotIn("repository-owned", checked.stderr)


if __name__ == "__main__":
    unittest.main()
