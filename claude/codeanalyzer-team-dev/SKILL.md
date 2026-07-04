---
name: codeanalyzer-team-dev
description: >
  Coordinate substantial CodeAnalyzer development as a value-driven, mixed-model
  team (Claude subagents plus Codex via `/codex:rescue`, `/codex:review`,
  and `/codex:adversarial-review`) with explicit goal priorities, isolated
  worktrees, disjoint worker ownership, architect/reviewer/adversarial-reviewer
  gates, verification planning, and optional PR publication. Use when the user
  invokes `/codeanalyzer-team-dev`, says "team development mode", "チーム開発モード",
  asks to split work across multiple Rust engineers, asks for parallel
  implementers/reviewers, or wants architecture and review perspectives before
  integration.
argument-hint: "[task description]"
---

# CodeAnalyzer Team Dev

## Operating Contract

Run CodeAnalyzer implementation, review, or repo-maintenance tasks as a coordinated team when the work splits into two or more disjoint write scopes, or one write scope plus independent review value. If it does not split, use light mode: the main agent implements and the review lenses still run. Keep the main agent (Claude) accountable for planning, worktree/branch layout, technical direction, integration, review disposition, verification, publication decisions, and the user-facing result.

Deliberately mix Claude subagents and Codex commands so that review and adversarial passes come from a different model family than the implementer, not just a second instance of the same model.

Treat explicit invocation of `/codeanalyzer-team-dev`, "team development mode", or equivalent wording as permission to delegate independent work to subagents where the active environment supports it. If this skill is triggered only because the user is editing the skill itself, or if delegation is unavailable, simulate the roles locally and state that in the final response.

For substantial product-code implementation, prefer ending with a pushed topic branch and ready-for-review PR only when the user requested or authorized publication and authentication, CI expectations, and repository state permit safe publication. Keep work local when the user asks for local-only work, when the task is analysis/planning-only, when the change is a small skill/docs/tooling edit, or when authentication / CI / repository state blocks safe publication.

Non-negotiables:

- Review is a completion gate. Scale review depth to task risk, but never skip review, interrupt reviewers solely because they are slow, or silently omit unresolved reviewer findings.
- Write-owning workers get isolated worktrees; nobody implements in the user's checkout.
- One behavior, one owner: never spawn a competing implementation or edit a worker-owned file because the worker is slow.
- Verification runs on the integrated tree, never on worker or Codex self-reports.
- Route at least one review lens to Codex when it is available, so implementer and reviewer come from different model families.
- Never push to `main`; publish only when the user authorized publication.

## Startup

1. Read `CLAUDE.md`, `AGENTS.md`, and any path-specific rules under `.claude/rules/` or `ai/rules/` before editing.
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
- Maintain visible coordination state with `TaskCreate`: active worktrees, active workers, assigned write scopes, outstanding questions, review findings, and verification status.
- Treat worker and Codex output as input to review, not as accepted truth. Inspect changed files with `Read`, reconcile conflicts, and adapt or reject worker changes as needed.
- Make the final engineering decision when reviewers disagree, using CodeAnalyzer guardrails and local code patterns.
- Run or explicitly skip verification based on the integrated workspace state, never on subagent or Codex self-reports.

Main-agent editing is limited to unassigned work, tiny skill/docs/tooling changes, integration glue after worker output, and the smallest necessary unblocking edits. If the main agent must touch an assigned scope, first state why the ownership boundary changed, then report the edit in the final response.

## Planning With Architect

Use this gate before implementation when the task touches Rust product code, crate boundaries, public API, lowering, dataflow, MIR, diagnostics, or phase behavior. Delegate the architect review to a Claude `Agent(subagent_type="Plan")`, or simulate it locally when delegation is unavailable.

1. Main agent drafts the plan after repository inspection.
2. Architect reviews the plan for boundary violations, dependency direction, phase separation, public API risk, missing alternatives, under-specified tests, and CodeAnalyzer guardrails.
3. Main agent revises the plan or records why feedback is not adopted.
4. Ask the user (via `AskUserQuestion`) before accepting feedback that changes architecture, public API, dependency choices, phase scope, or agreed design principles.
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

Maintain a short decision ledger (tracked alongside `TaskCreate` ownership entries):

