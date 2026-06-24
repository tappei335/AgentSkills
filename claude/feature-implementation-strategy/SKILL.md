---
name: feature-implementation-strategy
description: >
  Plan large or consequential feature implementations before code changes by
  defining the goal as a value function, mapping system impact, comparing
  candidate strategies, and using subagents via the Agent/Workflow tools (or
  local role simulation) for metacognitive critique. Use when the user asks for
  an implementation strategy, design approach, roadmap, task breakdown,
  architecture planning, tradeoff analysis, performance or memory planning,
  rollout or migration planning, risk review, "機能実装に向けた戦略検討",
  "実装方針", "設計方針", or similar planning before substantial implementation work.
---

# Feature Implementation Strategy

Use this skill for substantial implementation work where the main risk is not typing code, but choosing the right goal, scope, architecture, tradeoffs, sequencing, and verification plan.

## Operating Contract

Produce a strategy before editing product code. Treat implementation planning as value maximization under constraints: define what outcome matters, which engineering qualities matter most for this feature, and which tradeoffs are acceptable.

Do not optimize every dimension equally. Rank correctness, user value, delivery speed, runtime speed, memory use, readability, maintainability, operability, security, migration safety, rollout safety, and reviewability according to the user's goal and repository context.

If the user only asks for strategy, do not implement. If the user asks for both strategy and implementation, complete the strategy first, then proceed only when no unresolved product, architecture, public API, dependency, data migration, security, or rollout decision remains.

Ask before accepting a strategy that changes agreed architecture, public API, dependency choices, data contracts, security posture, user-visible behavior, operational behavior, or irreversible data shape. Use `AskUserQuestion` when offering discrete choices.

When the strategy is substantial and you want approval before any code change, present it through `EnterPlanMode` / `ExitPlanMode` rather than editing files.

## Strategic Framing

Start by making the objective explicit:

1. State the user goal in outcome terms, not implementation terms.
2. Identify the beneficiary: end user, operator, developer, reviewer, system reliability, business workflow, or future extension.
3. Define success criteria, non-goals, constraints, and assumptions.
4. Rank the value priorities for this task. Use an ordered list, not a generic set.
5. Identify hard constraints that cannot be traded away: API compatibility, data integrity, latency target, memory ceiling, dependency policy, migration window, rollout policy, security requirement, or deadline.
6. Identify where quality can be intentionally deferred without undermining the goal.

Example priority orders:

- User-facing workflow: correctness > UX continuity > rollout safety > latency > maintainability > delivery speed.
- Hot-path backend change: correctness > runtime speed > memory use > operability > maintainability > delivery speed.
- Emergency fix: correctness > rollback safety > delivery speed > blast-radius reduction > readability > completeness.
- Platform foundation: correctness > maintainability > architecture fit > testability > operability > delivery speed.

When the goal or priority order is ambiguous, infer a conservative value function from the request and repository evidence. Ask one concise question (via `AskUserQuestion`) only when the answer would materially change architecture, data shape, security posture, public behavior, or rollout strategy.

## System Map

Build a map before choosing an approach:

1. Read project instructions (`CLAUDE.md`, `AGENTS.md`, relevant docs) before forming the plan.
2. Inspect the current repository state (`Bash`: `git status` / `git diff`) and treat pre-existing changes as user work.
3. Inspect relevant code, tests, fixtures, configuration, schemas, docs, and existing patterns with `Read` / `Grep` / `Glob` (or an `Explore` subagent for broad sweeps). Do not rely on memory or agent self-reports.
4. Map affected boundaries: UI, API, domain logic, persistence, background jobs, integrations, analysis pipeline, CLI, infrastructure, observability, docs, and tests.
5. Trace data flow, control flow, ownership boundaries, public contracts, and user workflows touched by the feature.
6. Identify invariants, compatibility promises, permissions, failure modes, and existing extension points.
7. Distinguish known facts, inferences, assumptions, and unknowns.

Prefer repository evidence over plausible architecture stories. Cite important files (`path:line`), symbols, interfaces, schemas, or commands in the final strategy.

## Subagent Metacognition Protocol

Use subagents as metacognitive pressure, not as decision owners. The main agent remains responsible for synthesis, judgment, and final recommendation.

For large, ambiguous, high-risk, cross-boundary, performance-sensitive, security-sensitive, migration-heavy, or high-impact work, consult subagents when subagent use is available and authorized by the active tool rules. If subagents are unavailable, simulate the same roles locally and label them as simulated.

Claude Code delegates through the `Agent` tool — each subagent runs in its own isolated context and returns only its final message, so it is ideal for bounded, self-contained probes. Pick the agent type by job:

- `Plan` — design and architecture reasoning over the existing codebase; best for proposing or stress-testing an implementation path.
- `Explore` — read-only, broad fan-out search across files and naming conventions; returns conclusions, not file dumps. Use to locate extension points and existing patterns.
- `general-purpose` — multi-step research or open-ended investigation when the first few tries may miss.

Assign narrow roles with distinct lenses:

