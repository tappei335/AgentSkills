---
name: team-dev
description: Coordinate explicit multi-agent repository implementation with outcome-focused task framing, independent ownership, integration review, verification, and optional publication. Use when the user invokes `$team-dev`, says "team development mode" or "チーム開発モード", asks to split implementation across engineers or workers, or requests parallel implementers and reviewers. Do not use for planning-only strategy, investigation or audit, PR review, or small single-agent edits unless the user explicitly requests team mode.
---

# Team Dev

## Operating Contract

Keep the main agent accountable for the outcome, shared decisions, integration, verification, review disposition, and final response. Delegate only bounded work that is independent enough to run without repeated coordination. Use light mode when the task has no useful split.

Prefer a more specific skill when it matches the requested outcome:

- Use `$feature-implementation-strategy` for planning-only architecture, tradeoffs, roadmaps, or implementation strategy.
- Use `$maximize-research-results` for investigation, audit, diagnosis, comparison, or broad research.
- Use `$github-pr-review` or a project-specific review skill for PR review.
- Use an applicable UI or site-design skill when the change is primarily visual product work.

## Frame The Outcome

Before delegating, inspect repository instructions, relevant code, tests, build scripts, and CI. Write a compact team contract containing:

- **Outcome:** the user-visible or maintenance result.
- **Priorities:** the ranked value function used to resolve tradeoffs.
- **Scope:** non-goals, repository guardrails, and protected user changes.
- **Success:** required behavior, evidence, and checks.
- **Ownership:** each role's bounded write scope, integration contracts, and locked files.
- **Model policy:** automatic selection or justified per-role model and reasoning overrides.
- **Authority:** local actions allowed by the request and actions that still require approval.

Keep shared architecture, public contracts, schema shape, dependency choices, security posture, and release decisions with the main agent. Update the contract only when evidence invalidates an assumption.

## Choose The Smallest Useful Team

- **Light mode:** implement directly and apply local regular and adversarial review lenses. Use for small docs, skills, tooling, single-file, or tightly coupled changes.
- **Delegated mode:** assign one or more independent implementation or support slices and an independent reviewer when this improves throughput or confidence.
- **High-risk mode:** add an architect before cross-boundary implementation and an adversarial reviewer over the integrated diff.

Use only roles with a concrete contribution: sidecar investigator, implementer, test/fixture/docs worker, architect reviewer, regular reviewer, or adversarial reviewer. Do not create parallel work merely to fill roles.

Read [delegation.md](references/delegation.md) completely before spawning subagents, selecting per-role models, assigning real reviewers, or creating worktrees. If delegation is unavailable or disallowed, simulate only the useful review lenses locally and label them as simulated.

## Execute

1. Assign independent work with explicit outcomes, ownership, constraints, integration assumptions, evidence, and stop conditions.
2. Launch independent agents concurrently when safe. While they run, perform only non-overlapping integration, discovery, or review preparation.
3. Inspect worker diffs and evidence. Integrate deliberately; do not trust summaries alone.
4. Add focused tests, fixtures, docs, migrations, or generated artifacts required by the behavior change.
5. Review the integrated result at the risk-appropriate lenses. Classify every actionable finding as `fixed`, `not adopted` with a reason, or `blocked`.
6. Run repository-native checks on the integrated workspace. Re-run affected checks after material fixes.
7. Publish only when the user authorized the external write. Before committing, pushing, or opening a PR, confirm the intended diff and repository conventions.

Continue through safe, in-scope local reading, editing, and validation without asking for confirmation. Stop before destructive actions, external writes, material scope expansion, or decisions that change an agreed public API, data shape, dependency policy, security posture, or release risk.

## Completion Gate

Before reporting completion:

- Inspect `git diff --stat`, the full intended diff, and `git diff --check`.
- Confirm ownership boundaries, repository guardrails, behavior coverage, generated-file handling, and unrelated dirty files.
- Verify the final answer includes the outcome, material evidence, unresolved risk, and next action when one remains.

For skill-only changes in this repository, run:

```bash
python3 scripts/validate_skills.py
git diff --check -- <changed-skill-paths>
```

For standalone skills, use the skill creator's `quick_validate.py` as a generic fallback.

## Final Response

Lead with the implemented outcome. Include the operating mode and real or simulated roles, changed files, verification results, review disposition, publication state, and material remaining risks. Omit process detail that does not help the user assess or continue the work.
