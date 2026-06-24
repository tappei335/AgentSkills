---
name: codeanalyzer-team-dev
description: Coordinate substantial CodeAnalyzer development as a value-driven team workflow with explicit goal priorities, isolated worktrees, disjoint worker ownership, architect/reviewer/adversarial-reviewer gates, verification planning, and optional PR publication. Use when the user explicitly invokes `$codeanalyzer-team-dev`, says "team development mode", asks to split work across multiple Rust engineers, asks for parallel implementers/reviewers, or wants architecture and review perspectives before integration.
---

# CodeAnalyzer Team Dev

## Operating Contract

Run CodeAnalyzer implementation, review, or repo-maintenance tasks as a coordinated team when parallelism materially helps. Keep the main agent accountable for planning, worktree/branch layout, technical direction, integration, review disposition, verification, publication decisions, and the user-facing result.

Treat explicit invocation of `$codeanalyzer-team-dev`, "team development mode", or equivalent wording as permission to delegate independent work to subagents where the active environment supports it. If this skill is triggered only because the user is editing the skill itself, or if delegation is unavailable, simulate the roles locally and state that in the final response.

For substantial product-code implementation, prefer ending with a pushed topic branch and ready-for-review PR only when the user requested or authorized publication and authentication, CI expectations, and repository state permit safe publication. Keep work local when the user asks for local-only work, when the task is analysis/planning-only, when the change is a small skill/docs/tooling edit, or when authentication / CI / repository state blocks safe publication.

Review is a completion gate. Scale review depth to task risk, but do not skip review, interrupt reviewers solely because they are slow, or silently omit unresolved reviewer findings.

## Startup

1. Read `AGENTS.md` and any path-specific rules before editing.
2. Run `git status --short`; treat pre-existing changes as user work unless proven otherwise.
3. Inspect the relevant crates, fixtures, tests, docs, or skill files before planning.
4. If the current checkout is dirty, explicitly scope which files this rollout may touch.
5. Define the goal in outcome terms, the non-goals, and the value priorities for this rollout.
6. Identify critical-path decisions, sequencing, integration points, and guardrails that the main agent must own.
7. Split only genuinely independent work. Avoid duplicate exploration.

## Goal And Value Priorities

Do not parallelize before deciding what the rollout is optimizing. Define the value function first, then choose team shape and verification depth.

State:

- User-visible goal or repository-maintenance outcome.
- Success criteria and non-goals.
- Ranked priorities such as correctness, architecture fit, test coverage, fixture fidelity, implementation speed, reviewability, performance, memory use, migration safety, and publication speed.
- Hard constraints: CodeAnalyzer guardrails, phase scope, public API compatibility, dependency policy, generated-doc rules, CI requirements, and deadline.
- Intentional deferrals that do not undermine the goal.

Use the priorities to decide whether to favor a narrower safe patch, a broader architectural slice, extra fixture coverage, a faster local-only result, or a publishable PR.

## Main Agent Role

The main agent is the accountable lead, not an extra implementer.

- Draft the task contract: intent, non-goals, touched areas, constraints, worktree strategy, worker ownership, test strategy, risks, acceptance checks, review lenses, and publication criteria.
- Record the value priorities, decision ledger, checkpoint moments, and stop conditions before assigning implementation work.
- Own planning locally. Use the architect as a design reviewer and sparring partner for the main-drafted plan, not as the owner of planning.
- Decide the final plan after resolving architect feedback. Communicate the chosen approach, worker scopes, and rejected alternatives to workers.
- Assign product-code implementation to workers when there are independent slices. Do not use worker/reviewer latency as a reason for the main agent to start editing product code.
- Keep critical-path decisions local, especially architecture, phase scope, public API, dependency choices, verification scope, and review disposition.
- Maintain visible coordination state: active worktrees, active workers, assigned write scopes, outstanding questions, review findings, and verification status.
- Treat worker output as input to review, not as accepted truth. Inspect changed files, reconcile conflicts, and adapt or reject worker changes as needed.
- Run or explicitly skip verification based on the integrated workspace state, never on subagent self-reports.

