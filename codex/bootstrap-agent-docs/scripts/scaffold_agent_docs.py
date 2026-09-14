#!/usr/bin/env python3
"""Install the reusable agent-documentation tooling into a repository."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Dict, Mapping, Sequence, Tuple


SKILL_ROOT = Path(__file__).resolve().parent.parent
MANAGER_ASSET = SKILL_ROOT / "assets/manage-agent-docs.py"
README_TEMPLATE = SKILL_ROOT / "assets/AI-README.md"
LAYOUT_FILENAME = ".agent-docs-layout.json"
LAYOUT_VERSION = 1
DEFAULT_AGENT_DOCS_DIR = PurePosixPath("ai")
SOURCE_DIRECTORY_NAMES = ("fragments", "rules")
ALTERNATE_ROOTS = (
    PurePosixPath(".agent-docs"),
    PurePosixPath("tools/agent-docs"),
    PurePosixPath("docs/agent-docs"),
)
README_TOKEN = "{{AGENT_DOCS_DIR}}"
SAFE_PATH_COMPONENT = re.compile(r"[A-Za-z0-9._][A-Za-z0-9._-]*\Z")


class ScaffoldError(Exception):
    """Report a conflict or unsafe scaffold target."""


def parse_agent_docs_dir(value: str) -> PurePosixPath:
    if "\\" in value:
        raise ScaffoldError(
            f"agent documentation directory contains a backslash: {value!r}"
        )
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or not relative.parts
        or ".." in relative.parts
        or relative.as_posix() != value
    ):
        raise ScaffoldError(
            f"unsafe agent documentation directory: {value!r}"
        )
    if relative.parts[0] in {".git", ".claude"}:
        raise ScaffoldError(
            "agent documentation directory cannot be inside "
            f"{relative.parts[0]}/: {value!r}"
        )
    if any(not SAFE_PATH_COMPONENT.fullmatch(part) for part in relative.parts):
        raise ScaffoldError(
            "agent documentation directory contains unsupported "
            f"characters: {value!r}"
        )
    if relative.name in {"AGENTS.md", "CLAUDE.md"}:
        raise ScaffoldError(
            "agent documentation directory conflicts with a generated "
            f"document name: {value!r}"
        )
    return relative


def filesystem_path(relative: PurePosixPath) -> Path:
    return Path(*relative.parts)


def render_readme(agent_docs_dir: PurePosixPath) -> bytes:
    if not README_TEMPLATE.is_file():
        raise ScaffoldError(f"skill asset is missing: {README_TEMPLATE}")
    try:
        template = README_TEMPLATE.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ScaffoldError(
            f"cannot read skill asset {README_TEMPLATE}: {error}"
        ) from error
    if README_TOKEN not in template:
        raise ScaffoldError(
            f"README template is missing {README_TOKEN!r}: {README_TEMPLATE}"
        )
    return template.replace(
        README_TOKEN, agent_docs_dir.as_posix()
    ).encode("utf-8")


def layout_bytes(agent_docs_dir: PurePosixPath) -> bytes:
    payload = {
        "version": LAYOUT_VERSION,
        "agent_docs_dir": agent_docs_dir.as_posix(),
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def expected_files(
    agent_docs_dir: PurePosixPath,
) -> Dict[Path, Tuple[bytes, bool]]:
    if not MANAGER_ASSET.is_file():
        raise ScaffoldError(f"skill asset is missing: {MANAGER_ASSET}")
    root = filesystem_path(agent_docs_dir)
    try:
        manager_data = MANAGER_ASSET.read_bytes()
    except OSError as error:
        raise ScaffoldError(
            f"cannot read skill asset {MANAGER_ASSET}: {error}"
        ) from error
    return {
        root / "manage-agent-docs.py": (manager_data, True),
        root / "README.md": (render_readme(agent_docs_dir), False),
        root / LAYOUT_FILENAME: (layout_bytes(agent_docs_dir), False),
    }


def source_directories(agent_docs_dir: PurePosixPath) -> Tuple[Path, ...]:
    root = filesystem_path(agent_docs_dir)
    return tuple(root / name for name in SOURCE_DIRECTORY_NAMES)


def within_repository(root: Path, target: Path) -> bool:
    try:
        target.resolve(strict=False).relative_to(root.resolve(strict=True))
    except (OSError, ValueError):
        return False
    return True


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


def inspect_targets(
    root: Path,
    files: Mapping[Path, Tuple[bytes, bool]],
    directories: Sequence[Path],
) -> Dict[Path, str]:
    statuses: Dict[Path, str] = {}
    for relative, (expected_data, _) in files.items():
        target = root / relative
        if not within_repository(root, target):
            raise ScaffoldError(
                f"target escapes the repository through a symlink: {target}"
            )
        if not target.exists():
            statuses[relative] = "create"
        elif target.is_file() and target.read_bytes() == expected_data:
            statuses[relative] = "unchanged"
        else:
            statuses[relative] = "conflict"
    for relative in directories:
        target = root / relative
        if not within_repository(root, target):
            raise ScaffoldError(
                f"target escapes the repository through a symlink: {target}"
            )
        if not target.exists():
            statuses[relative] = "create-directory"
        elif target.is_dir():
            statuses[relative] = "unchanged-directory"
        else:
            statuses[relative] = "conflict"
    return statuses


def existing_namespace_conflicts(
    root: Path,
    agent_docs_dir: PurePosixPath,
    files: Mapping[Path, Tuple[bytes, bool]],
) -> bool:
    relative_root = filesystem_path(agent_docs_dir)
    namespace = root / relative_root
    candidate = root
    for part in agent_docs_dir.parts:
        candidate = candidate / part
        if candidate.exists() and not candidate.is_dir():
            return True
    if not namespace.exists():
        return False
    entries = tuple(namespace.iterdir())
    if not entries:
        return False

    marker_relative = relative_root / LAYOUT_FILENAME
    marker = root / marker_relative
    expected_marker = files[marker_relative][0]
    if marker.is_file() and marker.read_bytes() == expected_marker:
        return False

    allowed_names = {
        "manage-agent-docs.py",
        "README.md",
        LAYOUT_FILENAME,
        ".agent-docs-manifest.json",
        *SOURCE_DIRECTORY_NAMES,
    }
    if any(entry.name not in allowed_names for entry in entries):
        return True

    legacy_manager = namespace / "manage-agent-docs.py"
    if (
        legacy_manager.is_file()
        and b"Generate and check repository agent documentation"
        in legacy_manager.read_bytes()
    ):
        return False

    matching_assets = 0
    for relative, (expected_data, _) in files.items():
        target = root / relative
        if target.exists() and (
            not target.is_file() or target.read_bytes() != expected_data
        ):
            return True
        if target.is_file():
            matching_assets += 1
    if matching_assets:
        return False
    return True


def available_alternate_roots(
    root: Path, current: PurePosixPath
) -> Tuple[PurePosixPath, ...]:
    candidates = []
    for relative in ALTERNATE_ROOTS:
        if relative == current:
            continue
        candidate = root / filesystem_path(relative)
        try:
            available = not candidate.exists() or (
                candidate.is_dir() and not any(candidate.iterdir())
            )
        except OSError:
            available = False
        if available:
            candidates.append(relative)
    return tuple(candidates)


def format_option(relative: PurePosixPath) -> str:
    return f"--agent-docs-dir {relative.as_posix()}"


def print_conflict_recovery(
    root: Path,
    current: PurePosixPath,
    namespace_conflict: bool,
) -> None:
    print("Safe alternatives:", file=sys.stderr)
    if namespace_conflict:
        available = available_alternate_roots(root, current)
        if available:
            options = " or ".join(
                f"`{format_option(path)}`" for path in available[:2]
            )
            print(
                "- Preserve the existing "
                f"{current.as_posix()}/ directory and rerun with {options}.",
                file=sys.stderr,
            )
        else:
            print(
                "- Preserve the existing directory and choose another "
                "repository-approved path with --agent-docs-dir.",
                file=sys.stderr,
            )
    else:
        print(
            "- Preserve the conflicting scaffold file and integrate its "
            "authoritative changes before replacing it.",
            file=sys.stderr,
        )
        print(
            "- Do not select another agent-documentation directory merely "
            "to bypass a modified scaffold file.",
            file=sys.stderr,
        )
    print(
        "- Extend an existing documentation generator instead of installing this one.",
        file=sys.stderr,
    )
    print(
        "The selected directory is applied consistently to sources, the manager, "
        "the manifest, commands, and CI integration.",
        file=sys.stderr,
    )


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", required=True, type=Path, help="target repository root"
    )
    parser.add_argument(
        "--agent-docs-dir",
        default=DEFAULT_AGENT_DOCS_DIR.as_posix(),
        metavar="PATH",
        help=(
            "repository-relative source directory using alphanumeric, dot, "
            "underscore, or hyphen path components "
            f"(default: {DEFAULT_AGENT_DOCS_DIR.as_posix()})"
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run", action="store_true", help="show changes without writing"
    )
    mode.add_argument(
        "--check", action="store_true", help="verify the scaffold is installed"
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] = tuple(sys.argv[1:])) -> int:
    args = parse_args(argv)
    try:
        root = args.repo.resolve(strict=True)
        if not root.is_dir():
            raise ScaffoldError(f"repository root is not a directory: {root}")
        agent_docs_dir = parse_agent_docs_dir(args.agent_docs_dir)
        files = expected_files(agent_docs_dir)
        directories = source_directories(agent_docs_dir)
        statuses = inspect_targets(root, files, directories)
        namespace_conflict = existing_namespace_conflicts(
            root, agent_docs_dir, files
        )
    except (OSError, ScaffoldError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for relative, status_value in sorted(
        statuses.items(), key=lambda item: item[0].as_posix()
    ):
        print(f"[{status_value}] {relative.as_posix()}")
    if namespace_conflict:
        print(
            f"[conflict] {agent_docs_dir.as_posix()}/ "
            "is already repository-owned",
            file=sys.stderr,
        )

    conflicts = [path for path, value in statuses.items() if value == "conflict"]
    if conflicts or namespace_conflict:
        print(
            "Refusing to overwrite existing files or claim an existing namespace. "
            "Inspect each conflict before choosing a topology.",
            file=sys.stderr,
        )
        print_conflict_recovery(
            root, agent_docs_dir, namespace_conflict
        )
        return 1

    if args.check:
        missing = [
            path
            for path, value in statuses.items()
            if value in {"create", "create-directory"}
        ]
        if missing:
            print("The agent-documentation scaffold is incomplete.", file=sys.stderr)
            return 1
        print("[ok] agent-documentation scaffold is installed")
        return 0

    if args.dry_run:
        return 0

    try:
        for relative, (data, executable) in files.items():
            if statuses[relative] != "create":
                continue
            target = root / relative
            atomic_write(target, data)
            if executable:
                target.chmod(
                    target.stat().st_mode
                    | stat.S_IXUSR
                    | stat.S_IXGRP
                    | stat.S_IXOTH
                )
        for relative, status_value in statuses.items():
            if status_value == "create-directory":
                (root / relative).mkdir(parents=True, exist_ok=False)
    except OSError as error:
        print(f"error: could not install scaffold: {error}", file=sys.stderr)
        return 2
    print("[ok] installed agent-documentation scaffold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
