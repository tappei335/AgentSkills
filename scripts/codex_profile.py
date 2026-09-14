#!/usr/bin/env python3
"""Launch Codex with an installed model profile and its separate skills home."""

import argparse
import json
import os
from pathlib import Path

from build_skills import PROFILES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=PROFILES)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    # Separate launcher flags from the Codex arguments explicitly.
    import sys
    argv = sys.argv[1:]
    split = argv.index("--") if "--" in argv else len(argv)
    args = parser.parse_args(argv[:split])
    codex_args = argv[split + 1:] if split < len(argv) else []
    home = (args.codex_home or Path.home() / ".codex-profiles" / args.profile).expanduser().resolve()
    try:
        profile = json.loads((home / "agent-skills-profile.json").read_text())
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Install this profile with scripts/sync_skills.sh first: {exc}\n")
    if profile["name"] != args.profile:
        parser.exit(1, "Destination belongs to another profile\n")
    if not (home / "skills").is_dir():
        parser.exit(1, "Installed skills are missing; sync this profile again\n")
    command = ["codex", "-c", f"model={json.dumps(profile['root']['model'])}",
               "-c", f"model_reasoning_effort={json.dumps(profile['root']['effort'])}", *codex_args]
    if args.dry_run:
        print(json.dumps({"codex_home": str(home), "command": command}, indent=2))
        return
    environment = os.environ.copy()
    # Use CODEX_HOME for its supported purpose, scoped to the child process.
    environment["CODEX_HOME"] = str(home)
    os.execvpe(command[0], command, environment)


if __name__ == "__main__":
    main()
