#!/usr/bin/env python3
"""Generate and check repository agent documentation from shared sources."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Dict, List, Mapping, Sequence, Tuple


LAYOUT_FILENAME = ".agent-docs-layout.json"
LAYOUT_VERSION = 1
MANIFEST_VERSION = 1
SAFE_PATH_COMPONENT = re.compile(r"[A-Za-z0-9._][A-Za-z0-9._-]*\Z")


class AgentDocsError(Exception):
    """Report an invalid source layout or unsafe generation request."""


@dataclass(frozen=True)
class ManagedState:
    documents: Dict[str, str]
    claude_rules: Dict[str, str]


@dataclass(frozen=True)
class RepositoryLayout:
    root: Path
    agent_docs_dir: PurePosixPath

    @property
    def source_root(self) -> Path:
        return self.root.joinpath(*self.agent_docs_dir.parts)

    @property
    def fragments_root(self) -> Path:
        return self.source_root / "fragments"

    @property
    def rules_root(self) -> Path:
        return self.source_root / "rules"

    @property
    def manifest_relative_path(self) -> str:
        return (self.agent_docs_dir / ".agent-docs-manifest.json").as_posix()

    @property
    def manager_relative_path(self) -> str:
        return (self.agent_docs_dir / "manage-agent-docs.py").as_posix()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_agent_docs_dir(value: object) -> PurePosixPath:
    if not isinstance(value, str):
        raise AgentDocsError("layout field 'agent_docs_dir' must be a string")
    if "\\" in value:
        raise AgentDocsError(
            f"agent documentation directory contains a backslash: {value!r}"
        )
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or not relative.parts
        or ".." in relative.parts
        or relative.as_posix() != value
    ):
        raise AgentDocsError(
            f"unsafe agent documentation directory: {value!r}"
        )
    if relative.parts[0] in {".git", ".claude"}:
        raise AgentDocsError(
            "agent documentation directory cannot be inside "
            f"{relative.parts[0]}/: {value!r}"
        )
    if any(not SAFE_PATH_COMPONENT.fullmatch(part) for part in relative.parts):
        raise AgentDocsError(
            "agent documentation directory contains unsupported "
            f"characters: {value!r}"
        )
    if relative.name in {"AGENTS.md", "CLAUDE.md"}:
        raise AgentDocsError(
            "agent documentation directory conflicts with a generated "
            f"document name: {value!r}"
        )
    return relative


def load_repository_layout(
    manager_path: Path, invocation_root: Path
) -> RepositoryLayout:
    source_root = manager_path.resolve(strict=True).parent
    config_path = source_root / LAYOUT_FILENAME
    if not config_path.exists():
        if source_root.name != "ai":
            raise AgentDocsError(
                f"layout config is missing: {config_path}"
            )
        return RepositoryLayout(
            source_root.parent.resolve(strict=True), PurePosixPath("ai")
        )
    if not config_path.is_file():
        raise AgentDocsError(f"layout config is not a file: {config_path}")
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AgentDocsError(f"cannot read {config_path}: {error}") from error
    if not isinstance(payload, dict) or payload.get("version") != LAYOUT_VERSION:
        raise AgentDocsError(
            f"{config_path} must use layout version {LAYOUT_VERSION}"
        )
    agent_docs_dir = parse_agent_docs_dir(payload.get("agent_docs_dir"))
    root = invocation_root.resolve(strict=True)
    if not root.is_dir():
        raise AgentDocsError(
            f"repository root is not a directory: {root}"
        )
    git_root = next(
        (
            candidate
            for candidate in (source_root, *source_root.parents)
            if (candidate / ".git").exists()
        ),
        None,
    )
    if git_root is not None and root != git_root:
        raise AgentDocsError(
            f"run the command from the Git repository root: {git_root}"
        )
    expected_source = root.joinpath(*agent_docs_dir.parts).resolve(strict=False)
    if expected_source != source_root:
        raise AgentDocsError(
            "layout config does not match the manager path from the current "
            f"repository root: {config_path}. Run the command from the "
            "repository root."
        )
    return RepositoryLayout(root, agent_docs_dir)


def ensure_within_root(layout: RepositoryLayout, path: Path, label: str) -> Path:
    try:
        path.resolve(strict=False).relative_to(layout.root.resolve(strict=True))
    except (OSError, ValueError) as error:
        raise AgentDocsError(f"{label} escapes the repository: {path}") from error
    return path


def repo_path(layout: RepositoryLayout, relative: str, section: str) -> Path:
    if "\\" in relative:
        raise AgentDocsError(
            f"invalid {section} manifest path with a backslash: {relative!r}"
        )
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts:
        raise AgentDocsError(f"unsafe {section} manifest path: {relative!r}")
    if pure.as_posix() != relative:
        raise AgentDocsError(f"non-canonical {section} manifest path: {relative!r}")
    if section == "documents" and pure.name not in {"AGENTS.md", "CLAUDE.md"}:
        raise AgentDocsError(f"invalid managed document path: {relative!r}")
    if section == "documents":
        forbidden_prefixes = (
            (".git",),
            (".claude", "rules"),
            (*layout.agent_docs_dir.parts, "fragments"),
            (*layout.agent_docs_dir.parts, "rules"),
        )
        if any(
            pure.parts[: len(prefix)] == prefix
            for prefix in forbidden_prefixes
        ):
            raise AgentDocsError(
                f"forbidden managed document path: {relative!r}"
            )
    if section == "claude_rules" and pure.parts[:2] != (".claude", "rules"):
        raise AgentDocsError(f"invalid managed Claude rule path: {relative!r}")
    return ensure_within_root(
        layout,
        layout.root.joinpath(*pure.parts),
        f"managed {section} path",
    )


def validate_hash_map(
    value: object, section: str, layout: RepositoryLayout
) -> Dict[str, str]:
    if not isinstance(value, dict):
        raise AgentDocsError(f"manifest field {section!r} must be an object")
    result: Dict[str, str] = {}
    for relative, digest in value.items():
        if not isinstance(relative, str) or not isinstance(digest, str):
            raise AgentDocsError(
                f"manifest field {section!r} must map paths to SHA-256 strings"
            )
        repo_path(layout, relative, section)
        if len(digest) != 64 or any(
            char not in "0123456789abcdef" for char in digest
        ):
            raise AgentDocsError(
                f"manifest contains an invalid SHA-256 for {relative!r}"
            )
        result[relative] = digest
    return result


def load_manifest(layout: RepositoryLayout) -> Tuple[ManagedState, bool]:
    manifest_path = ensure_within_root(
        layout,
        layout.root / layout.manifest_relative_path,
        "manifest path",
    )
    if not manifest_path.exists():
        return ManagedState({}, {}), False
    if not manifest_path.is_file():
        raise AgentDocsError(f"manifest path is not a file: {manifest_path}")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AgentDocsError(f"cannot read {manifest_path}: {error}") from error
    if not isinstance(payload, dict) or payload.get("version") != MANIFEST_VERSION:
        raise AgentDocsError(
            f"{manifest_path} must use manifest version {MANIFEST_VERSION}"
        )
    documents = validate_hash_map(
        payload.get("documents"), "documents", layout
    )
    rules = validate_hash_map(
        payload.get("claude_rules"), "claude_rules", layout
    )
    return ManagedState(documents, rules), True


def target_for_fragment(name: str) -> Tuple[str, ...]:
    if name.endswith(".agents.md"):
        return ("agents",)
    if name.endswith(".claude.md"):
        return ("claude",)
    return ("agents", "claude")


def read_fragment(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise AgentDocsError(f"cannot read fragment {path}: {error}") from error
    if not content.strip():
        raise AgentDocsError(f"fragment is empty: {path}")
    first_line = content.lstrip("\ufeff").splitlines()[0].strip()
    if first_line in {"# AGENTS.md", "# CLAUDE.md"}:
        raise AgentDocsError(
            f"fragment repeats a generated document title: {path}"
        )
    return content.rstrip()


def render_document(title: str, fragments: Sequence[Path]) -> bytes:
    sections = [f"# {title}"]
    for fragment in fragments:
        sections.extend(("", read_fragment(fragment)))
    return ("\n".join(sections) + "\n").encode("utf-8")


def discover_documents(layout: RepositoryLayout) -> Dict[str, bytes]:
    fragments_root = ensure_within_root(
        layout, layout.fragments_root, "fragment source directory"
    )
    if not fragments_root.is_dir():
        raise AgentDocsError(f"fragment directory does not exist: {fragments_root}")

    groups: Dict[PurePosixPath, List[Path]] = {}
    candidates = sorted(
        (path for path in fragments_root.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(fragments_root).as_posix(),
    )
    for fragment in candidates:
        ensure_within_root(layout, fragment, "fragment source")
        relative_parent = fragment.parent.relative_to(fragments_root)
        relative = PurePosixPath(relative_parent.as_posix())
        groups.setdefault(relative, []).append(fragment)

    root_key = PurePosixPath(".")
    if root_key not in groups:
        raise AgentDocsError(
            f"add at least one root fragment directly under {fragments_root}"
        )

    outputs: Dict[str, bytes] = {}
    for relative_dir, fragments in sorted(
        groups.items(), key=lambda item: item[0].as_posix()
    ):
        output_dir = (
            layout.root
            if relative_dir == root_key
            else layout.root.joinpath(*relative_dir.parts)
        )
        if not output_dir.is_dir():
            raise AgentDocsError(
                "fragment directory has no matching repository directory: "
                f"{layout.agent_docs_dir.as_posix()}/fragments/"
                f"{relative_dir.as_posix()}"
            )
        for target, filename in (("agents", "AGENTS.md"), ("claude", "CLAUDE.md")):
            selected = [
                fragment
                for fragment in fragments
                if target in target_for_fragment(fragment.name)
            ]
            if not selected:
                if relative_dir == root_key:
                    raise AgentDocsError(
                        f"root fragments do not produce the required {filename}"
                    )
                continue
            output_path = output_dir / filename
            relative_output = output_path.relative_to(layout.root).as_posix()
            outputs[relative_output] = render_document(filename, selected)
    return outputs


def discover_claude_rules(layout: RepositoryLayout) -> Dict[str, bytes]:
    rules_root = ensure_within_root(
        layout, layout.rules_root, "rule source directory"
    )
    if not rules_root.exists():
        return {}
    if not rules_root.is_dir():
        raise AgentDocsError(f"rule source is not a directory: {rules_root}")

    outputs: Dict[str, bytes] = {}
    for source in sorted(
        (path for path in rules_root.rglob("*.md") if path.is_file()),
        key=lambda path: path.relative_to(rules_root).as_posix(),
    ):
        ensure_within_root(layout, source, "rule source")
        try:
            data = source.read_bytes()
            data.decode("utf-8")
        except (OSError, UnicodeError) as error:
            raise AgentDocsError(f"cannot read rule {source}: {error}") from error
        relative = source.relative_to(rules_root)
        target = Path(".claude/rules") / relative
        outputs[target.as_posix()] = data
    return outputs


def expected_state(
    documents: Mapping[str, bytes], rules: Mapping[str, bytes]
) -> ManagedState:
    return ManagedState(
        {relative: sha256(data) for relative, data in sorted(documents.items())},
        {relative: sha256(data) for relative, data in sorted(rules.items())},
    )


def reject_output_collisions(
    documents: Mapping[str, bytes], rules: Mapping[str, bytes]
) -> None:
    collisions = sorted(set(documents) & set(rules))
    if collisions:
        raise AgentDocsError(
            "document and Claude rule sources target the same path: "
            + ", ".join(collisions)
        )


def manifest_bytes(state: ManagedState) -> bytes:
    payload = {
        "version": MANIFEST_VERSION,
        "documents": state.documents,
        "claude_rules": state.claude_rules,
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_existing(path: Path) -> bytes:
    if not path.is_file():
        raise AgentDocsError(f"managed output path is not a regular file: {path}")
    try:
        return path.read_bytes()
    except OSError as error:
        raise AgentDocsError(f"cannot read managed output {path}: {error}") from error


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=str(path.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o644)
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()


def stale_removed_paths(
    layout: RepositoryLayout,
    previous: Mapping[str, str],
    expected: Mapping[str, bytes],
    section: str,
) -> List[str]:
    errors: List[str] = []
    for relative, old_digest in previous.items():
        if relative in expected:
            continue
        path = repo_path(layout, relative, section)
        if path.exists() and sha256(read_existing(path)) != old_digest:
            errors.append(
                f"refusing to remove modified obsolete managed file: {relative}"
            )
    return errors


def modified_managed_paths(
    layout: RepositoryLayout,
    previous: Mapping[str, str],
    expected: Mapping[str, bytes],
    section: str,
) -> List[str]:
    errors: List[str] = []
    for relative in sorted(set(previous) & set(expected)):
        path = repo_path(layout, relative, section)
        if not path.exists():
            continue
        actual = read_existing(path)
        if sha256(actual) != previous[relative] and actual != expected[relative]:
            errors.append(
                f"refusing to replace modified managed {section} file: {relative}"
            )
    return errors


def alternate_instruction_paths(relative: str) -> Tuple[str, ...]:
    pure = PurePosixPath(relative)
    if pure.name == "AGENTS.md":
        return ((pure.parent / "AGENTS.override.md").as_posix(),)
    if pure.name == "CLAUDE.md":
        return ((pure.parent / ".claude/CLAUDE.md").as_posix(),)
    return ()


def active_alternate_configs(
    layout: RepositoryLayout, documents: Mapping[str, bytes]
) -> List[str]:
    errors: List[str] = []
    seen = set()
    for relative in sorted(documents):
        for alternate in alternate_instruction_paths(relative):
            if alternate in seen:
                continue
            seen.add(alternate)
            path = ensure_within_root(
                layout,
                layout.root.joinpath(*PurePosixPath(alternate).parts),
                "alternate instruction path",
            )
            if alternate in documents or path.exists():
                errors.append(
                    "active alternate instruction conflicts with managed output: "
                    f"{alternate}"
                )
    return errors


def print_conflict_alternatives(errors: Sequence[str]) -> None:
    print("Safe alternatives:", file=sys.stderr)
    if any(".claude/CLAUDE.md" in error for error in errors):
        print(
            "- Preserve .claude/CLAUDE.md as canonical and adapt the generator, "
            "manifest, commands, and CI to write there.",
            file=sys.stderr,
        )
        print(
            "- Or migrate its retained content into fragments, generate root "
            "CLAUDE.md, and then remove the alternate file explicitly.",
            file=sys.stderr,
        )
    if any("AGENTS.override.md" in error for error in errors):
        print(
            "- Preserve AGENTS.override.md as canonical and adapt the managed "
            "outputs so they do not generate a shadowed AGENTS.md at that scope.",
            file=sys.stderr,
        )
        print(
            "- Or migrate its retained content into fragments and remove the "
            "override only after verifying the effective instruction chain.",
            file=sys.stderr,
        )
    if any("unmanaged" in error or "modified managed" in error for error in errors):
        print(
            "- Preserve the existing file and adapt the managed output set, or "
            "migrate its authoritative content into fragments or rules before "
            "adoption.",
            file=sys.stderr,
        )
    print(
        "Choose the option that preserves repository conventions; do not delete "
        "a conflicting file merely to make generation pass.",
        file=sys.stderr,
    )


def unmanaged_conflicts(
    layout: RepositoryLayout,
    expected: Mapping[str, bytes],
    previous: Mapping[str, str],
    section: str,
    adopt_existing: bool,
) -> List[str]:
    if adopt_existing:
        return []
    errors: List[str] = []
    for relative, expected_data in expected.items():
        path = repo_path(layout, relative, section)
        if not path.exists() or relative in previous:
            continue
        actual = read_existing(path)
        if actual != expected_data:
            errors.append(
                f"refusing to replace unmanaged {section} file: {relative}"
            )
    return errors


def remove_obsolete(
    layout: RepositoryLayout,
    previous: Mapping[str, str],
    expected: Mapping[str, bytes],
    section: str,
) -> None:
    for relative in sorted(set(previous) - set(expected), reverse=True):
        path = repo_path(layout, relative, section)
        if not path.exists():
            continue
        path.unlink()
        print(f"removed {relative}")
        if section == "claude_rules":
            rules_root = layout.root / ".claude/rules"
            parent = path.parent
            while parent != rules_root and rules_root in parent.parents:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent


def build(layout: RepositoryLayout, adopt_existing: bool) -> int:
    documents = discover_documents(layout)
    rules = discover_claude_rules(layout)
    reject_output_collisions(documents, rules)
    previous, _ = load_manifest(layout)

    errors: List[str] = []
    errors.extend(active_alternate_configs(layout, documents))
    errors.extend(
        unmanaged_conflicts(
            layout,
            documents,
            previous.documents,
            "documents",
            adopt_existing,
        )
    )
    errors.extend(
        unmanaged_conflicts(
            layout,
            rules,
            previous.claude_rules,
            "claude_rules",
            adopt_existing,
        )
    )
    errors.extend(
        stale_removed_paths(
            layout, previous.documents, documents, "documents"
        )
    )
    errors.extend(
        stale_removed_paths(
            layout, previous.claude_rules, rules, "claude_rules"
        )
    )
    errors.extend(
        modified_managed_paths(
            layout, previous.documents, documents, "documents"
        )
    )
    errors.extend(
        modified_managed_paths(
            layout, previous.claude_rules, rules, "claude_rules"
        )
    )
    if errors:
        for error in errors:
            print(f"[blocked] {error}", file=sys.stderr)
        print_conflict_alternatives(errors)
        if any("active alternate instruction" in error for error in errors):
            print(
                "--adopt-existing does not bypass alternate-instruction conflicts.",
                file=sys.stderr,
            )
        return 1

    remove_obsolete(layout, previous.documents, documents, "documents")
    remove_obsolete(layout, previous.claude_rules, rules, "claude_rules")

    for relative, data in sorted(documents.items()):
        path = repo_path(layout, relative, "documents")
        atomic_write(path, data)
        print(f"wrote {relative}")
    for relative, data in sorted(rules.items()):
        path = repo_path(layout, relative, "claude_rules")
        atomic_write(path, data)
        print(f"wrote {relative}")

    state = expected_state(documents, rules)
    manifest_path = ensure_within_root(
        layout,
        layout.root / layout.manifest_relative_path,
        "manifest path",
    )
    atomic_write(manifest_path, manifest_bytes(state))
    print(f"wrote {layout.manifest_relative_path}")
    return 0


def print_diff(relative: str, actual: bytes, expected: bytes) -> None:
    try:
        actual_text = actual.decode("utf-8").splitlines()
        expected_text = expected.decode("utf-8").splitlines()
    except UnicodeError:
        return
    diff = list(
        difflib.unified_diff(
            actual_text,
            expected_text,
            fromfile=relative,
            tofile=f"{relative} (expected)",
            lineterm="",
        )
    )
    for line in diff[:80]:
        print(line)
    if len(diff) > 80:
        print("... diff truncated ...")


def check_outputs(
    layout: RepositoryLayout,
    expected: Mapping[str, bytes],
    label: str,
    section: str,
) -> List[str]:
    issues: List[str] = []
    for relative, expected_data in sorted(expected.items()):
        path = repo_path(layout, relative, section)
        if not path.exists():
            issues.append(f"missing {label}: {relative}")
            continue
        actual = read_existing(path)
        if actual != expected_data:
            issues.append(f"stale {label}: {relative}")
            print_diff(relative, actual, expected_data)
    return issues


def check(layout: RepositoryLayout) -> int:
    documents = discover_documents(layout)
    rules = discover_claude_rules(layout)
    reject_output_collisions(documents, rules)
    expected = expected_state(documents, rules)
    previous, manifest_exists = load_manifest(layout)

    alternate_issues = active_alternate_configs(layout, documents)
    issues: List[str] = []
    issues.extend(alternate_issues)
    issues.extend(
        check_outputs(layout, documents, "document", "documents")
    )
    issues.extend(
        check_outputs(layout, rules, "Claude rule", "claude_rules")
    )
    if not manifest_exists:
        issues.append(f"missing manifest: {layout.manifest_relative_path}")
    else:
        manifest_path = ensure_within_root(
            layout,
            layout.root / layout.manifest_relative_path,
            "manifest path",
        )
        if read_existing(manifest_path) != manifest_bytes(expected):
            issues.append(
                f"stale manifest: {layout.manifest_relative_path}"
            )

    for relative in sorted(set(previous.documents) - set(documents)):
        if repo_path(layout, relative, "documents").exists():
            issues.append(f"obsolete managed document: {relative}")
    for relative in sorted(set(previous.claude_rules) - set(rules)):
        if repo_path(layout, relative, "claude_rules").exists():
            issues.append(f"obsolete managed Claude rule: {relative}")

    if issues:
        for issue in issues:
            print(f"[stale] {issue}", file=sys.stderr)
        if alternate_issues:
            print_conflict_alternatives(alternate_issues)
        if len(issues) > len(alternate_issues):
            print(
                "Run "
                f"'python3 {layout.manager_relative_path} build' "
                "to regenerate.",
                file=sys.stderr,
            )
        return 1

    print("[ok] agent documents, Claude rules, and manifest are in sync")
    return 0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build", help="regenerate managed outputs")
    build_parser.add_argument(
        "--adopt-existing",
        action="store_true",
        help="replace colliding unmanaged outputs after their content was migrated",
    )
    subparsers.add_parser("check", help="fail when managed outputs are stale")
    return parser.parse_args(argv)


def main(argv: Sequence[str] = tuple(sys.argv[1:])) -> int:
    args = parse_args(argv)
    try:
        layout = load_repository_layout(Path(__file__), Path.cwd())
        if args.command == "build":
            return build(layout, args.adopt_existing)
        return check(layout)
    except (AgentDocsError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
