---
name: team-dev
description: Coordinate explicit multi-agent repository implementation work with value priorities, disjoint ownership, real or simulated team roles, integration review, verification, and optional PR publication. Use when the user invokes `$team-dev`, says "team development mode" or "チーム開発モード", asks to split implementation across multiple engineers/workers, or requests parallel implementers plus reviewers for a substantial code change. Do not use for planning-only strategy, investigation/audit, PR review, or small single-agent edits unless the user explicitly asks for team mode.
---

# Team Dev

## Operating Contract

Run substantial repository changes as a coordinated team workflow only when the work splits into two or more disjoint write scopes, or one write scope plus independent review value. If it does not split, use light team mode. Keep the main agent accountable for goal framing, worker scope, repository guardrails, integration, review disposition, verification, publication decisions, and the final user-facing result.

Prefer more specific skills when they match the request better:

- Use `$feature-implementation-strategy` for planning-only architecture, tradeoff, roadmap, or implementation strategy work.
- Use `$maximize-research-results` for investigation, audit, diagnosis, comparison, or broad research.
- Use `$github-pr-review` or a project-specific PR review skill for PR review.
- Use UI or site-design skills when the task is primarily product UI or site recreation.

If `$team-dev` is explicitly invoked for a small docs, skill, tooling, or single-file change, use light team mode: make the scoped edit directly, simulate the relevant review lenses locally, and report why full worker delegation or worktree isolation was unnecessary.

## Mode Gate

Before assigning work, decide the operating mode and state it briefly.

1. Define the outcome goal, success criteria, non-goals, and ranked value priorities.
2. Read repository instructions and inspect relevant code, tests, docs, build scripts, and CI before planning.
3. Extract project guardrails: dependency direction, generated-file rules, public API promises, schemas/migrations, security boundaries, review rules, and required checks.
4. Decide whether real delegation is allowed and useful under the active tool policy. If real subagents are unavailable or disallowed, simulate roles locally and do not describe the result as parallel execution.
5. Decide whether worktrees are necessary. Use explicit worktrees for concurrent write-owning workers or dirty-checkout isolation. Do not require worktrees for planning-only, read-only review, local simulation, or small single-agent edits.
6. Split only independent work with clear write ownership. Keep shared architecture, public contracts, schema shape, dependency choices, and release decisions with the main agent.

Read [delegation.md](references/delegation.md) before spawning subagents, assigning reviewers, or creating worktrees.

## Team Contract

Draft a compact team contract before implementation:

- **Goal:** user-visible outcome or repository-maintenance result.
- **Priorities:** ordered value function, such as correctness > migration safety > reviewability > speed.
- **Non-goals:** explicit boundaries and intentional deferrals.
- **Guardrails:** repository rules and invariants that workers must preserve.
- **Plan:** architecture shape, affected areas, integration points, and stop conditions.
- **Ownership:** worker roles, write scopes, worktrees/branches when used, and locked files.
- **Review:** architect, regular, and adversarial lenses scaled to risk.
- **Verification:** commands or manual checks required before finalizing.
- **Publication:** local-only, commit-only, or PR plan, including blockers.

Use the contract to prevent scope drift. Update it when evidence invalidates an assumption.

## Role Selection

Use only roles that materially help the task.

- **Main integrator:** owns decisions, plan revisions, integration, verification, and final response.
- **Implementer:** owns one disjoint product-code slice, package, module, screen, migration, or command.
- **Test/fixture/docs worker:** owns acceptance coverage or supporting artifacts after expected behavior is specified.
- **Sidecar investigator:** performs read-only discovery for unfamiliar code or hidden dependencies.
- **Architect reviewer:** checks boundaries, dependency direction, public API/data impact, migration safety, and alternatives.
- **Regular reviewer:** checks correctness, regressions, tests, fixtures, diagnostics, accessibility, security, and user-visible behavior.
- **Adversarial reviewer:** challenges assumptions, degraded cases, scope creep, accidental API changes, false-green validation, and unnecessary abstraction.

Workers must be told that they are not alone in the codebase, must not revert others' edits, must stay within assigned ownership, must preserve discovered guardrails, and must list changed files in their final response.

Suggested shapes:

- **Light mode:** main agent implements; local regular/adversarial review. Use for small docs, skills, tooling, or narrow edits.
- **Narrow implementation:** one implementer plus one reviewer. Add architect review when public contracts, migrations, or boundaries are involved.
- **Cross-boundary change:** two or more disjoint implementers plus architect and regular review.
- **High-risk change:** add adversarial review over the integrated diff, and refresh verification after every material fix.

## Execution

1. Complete the mode gate and team contract.
2. Create worktrees only when the mode requires concurrent writers or dirty-checkout isolation.
3. Delegate sidecar investigation or disjoint implementation with explicit ownership. Launch independent agents in parallel when possible.
4. While workers run, do only non-overlapping main-agent work: inspect, refine the plan, prepare review criteria, or draft PR text.
5. Integrate worker results deliberately. Inspect diffs and changed files instead of trusting summaries.
6. Add or update focused tests, fixtures, docs, migrations, or generated artifacts for behavior changes.
7. Run architect, regular, and adversarial review lenses according to risk. Real reviewers are preferred when available; otherwise local simulation must be labeled.
8. Resolve every actionable reviewer finding as fixed, intentionally not adopted with reason, or blocked.
9. Verify the integrated workspace using repository-native commands.
10. Publish only when authorized and safe: commit intended changes, push a topic branch, and open a ready PR when requested or expected.

Re-evaluate after architect feedback, first worker output, integration, verification failure, and before publication. Pause for user input when a finding would change agreed architecture, public API, dependency policy, data shape, security posture, or release risk.

## Review And Verification

Review is a completion gate. Do not skip it, replace still-running real reviewers solely for speed, or omit unresolved findings.

At minimum inspect:

- `git diff --stat` and `git diff --check`.
- Changed code paths and changed tests, fixtures, docs, migrations, or generated artifacts.
- Repository guardrails, especially dependency direction, generated-file handling, public API changes, schema/migration impact, behavior coverage, and unrelated dirty files.
- Worker and reviewer findings already received.

Choose verification from the repository's own tooling: CI workflows, package scripts, Makefiles, contribution docs, and local conventions. Prefer build/typecheck, formatter, linter/static analysis, targeted tests, broader tests for shared behavior, and generated-file checks when source-of-truth files changed.

For skill-only changes inside this AgentSkills repository, prefer:

```bash
python3 scripts/validate_skills.py
git diff --check -- <changed-skill-paths>
```

For installed or standalone skills outside this repository, use `quick_validate.py` as a generic fallback:

```bash
python3 /home/ippei/.codex/skills/.system/skill-creator/scripts/quick_validate.py <path-to-skill-folder>
```

## Final Response

For implementation tasks, report:

- Implemented scope.
- Operating mode, roles used, and whether roles were delegated or simulated locally.
- Worktrees and branches used, or why they were unnecessary.
- Files changed.
- Verification commands run, failures, and skipped checks.
- Review findings disposition.
- Branch, commit, and PR URL when publication succeeded.
- Publication blockers or the reason work stayed local.
- Remaining risks or follow-up choices, if any.

For planning-only or review-only requests that explicitly invoked `$team-dev`, report the selected mode, why implementation delegation did or did not apply, findings or plan output, and any blocked publication or verification step.
