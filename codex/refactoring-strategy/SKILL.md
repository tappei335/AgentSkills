---
name: refactoring-strategy
description: Design strategies for large-scale refactoring, technical-debt reduction, and legacy modernization without editing product code by surveying the codebase with churn and hotspot evidence, inventorying and prioritizing debt, choosing an incremental migration pattern (Strangler Fig, Branch by Abstraction, Parallel Change), and producing a phased, verifiable roadmap with required subagent critique. Use when the user asks Codex for a refactoring strategy or plan, technical-debt assessment or prioritization, modernization roadmap, staged or incremental migration design, monolith or module split planning, legacy decomposition, "リファクタリング戦略", "リファクタリング計画", "技術的負債の整理", "段階的移行", "レガシー改善", or similar planning-only refactoring work. Do not use for executing small local refactors.
---

# Refactoring Strategy

Use this skill to design large-scale refactoring: the evidence survey, debt prioritization, target structure, migration pattern, phasing, and safety plan. The output is a strategy document, not code changes.

## Operating Contract

Do not edit product code under this skill. Deliver a strategy the user or another agent can execute. If the user also wants execution, finish the strategy first and get explicit approval on scope, phasing, and the safety plan before any edit.

Treat behavior preservation as the default invariant: the plan must specify how each phase proves behavior did not change. If the goal also requires behavior changes, split them into separate, labeled work items — never fold them into refactoring phases.

Anchor every claim about the codebase in inspected evidence (`path:line`, commands run, measured numbers). Do not prioritize debt from folklore, code style alone, or unverified team lore.

## Goal Framing

Refactoring is a means. Make the payoff explicit before surveying code:

1. State what the refactor should unlock: delivery speed in specific areas, defect reduction, performance headroom, onboarding, a blocked feature, dependency upgrades, scaling, or retirement of risk.
2. Define measurable success criteria (change lead time in the target area, incident rate, build or test time, coverage on hot paths, dependency count) and explicit non-goals.
3. Record hard constraints: release cadence, freeze windows, compatibility promises, team capacity, deadlines, and risk tolerance.
4. If the request is "clean this up" with no outcome attached, derive candidate outcomes from repository evidence and confirm them with one concise question before deep work.

## Evidence Survey

Build the current-state map with measurements, not impressions:

1. Read project instructions (`AGENTS.md`, ADRs, docs) and recent git history.
2. Measure churn and hotspots — refactoring pays where change frequency and complexity intersect:
   - Churn: `git log --since=<window> --pretty=format: --name-only | sort | uniq -c | sort -rn | head -40`
   - Ownership concentration: `git log --format='%an' -- <path> | sort | uniq -c | sort -rn`
   - Size and complexity via available linters, `cloc`, or language tooling.
3. Map dependency structure: import graphs, cyclic dependencies, layering violations, God modules, shared mutable state, and hidden coupling through databases, globals, or events.
4. Assess the safety net: test coverage on the hot paths (not global averages), test runtime and flakiness, type coverage, CI gates, and production observability.
5. Locate public contracts that constrain moves: APIs, schemas, events, file formats, serialized state, and consumer expectations.
6. Distinguish facts, inferences, assumptions, and unknowns.

Delegate broad fan-out (find all callers, catalog duplicated patterns, locate boundary violations) to explorer subagents; read load-bearing files directly. Verify reference counts with language tooling instead of guessing from grep.

## Debt Inventory And Prioritization

1. Catalog debt items concretely: symptom, locations, root cause, blast radius.
2. Score each item by value unlocked × change frequency against effort × migration risk. High-churn hotspots outrank aesthetically offensive but stable code.
3. Explicitly park debt not worth fixing: stable, isolated, low-churn code stays as-is, however ugly. List parked items so the decision is visible.
4. Order by enabling dependency: seams before extraction, characterization tests before moves, boundary hardening before splits.

## Target State And Migration Pattern

1. Describe the target structure only to the depth phasing requires — boundaries, ownership, contracts — not a full redesign.
2. Choose a migration pattern per major move; default to incremental. See [references/migration-patterns.md](references/migration-patterns.md) for the catalog and selection guidance.
3. A big-bang rewrite requires explicit justification against the criteria in the reference and user sign-off.
4. Define coexistence rules while old and new structures live together: which side owns writes, the intended lifespan of the transition, and what prevents drift (lint rules, module-boundary checks, CI rules that block new dependencies on the old structure).

## Safety And Verification Plan

For each phase, state how behavior preservation is proven:

- Characterization or golden-master tests pinned before moving untested code.
- Contract, integration, and regression tests at the affected boundaries.
- Mechanical or tool-assisted transforms preferred over manual editing (IDE renames, codemods, language-server-verified references).
- Runtime verification where tests are weak: shadow traffic, parallel-run diffs, and metrics or alerts to watch after each phase ships.
- A rollback path per phase: revertible commits, flags, and expand–contract ordering so each step is individually reversible.

## Phasing And Checkpoints

1. Slice the migration into phases that are independently shippable and individually revertible; no phase may leave the system unable to release.
2. Make phase 1 a pilot: the smallest slice that exercises the full loop (seam → test → move → verify) to validate cost and risk estimates before committing the whole roadmap.
3. For each phase list scope, affected boundaries, verification gate, rollback trigger, and estimated size.
4. Define stop conditions that pause the roadmap: verification gaps, newly discovered coupling, contract ambiguity, or capacity changes.
5. Mark what must stay sequential (contract decisions, shared seams) and what can proceed in parallel.

## Subagent Metacognition Protocol

Use subagents as metacognitive pressure, not as decision owners. The main agent remains responsible for synthesis and the final roadmap.

Always consult real subagents before finalizing the strategy; scale the number of roles to the task's risk. If subagent tools are unavailable, blocked, or disallowed by the active tool rules, stop and report that the strategy cannot be completed under this skill's required subagent protocol. Do not use local substitutes.

Codex delegates through collab subagents. Use `explorer` agents for the read-only critic roles below — give each a narrow question and an expected output shape. Use a `worker` only when a critique needs a hands-on spike or measurement in a forked workspace. Each subagent starts cold and cannot see this conversation, so put the goal, constraints, and evidence into the prompt text.

Assign narrow roles with distinct lenses:

- Payoff critic: challenge whether the refactor is tied to a real outcome and whether a smaller intervention would deliver it.
- Hotspot verifier: check churn, complexity, and coupling claims against the actual history and code.
- Coupling mapper: hunt for hidden dependencies (database-level, globals, events, reflection, serialization) that would break the proposed boundaries.
- Safety skeptic: find where the verification plan could let a behavior change slip through.
- Sequencing critic: find phases that are not actually shippable or revertible on their own.
- Adversarial reviewer: assume the migration stalls halfway — identify which coexistence state would rot and what limits the damage.

Reconcile every material critique as adopted, rejected with reason, or unresolved with its confidence impact.

## Output Format

1. Goal, success metrics, constraints, and non-goals.
2. Evidence survey: hotspots, coupling map, safety-net assessment, with `path:line` references and measured numbers.
3. Debt inventory with prioritization and explicitly parked items.
4. Target state and chosen migration patterns with rationale.
5. Phased roadmap with verification gates and rollback paths per phase.
6. Coexistence and drift-prevention rules.
7. Subagent critique summary: strongest objections, adopted changes, unresolved risks.
8. Open decisions for the user.

Scale the document to the decision at stake; compress sections that would not change the roadmap.
