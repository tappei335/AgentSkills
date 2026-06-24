#!/usr/bin/env python3
"""Validate the skill repository structure."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME_RE = re.compile(r"^[a-z0-9-]+$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class ValidationError(Exception):
    pass


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValidationError("missing opening frontmatter delimiter")

    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValidationError("missing closing frontmatter delimiter") from exc

    frontmatter_lines = lines[1:end]
    frontmatter: dict[str, str] = {}
    keys: list[str] = []
    index = 0

    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith((" ", "\t")):
            raise ValidationError(f"unexpected indented frontmatter line: {line!r}")
        if ":" not in line:
            raise ValidationError(f"invalid frontmatter line: {line!r}")

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        keys.append(key)

        if value in {">", "|"}:
            folded: list[str] = []
            index += 1
            while index < len(frontmatter_lines):
                next_line = frontmatter_lines[index]
                if next_line and not next_line.startswith((" ", "\t")):
                    break
                folded.append(next_line.strip())
                index += 1
            frontmatter[key] = " ".join(part for part in folded if part)
            continue

        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        frontmatter[key] = value
        index += 1

    return frontmatter, keys


def skill_paths() -> list[Path]:
    paths: list[Path] = []
    for agent_dir in (ROOT / "codex", ROOT / "claude"):
        if not agent_dir.exists():
            continue
        paths.extend(sorted(agent_dir.glob("*/SKILL.md")))
    return sorted(paths)


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    agent = rel.parts[0]
    skill_dir = path.parent

    try:
        frontmatter, keys = parse_frontmatter(path)
    except ValidationError as exc:
        return [f"{rel}: {exc}"]

    name = frontmatter.get("name", "").strip()
    description = frontmatter.get("description", "").strip()

    if not name:
        errors.append(f"{rel}: missing name")
    elif not SKILL_NAME_RE.fullmatch(name):
        errors.append(f"{rel}: name must use lowercase letters, digits, and hyphens")
    elif name != skill_dir.name:
        errors.append(f"{rel}: name {name!r} does not match directory {skill_dir.name!r}")

    if not description:
        errors.append(f"{rel}: missing description")
    elif len(description) < 80:
        errors.append(f"{rel}: description is too short to be a useful trigger")

    if agent == "codex":
        extra_keys = [key for key in keys if key not in {"name", "description"}]
        if extra_keys:
            errors.append(f"{rel}: Codex frontmatter has unsupported keys: {', '.join(extra_keys)}")
        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if not openai_yaml.exists():
            errors.append(f"{rel}: missing agents/openai.yaml")
        else:
            text = openai_yaml.read_text(encoding="utf-8")
            for required in ("display_name:", "short_description:", "default_prompt:"):
                if required not in text:
                    errors.append(f"{openai_yaml.relative_to(ROOT)}: missing {required}")

    validate_markdown_links(path, errors)
    for reference in sorted((skill_dir / "references").glob("*.md")):
        validate_markdown_links(reference, errors)
    validate_executable_scripts(skill_dir, errors)

    return errors


def validate_markdown_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for match in MARKDOWN_LINK_RE.finditer(text):
        raw_target = match.group(1).strip()
        if is_external_or_anchor(raw_target):
            continue
        target = raw_target.split("#", 1)[0].strip()
        if not target or target.startswith("<"):
            continue
        target_path = (path.parent / target).resolve()
        try:
            target_path.relative_to(ROOT)
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}")
            continue
        if not target_path.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link: {raw_target}")


def is_external_or_anchor(target: str) -> bool:
    return (
        target.startswith("#")
        or target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
    )


def validate_executable_scripts(skill_dir: Path, errors: list[str]) -> None:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return
    for script in sorted(scripts_dir.iterdir()):
        if not script.is_file():
            continue
        first_line = script.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        if first_line and first_line[0].startswith("#!") and not os.access(script, os.X_OK):
            errors.append(f"{script.relative_to(ROOT)}: shebang script is not executable")


def main() -> int:
    paths = skill_paths()
    if not paths:
        print("No skills found")
        return 1

    errors: list[str] = []
    for path in paths:
        errors.extend(validate_skill(path))

    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(paths)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
