import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional


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
        stale = self.run_manager("check")
        rebuilt = self.run_manager("build")

        self.assertEqual(stale.returncode, 1)
        self.assertIn("stale document", stale.stderr)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
        self.assertIn("- new", (self.repo / "AGENTS.md").read_text())
        self.assertEqual(self.run_manager("check").returncode, 0)

    def test_legacy_default_layout_without_marker_still_builds(self) -> None:
        (self.repo / "ai/.agent-docs-layout.json").unlink()
        self.write_root_fragment("# Rules\n\n- shared\n")

        built = self.run_manager("build")

        self.assertEqual(built.returncode, 0, built.stderr)
        self.assertEqual(self.run_manager("check").returncode, 0)

    def test_layout_marker_cannot_repoint_manager(self) -> None:
        (self.repo / "ai/.agent-docs-layout.json").write_text(
            '{\n  "agent_docs_dir": "tools/agent-docs",\n  "version": 1\n}\n',
            encoding="utf-8",
        )

        checked = self.run_manager("check")

        self.assertEqual(checked.returncode, 2)
        self.assertIn(
            "layout config does not match the manager path",
            checked.stderr,
        )

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

    def run_installed_manager(
        self,
        agent_docs_dir: str,
        command: str,
        cwd: Optional[Path] = None,
    ) -> subprocess.CompletedProcess:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                "python3",
                str(self.repo / agent_docs_dir / "manage-agent-docs.py"),
                command,
            ],
            cwd=cwd or self.repo,
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
        self.assertIn("--agent-docs-dir .agent-docs", result.stderr)
        self.assertIn("--agent-docs-dir tools/agent-docs", result.stderr)
        self.assertFalse((namespace / "manage-agent-docs.py").exists())

    def test_alternate_nested_directory_installs_and_builds(self) -> None:
        (self.repo / ".git").mkdir()
        namespace = self.repo / "ai"
        namespace.mkdir()
        existing = namespace / "__init__.py"
        existing.write_text("# repository package\n", encoding="utf-8")

        installed = self.run_scaffolder(
            "--agent-docs-dir", "tools/agent-docs"
        )
        scaffold_checked = self.run_scaffolder(
            "--agent-docs-dir", "tools/agent-docs", "--check"
        )

        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(
            scaffold_checked.returncode, 0, scaffold_checked.stderr
        )
        self.assertEqual(
            existing.read_text(encoding="utf-8"), "# repository package\n"
        )
        source_root = self.repo / "tools/agent-docs"
        readme = (source_root / "README.md").read_text(encoding="utf-8")
        self.assertIn("tools/agent-docs/fragments/", readme)
        self.assertIn(
            "python3 tools/agent-docs/manage-agent-docs.py check", readme
        )
        self.assertNotIn("{{AGENT_DOCS_DIR}}", readme)

        (source_root / "fragments/10-root.md").write_text(
            "# Rules\n\n- shared\n", encoding="utf-8"
        )
        (source_root / "rules/python.md").write_text(
            "---\npaths:\n  - \"**/*.py\"\n---\n\n# Python\n",
            encoding="utf-8",
        )

        built = self.run_installed_manager("tools/agent-docs", "build")
        checked = self.run_installed_manager("tools/agent-docs", "check")
        wrong_root = self.run_installed_manager(
            "tools/agent-docs", "check", cwd=SKILL_ROOT
        )

        self.assertEqual(built.returncode, 0, built.stderr)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(wrong_root.returncode, 2)
        self.assertIn("Git repository root", wrong_root.stderr)
        self.assertTrue(
            (source_root / ".agent-docs-manifest.json").is_file()
        )
        self.assertFalse((namespace / ".agent-docs-manifest.json").exists())
        self.assertTrue((self.repo / "AGENTS.md").is_file())
        self.assertTrue((self.repo / ".claude/rules/python.md").is_file())

    def test_unsafe_agent_docs_directories_are_rejected(self) -> None:
        for value in (
            "../agent-docs",
            "/tmp/agent-docs",
            ".claude/agent-docs",
            "tools//agent-docs",
            "AGENTS.md",
            "agent docs",
            "agent;docs",
            "-agent-docs",
        ):
            with self.subTest(value=value):
                arguments = (
                    (f"--agent-docs-dir={value}",)
                    if value.startswith("-")
                    else ("--agent-docs-dir", value)
                )
                result = self.run_scaffolder(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertIn("agent documentation directory", result.stderr)

    def test_existing_ai_file_is_reported_as_a_namespace_conflict(self) -> None:
        (self.repo / "ai").write_text("reserved\n", encoding="utf-8")

        result = self.run_scaffolder()

        self.assertEqual(result.returncode, 1)
        self.assertIn("ai/ is already repository-owned", result.stderr)
        self.assertEqual(
            (self.repo / "ai").read_text(encoding="utf-8"), "reserved\n"
        )

    def test_non_directory_parent_blocks_nested_scaffold(self) -> None:
        parent = self.repo / "tools"
        parent.write_text("reserved\n", encoding="utf-8")

        result = self.run_scaffolder(
            "--agent-docs-dir", "tools/agent-docs"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "tools/agent-docs/ is already repository-owned", result.stderr
        )
        self.assertEqual(parent.read_text(encoding="utf-8"), "reserved\n")

    def test_installed_scaffold_is_not_reported_as_namespace_conflict(self) -> None:
        installed = self.run_scaffolder()
        checked = self.run_scaffolder("--check")

        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertNotIn("repository-owned", checked.stderr)
        self.assertTrue(
            (self.repo / "ai/.agent-docs-layout.json").is_file()
        )
        self.assertNotIn(
            "{{AGENT_DOCS_DIR}}",
            (self.repo / "ai/README.md").read_text(encoding="utf-8"),
        )

    def test_modified_scaffold_file_does_not_suggest_changing_roots(self) -> None:
        installed = self.run_scaffolder()
        self.assertEqual(installed.returncode, 0, installed.stderr)
        readme = self.repo / "ai/README.md"
        readme.write_text("# Local maintenance notes\n", encoding="utf-8")

        result = self.run_scaffolder()

        self.assertEqual(result.returncode, 1)
        self.assertIn("modified scaffold file", result.stderr)
        self.assertIn("Do not select another", result.stderr)
        self.assertNotIn("--agent-docs-dir .agent-docs", result.stderr)
        self.assertEqual(
            readme.read_text(encoding="utf-8"),
            "# Local maintenance notes\n",
        )

    def test_legacy_scaffold_conflict_does_not_suggest_changing_roots(
        self,
    ) -> None:
        namespace = self.repo / "ai"
        namespace.mkdir()
        (namespace / "manage-agent-docs.py").write_text(
            '"""Generate and check repository agent documentation '
            'from shared sources."""\n',
            encoding="utf-8",
        )
        (namespace / "fragments").mkdir()
        (namespace / "rules").mkdir()

        result = self.run_scaffolder()

        self.assertEqual(result.returncode, 1)
        self.assertIn("modified scaffold file", result.stderr)
        self.assertNotIn("--agent-docs-dir .agent-docs", result.stderr)


if __name__ == "__main__":
    unittest.main()
