# Delegation Playbook

Use this reference only when `$team-dev` will spawn subagents, assign real reviewers, or create worktrees.

## Capability And Task Gate

- Spawn subagents only when the user explicitly invoked team mode or requested delegation or parallel workers, and the active policy allows it.
- Delegate a task only when its outcome, ownership, inputs, dependencies, and stop condition can be stated clearly.
- Run independent tasks concurrently. Keep coupled tasks sequential or under one owner.
- Use read-only agents for narrow discovery or review and write-owning agents for bounded implementation.
- Keep semantic decisions, approvals, integration, and final validation with the main agent.
- If delegation is unavailable, use local review lenses and report them as simulation, never as parallel execution.

## Model And Reasoning Selection

Prefer automatic model selection unless quality, latency, or cost requirements justify an override. When the runtime supports per-agent configuration, match the model to the work:

- Use `gpt-5.6` for ambiguous or high-value architecture, cross-boundary implementation, difficult debugging, security work, and final reasoning that needs strong judgment and follow-through.
- Use `gpt-5.6-terra` for everyday implementation, exploration, large-file scans, supporting-document review, and other bounded work that benefits from strong tool use at lower latency and cost.
- Use `gpt-5.6-luna` for clear, repeatable, high-volume tasks with objective acceptance criteria, such as extraction, classification, mechanical transformation, or structured summaries.

Choose the lowest reasoning effort that meets the acceptance criteria:

- Use `low` for straightforward mechanical work and `medium` as the normal default.
- Use `high` for complex logic, edge cases, architect review, adversarial review, or security review.
- Reserve `xhigh` or `max` for the hardest quality-first tasks after a lower setting proves insufficient.
- Use Ultra only at the root when the product supports it and meaningful parallel work justifies the extra agents and tokens; do not assign it reflexively to workers.

Do not pin every role to the most capable model. Keep the main integrator or critical reviewer strong, and use efficient models for well-specified supporting slices. For repeated workflows, compare representative results for correctness, completeness, evidence, latency, and token use before standardizing a model or effort.

For a custom Codex agent, set `model` and `model_reasoning_effort`; omit them to inherit the parent configuration. If the spawn interface cannot select a model, use a configured custom agent or inherit the parent model. Never claim a per-role model was used unless the runtime or agent configuration confirms it. Record only material overrides and their rationale in the team contract.

## Worker Prompt

Make each prompt outcome-focused and self-contained. State each instruction once. Include:

- the slice outcome and acceptance evidence;
- write ownership and files or modules that must not be edited;
- repository guardrails and protected user or worker changes;
- contracts with other slices and known dependencies;
- relevant checks and a clear stop or escalation condition;
- the required return shape: changed files, checks and results, skipped checks, risks, and open questions.

Use this compact shape:

```text
You own one slice of a coordinated change. Other agents may edit other scopes.
Do not revert changes outside your ownership.

Outcome and acceptance evidence:
...

Write ownership / do not edit:
...

Guardrails and integration contracts:
...

Checks and stop conditions:
...

Return: changed files; checks and results; skipped checks; risks; open questions.
```

Do not prescribe every implementation step when the outcome and hard constraints are sufficient. Add procedural detail only for fragile operations or a known failure mode.

## Role Selection

- **Sidecar investigator:** answer one read-only question about call sites, dependencies, fixtures, conventions, or CI.
- **Implementer:** own one package, module, screen, migration, command, or other disjoint write scope.
- **Test/fixture/docs worker:** own supporting evidence after expected behavior is fixed.
- **Architect reviewer:** evaluate public contracts, migrations, dependencies, cross-package boundaries, security boundaries, or broad behavior before implementation.
- **Regular reviewer:** inspect the integrated diff for correctness, regressions, coverage, diagnostics, accessibility, and security.
- **Adversarial reviewer:** challenge assumptions, degraded cases, false-green validation, accidental API changes, scope creep, and unnecessary abstraction.

Ask reviewers for prioritized findings with file or command evidence. Separate actionable defects from optional suggestions.

## Worktree Policy

Use isolated worktrees, branches, or forked workspaces when two or more agents write concurrently, when a dirty checkout needs protection, or when an experiment should be disposable. Record each path, branch, owner, and write scope.

Do not require isolation for read-only agents, local role simulation, or a single small write scope. Never discard a worktree with unintegrated changes unless the user explicitly authorizes that loss.

## Integration And Review

For every returned slice:

1. Inspect its changed files, diff, checks, and risks.
2. Compare it with the team contract, ownership, integration contracts, and repository guardrails.
3. Reject or rewrite violations instead of silently broadening scope.
4. Integrate by the repository-appropriate mechanism.
5. Run affected checks on the integrated tree.

Review only a concrete, sufficiently integrated diff. Record each actionable finding as `fixed`, `not adopted` with a reason, or `blocked` by user input or external state.

## Publication Guard

Treat commits as persistent repository mutations and pushes, PR actions, review comments, approvals, thread resolution, force-pushes, and merges as external writes. Perform only the actions the user authorized. Before publication, confirm that the diff contains only intended changes and follows repository templates and branch conventions. If blocked, report the exact local state and required next action.