- Decided now: architecture, owner boundaries, touched crates, public API shape, fixture strategy, docs strategy, verification gates, publication plan.
- Deferred intentionally: choices that can wait without increasing risk.
- Stop conditions: findings that pause implementation, such as guardrail pressure, unexpected dependency reversal, fixture count drift, unclear phase scope, or verification proving the plan false.
- Re-evaluation checkpoints: after architect review, after first worker result, after integration, after verification failure, and before PR publication.

## Worktree And Ownership Discipline

Do team-development implementation in explicit git worktrees. Do not run worker implementation directly in the user's current checkout.

- Make rollout edits in the integration worktree or worker worktrees, including small docs, skill, and tooling edits.
- Before implementation edits, create or choose an integration worktree on a topic branch with an allowed prefix (`feat/`, `fix/`, `refactor/`, `docs/`, or `chore/`).
- If the current checkout has unrelated dirty changes, leave them untouched. Create the integration worktree from the intended base commit or branch, not from uncommitted user work.
- Give each implementation worker its own isolated workspace. For Claude implementation workers, use `Agent(subagent_type="general-purpose", isolation="worktree")` so the worker gets its own git worktree/branch and cannot revert another worker's edits or contaminate the main worktree. For Codex implementation workers (`/codex:rescue`), assign a clearly isolated branch/worktree.
- Record every active worktree path, branch, owner, and write scope in the plan or progress update (`TaskCreate`).
- Treat each assigned write scope as locked until the worker returns, is explicitly redirected, or is closed for a stated reason.
- Do not edit files, modules, fixtures, or docs owned by an active worker just because the worker is slow.
- Do not create a competing implementation for the same behavior while an implementer owns it.
- If a worker appears blocked, first request status or narrow the assignment via `SendMessage(to=<agent name>)`. Close or replace the worker only when it is stale, mis-scoped, blocked by changed requirements, or the user redirects the task.
- Keep reviewers read-only unless explicitly assigned a fix-up worktree.
- Integrate worker results into the integration worktree deliberately, using commits, patches, or cherry-picks as appropriate. Review the resulting diff after integration.
- Do not delete worktrees that may contain uncommitted work. Clean them up only after confirming their changes were integrated or intentionally discarded.

Safe main-agent work while workers run includes non-mutating inspection, plan refinement, dependency/rule checks, drafting review criteria, preparing PR text, and editing unassigned files.

## Team Roles (Mixed-Model)

Use only roles that materially help the task, and prefer model diversity for review roles. A one-file fix does not need five subagents.

| Role | Default delegation | Responsibility / why |
|---|---|---|
| Rust implementer A (slice 1) | Claude `Agent(subagent_type="general-purpose", isolation="worktree")` | Own one clear product-code slice, preferably one crate/module boundary. Claude follows repo-local `CLAUDE.md` / `.claude/rules/` well; worktree isolation prevents write conflicts. |
| Rust implementer B (slice 2, or the harder slice) | `/codex:rescue --background [task text]` | Own tests, fixtures, edge cases, or another non-overlapping product-code slice. A different model family catches blind spots the Claude implementer misses; background so the main agent is not blocked. |
| Architect reviewer | Claude `Agent(subagent_type="Plan")` | Review the main-drafted plan before implementation, then check crate boundaries, dependency direction, phase separation, public API impact, and design alternatives. Has direct access to `CLAUDE.md` / decision-record docs. |
| Regular reviewer | `/codex:review --background` | Independent correctness/regression pass from a different model: tests, fixtures, diagnostics, and user-visible behavior. |
| Adversarial reviewer | `/codex:adversarial-review --background [focus]` | Challenge assumptions, scope creep, degraded cases, undocumented behavior changes, accidental public API changes, and over-generalization. Run after the integrated diff exists so there is something concrete to attack. |
| Sidecar exploration | Claude `Agent(subagent_type="Explore")` | Fast read-only repo-local discovery; no need to route to Codex. |

When spawning workers, tell each worker they are not alone in the codebase, must not revert others' edits, must stay within assigned write ownership, and must list changed files in their final response.

Suggested team sizes:

- Small skill/docs/tooling edit: main agent implements in the integration worktree; simulate regular and adversarial review locally.
- Narrow Rust bug fix: one implementer plus one reviewer; add architect review only if crate boundaries, public API, phase separation, or guardrails are touched.
- Cross-crate or behavior-changing Rust work: two implementers when write scopes are disjoint, plus architect and regular review.
- Risky architecture, lowering, dataflow, or MIR changes: full team, with adversarial review refreshed on the integrated diff.