Main-agent editing is limited to unassigned work, tiny skill/docs/tooling changes, integration glue after worker output, and the smallest necessary unblocking edits. If the main agent must touch an assigned scope, first state why the ownership boundary changed, then report the edit in the final response.

## Planning With Architect

Use this gate before implementation when the task touches Rust product code, crate boundaries, public API, lowering, dataflow, MIR, diagnostics, or phase behavior.

1. Main agent drafts the plan after repository inspection.
2. Architect reviews the plan for boundary violations, dependency direction, phase separation, public API risk, missing alternatives, under-specified tests, and CodeAnalyzer guardrails.
3. Main agent revises the plan or records why feedback is not adopted.
4. Ask the user before accepting feedback that changes architecture, public API, dependency choices, phase scope, or agreed design principles.
5. Main agent publishes the final plan to workers. Workers implement the chosen plan; they do not independently redefine architecture.

## Split Criteria And Decision Ledger

Split work only when the ownership boundary is real enough to prevent duplicate or conflicting edits.

Good split candidates:

- Separate language crates or language-owned lowerers with a shared contract already defined by the main plan.
- One worker on implementation and another on fixtures/tests when the expected behavior is already specified.
- Independent docs, fixture matrix, or generated-agent-doc updates after the source-of-truth edits are known.
- Sidecar exploration or review tasks that are read-only.

Do not split:

- Shared architecture decisions, phase scope, dependency direction, public APIs, or generated-doc source of truth.
- Multiple implementations of the same behavior.
- Tightly coupled HIR/MIR/dataflow edits where the boundary is still being discovered.
- Fixes that require one worker to edit files already assigned to another active worker.

Maintain a short decision ledger:

- Decided now: architecture, owner boundaries, touched crates, public API shape, fixture strategy, docs strategy, verification gates, publication plan.
- Deferred intentionally: choices that can wait without increasing risk.
- Stop conditions: findings that pause implementation, such as guardrail pressure, unexpected dependency reversal, fixture count drift, unclear phase scope, or verification proving the plan false.
- Re-evaluation checkpoints: after architect review, after first worker result, after integration, after verification failure, and before PR publication.

## Worktree And Ownership Discipline

Do team-development implementation in explicit git worktrees. Do not run worker implementation directly in the user's current checkout.

- Make rollout edits in the integration worktree or worker worktrees, including small docs, skill, and tooling edits.
- Before implementation edits, create or choose an integration worktree on a topic branch with an allowed prefix (`feat/`, `fix/`, `refactor/`, `docs/`, or `chore/`).
- If the current checkout has unrelated dirty changes, leave them untouched. Create the integration worktree from the intended base commit or branch, not from uncommitted user work.
- Give each implementation worker its own git worktree/branch or clearly isolated forked workspace. Prefer real git worktrees when filesystem operations are available.
- Record every active worktree path, branch, owner, and write scope in the plan or progress update.
- Treat each assigned write scope as locked until the worker returns, is explicitly redirected, or is closed for a stated reason.
- Do not edit files, modules, fixtures, or docs owned by an active worker just because the worker is slow.
- Do not create a competing implementation for the same behavior while an implementer owns it.
- If a worker appears blocked, first request status or narrow the assignment. Close or replace the worker only when it is stale, mis-scoped, blocked by changed requirements, or the user redirects the task.
- Keep reviewers read-only unless explicitly assigned a fix-up worktree.
- Integrate worker results into the integration worktree deliberately, using commits, patches, or cherry-picks as appropriate. Review the resulting diff after integration.
- Do not delete worktrees that may contain uncommitted work. Clean them up only after confirming their changes were integrated or intentionally discarded.

Safe main-agent work while workers run includes non-mutating inspection, plan refinement, dependency/rule checks, drafting review criteria, preparing PR text, and editing unassigned files.

## Team Roles

Use only roles that materially help the task.