- Goal critic: challenge whether the goal, success criteria, and value priorities match the user's real need.
- System mapper: find affected boundaries, hidden coupling, data flow, ownership issues, and existing extension points.
- Architecture critic: test whether candidate approaches fit existing architecture or distort responsibilities.
- Simplifier: identify scope that can be removed, phased, or deferred without losing core value.
- Risk reviewer: look for correctness, security, privacy, migration, rollback, operability, and blast-radius failures.
- Performance and memory reviewer: examine hot paths, algorithmic cost, I/O, batching, caching, cloning, allocation, and peak memory.
- Verification strategist: propose tests, fixtures, observability, manual checks, benchmarks, and rollback validation that create real confidence.
- Adversarial reviewer: assume the plan will fail and identify why. Prompt it to default to refuting when uncertain.

Delegate bounded questions, not the whole strategy. Give each subagent the goal, value priorities, constraints, relevant evidence (cite `path:line`), candidate approaches when known, the exact failure mode or decision to evaluate, and the expected output shape. Ask for concise facts, inferences, objections, and recommended changes with citations where possible. Launch independent subagents in a single message so they run concurrently.

For heavier planning — many independent subquestions to cover in parallel, or a generate-candidates → judge → synthesize structure that benefits from deterministic fan-out — reach for the `Workflow` tool. Only escalate to `Workflow` when the user has explicitly opted into multi-agent orchestration; otherwise propose it and ask.

Reconcile every material critique as adopted, rejected with reason, or unresolved with confidence impact. Do not let disagreement block progress unless it exposes a concrete product, architecture, public API, dependency, data, security, or rollout decision that needs user input.

## Candidate Strategy Design

Create candidates after the system map is credible:

1. Define at least two candidate approaches for non-trivial work. Include a minimal viable path and a more durable path when they differ.
2. For each candidate, explain the architectural shape, implementation sequence, changed boundaries, data or API changes, rollout path, and rollback path.
3. Evaluate each candidate against the task's ranked value priorities, not against a generic ideal.
4. Make tradeoffs explicit:
   - Delivery speed: diff size, complexity, reviewability, coordination cost, dependency churn, and migration cost.
   - Runtime speed: algorithmic complexity, hot-path impact, traversal count, I/O, network calls, batching, caching, concurrency, and incremental reuse.
   - Memory use: peak memory, retained state, cloning or copying, object lifetimes, data structures, streaming, pagination, and cache bounds.
   - Readability and maintainability: local clarity, responsibility boundaries, naming, abstraction weight, testability, and future change cost.
   - Correctness and risk: invariants, data integrity, security, privacy, degraded modes, compatibility, rollback, and operational safety.
   - Review confidence: evidence quality, critique results, testability, and remaining unknowns.
5. Choose the strategy that maximizes the stated value function. Do not choose a strategy merely because it is easiest to implement or most theoretically complete.

Prefer the smallest strategy that preserves the long-term architecture needed by the goal. Avoid speculative abstraction that does not reduce present complexity or protect an identified future change.

## Decision Ledger

Record decisions that matter:

- Decided now: architecture, ownership, public contracts, data shape, dependency choices, rollout model, verification gates.
- Deferred intentionally: decisions that can wait without increasing risk.
- Rejected alternatives: approaches considered and why they lose under the value priorities.
- Open decisions: questions requiring user, product, security, operations, or maintainer input.
- Irreversible or expensive decisions: migrations, API changes, data deletion, dependency adoption, behavior changes, and rollout commitments.

Use the ledger to prevent accidental scope drift and to make later implementation checkpoints auditable.

## Execution Slices And Checkpoints

Break the chosen strategy into slices that can be reviewed and verified:

1. Order slices to reduce uncertainty early: schema or contract proof, architecture scaffolding, core behavior, integration, UI or workflow, migration, observability, cleanup.
2. For each slice, list likely files or components, expected behavior, tests or fixtures, and acceptance checks.
3. Identify parallelizable work and work that must stay sequential because it decides architecture, API shape, data shape, rollout behavior, or shared contracts.
4. Define checkpoint moments where the plan should be re-evaluated before continuing.
5. State stop conditions: findings that should pause implementation and trigger user or maintainer input.

During implementation after the strategy, update the plan when evidence disproves an assumption. Do not keep executing a stale strategy just because it was written first.

## Verification And Rollout Plan

Define verification before coding starts:

- Unit, integration, end-to-end, fixture, snapshot, migration, compatibility, and regression tests as appropriate.
- Static checks, formatting, linting, type checks, schema validation, generated code checks, and docs checks.
- Performance or memory measurement when the value priorities or chosen strategy depend on speed or memory claims.
- Observability: logs, metrics, traces, audit events, dashboards, or alerts needed to detect bad rollout behavior.
- Manual checks for user workflows, accessibility, error states, degraded modes, and operator actions.
- Rollout, feature flags, backfill, dual-read/write, compatibility window, rollback, and data recovery where relevant.

Verification should prove the strategy's value priorities, not just that code was exercised.

## Output Format

Use this structure unless the user requested a different format:

1. Goal and value priorities.
2. Current-system evidence and system map (with `path:line` references).
3. Constraints, assumptions, and non-goals.
4. Candidate strategies with a compact tradeoff comparison.
5. Recommended strategy and why it maximizes the value function.
6. Decision ledger.
7. Execution slices and checkpoints.
8. Verification, rollout, and rollback plan.
9. Subagent metacognition summary: roles consulted or simulated, strongest objections, adopted changes, rejected recommendations, and unresolved risks.
10. Open decisions or questions.

Keep the strategy concrete enough that another agent can implement it without redesigning the feature, while still making the reasoning and tradeoffs visible enough for review.