## Delegation Rules

- **Parallelize independent work.** When spawning multiple independent Claude subagents, put all tool calls in a single message so they run concurrently. Do not serialize independent workers.
- **Isolate implementer writes.** Implementation workers that will write product code should use `isolation: "worktree"` so they cannot revert each other's edits or contaminate the main worktree.
- **Brief workers fully.** Each worker starts cold and has no view of this conversation. Include: the specific slice scope, disjoint file ownership, the repo invariants from `CLAUDE.md` that apply, the verification commands expected, and the instruction that the worker is not alone in the codebase and must list changed files in its final response.
- **Continue, do not respawn.** Use `SendMessage(to=<agent name>)` to continue an existing worker with full context. Spawning a new `Agent()` for follow-up work loses context and risks redoing the same task.
- **Codex commands are forwarders.** `/codex:rescue`, `/codex:review`, and `/codex:adversarial-review` return Codex output verbatim. Do not paraphrase their output before integrating, and do not ask the Codex side to fetch results, poll status, or do follow-up work. The main agent owns follow-up.
- **Codex context is forked.** `/codex:rescue` runs with forked context, so put every decision, constraint, and acceptance criterion into the prompt text. Do not assume Codex has seen this conversation.
- **Never skip hooks or force-push on a worker's behalf.** Workers and Codex must not push, force-push, skip `--no-verify`, or bypass pre-commit signing. If a worker is blocked by a hook, diagnose the underlying issue.

## Fallback When Codex Is Unavailable

If `/codex:rescue` reports that the Codex CLI is missing or unauthenticated, tell the user to run `/codex:setup`. Until Codex is available, downgrade the team shape:

- Implementer B → Claude `Agent(general-purpose, isolation="worktree")` with an explicit instruction to take a different implementation angle than Implementer A.
- Regular reviewer → Claude `Agent(general-purpose)` with a review-only prompt.
- Adversarial reviewer → Claude `Agent(general-purpose)` with an adversarial prompt that explicitly challenges the chosen approach.

State clearly in the final response that Codex roles were simulated locally, not actually delegated to a second model.

## Effort Policy

Match reasoning effort or model tier to role instead of reducing parallelism. Where the environment exposes per-agent effort (`Workflow`) or model selection (`Agent`), and for the effort each `/codex:*` command runs at, choose by role:

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