- Rust implementer A: own one clear product-code slice, preferably one crate/module boundary.
- Rust implementer B: own tests, fixtures, edge cases, or another non-overlapping product-code slice.
- Architect reviewer: review the main-drafted plan before implementation and later check crate boundaries, dependency direction, phase separation, public API impact, and design alternatives.
- Regular reviewer: check correctness, regressions, missing tests, fixtures, diagnostics, and user-visible behavior.
- Adversarial reviewer: challenge assumptions, scope creep, degraded cases, undocumented behavior changes, accidental public API changes, and over-generalization.

When spawning workers, tell each worker they are not alone in the codebase, must not revert others' edits, must stay within assigned write ownership, and must list changed files in their final response.

Suggested team sizes:

- Small skill/docs/tooling edit: main agent implements in the integration worktree; simulate regular and adversarial review locally.
- Narrow Rust bug fix: one implementer plus one reviewer; add architect review only if crate boundaries, public API, phase separation, or guardrails are touched.
- Cross-crate or behavior-changing Rust work: two implementers when write scopes are disjoint, plus architect and regular review.
- Risky architecture, lowering, dataflow, or MIR changes: full team, with adversarial review refreshed on the integrated diff.

## Effort Policy

When the active environment supports per-agent reasoning effort, choose effort by role instead of reducing parallelism:

- Main integrator: use `high` for substantial implementation tasks because it owns architecture judgment, review disposition, final verification, and publication.
- Rust implementers: use `medium` by default. Use `high` for ambiguous lowering, dataflow, crate-boundary, or cross-module changes.
- Tests / fixtures workers: use `medium` by default. Use `low` only for narrow, mechanical fixture or docs alignment work with clear examples.
- Architect reviewer: use `high`.
- Regular reviewer: use `medium`.
- Adversarial reviewer: use `high`, especially for final integrated-diff review.
- `xhigh`: reserve for exceptional blockers such as repeated build failures, subtle design conflicts, or review findings that need deep root-cause analysis.

Do not compensate for long rollouts by lowering the review bar. Prefer starting reviewers early, keeping implementers at appropriate effort, and escalating only roles or subtasks that need deeper reasoning.

## CodeAnalyzer Guardrails

Preserve these repository invariants unless the user has explicitly agreed to revisit them:

- No common AST or shared lowest-common-denominator syntax type.
- Parser, AST, HIR, and type resolution stay language-owned.
- Shared code starts at CFG, dataflow, diagnostics, and other IR-level infrastructure.
- Dependencies flow from common crates to language crates; reverse and cross-language dependencies are forbidden.
- Keep AST, HIR, MIR and their checker tiers distinct.
- Do not edit decision-record docs without explicit agreement.
- Do not edit generated agent docs or rule mirrors directly.
- Ask before adding external crate dependencies.

If a requested implementation pressures these guardrails, pause and ask before proceeding.

## Execution

1. Complete startup inspection and draft the task contract.
2. Run the Planning With Architect gate when required.
3. Record the decision ledger, worker scopes, re-evaluation checkpoints, and stop conditions.
4. Create or select the integration worktree and topic branch before implementation edits begin.
5. Delegate sidecar investigation or disjoint implementation. Record each active worker's worktree and write ownership.
6. While workers run, continue only non-overlapping main-agent work. Wait when the next useful step would require editing a worker-owned area or replacing an active review.
7. Integrate worker results carefully; review diffs instead of trusting self-reports.
8. Add or update focused tests and fixtures for behavior changes.
9. Re-evaluate the plan at each checkpoint. Update worker scope or pause for user input when evidence disproves the plan.
10. Start regular/adversarial reviewers as soon as meaningful partial diff or worker output exists; refresh review over the integrated diff.
11. Keep documentation and skill changes scoped. If `ai/fragments/` or `ai/rules/` changes, run `make agent-docs` and `make check-agent-docs`. Do not edit generated `AGENTS.md`, `CLAUDE.md`, or `.claude/rules/` directly.
12. Resolve every actionable reviewer finding: fixed, intentionally not adopted with reason, or blocked with explanation.
13. Verify the integrated workspace.
14. For publishable product-code tasks, commit the intended diff, push the topic branch, and open a ready-for-review PR from the integration worktree.
15. When a ready PR is opened and the user expects bot review, invoke `$codeanalyzer-pr-review` on that PR or report exactly why bot review was skipped.

