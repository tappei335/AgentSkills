---
name: feature-implementation-strategy
description: Plan large or consequential feature implementations before code changes by defining the outcome and ranked value priorities, mapping system impact, comparing candidate strategies, and requiring real subagent critique. Use when the user requests an implementation strategy, design approach, architecture plan, roadmap, task breakdown, performance or memory plan, rollout or migration plan, risk review, "機能実装に向けた戦略検討", "実装方針", or "設計方針" before substantial implementation work.
---

# Feature Implementation Strategy

## Operating Contract

Produce a decision-ready implementation strategy before editing product code. If the user requests only planning, preserve the workspace. If implementation is also requested, finish the strategy first and continue only after material product, architecture, API, dependency, data, security, and rollout decisions are resolved.

Treat planning as value maximization under constraints. Rank the qualities that matter for this feature rather than optimizing correctness, user value, delivery speed, runtime, memory, maintainability, operability, security, migration safety, and reviewability equally.

Ask a question only when an ambiguity would materially change public behavior, architecture, data shape, security posture, dependencies, or rollout risk. Otherwise proceed with a conservative stated assumption.

## Frame The Decision

Create a compact decision contract:

- **Outcome and beneficiary:** what changes and who benefits.
- **Success:** measurable behavior and acceptance evidence.
- **Priorities:** ordered value function used to resolve tradeoffs.
- **Constraints:** compatibility, latency, memory, dependency, migration, security, rollout, capacity, and deadline limits.
- **Non-goals and deferrals:** quality or scope intentionally excluded.

Infer a conservative priority order from the request and repository evidence when the user does not provide one. Keep hard constraints separate from preferences.

## Map The System

Read repository instructions and inspect relevant code, tests, fixtures, configuration, schemas, docs, build rules, and current user changes. Trace only the boundaries that can affect the decision:

- user workflow, control flow, data flow, ownership, and extension points;
- UI, API, domain, persistence, jobs, integrations, CLI, infrastructure, and observability touched;
- public contracts, invariants, permissions, degraded modes, and compatibility promises;
- existing patterns that candidates should reuse or deliberately replace.

Support material claims with files, symbols, schemas, commands, or measured results. Distinguish facts, inferences, assumptions, and unknowns.

## Compare Candidate Strategies

For non-trivial work, compare at least a minimal viable path and a durable path when they meaningfully differ. Describe each candidate only to the depth needed to choose:

- architecture and responsibility boundaries;
- implementation sequence and changed contracts;
- data, migration, rollout, observability, and rollback shape;
- delivery and coordination cost;
- runtime, memory, security, correctness, maintenance, and review-confidence tradeoffs.

Score candidates against the ranked value priorities, not a generic ideal. Recommend the smallest approach that achieves the outcome without creating an identified architectural dead end. Reject speculative abstraction that protects no concrete requirement or near-term change.

Record decided, deferred, rejected, open, and expensive-to-reverse choices in a decision ledger.

## Subagent Critique Gate

Consult at least one real subagent before finalizing. Scale independent critique to risk and do not spawn roles merely to fill a checklist. If subagent tools are unavailable, blocked, or disallowed, stop and report that the strategy cannot satisfy this skill's critique gate. Do not substitute local role-play.

Give each read-only critic the decision contract, relevant evidence, candidate choices, one narrow lens, and a required output of prioritized findings with citations, confidence, and a concrete correction. Useful lenses are goal fit, hidden coupling, architecture fit, simplification, correctness/security/rollout risk, performance and memory, verification strength, and adversarial failure.

Prefer automatic model selection unless quality, latency, or cost requires an override. When supported, use `gpt-5.6-terra` with medium effort for system mapping and evidence sweeps; use `gpt-5.6` with high effort for architecture, risk, performance, or adversarial critique; use `gpt-5.6-luna` with low effort only for mechanical, objectively checkable inventories. Reserve `xhigh` or `max` for the hardest quality-first synthesis after a lower setting proves insufficient.

For custom Codex agents, set `model` and `model_reasoning_effort`; omit them to inherit the parent configuration. Never claim an override unless the runtime or agent configuration confirms it.

Wait for required critics and reconcile every material finding as adopted, rejected with reason, or unresolved with its confidence impact. The main agent owns the final recommendation.

## Build Execution Slices

Order slices to reduce uncertainty early. For each slice specify the outcome, likely components, dependencies, behavior, tests or fixtures, acceptance checks, rollback, and stop conditions. Keep shared-contract decisions sequential; mark genuinely independent work for parallel execution.

Define verification before coding: repository-native static checks and tests, performance or memory measurements when they drive the decision, user and operator workflow checks, observability, migration validation, rollout gates, and recovery.

Re-evaluate the strategy at contract, architecture, migration, and rollout checkpoints or whenever implementation evidence disproves an assumption.

## Output

Lead with the recommended strategy and why it wins under the value priorities. Include:

1. Decision contract and system evidence.
2. Candidate comparison and recommendation.
3. Decision ledger.
4. Execution slices and checkpoints.
5. Verification, rollout, rollback, and stop conditions.
6. Subagent findings and disposition.
7. Material risks and open user decisions.

Keep the strategy concrete enough to implement without redesigning the feature. Remove repeated process narration and sections that would not change what gets built.
