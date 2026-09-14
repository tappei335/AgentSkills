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

Use the judgment role for architecture, difficult debugging, security, and critical review; the bounded role for implementation and exploration with clear scope; and the mechanical role only for objectively checkable extraction or transformation. Read [model selection](../../../policies/model-selection.md) before choosing a model or reasoning effort. Record material overrides and their rationale in the team contract.

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
