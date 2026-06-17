---
name: feature-implementation-strategy
description: Plan feature implementation before code changes, using evidence, candidate strategies, and optional subagent consultation to improve accuracy through advisor input, sparring, and adversarial review while maximizing delivery speed, runtime performance, memory use, correctness, maintainability, and verification confidence. Use when the user asks for implementation strategy, design approach, roadmap, task breakdown, tradeoff analysis, performance or memory planning, risk review, "機能実装に向けた戦略検討", "実装方針", "設計方針", or similar planning before implementation.
---

# Feature Implementation Strategy

## Operating Contract

Produce an implementation strategy before editing product code. Optimize the plan for the requested outcome, delivery speed, runtime speed, memory use, correctness, maintainability, and verification confidence.

If the user only asks for strategy, do not implement. If the user asks for both strategy and implementation, complete the strategy first, then proceed only when no unresolved product, architecture, public API, dependency, data migration, or rollout decision remains.

Ask before accepting a strategy that changes agreed architecture, public API, dependency choices, data contracts, security posture, or user-visible product behavior.

## Startup

1. Read project instructions and relevant docs before forming the plan.
2. Inspect the current repository state and treat pre-existing changes as user work.
3. Inspect the relevant code, tests, fixtures, configuration, schemas, docs, and existing patterns. Do not rely on memory or agent self-reports.
4. Restate the feature goal, success criteria, non-goals, constraints, and assumptions.
5. Identify the affected ownership boundary: UI, API, domain logic, persistence, background jobs, integrations, analysis pipeline, CLI, infrastructure, docs, or tests.

If required information is missing, make conservative assumptions when reversible. Ask one concise question when proceeding would create meaningful product, architecture, data, security, or operational risk.

## Subagent Consultation

For non-trivial, ambiguous, high-risk, performance-sensitive, security-sensitive, cross-boundary, or high-impact work, consult subagents as planning advisors when subagent use is available and authorized by the user's request or active tool rules.

Use distinct roles:

- Advisor: propose a practical implementation path, hidden constraints, likely sequencing, and useful simplifications.
- Sparring partner: challenge the preferred approach, goal framing, and tradeoffs; suggest simpler or more robust alternatives.
- Adversarial reviewer: look for correctness, performance, memory, security, migration, rollout, observability, and verification failures.

Delegate narrow questions, not ownership of the strategy. Give each subagent the feature goal, constraints, relevant evidence, candidate approaches, and the specific decision or risk to evaluate. Ask for concise recommendations, risks, and tests rather than full implementation.

Avoid duplicate work by assigning distinct lenses such as API compatibility, performance and memory, test strategy, migration risk, operational safety, or invariant pressure. Prefer one consultation pass and one adversarial review pass unless the feature's risk clearly justifies more.

Skip subagent consultation for small, reversible, low-risk changes where direct evidence is sufficient. If subagents are unavailable or not authorized, simulate the advisor, sparring partner, and adversarial reviewer roles locally.

Do not outsource the decision. Treat subagent output as evidence to evaluate, not authority to defer to. Reconcile it against repository evidence, project instructions, existing architecture, and user constraints; discard unsupported claims.

Do not let subagent disagreement block progress unless it exposes a concrete product, architecture, public API, dependency, data, security, or rollout decision that needs user input.

## Strategy Workflow

1. Map the requested feature to existing architecture, module ownership, extension points, and user or system workflows.
2. Gather evidence from current code, tests, docs, runtime behavior, logs, schemas, and recent patterns. Cite the important files, symbols, or interfaces in the final strategy.
3. Define at least two candidate approaches for non-trivial work. Include a minimal viable path and a more robust or scalable path when they differ.
4. Score each candidate across:
   - Delivery speed: diff size, complexity, reviewability, migration cost, dependency churn, and coordination cost.
   - Runtime speed: algorithmic complexity, hot-path impact, traversal count, I/O, network calls, batching, caching, concurrency, and incremental reuse.
   - Memory use: peak memory, retained state, cloning or copying, object lifetimes, data structure choice, streaming, pagination, and cache size.
   - Quality: correctness, maintainability, testability, observability, failure modes, accessibility or usability where relevant, docs, and compatibility.
   - Risk: rollback path, data integrity, security, privacy, operational safety, degraded cases, public API exposure, and invariant pressure.
   - Review confidence: agreement or disagreement across advisors and reviewers, strength of evidence behind objections, unresolved risks, and changes made after critique.
5. For non-trivial work, gather independent critiques of the candidate approaches through subagents or local role simulation. Record meaningful disagreements, missed risks, and alternative slices before choosing a strategy.
6. Choose one strategy. Explain why it maximizes the requested objective instead of merely being easy to implement.
7. Break the chosen strategy into implementation slices. For each slice, state likely files or components, expected behavior, tests or fixtures, and acceptance checks.
8. Identify work that can run in parallel and work that must stay sequential because it decides architecture, API shape, data shape, rollout behavior, or shared contracts.
9. Define verification before coding starts. Include focused unit tests, integration or end-to-end tests, static checks, formatting/linting, manual checks, performance measurement, memory checks, and rollback validation as appropriate for the codebase.

## Performance And Memory Lens

Prefer simple, measurable performance decisions over speculative optimization.

- Start from expected input scale, traffic shape, latency targets, memory limits, and hot paths.
- Avoid repeated full-data scans when a local pass, index, cache, stream, incremental update, or existing query can serve the same need.
- Avoid unnecessary deep clones, large temporary collections, eager materialization, duplicate serialization, and unbounded caches.
- Prefer streaming, pagination, batching, pooling, stable identifiers, compact summaries, and backpressure when they match existing local patterns.
- Treat graceful degradation as an explicit design point when exact behavior would be expensive, unreliable, or outside the current scope.
- Add benchmarks or profiling only when the feature is performance-sensitive or when the strategy depends on an unproven performance claim.

## Output Format

Use this structure unless the user requested a different format:

1. Goal and constraints.
2. Current-system evidence.
3. Candidate strategies with a compact tradeoff table.
4. Recommended strategy and rationale.
5. Implementation sequence.
6. Verification plan.
7. Subagent input summary: consulted or simulated roles, strongest objections, adopted changes, and rejected recommendations with reasons.
8. Open decisions, risks, or assumptions.

Keep the recommendation concrete enough that another agent can implement it without redesigning the feature.
