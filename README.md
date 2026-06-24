# Agent Skills Repository

This repository manages Codex and Claude skills.

## Layout

- `codex/<skill-name>/` - Codex skills. Each skill should include `SKILL.md`; Codex skills should also include `agents/openai.yaml`.
- `claude/<skill-name>/` - Claude skills. Claude-specific tool names and frontmatter may live here.
- `<skill>/references/` - Optional reference material loaded only when the skill needs it.
- `<skill>/scripts/` - Optional deterministic helpers used by the skill.

## Conventions

- Keep `SKILL.md` concise and procedural. Put detailed variants, examples, or long reference material in `references/`.
- Put trigger guidance in the `description` frontmatter because the body is loaded only after the skill triggers.
- Keep Codex frontmatter to `name` and `description`.
- Name skill directories exactly the same as the `name` field.
- Prefer copying a skill to both `codex/` and `claude/` only when the workflow is useful in both agents; adapt tool names separately.

## Sync

Copy repository skills into the local agent skill directories:

```sh
scripts/sync_skills.sh
```

Preview changes without copying:

```sh
scripts/sync_skills.sh --dry-run
```

Sync only one agent:

```sh
scripts/sync_skills.sh --agent codex
scripts/sync_skills.sh --agent claude
```

The script replaces destination skill directories with the same name, such as `~/.codex/skills/<skill-name>` or `~/.claude/skills/<skill-name>`. Skills that exist only in the destination are left untouched.

## Validation

Run the repository checks after editing skills:

```sh
python3 scripts/validate_skills.py
```

The validator checks required frontmatter, directory/name consistency, Codex `agents/openai.yaml`, broken relative markdown links, and executable bits for shebang scripts.