- No common AST or lowest-common-denominator shared syntax type.
- Sharing stops below IR: CFG, dataflow, and diagnostics can be shared; parser, AST, HIR, and type resolution stay per-language.
- Dependencies flow from common crates to language crates; reverse and cross-language dependencies are forbidden.
- Keep AST, HIR, MIR and their checker tiers distinct.
- Do not edit decision-record docs without explicit agreement.
- Do not edit generated agent docs or rule mirrors directly (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/`). Change `ai/fragments/` or `ai/rules/` and run `make agent-docs`.
- Ask before adding external crate dependencies.
- Never push directly to `main`; always go through a topic branch + PR.

If a requested implementation pressures these guardrails, pause and ask before proceeding. Include these guardrails in worker and Codex prompts so they do not silently cross them.

## Execution

1. Complete startup inspection and draft the task contract.
2. Run the Planning With Architect gate when required.
3. Record the decision ledger, worker scopes (`TaskCreate`), re-evaluation checkpoints, and stop conditions.
4. Create or select the integration worktree and topic branch before implementation edits begin.
5. Delegate sidecar investigation or disjoint implementation. Launch independent workers in a single message; use `run_in_background: true` for long-running Claude subagents and `--background` for Codex commands so the main agent keeps working. Record each active worker's worktree and write ownership.
6. While workers run, continue only non-overlapping main-agent work. Wait when the next useful step would require editing a worker-owned area or replacing an active review.
7. Integrate worker results carefully; `Read` the changed files and worktree diffs instead of trusting self-reports.
8. Add or update focused tests and fixtures for behavior changes.
9. Re-evaluate the plan at each checkpoint. Update worker scope or pause for user input when evidence disproves the plan.
10. Start regular/adversarial reviewers (`/codex:review`, `/codex:adversarial-review`, or simulated Claude agents) as soon as meaningful partial diff or worker output exists; refresh review over the integrated diff.
11. Keep documentation and skill changes scoped. If `ai/fragments/` or `ai/rules/` changes, run `make agent-docs` and `make check-agent-docs`. Do not edit generated `AGENTS.md`, `CLAUDE.md`, or `.claude/rules/` directly.
12. Resolve every actionable reviewer finding: fixed, intentionally not adopted with reason, or blocked with explanation.
13. Verify the integrated workspace.
14. For publishable product-code tasks, commit the intended diff, push the topic branch, and open a ready-for-review PR from the integration worktree.
15. When a ready PR is opened and the user expects bot review, invoke the `codeanalyzer-pr-review` skill (Skill tool: `/codeanalyzer-pr-review <PR>`) on that PR or report exactly why bot review was skipped.

## Review Pass

Run role-based review throughout the rollout and refresh it before finalizing. Prefer model diversity: route reviewers to a different model family than the implementer.

- Architect (Claude `Agent(subagent_type="Plan")`) first reviews the main plan, then checks crate boundaries, dependency direction, IR tiering, design-doc consistency, and public API impact.
- Regular reviewer (`/codex:review`) checks correctness, regressions, tests, fixtures, diagnostics, and CLI behavior.
- Adversarial reviewer (`/codex:adversarial-review`) checks stale assumptions, false-green validation, boundary cases, degraded behavior, scope creep, accidental public API changes, and unnecessary abstraction.

If delegated reviewers are unavailable, simulate the review locally with the same lenses. If delegated reviewers are still running, local review may supplement them but must not replace them solely to save time; wait for delegated review before publication unless the reviewer is clearly stale, mis-scoped, blocked, duplicate to a completed review, or the user approves continuing without it. When proceeding without a delegated reviewer, record why the local review is sufficient and what residual risk remains.

At minimum, inspect:

- `git diff --stat` and `git diff --check`.
- The changed code paths and changed tests or fixtures.
- CodeAnalyzer guardrails, especially dependency direction, IR tier separation, generated docs, behavior coverage, and unrelated dirty files.
- Any reviewer or worker findings already received.

The main agent makes the final call when reviewers disagree, using CodeAnalyzer guardrails and local code patterns.

## Verification

The main agent runs verification locally on the integrated tree, not on a worker's or Codex's report. Choose verification based on touched files.

For Rust/product-code changes, prefer the full gate:

```bash
cargo build --workspace
cargo test --workspace
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
make check-agent-docs
make check-git-hooks
```

Do not claim the workspace builds unless `cargo build --workspace` actually ran successfully on the integrated tree. `cargo check` and `cargo test` alone can give false-green from caching.

For narrower changes, scale verification deliberately:

- Crate-local Rust behavior: run `cargo build --workspace`, targeted tests for the touched crate or fixture path, and fmt/clippy when feasible.
- Fixture-only or diagnostics changes: run the targeted fixture/test command plus `cargo build --workspace` when behavior changed.
- `ai/fragments/` or `ai/rules/`: run `make agent-docs` and `make check-agent-docs`; inspect generated `AGENTS.md`, `CLAUDE.md`, and `.claude/rules/` only as generated outputs.
- Docs-only changes outside generated agent docs: run docs-specific checks when available and inspect links or stale references.
- Hook/tooling changes: run `make check-git-hooks` or the touched hook's focused check.

For skill-only changes inside the AgentSkills repository, prefer:

```bash
python3 scripts/validate_skills.py
git diff --check -- <changed-skill-paths>
```

For installed or standalone skills outside that repository, use the generic fallback:

```bash
python3 /home/ippei/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/quick_validate.py <path-to-skill-folder>
```

## PR Publication

Before publishing an implementation task:

- Confirm the integration worktree contains only intended changes, or explicitly stage only intended files.
- Commit with a terse message that describes the completed slice.
- Push the current topic branch with upstream tracking.
- Open a ready-for-review PR whose body states intent, scope of impact, related issue(s), verification run, and review disposition.
- Decide whether to run `/codeanalyzer-pr-review` after PR creation. Prefer running it when the task changed Rust product code, CodeAnalyzer guardrails, roadmap slices, fixtures, generated-agent-doc sources, or behavior visible to CI.
- If publishing is blocked, report the blocker, the local state, and the exact command or user action needed next.

## Final Response

For implementation tasks, report:

- Implemented scope.
- Roles used, and for each role whether it was delegated (to a Claude subagent or a Codex command) or simulated locally.
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
