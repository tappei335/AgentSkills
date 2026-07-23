---
name: bootstrap-agent-docs
description: Create or modernize concise, maintainable repository-wide AI agent configuration, including curated AGENTS.md and CLAUDE.md files, nested instructions, trigger-scoped Claude rules, regeneration commands, and CI drift checks. Use when a user asks to add, standardize, synchronize, migrate, trim, or reproduce agent-facing repository instructions in any codebase, especially when root instructions are duplicated, bloated, missing, hand-maintained, or inconsistent.
---

# Bootstrap Agent Docs

Create an evidence-based agent documentation system that fits the target repository. Spend root context only on non-obvious, always-relevant constraints; route narrower knowledge to triggered rules, nested instructions, or ordinary repository docs.

## Outcome Contract

Deliver all of the following unless the target repository or user request narrows the scope:

- Treat `ai/fragments/` as the maintenance source for checked-in `AGENTS.md` and `CLAUDE.md` files without announcing that fact inside the generated root documents.
- Keep root instructions aggressively curated: retain only guidance that changes behavior, applies broadly at that scope, and is costly to miss or rediscover.
- Keep `CLAUDE.md` especially small. Move path- or situation-specific guidance into `ai/rules/` so Claude loads it only when triggered.
- Use nested instructions for subtree-specific guidance that AGENTS or both tools need; do not duplicate those details at the root.
- Share content only when it deserves the root context of both tools. Use target-specific fragments when Claude rules or AGENTS discovery needs make the content asymmetric.
- Provide one build command and one non-mutating drift-check command.
- Connect the drift check to the repository's existing task runner and CI when those integration points exist.
- Preserve the meaning of existing agent instructions and avoid overwriting unmanaged files without an explicit migration step.
- Isolate Git-backed implementation in a dedicated worktree and keep the user's primary or dirty checkout untouched.
- Follow the repository's branch convention; when none exists, use a meaningful change-type prefix such as `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`, or `ci/`.
- Introduce no new coding policy unless repository evidence or the user request authorizes it.

## Inspect Before Editing

1. Resolve the target repository root and read every applicable `AGENTS.md`, `AGENTS.override.md`, root or `.claude/CLAUDE.md`, and path-specific rule before changing files. Inspect the effective Codex configuration for `project_doc_fallback_filenames` when available, and include matching repository files in the inventory.
2. Run `git status --short`. Treat all pre-existing changes as user work and keep the rollout disjoint from them.
3. Inventory agent configuration, manifests, task runners, CI workflows, contribution guides, architecture records, and generated-file policies. Prefer `rg --files` and targeted `rg` searches.
4. Derive project facts from authoritative repository evidence. Read [references/content-model.md](references/content-model.md) before deciding what deserves root context and what should become a triggered rule.
5. Classify the adoption case using [references/adoption-patterns.md](references/adoption-patterns.md) when any agent file, rule directory, generator, or CI check already exists.
6. Identify conflicts that require a user decision, such as contradictory existing policies or a requested change to an agreed architecture boundary. Do not treat ordinary content organization as a blocking decision.

## Work In An Isolated Git State

For a Git repository, perform file-changing work in a dedicated worktree created from the intended base. Reuse a suitable task worktree when one already exists; otherwise create one without moving, cleaning, or repurposing the user's current checkout. Keep unrelated dirty state out of the task branch.

Use the repository's documented branch naming convention when it exists. Otherwise name a new branch `<type>/<short-kebab-description>` using the dominant change type:

- `feat/` for user-facing or capability additions.
- `fix/` for defect corrections.
- `chore/` for maintenance and repository configuration.
- `docs/`, `refactor/`, `test/`, or `ci/` when one of those scopes is more precise.

Avoid generic prefixes or names that describe only the agent, ticket runner, or temporary execution context. If Git worktrees are unavailable or conflict with the repository's established workflow, state the reason and use the safest repository-approved isolation method.

## Choose The Smallest Useful Topology

Use generated root `AGENTS.md` and `CLAUDE.md` files by default, but make their content smaller than the source knowledge base. Apply this placement order to every candidate instruction:

1. Delete it when a capable agent can infer it cheaply or it merely describes the documentation machinery.
2. Keep it in ordinary repository docs when it is explanatory knowledge rather than an operating constraint.
3. Put it in `ai/rules/` when Claude needs it only for matching paths or situations.
4. Put it in nested fragments when a subtree needs it and AGENTS or both tools must discover it.
5. Keep it at the root only when it is non-obvious, broadly active, and costly to violate.

Do not put a generated-file banner, fragment-source explanation, exhaustive directory listing, or generic advice in root outputs. Store maintenance instructions in `ai/README.md`. Keep `CLAUDE.md` no larger than necessary after accounting for rules; do not mirror an AGENTS-only discovery index into it.

## Install The Reusable Tooling

Use the bundled scaffolder only after the inspection:

```sh
python3 <skill-dir>/scripts/scaffold_agent_docs.py --repo <repo-root> --dry-run
python3 <skill-dir>/scripts/scaffold_agent_docs.py --repo <repo-root>
```

The scaffolder installs the reference generator and its source-layout documentation without replacing different existing files. If it reports a conflict, inspect and integrate the asset manually; do not bypass the conflict by deleting user files.

