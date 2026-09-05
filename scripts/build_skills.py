#!/usr/bin/env python3
"""Build portable Codex skills from shared sources and optional profile additions."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ("gpt-6", "gpt-5.6")


def read_profile(root: Path, name: str) -> dict:
    if name not in PROFILES:
        raise ValueError(f"Unknown profile: {name}")
    data = json.loads((root / "profiles" / f"{name}.json").read_text())
    if set(data) != {"name", "root", "roles"} or data["name"] != name:
        raise ValueError(f"Invalid profile: {name}")
    if set(data["roles"]) != {"judgment", "bounded", "mechanical"}:
        raise ValueError(f"Invalid roles: {name}")
    for settings in [data["root"], *data["roles"].values()]:
        if set(settings) != {"model", "effort"}:
            raise ValueError(f"Invalid model settings: {name}")
        model = settings["model"]
        if not isinstance(model, str) or not model or any(c.isspace() for c in model):
            raise ValueError(f"Invalid model ID: {name}")
        if settings["effort"] not in {"low", "medium", "high", "xhigh", "max", "ultra"}:
            raise ValueError(f"Invalid reasoning effort: {name}")
    return data


def build(output: Path, profile: str | None = None, root: Path = ROOT) -> None:
    """Publish a fresh directory; never overwrite an existing distribution."""
    if output.exists() or output.is_symlink():
        raise ValueError(f"Output already exists; choose a fresh directory: {output}")
    data = read_profile(root, profile) if profile else None
    policy_path = root / "policies/model-selection.md"
    policy = policy_path.read_text()
    if data:
        policy += f"\n## Selected Profile: {profile}\n\n"
        policy += "These candidates apply only when a justified override is supported. Child models may differ from the root model.\n\n"
        for role, settings in data["roles"].items():
            policy += f"- {role}: `{settings['model']}`, `{settings['effort']}` effort.\n"

    skills = sorted((root / "codex").glob("*/SKILL.md"))
    if not skills:
        raise ValueError("No Codex skills found")
    variant_root = root / "variants" / profile if profile else None
    if variant_root and variant_root.exists():
        names = {p.parent.name for p in skills}
        for entry in variant_root.iterdir():
            if entry.name == ".gitkeep":
                continue
            if not entry.is_dir() or entry.name not in names | {"_shared"}:
                raise ValueError(f"Unknown variant skill: {entry}")
            if {p.name for p in entry.iterdir()} != {"instructions.md", "evidence.md"}:
                raise ValueError(f"Variant requires only instructions.md and evidence.md: {entry}")
            if any(not p.read_text().strip() for p in entry.iterdir()):
                raise ValueError(f"Empty variant: {entry}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".build-skills-", dir=output.parent) as temp:
        stage = Path(temp) / "distribution"
        stage.mkdir()
        for source in skills:
            dest = stage / "skills" / source.parent.name
            shutil.copytree(source.parent, dest)
            # Rewrite only links to the shared policy; distribute a local copy.
            for original in source.parent.rglob("*.md"):
                text = original.read_text()
                def replace(match: re.Match) -> str:
                    target = match.group(1)
                    if (original.parent / target).resolve() != policy_path.resolve():
                        return match.group(0)
                    local = dest / "references/model-policy.md"
                    relative = os.path.relpath(local, (dest / original.relative_to(source.parent)).parent)
                    return f"]({relative})"
                text = re.sub(r"\]\(([^)]+)\)", replace, text)
                (dest / original.relative_to(source.parent)).write_text(text)
            (dest / "references").mkdir(exist_ok=True)
            (dest / "references/model-policy.md").write_text(policy)
            shared_variant = variant_root / "_shared" if variant_root else None
            if shared_variant and shared_variant.exists():
                shutil.copyfile(shared_variant / "instructions.md", dest / "references/model-profile.md")
                # Read behavioral guidance before encountering workflow-specific gates.
                document = dest / "SKILL.md"
                text = document.read_text()
                frontmatter_end = text.index("\n---", 3) + len("\n---")
                text = (text[:frontmatter_end]
                        + "\n\nRead [profile guidance](references/model-profile.md) before applying this workflow."
                        + text[frontmatter_end:])
                document.write_text(text)
            variant = variant_root / source.parent.name if variant_root else None
            if variant and variant.exists():
                shutil.copyfile(variant / "instructions.md", dest / "references/model-variant.md")
                with (dest / "SKILL.md").open("a") as stream:
                    stream.write("\n## Model-Specific Instructions\n\nRead [profile instructions](references/model-variant.md) before starting this workflow.\n")
        (stage / "profile.json").write_text(json.dumps(data, indent=2) + "\n")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_skills.py"), "--root", str(stage)],
            capture_output=True, text=True,
        )
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        stage.rename(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.output.absolute(), args.profile)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"error: {exc}\n")
    print(f"Built {args.profile or 'common'} skills: {args.output}")


if __name__ == "__main__":
    main()
