---
name: github-pr-review
description: Review GitHub pull requests in any repository and produce actionable findings. Use when the user asks to review a PR by number, URL, branch, commit, commit range, or diff; asks for a code-review pass; asks to draft or publish PR review comments; or asks to re-review after fixes. Do not use for implementation tasks unless the user asks to fix findings after review.
---

# GitHub PR Review

Review the specified GitHub pull request with a code-review stance: prioritize correctness, regressions, security/privacy, project invariants, missing tests, and CI risk over summaries or style commentary.

## Workflow

1. Identify the repository and PR from the user's PR number, URL, branch, commit SHA, commit range, current checkout, or provided diff. If the PR cannot be identified, ask one concise question for the missing identifier.
2. Read repository instructions that apply to the touched paths, such as `AGENTS.md`, `CLAUDE.md`, `.github/pull_request_template.md`, `CONTRIBUTING.md`, and path-local rules. A more specific project review skill or rule takes precedence over this generic workflow.
3. Determine the review mode:
   - Initial review: inspect the full changed surface and relevant surrounding code.
   - Re-review: inspect prior review comments, unresolved threads, new commits since the prior review, and whether earlier findings were actually resolved.
   - CI-focused review: inspect failing checks and logs first, then connect failures to changed code or call out inconclusive infrastructure/flake evidence.
4. Fetch PR metadata, changed files, diff or per-file patches, existing review comments or unresolved threads, PR body, and CI/check status. Use the GitHub app tools when available; use `gh pr view`, `gh pr diff`, `gh pr checks`, and local git commands as fallback or for richer context.
5. Inspect the surrounding code, tests, fixtures, docs, and public contracts needed to verify the diff. Do not rely only on file names or the PR description.
6. Review for actionable issues: functional correctness, regressions, security/privacy, data/API contract drift, architecture or project-rule violations, missing tests/fixtures, documentation drift, performance or scalability risk, and CI/check gaps.
7. Run local validation only when feasible and proportional to the change. Prefer the repository's own required commands. Report commands that were not run and why.
8. Run the final skeptical pass before answering.
9. Produce findings first. If there are no actionable findings, say that clearly and mention only meaningful residual risks or check gaps.

## CI And Re-Review

Treat CI as evidence to investigate, not as an automatic finding. When checks fail, inspect the failing job, relevant logs, and changed code path before deciding whether the PR introduced the failure. Distinguish deterministic product/test failures from flakes, infrastructure failures, missing secrets, stale base branches, or unrelated failures.

For re-reviews, do not repeat resolved findings. Start from prior comments and unresolved threads, then inspect the incremental diff since the last review when that commit range is available. State which prior findings appear resolved, still unresolved, or replaced by a different issue.

## Publishing

Default to a chat-only review unless the user explicitly asks to post, publish, comment on the PR, request changes, or a project-specific skill/rule says publishing is the default.

When publishing:

- Use the repository's preferred review path when documented. Otherwise use the GitHub app connector or `gh` as appropriate.
- Prefer inline comments only when the issue maps to a specific changed diff line and the fix is local to that line or nearby block.
- Prefer a top-level review comment for cross-file design issues, missing tests, CI failures, rollout risks, or findings that cannot be anchored cleanly to one changed line.
- Avoid scattering duplicate inline comments for the same root cause; write one finding with representative locations instead.
- Do not approve, request changes, merge, close, resolve threads, push commits, or modify files unless the user explicitly asks for that action.
- Do not post with the user's local GitHub identity if the user requested a bot/app identity and the repository lacks that configured path; instead explain the blocker and provide the exact review Markdown.
- Keep paths repository-relative. Do not include local absolute paths, home directories, tokens, or environment details in PR comments.

## Findings

Prefer concrete findings over general suggestions. Each finding should include:

- `Severity`: `Critical`, `High`, `Medium`, or `Low`.
- `Type`: `Potential issue`, `Refactor suggestion`, or `Nitpick`.
- `Category`: `Functional correctness`, `Security / privacy`, `Data integrity / API contract`, `Architecture / invariants`, `Test / fixture coverage`, `Documentation drift`, `Performance / scalability`, `Stability / availability`, or `Maintainability`.
- `Location`: repository-relative file path with line or diff location when available.
- `Problem`, `Impact`, and `Suggested fix`.

Severity guidance:

- `Critical`: likely exploit, data loss, severe privacy breach, production outage, irreversible migration failure, or a merge-blocking correctness issue with high confidence.
- `High`: likely user-visible regression, security/privacy weakness, data corruption, broken public contract, or deterministic CI failure in a common or important path.
- `Medium`: plausible correctness, compatibility, test coverage, performance, scalability, or maintainability issue that can break realistic usage but is bounded in blast radius.
- `Low`: limited edge case, documentation drift, minor maintainability risk, or small test gap with low immediate impact.

Use `Nitpick` only when the user asks for style-level review or the issue blocks documented project standards. Avoid generic praise, release notes, broad refactor ideas, preference-only style comments, speculative future improvements, and findings that cannot be tied to PR behavior or project rules.

Do not file a finding solely because code could be cleaner. File it only when the current diff creates a realistic bug, regression, review blocker, project-rule violation, or material maintenance risk.

## Final Skeptical Pass

Before finalizing:

1. Re-read each finding and try to disprove it from the diff, surrounding code, tests, or CI evidence.
2. Check whether the finding is in scope for this PR and caused or exposed by the change.
3. Verify severity against the rubric; downgrade or remove overstated findings.
4. Re-check the highest-risk changed path for a missed correctness, security, data, or compatibility issue.
5. If there are no findings, confirm that the changed behavior, tests, and CI evidence were sufficient for a no-finding review.

## Review Format

Use this structure for reviews with findings:

```markdown
## Review

### Findings

| # | Severity | Type / category | Location | Finding |
|---|---|---|---|---|
| 1 | Medium | Potential issue / Functional correctness | `src/path/file.rs:123` | Concise issue title |

<details>
<summary><strong>1. Medium:</strong> Concise issue title</summary>

**Location**
`src/path/file.rs:123`

**Classification**
Potential issue / Functional correctness

**Problem**
What is wrong.

**Impact**
What can break or regress.

**Suggested fix**
Minimal correction direction.

</details>

### Checks

Only include when CI is failing, missing, stale, or local/manual validation changes review interpretation.

### Notes

Open questions, assumptions, or residual risks that are not findings.
```

Use this shorter structure when there are no actionable findings:

```markdown
## Review

### Findings

No blocking findings.

### Checks

Only include meaningful CI or validation gaps.
```
