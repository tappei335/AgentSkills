#!/usr/bin/env python3
"""Install the reusable agent-documentation tooling into a repository."""

from __future__ import annotations

import argparse
import os
import stat
import sys
import tempfile
from pathlib import Path
from typing import Dict, Sequence, Tuple


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS: Tuple[Tuple[Path, Path], ...] = (
    (SKILL_ROOT / "assets/manage-agent-docs.py", Path("ai/manage-agent-docs.py")),
    (SKILL_ROOT / "assets/AI-README.md", Path("ai/README.md")),
)
SOURCE_DIRECTORIES = (Path("ai/fragments"), Path("ai/rules"))


class ScaffoldError(Exception):
    """Report a conflict or unsafe scaffold target."""


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


def inspect_targets(root: Path) -> Dict[Path, str]:
    statuses: Dict[Path, str] = {}
    for source, relative in ASSETS:
        if not source.is_file():
            raise ScaffoldError(f"skill asset is missing: {source}")
        target = root / relative
        if not within_repository(root, target):
            raise ScaffoldError(
                f"target escapes the repository through a symlink: {target}"
            )
        if not target.exists():
            statuses[relative] = "create"
        elif target.is_file() and target.read_bytes() == source.read_bytes():
            statuses[relative] = "unchanged"
        else:
            statuses[relative] = "conflict"
    for relative in SOURCE_DIRECTORIES:
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


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", required=True, type=Path, help="target repository root"
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
        statuses = inspect_targets(root)
    except (OSError, ScaffoldError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for relative, status_value in sorted(
        statuses.items(), key=lambda item: item[0].as_posix()
    ):
        print(f"[{status_value}] {relative.as_posix()}")

    conflicts = [path for path, value in statuses.items() if value == "conflict"]
    if conflicts:
        print(
            "Refusing to overwrite existing files. "
            "Inspect and integrate each conflict manually.",
            file=sys.stderr,
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
        for relative, status_value in statuses.items():
            if status_value == "create-directory":
                (root / relative).mkdir(parents=True, exist_ok=False)
        for source, relative in ASSETS:
            if statuses[relative] != "create":
                continue
            target = root / relative
            atomic_write(target, source.read_bytes())
            if target.name == "manage-agent-docs.py":
                target.chmod(
                    target.stat().st_mode
                    | stat.S_IXUSR
                    | stat.S_IXGRP
                    | stat.S_IXOTH
                )
    except OSError as error:
        print(f"error: could not install scaffold: {error}", file=sys.stderr)
        return 2
    print("[ok] installed agent-documentation scaffold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
