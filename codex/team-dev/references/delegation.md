# Delegation Playbook

Use this reference when `$team-dev` will spawn subagents, assign reviewers, or create worktrees.

## Capability Gate

Before delegation, check the active tool policy.

- Spawn real subagents only when the user explicitly invoked `$team-dev`, asked for delegation/parallel workers, or otherwise authorized multi-agent work.
- Use `explorer` agents for read-only codebase questions. Give them a narrow question and expected output shape.
- Use `worker` agents for bounded implementation. Assign a disjoint write scope and tell them to edit directly in their forked workspace when the tool supports that.
- If real subagents are unavailable, blocked, or disallowed, use local role simulation and label it as simulation in the final response.
- Do not pretend local simulation was parallel execution.

## Worker Prompt Checklist

Every worker prompt should include:

- Goal and success criteria for that slice.
- Relevant repository guardrails and project instructions.
- Assigned write scope and files or modules the worker must avoid.
- Integration assumptions and contracts with other slices.
- Expected verification command for the slice, if known.
- Instruction not to revert user edits or other workers' edits.
- Instruction to list changed files, verification run, skipped checks, risks, and open questions.

Prefer this shape:

```text
You are one worker in a coordinated team. Other agents may edit other scopes.
Do not revert user changes or edits outside your ownership.

Goal:
...

Write ownership:
...

Do not edit:
...

Guardrails:
...

Expected checks:
...

Final response:
- files changed
- checks run and results
- risks/open questions
```

## Role Mapping

- **Sidecar investigator:** use an `explorer` for a specific read-only question such as hidden call sites, fixture patterns, dependency direction, or CI command discovery.
- **Implementer:** use a `worker` for one clear write scope such as a package, module, screen, migration, fixture set, or docs set.
- **Reviewers:** use read-only prompts unless a fix-up worktree is explicitly assigned. Ask reviewers to separate findings from nice-to-have suggestions and to cite files or commands.
- **Architect reviewer:** run before implementation for public APIs, schema/migration work, dependency changes, cross-package contracts, security boundaries, or broad behavior changes.
- **Adversarial reviewer:** run after a meaningful integrated diff exists.

Use multiple agents in parallel only when their tasks are independent. Do not assign two agents to implement the same behavior.

## Worktree Policy

Use explicit git worktrees when:

- Two or more workers will write concurrently.
- The current checkout is dirty and integration should avoid uncommitted user work.
- A worker needs a disposable branch for experimentation before integration.

Do not require worktrees when:

- The task is planning-only, review-only, or investigation-only.
- The main agent is performing a small single-scope edit.
- Delegation is unavailable and roles are simulated locally.
- A reviewer is read-only.

When worktrees are used:

1. Create or select an integration worktree on a topic branch.
2. Give each write-owning worker an isolated worktree, branch, or forked workspace.
3. Record path, branch, owner, and write scope.
4. Treat each write scope as locked until the worker returns, is redirected, or is closed.
5. Integrate by patch, cherry-pick, merge, or manual application after reviewing the worker diff.
6. Do not delete a worktree that may contain uncommitted work unless its changes were integrated or intentionally discarded.

## Integration And Review

After a worker returns:

1. Read the worker's changed files and diff.
2. Compare the diff to the team contract and repository guardrails.
3. Reject or rewrite changes that violate ownership, architecture, generated-file rules, or user constraints.
4. Run or schedule verification on the integrated tree, not only inside the worker workspace.
5. Feed the integrated diff to reviewers when there is enough concrete change to inspect.

Review disposition must be explicit:

- `fixed`: implemented and verified or ready for verification.
- `not adopted`: rejected with a reason grounded in goal priorities or repository evidence.
- `blocked`: needs user, maintainer, external system, credentials, CI, or design input.

## Publication Guard

Before pushing or opening a PR:

- Confirm publication was requested or is expected for the task.
- Confirm only intended changes are included.
- Respect repository PR templates and branch naming conventions.
- Do not push, force-push, merge, approve, resolve threads, or post with the user's identity unless explicitly asked.
- If publishing is blocked, report the blocker and the exact local state.
