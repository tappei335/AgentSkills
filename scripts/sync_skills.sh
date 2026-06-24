#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/sync_skills.sh [--agent codex|claude|all] [--dry-run]

Copies skills from this repository into the local agent skill directories:
  codex/*  -> ~/.codex/skills/*
  claude/* -> ~/.claude/skills/*

Existing destination skill directories with the same name are replaced.
Skills that exist only in the destination are left untouched.
EOF
}

AGENT="all"
DRY_RUN=0

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
  sync_agent "codex" "${REPO_ROOT}/codex" "${HOME}/.codex/skills"
fi

if [[ "$AGENT" == "claude" || "$AGENT" == "all" ]]; then
  sync_agent "claude" "${REPO_ROOT}/claude" "${HOME}/.claude/skills"
fi
