---
name: refactoring-strategy
description: Design evidence-based strategies for large-scale refactoring, technical-debt reduction, and legacy modernization without editing product code. Use when the user requests a refactoring strategy or plan, technical-debt assessment or prioritization, modernization roadmap, staged migration, monolith or module decomposition, "リファクタリング戦略", "リファクタリング計画", "技術的負債の整理", "段階的移行", or "レガシー改善". Require hotspot evidence, an incremental migration pattern, a phased and reversible roadmap, and real subagent critique. Do not use for executing small local refactors.
---

# Refactoring Strategy

## Operating Contract

Produce a decision-ready strategy, not product-code changes. Inspect files, history, tests, build configuration, and diagnostics as needed, but preserve the workspace. If implementation is also requested, finish the strategy and hand off the approved phases to an implementation workflow.

Treat behavior preservation as the default invariant. Separate intended behavior changes into labeled work outside the refactoring phases. Support codebase claims with inspected evidence such as `path:line`, commands, or measured results; label inferences, assumptions, and unknowns.

Ask a question only when an ambiguity would materially change the outcome, public contracts, migration shape, or risk posture. Otherwise proceed with a stated assumption and expose it in the strategy.

## Frame The Decision

Create a compact decision contract before the survey:

- **Outcome:** what the refactor must unlock and for whom.
- **Success:** measurable leading and lagging indicators.
- **Priorities:** ranked value function for tradeoffs.
- **Constraints:** compatibility, release cadence, capacity, deadlines, and risk tolerance.
- **Non-goals:** behavior changes and debt intentionally outside scope.

If the request is only “clean this up,” derive candidate outcomes from repository evidence and state the one used for prioritization.

## Build The Evidence Base

Inspect repository instructions, architecture records, dependency and build files, tests, CI, and relevant history. Focus the survey on evidence that can change the roadmap:

- Find hotspots where change frequency intersects complexity, defects, or coordination cost. Use repository tooling first; use targeted `git log` aggregation when no native report exists.
- Map dependency direction, cycles, shared mutable state, database or event coupling, reflection, serialization, and other hidden contracts.
- Assess safety on the affected paths: characterization coverage, integration tests, type checks, CI gates, runtime observability, test duration, and flakiness.
- Identify public APIs, schemas, events, persisted formats, and downstream consumers that constrain migration.

Read load-bearing files directly. Use subagents for independent, read-heavy fan-out and require distilled evidence rather than raw search output. Verify reference counts with language tooling when available.

Inventory each debt item by symptom, evidence, root cause, blast radius, value unlocked, change frequency, effort, and migration risk. Prioritize enabling seams and high-value hotspots. Explicitly park stable, isolated, low-churn debt whose payoff does not justify its risk.

## Choose The Target And Migration

Describe only the target boundaries, ownership, dependency direction, and contracts needed to make migration decisions. Avoid speculative redesign beyond the roadmap horizon.

Read [migration-patterns.md](references/migration-patterns.md) completely when choosing patterns. Default to incremental migration and justify the selected pattern against the evidence. Require explicit user approval for any big-bang rewrite.

Define the coexistence state while old and new structures overlap: write ownership, compatibility rules, transition lifetime, deletion criteria, and automated drift prevention.

## Build A Reversible Roadmap

Make every phase independently shippable and revertible without leaving the system unreleasable. Use the smallest end-to-end slice as the pilot to validate effort, coupling, and verification assumptions.

For each phase specify:

- outcome, scope, dependencies, and affected contracts;
- characterization, contract, integration, regression, or runtime evidence required to enter and exit;
- migration and coexistence mechanics, including mechanical transforms where possible;
- rollback action, rollback trigger, stop condition, and estimated size;
- work that must remain sequential and work that can run independently.

Use shadow traffic, parallel-run diffs, metrics, or alerts when tests cannot prove preservation. Prefer expand–migrate–contract ordering and schedule removal of transitional paths as explicit work.

## Subagent Critique Gate

Consult at least one real subagent before finalizing. Scale independent critique to risk; do not spawn roles merely to fill a checklist. If subagent tools are unavailable, blocked, or disallowed, stop and report that the strategy cannot satisfy this skill’s critique gate. Do not substitute local role-play.

Use read-only agents for critique and evidence checks. Give each the decision contract, relevant evidence, one narrow lens, and a required output of prioritized findings with citations, confidence, and a concrete correction. Useful lenses are payoff and scope, hotspot evidence, hidden coupling, behavior-preservation gaps, phase reversibility, and half-migrated failure modes.

Prefer automatic model selection unless quality, latency, or cost requires an override. When supported, use `gpt-5.6-terra` with medium effort for repository scans and evidence aggregation; use `gpt-5.6` with high effort for architecture, safety, or adversarial critique; use `gpt-5.6-luna` with low effort only for mechanical, objectively checkable aggregation. Reserve `xhigh` or `max` for the hardest quality-first synthesis after a lower setting proves insufficient.

For a custom Codex agent, set `model` and `model_reasoning_effort`; omit them to inherit the parent configuration. If the spawn interface cannot select a model, use a configured agent or inherit the parent model, and do not claim an override occurred.

Wait for required critics, inspect their evidence, and reconcile every material finding as adopted, rejected with reason, or unresolved with its confidence impact. The main agent owns the final prioritization and roadmap.

## Output

Lead with the recommendation and the value it unlocks. Include:

1. Decision contract and key assumptions.
2. Evidence summary: hotspots, coupling, safety net, and constrained contracts.
3. Prioritized debt inventory and parked items.
4. Target boundaries and migration-pattern rationale.
5. Phased roadmap with verification, rollback, stop, and deletion gates.
6. Coexistence and drift-prevention rules.
7. Subagent findings and disposition.
8. Material risks and open user decisions.

Keep all evidence, decisions, caveats, and next actions. Remove repeated process narration and background that does not change the roadmap.
