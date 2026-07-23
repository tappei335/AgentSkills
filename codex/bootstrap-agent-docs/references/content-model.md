# Agent Documentation Content Model

Use this reference to select the smallest set of instructions that materially improves agent decisions.

## Contents

- Evidence map
- Root admission test
- Suggested fragments
- Writing rules
- Nested instructions
- Claude rules
- Acceptance review

## Evidence Map

| Instruction area | Prefer these sources | Include only when verified |
|---|---|---|
| Canonical commands | CI workflows, task runner, contributor guide | Non-obvious authoritative commands and working directory |
| Architecture boundaries | Decision records, dependency manifests, module docs | Stable boundaries or dependency directions that are costly to violate |
| Contribution constraints | CONTRIBUTING, hooks, release docs, repository policy | Exceptional branch, generation, test, or review requirements |
| Git workflow | Contributor docs, existing branch names, worktree layout | Required isolation method and established branch classification |
| Safety constraints | Secret policy, protected artifacts, destructive tooling | Repository-specific high-cost failure modes |
| Path-specific behavior | Existing scoped rules, local build files, subtree docs | Concrete globs, commands, conventions, or ownership boundaries |

Cross-check important claims when practical. If prose and CI disagree, resolve the discrepancy instead of placing both commands at the root.

## Root Admission Test

Keep an instruction in root `AGENTS.md` or `CLAUDE.md` only when all three answers are yes:

1. Does it change how a capable agent would act?
2. Does it apply to most work under this file's scope?
3. Is it non-obvious or costly to miss, rediscover, or violate?

Otherwise route it elsewhere:

- Delete self-evident or generic advice.
- Link explanatory knowledge from ordinary repository docs.
- Move path- or situation-specific Claude guidance into `ai/rules/`.
- Move subtree guidance into nested fragments.
- Use a compact AGENTS-only routing index only when non-Claude agents must discover glob-scoped rules.

Do not spend root context explaining that files are generated, naming the fragment directory, documenting regeneration, or listing obvious directories. Keep that maintenance information in `ai/README.md` and repository-native task documentation.

Build `CLAUDE.md` from always-on constraints after inspecting what rules can trigger. Do not copy a rule's full text into `CLAUDE.md`. It is acceptable and usually desirable for `CLAUDE.md` to be shorter than `AGENTS.md`.

## Suggested Fragments

Use only fragments that pass the admission test. These numbers are conventions.

| Fragment | Purpose | Typical target |
|---|---|---|
| `10-git-workflow.md` | Worktree isolation and meaningful branch classification | Shared |
| `20-commands.md` | Non-obvious canonical verification commands | Shared |
| `30-boundaries.md` | Always-on architecture or dependency constraints | Shared |
| `40-routing.agents.md` | Compact non-Claude rule discovery, when needed | AGENTS |
| `70-never.md` | Repository-specific high-cost prohibited actions | Shared |

Add a project overview or repository map only when it conveys boundaries or ownership that manifests and directory names do not make clear.

## Writing Rules

- Lead with an imperative or a factual constraint.
- Name exact commands and their working directory only when the choice is non-obvious.
- Link detailed designs instead of repeating them.
- Explain the reason only when it changes judgment or prevents a tempting mistake.
- Make completion criteria observable and repository-specific.
- Remove “write clean code,” “add tests,” “follow existing style,” and similar defaults unless the repository defines an unusual concrete meaning.
- Keep maintenance mechanics out of root output even when the output is generated mechanically.

## Nested Instructions

Create `ai/fragments/<relative-directory>/` only when the subtree has distinct commands, architecture, ownership, or recurring constraints. The directory must map to an existing repository directory.

Inherit parent guidance instead of repeating it. Add only the local delta. Do not create nested files for every directory.

## Claude Rules

Prefer a rule whenever a path glob can activate the instruction only when relevant. Common candidates include language conventions, source-file organization, manifest edits, tests, fixtures, documentation, deployment, generated sources, and schema files.

Store the source under `ai/rules/` with Claude-compatible frontmatter:

```markdown
---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Python edit constraints

- Run the verified package-specific check.
```

Keep each glob narrow and each rule operational. Do not assume AGENTS-aware tools scan `.claude/rules/`; provide a nested instruction or compact AGENTS-only route only when they need the same guidance.

## Acceptance Review

Confirm all of the following:

- Every root line passes the root admission test.
- Root output contains no generation banner, fragment-path explanation, or generic advice.
- `CLAUDE.md` does not duplicate instructions already activated by rules.
- AGENTS can discover required scoped guidance without loading all rule bodies globally.
- Nested output adds only local deltas.
- Existing policy meaning survived migration while redundant wording did not.
- Git-backed changes use an isolated worktree, and new branch names follow the repository convention or a meaningful change-type prefix.
- Commands and relative links work from the generated output location.
- Every newly introduced behavioral constraint is supported by repository evidence or explicit user authorization.
