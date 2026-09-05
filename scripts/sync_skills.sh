#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/sync_skills.sh [--agent codex|claude|all] [--profile gpt-6|gpt-5.6] [--codex-home PATH] [--dry-run]

Copies skills from this repository into the local agent skill directories:
  codex/*  -> ~/.codex/skills/*
  claude/* -> ~/.claude/skills/*

Profile mode requires --agent codex and defaults to ~/.codex-profiles/<profile>.
--codex-home overrides the Codex destination home. Profile mode refuses the shared home.

Existing destination skill directories with the same name are replaced.
Skills that exist only in the destination are left untouched.
EOF
}

AGENT="all"
DRY_RUN=0
PROFILE=""
CODEX_DEST_HOME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --agent" >&2
        exit 1
      fi
      AGENT="$2"
      shift 2
      ;;
    --profile|--codex-home)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "Missing value for $1" >&2
        exit 1
      fi
      if [[ "$1" == "--profile" ]]; then PROFILE="$2"; else CODEX_DEST_HOME="$2"; fi
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ "$AGENT" != "codex" && "$AGENT" != "claude" && "$AGENT" != "all" ]]; then
  echo "--agent must be codex, claude, or all" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if [[ -n "$PROFILE" ]]; then
  if [[ "$PROFILE" != "gpt-6" && "$PROFILE" != "gpt-5.6" ]]; then
    echo "Unknown profile: $PROFILE" >&2
    exit 1
  fi
  if [[ "$AGENT" != "codex" ]]; then
    echo "--profile requires --agent codex" >&2
    exit 1
  fi
  CODEX_DEST_HOME="${CODEX_DEST_HOME:-${HOME}/.codex-profiles/${PROFILE}}"
else
  CODEX_DEST_HOME="${CODEX_DEST_HOME:-${CODEX_HOME:-${HOME}/.codex}}"
fi

BUILD_TEMP="$(mktemp -d)"
trap 'rm -rf "$BUILD_TEMP"' EXIT
if [[ "$AGENT" == "codex" || "$AGENT" == "all" ]]; then
  CODEX_DEST_HOME="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$CODEX_DEST_HOME")"
  build_args=(--output "${BUILD_TEMP}/distribution")
  if [[ -n "$PROFILE" ]]; then build_args+=(--profile "$PROFILE"); fi
  python3 "${SCRIPT_DIR}/build_skills.py" "${build_args[@]}"
  # Reject profile mixing before replacing any destination skills.
  python3 - "$CODEX_DEST_HOME" "$PROFILE" <<'PYCODE'
import json, os, sys
from pathlib import Path
home = Path(sys.argv[1]).expanduser().resolve()
profile = sys.argv[2]
marker = home / "agent-skills-profile.json"
shared = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()
if profile and (home == (Path.home() / ".codex").resolve() or (home == shared and not marker.exists())):
    sys.exit("Profile sync requires a separate Codex home")
if marker.exists():
    if json.loads(marker.read_text())["name"] != profile:
        sys.exit("Destination belongs to another profile")
elif profile and (home / "skills").exists() and any((home / "skills").iterdir()):
    sys.exit("Profile destination has unmanaged skills; choose a fresh Codex home")
PYCODE
fi

sync_agent() {
  local agent="$1"
  local source_root="$2"
  local dest_root="$3"

  if [[ ! -d "$source_root" ]]; then
    echo "Skipping ${agent}: source directory not found: ${source_root}" >&2
    return
  fi

  echo "Syncing ${agent} skills:"
  echo "  from ${source_root}"
  echo "  to   ${dest_root}"

  if [[ "$DRY_RUN" -eq 0 ]]; then
    mkdir -p "$dest_root"
  fi

  local found=0
  local source_dir
  while IFS= read -r -d '' source_dir; do
    found=1
    local skill_name
    skill_name="$(basename "$source_dir")"

    if [[ ! -f "${source_dir}/SKILL.md" ]]; then
      echo "  - skip ${skill_name}: missing SKILL.md" >&2
      continue
    fi

    local dest_dir="${dest_root}/${skill_name}"
    echo "  - ${skill_name}"

    if [[ "$DRY_RUN" -eq 1 ]]; then
      continue
    fi

    local tmp_parent
    tmp_parent="$(mktemp -d "${dest_root}/.sync-${skill_name}.XXXXXX")"
    cp -a "$source_dir" "${tmp_parent}/${skill_name}"
    rm -rf "$dest_dir"
    mv "${tmp_parent}/${skill_name}" "$dest_dir"
    rmdir "$tmp_parent"
  done < <(find "$source_root" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

  if [[ "$found" -eq 0 ]]; then
    echo "  (no skills found)"
  fi
}

if [[ "$AGENT" == "codex" || "$AGENT" == "all" ]]; then
  sync_agent "codex" "${BUILD_TEMP}/distribution/skills" "${CODEX_DEST_HOME}/skills"
  if [[ -n "$PROFILE" && "$DRY_RUN" -eq 0 ]]; then
    cp "${BUILD_TEMP}/distribution/profile.json" "${CODEX_DEST_HOME}/agent-skills-profile.json"
  fi
fi

if [[ "$AGENT" == "claude" || "$AGENT" == "all" ]]; then
  sync_agent "claude" "${REPO_ROOT}/claude" "${HOME}/.claude/skills"
fi
