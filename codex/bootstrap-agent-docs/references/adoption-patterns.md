# Adoption Patterns

Select the pattern that matches the repository's current state. Preserve existing behavior before improving organization.

## Greenfield Repository

1. Install the tooling.
2. Write only the always-on constraints that pass the root admission test.
3. Put concrete path-triggered Claude guidance in rules before drafting `CLAUDE.md`.
4. Build the root outputs.
5. Add task-runner and CI entry points.
6. Add nested fragments only after a concrete local need appears.

Do not populate the repository with speculative rules or empty nested documentation.

## One Existing Agent File

Treat the existing file as migration input, not generated output.

1. Classify each section as root, triggered rule, nested instruction, ordinary documentation, or discard.
2. Split retained content by concern. Preserve policy meaning without preserving redundant wording.
3. Keep agent-specific capabilities in a suffixed fragment only when they belong in that tool's always-on context.
4. Generate both outputs and compare the original file section by section.
5. Use `build --adopt-existing` only after every meaningful instruction has a destination or an explicit reason for removal.

## Existing AGENTS.md And CLAUDE.md

Create a short migration ledger before editing:

| Existing section | Shared or specific | Destination | Conflict resolution |
|---|---|---|---|
| Build commands | Shared | `20-commands.md` | Use the command confirmed by CI |
| File-type convention | Claude-triggered | `ai/rules/<topic>.md` | Remove the duplicate from `CLAUDE.md` |
| Non-Claude discovery | AGENTS-specific | Nested or routing fragment | Link narrowly; do not inline every rule |
| Generation explanation | Maintenance only | `ai/README.md` or discard | Keep it out of root output |
| Generic advice | Neither | Discard | Retain only a repository-specific constraint |

Consolidate semantically identical always-on prose into shared fragments. Move triggered guidance out of `CLAUDE.md`, even when AGENTS needs a separate discovery route. If the files contradict each other on architecture, safety, public API, or workflow policy, ask for a decision rather than choosing silently.

## Alternate Active Instruction Files

Inventory the effective instruction chain, not only the preferred output names:

- Codex checks `AGENTS.override.md` before `AGENTS.md` in each scope and may use names from `project_doc_fallback_filenames` when neither standard file is present.
- Claude accepts project instructions at either `CLAUDE.md` or `.claude/CLAUDE.md`; `CLAUDE.local.md` may add uncommitted local guidance.

Record every checked-in alternate file in the migration ledger. When a managed output would conflict, present both safe directions: preserve the established alternate as canonical and adapt the generator or managed output set, or migrate retained policy into fragments or rules and remove the alternate only after verifying the effective chain. Recommend a direction from repository conventions rather than treating the reference topology as mandatory. Do not use `--adopt-existing` to bypass an alternate-file conflict. Treat personal `CLAUDE.local.md` as user context: do not manage or delete it, but report material conflicts that affect verification.

When effective Codex fallback names cannot be resolved from the available configuration, state that verification gap. Prefer an available instruction-inspection command from the target agent over guessing which file is active.

## Existing Generator

Do not install a second generator for the same outputs. Inspect whether the existing implementation already provides:

- Shared and tool-specific source content.
- A root curation policy that avoids loading maintenance or obvious prose.
- Nested output support.
- A non-mutating drift check.
- Safe handling and active use of path rules to keep `CLAUDE.md` small.
- Stable task-runner and CI entry points.

Extend the existing mechanism when practical. Use the bundled reference tool only when replacement is within scope and preserves the repository's public commands.

## Monorepo Or Multi-Package Repository

Start with one root operating contract. Add nested fragments at package or ownership boundaries, not for every directory. Confirm that each fragment path maps to a real directory and that commands state whether they run from the workspace root or package directory.

Avoid copying root commands into every child. Child instructions should add or override only local facts.

## Existing Claude Rules

The reference generator manages only paths recorded in `ai/.agent-docs-manifest.json` and leaves unrelated `.claude/rules/` files in place. A source rule that collides with an unmanaged file causes adoption to fail unless its content is identical or `--adopt-existing` is used deliberately.

Before drafting `CLAUDE.md`, inventory existing rules and remove root prose that they already activate. Before adopting a collision:

1. Compare both files.
2. Move the authoritative content into `ai/rules/`.
3. Preserve any tool-owned metadata required by Claude.
4. Confirm non-Claude agents can discover equivalent guidance only if they need it.
5. Confirm `CLAUDE.md` does not duplicate the rule body.
6. Run build and check again.

## Workflow Integration

Use the repository's current command surface:

| Existing runner | Suggested regeneration entry | Suggested check entry |
|---|---|---|
| Make | `agent-docs` | `check-agent-docs` |
| npm/pnpm/yarn | `agent-docs` | `check:agent-docs` |
| Just | `agent-docs` | `check-agent-docs` |
| Task | `agent-docs` | `check-agent-docs` |
| None | Document the direct Python commands | Document the direct Python commands |

Use the names already established by the repository when equivalents exist. Make the check call `python3 ai/manage-agent-docs.py check`; it must not rewrite the worktree.

Add that same check to an existing lightweight CI validation job. Ensure the job provisions Python 3.8+ before using the reference tool. If the repository intentionally has no Python runtime, implement the same contract in its existing runtime and test both generation and stale-output failure.

## Existing Uncommitted Changes

Create or reuse a dedicated task worktree from the intended base and keep the migration away from unrelated modified or untracked files. Do not clean, move, or repurpose the user's dirty checkout to obtain a clean state. If an existing agent file is already modified, inspect the diff and treat both the base and working-tree content as user input. Do not overwrite it with generated output until the user changes have been incorporated or the user directs otherwise.

Follow the repository's established branch naming convention. When no convention exists, use `<type>/<short-kebab-description>` with a meaningful type such as `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, or `ci`; avoid names that identify only the agent or temporary task runner.