The installed reference tool requires Python 3.8 or newer. If Python is not already available in local development and CI, port the behavior described in the installed `ai/README.md` to the repository's existing runtime instead of introducing an unapproved toolchain dependency.

## Build The Source Model

1. Classify existing prose before generating over it: keep at root, move to a rule, move to nested instructions, link from ordinary docs, or discard as obvious/redundant. Preserve policy meaning, not wording or volume.
2. Create the fewest root fragments that cover verified always-on constraints. Typical candidates are non-obvious canonical commands, architecture boundaries, and high-cost prohibitions. Include repository maps or workflow prose only when they materially change decisions.
3. Use these suffixes at every fragment level:
   - `NN-name.md` for shared content.
   - `NN-name.agents.md` for AGENTS-only content.
   - `NN-name.claude.md` for CLAUDE-only content.
4. Mirror the target directory below `ai/fragments/` for nested files. For example, `ai/fragments/packages/api/10-overview.md` generates instructions in `packages/api/`.
5. Prefer `ai/rules/` for Claude guidance tied to languages, manifests, tests, docs, deployment files, or other concrete triggers. Do not repeat the full rule in `CLAUDE.md`. Keep equivalent guidance discoverable through nested or AGENTS-specific fragments only when non-Claude agents also need it.
6. For Git repositories, add a concise shared workflow fragment that requires isolated worktrees and meaningful branch classification, adapting the exact wording and allowed prefixes to any established repository convention.
7. Treat any other new behavioral constraint as a policy change. Add anti-special-case guidance, file-size or cohesion rules, test mandates, or similar coding preferences only when an existing policy, repeated repository evidence, or the user request justifies them.
8. Keep source layout, regeneration, mirrors, and manifest maintenance in `ai/README.md` and task-runner documentation, not in root agent context.

## Generate Safely

Run the installed tool after source fragments exist:

```sh
python3 ai/manage-agent-docs.py check
python3 ai/manage-agent-docs.py build
python3 ai/manage-agent-docs.py check
```

The first check is expected to fail during initial adoption and exposes the pending output. The build refuses to replace unmanaged outputs, modified managed outputs, or outputs shadowed by `AGENTS.override.md` or an alternate `.claude/CLAUDE.md`. Migrate active alternate instructions into the source model and remove the conflicting file explicitly. After migrating and reviewing an unmanaged output, use the one-time adoption flag:

```sh
python3 ai/manage-agent-docs.py build --adopt-existing
```

Never use the adoption flag as a shortcut around content migration. Inspect the generated root and nested outputs after building.

## Integrate With Repository Workflows

Expose stable repository-native entry points for regeneration and checking. Extend the existing Makefile, package scripts, Justfile, Taskfile, or equivalent rather than introducing a competing task runner. Keep the direct Python commands documented as a fallback.

Add the non-mutating check to an existing lightweight CI job when CI is present. Avoid creating an unrelated workflow if the repository has a standard validation job that can own the check. Do not claim CI enforcement when only a local command was added.

If the source repository already generates contributor or agent docs through another mechanism, extend that mechanism or preserve its public commands where practical. Avoid two generators owning the same output.

## Verify The Result

1. Run the direct `build` and `check` commands.
2. Run the repository-native regeneration and check entry points added or changed by this work.
3. Exercise drift detection by changing a fragment in a disposable copy or temporary repository, confirming `check` fails, rebuilding, and confirming it passes.
4. Audit every root line by asking why it must be always loaded instead of deleted, linked, nested, or triggered. Confirm generated root outputs contain no generation/source banner or self-evident maintenance prose.
5. Confirm Claude rules cover the intended paths without duplicating their full text in `CLAUDE.md`. Confirm AGENTS can still discover any equivalent guidance it needs.
6. Verify the effective instruction chain: account for `AGENTS.override.md`, configured fallback filenames, root and `.claude/CLAUDE.md`, nested instructions, and Claude rules. Confirm no unmanaged active file shadows or duplicates generated guidance.
7. Confirm implementation occurred in an isolated worktree and that the branch name follows the repository convention or the fallback change-type scheme.
8. Run `git diff --check`, inspect `git diff --stat`, and review the complete diff. Confirm unrelated dirty files remain untouched.
9. Run the bundled regression tests and skill validator when editing this skill itself:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s <skill-dir>/tests -v
python3 <skill-creator-dir>/scripts/quick_validate.py <skill-dir>
```

Report the source layout, generated outputs, workflow/CI integration, commands actually run, and any intentionally omitted topology such as nested docs or path rules.

## Guardrails

- Do not invent build commands, branch rules, architecture decisions, ownership, or supported toolchains.
- Do not weaken, silently reinterpret, or discard existing instructions during consolidation.
- Do not retain obvious statements merely because they already exist. Remove prose that does not change a capable agent's decisions.
- Do not include credentials, local absolute paths, transient branch state, personal preferences, generated-file explanations, or generic advice that adds no repository knowledge.
- Do not edit generated outputs to fix prose; edit the fragments and rebuild.
- Do not make path rules and nested instructions contradict each other.
- Do not add nested files to every directory. Excess context is a maintenance cost.
- Do not inject generic coding preferences merely because they are broadly useful. Require repository evidence or explicit user authorization for new behavioral policy.
