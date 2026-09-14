# Migration Pattern Catalog

Selection guide, then mechanics and risks per pattern. Combine patterns freely: a Strangler Fig program typically uses Parallel Change at each contract, characterization tests before each move, and an Anti-Corruption Layer at the legacy boundary.

## Selection Guide

| Situation | Pattern |
| --- | --- |
| Replace a whole subsystem or service while it keeps serving traffic | Strangler Fig |
| Replace an internal component while trunk stays releasable | Branch by Abstraction |
| Change a contract (API, schema, function signature) with many consumers | Parallel Change (Expand–Migrate–Contract) |
| New code must interact with a legacy model you do not want to inherit | Anti-Corruption Layer |
| Code to move has no meaningful tests | Characterization Testing first |
| Legacy code cannot be tested without large edits | Seams, Sprout, and Wrap |
| Database or persisted-format change under live traffic | Expand–Contract for Data |
| Split a monolith or extract a module | Boundary Hardening, then extraction |
| Team wants to rewrite from scratch | Big-Bang Rewrite criteria (rarely met) |

## Strangler Fig

Replace a system incrementally by routing traffic through a facade that dispatches per-capability to old or new implementation, migrating one capability at a time until the old system is unused, then deleting it.

- Use when: replacing a subsystem, service, or framework that must keep serving users throughout.
- Mechanics: put an interception point in front (router, proxy, facade, adapter); pick one capability; build the new path; shift traffic (flagged or percentage-based); verify; repeat. Deletion of the old path is part of each slice's definition of done.
- Risks: the facade becomes permanent architecture; capabilities with shared state resist per-capability cutover. Mitigate with an explicit deletion schedule and by migrating state ownership per capability, not at the end.

## Branch by Abstraction

Replace an internal component on trunk, without a long-lived branch, by introducing an abstraction both implementations satisfy.

- Use when: swapping a library, engine, or internal layer whose consumers are all in this codebase, and long-lived branches are unacceptable.
- Mechanics: introduce an abstraction over the old implementation; move consumers to the abstraction one by one; build the new implementation behind it; switch (flag or config); delete the old implementation and, if it no longer pays for itself, the abstraction.
- Risks: the abstraction leaks the old implementation's shape, constraining the new one. Mitigate by designing the abstraction from consumer needs, not from the old API.

## Parallel Change (Expand–Migrate–Contract)

Change a contract without a breaking cutover by making the provider accept both forms temporarily.

- Use when: renaming or reshaping an API, event, function signature, or format with consumers you cannot update atomically.
- Mechanics: expand — provider supports old and new forms side by side; migrate — move consumers to the new form, tracking progress mechanically (deprecation warnings, usage metrics, grep-zero); contract — remove the old form.
- Risks: the contract step is skipped and both forms live forever. Mitigate by scheduling the contract step as its own tracked task when the expand step ships.

## Anti-Corruption Layer

Isolate new code from a legacy model with a translation layer, so legacy concepts do not leak into the new design.

- Use when: new modules must call into (or be called by) legacy code whose data model or semantics you are deliberately replacing.
- Mechanics: define the new model on its own terms; write adapters that translate at the boundary in both directions; forbid direct legacy imports in new code with lint or module-boundary rules.
- Risks: the layer grows into a second God module. Keep it thin, per-context, and delete translations as legacy concepts retire.

## Characterization (Golden Master) Testing

Pin current behavior — including behavior that looks wrong — before changing untested code, so the refactor can prove preservation.

- Use when: any move touches code without meaningful tests.
- Mechanics: drive the code with representative and edge-case inputs; record actual outputs as the expected values; commit these tests; refactor against them; afterwards, review pinned oddities separately as candidate bug fixes (behavior changes, done outside the refactor).
- Risks: tests pin incidental details (timestamps, ordering, formatting) and turn brittle. Normalize incidental output before asserting.

## Seams, Sprout, and Wrap

Make untestable legacy code observable and extendable with minimal edits (Feathers' techniques).

- Use when: characterization tests cannot be written because dependencies (network, database, clock, globals) are hard-wired.
- Mechanics: a seam is any point where behavior can be substituted without editing call sites — extract the dependency behind a parameter, interface, or link-time substitute, changing as little as possible. Sprout: put new logic in a new, tested unit called from the legacy code, instead of editing legacy internals. Wrap: rename the legacy function and introduce a wrapper with the old name that adds behavior around it.
- Risks: seam-making edits are themselves untested changes. Keep them mechanical, minimal, and separately reviewed.

## Expand–Contract for Data

Apply Parallel Change to schemas and persisted formats, where "consumers" include stored data itself.

- Use when: renaming or restructuring tables, columns, document shapes, serialized blobs, or event schemas under live traffic.
- Mechanics: expand — add the new shape alongside the old; dual-write; backfill existing data with a resumable, verified job; migrate reads to the new shape; verify (row counts, checksums, shadow reads); contract — stop dual-writing, then drop the old shape after a safety window.
- Risks: backfill and live writes race; old rows are missed. Make the backfill idempotent, verify with counts or checksums, and keep the old shape until verification passes in production.

## Boundary Hardening And Module Extraction

Enforce the future boundary inside the current codebase before physically extracting anything.

- Use when: splitting a monolith, extracting a package or service, or introducing internal module ownership.
- Mechanics: define the intended module seams; make dependencies explicit (no reach-ins, no shared mutable state, no cross-boundary database joins) while everything still lives in one deployable; enforce with import-boundary lint or build rules; only after the boundary holds under enforcement, extract — the extraction itself becomes mechanical.
- Risks: extracting first and discovering hidden coupling in production. The order is the mitigation: harden in place, then move.

## Big-Bang Rewrite

Replacing a system wholesale in one cutover. It loses to incremental migration in almost every case; treat it as justified only when all of these hold:

- The system is small enough that the rewrite fits in a horizon short enough for requirements not to move (weeks, not quarters).
- Its behavior is completely specified by tests or a spec that the new system can be verified against.
- The platform is genuinely dead (unbuildable toolchain, unlicensable runtime) so incremental coexistence is impossible.
- A functionality freeze during the rewrite is acceptable to the business.

If any criterion fails, choose Strangler Fig or Branch by Abstraction instead. If all hold, plan the cutover with a rehearsed rollback and a shadow-run comparison period before the switch.