## Review Pass

Run role-based review throughout the rollout and refresh it before finalizing.

- Architect first reviews the main plan, then checks crate boundaries, dependency direction, IR tiering, design-doc consistency, and public API impact.
- Regular reviewer checks correctness, regressions, tests, fixtures, diagnostics, and CLI behavior.
- Adversarial reviewer checks stale assumptions, false-green validation, boundary cases, degraded behavior, scope creep, and unnecessary abstraction.

If delegated reviewers are unavailable, simulate the review locally with the same lenses. If delegated reviewers are still running, local review may supplement them but must not replace them solely to save time; wait for delegated review before publication unless the reviewer is clearly stale, mis-scoped, blocked, duplicate to a completed review, or the user approves continuing without it. When proceeding without a delegated reviewer, record why the local review is sufficient and what residual risk remains.

At minimum, inspect:

- `git diff --stat` and `git diff --check`.
- The changed code paths and changed tests or fixtures.
- CodeAnalyzer guardrails, especially dependency direction, IR tier separation, generated docs, behavior coverage, and unrelated dirty files.
- Any reviewer or worker findings already received.

## Verification

Choose verification based on touched files.

For Rust/product-code changes, prefer the full gate:

```bash
cargo build --workspace
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
make check-agent-docs
make check-git-hooks
```

Do not claim the workspace builds unless `cargo build --workspace` actually ran successfully.

For narrower changes, scale verification deliberately:

- Crate-local Rust behavior: run `cargo build --workspace`, targeted tests for the touched crate or fixture path, and fmt/clippy when feasible.
- Fixture-only or diagnostics changes: run the targeted fixture/test command plus `cargo build --workspace` when behavior changed.
- `ai/fragments/` or `ai/rules/`: run `make agent-docs` and `make check-agent-docs`; inspect generated `AGENTS.md`, `CLAUDE.md`, and `.claude/rules/` only as generated outputs.
- Docs-only changes outside generated agent docs: run docs-specific checks when available and inspect links or stale references.
- Hook/tooling changes: run `make check-git-hooks` or the touched hook's focused check.

For skill-only changes, prefer:

```bash
python3 /home/ippei/.codex/skills/.system/skill-creator/scripts/quick_validate.py <path-to-skill-folder>
git diff --check -- <changed-skill-paths>
```

Regenerate `agents/openai.yaml` only when its human-facing metadata is stale relative to `SKILL.md`.

## PR Publication

Before publishing an implementation task:

- Confirm the integration worktree contains only intended changes, or explicitly stage only intended files.
- Commit with a terse message that describes the completed slice.
- Push the current topic branch with upstream tracking.
- Open a ready-for-review PR whose body states intent, scope of impact, related issue(s), verification run, and review disposition.
- Decide whether to run `$codeanalyzer-pr-review` after PR creation. Prefer running it when the task changed Rust product code, CodeAnalyzer guardrails, roadmap slices, fixtures, generated-agent-doc sources, or behavior visible to CI.
- If publishing is blocked, report the blocker, the local state, and the exact command or user action needed next.

## Final Response

For implementation tasks, report:

- Implemented scope.
- Roles used and whether they were delegated or simulated locally.
- Worktrees and branches used, including the integration worktree.
- Files changed.
- Verification commands run, failures, and skipped checks.
- Review findings disposition.
- Branch, commit, and ready PR URL when publication succeeded.
- Publication blockers or the reason work stayed local when a ready PR was not opened.
- Remaining risks or follow-up choices, if any.

For planning-only tasks, report the goal, value priorities, decision ledger, proposed worker split, checkpoints, verification plan, and open decisions.

For review-only tasks, report findings by reviewer lens, which findings were adopted or rejected, and whether implementation or publication is blocked.

For repo-maintenance or skill-only tasks, report the scoped change, why team mode was or was not used, validation run, and any sync or publication step that remains.
