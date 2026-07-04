---
name: codeanalyzer-pr-review
description: Review CodeAnalyzer GitHub pull requests and publish the review through the CodeAnalyzer Review Bot workflow. Use when explicitly invoked for a CodeAnalyzer PR by PR number, PR URL, branch, commit, or range, especially when review comments should be posted back to GitHub instead of returned only in chat. Do not use for implementation tasks unless the user asks to fix findings after review.
argument-hint: "[PR number | PR URL | branch | commit | range]"
disable-model-invocation: true
---

# CodeAnalyzer PR Review

Invoke this skill explicitly as `/codeanalyzer-pr-review $ARGUMENTS` when GitHub review publication is intended.

Review the specified CodeAnalyzer PR and publish the result to GitHub by default.

Hard rules, in priority order:

1. Review the GitHub PR, never a local substitute. If no PR resolves, stop and ask for the identifier.
2. Publish through the CodeAnalyzer Review Bot workflow by default. Chat-only requires an explicit opt-out: `dry-run`, `chat only`, `do not comment`, `コメントしないで`, or equivalent.
3. No evidence, no finding: every finding carries location, severity, type/category, evidence, impact, and a minimal fix direction.
4. Run the Final Skeptical Pass before publishing. Cut any finding you cannot defend from the diff, surrounding code, tests, CI, or CodeAnalyzer docs.
5. Never approve, request changes, merge, resolve threads, push commits, or post with the user's GitHub identity unless explicitly asked.

## Inputs

Accept a PR number, PR URL, branch name, commit SHA, or commit range only as a way to identify a GitHub PR. If the PR cannot be identified and fetched from GitHub, stop and ask one concise question for the missing PR identifier. Do not review the local branch, local diff, or commit range as a substitute for a GitHub PR.

Honor explicit scope requests such as "focus on TypeScript", "architecture only", "no tests", or "comment only on blockers".

## Workflow

1. Identify the repository and PR.
2. Pass the PR Resolution Gate before reading or reviewing local code.
3. Read repository instructions that apply to the touched paths, such as `CLAUDE.md`, `AGENTS.md`, `.github/pull_request_template.md`, `CONTRIBUTING.md`, path-local rules, and relevant CodeAnalyzer design or roadmap docs.
4. Determine the review mode:
   - Initial review: inspect the full changed surface and relevant surrounding code.
   - Re-review: inspect prior review comments, unresolved threads, new commits since the prior review, and whether earlier findings were actually resolved.
   - CI-focused review: inspect failing checks and logs first, then connect failures to changed code or call out inconclusive infrastructure/flake evidence.
5. Fetch PR metadata, changed files, diff or patches, existing comments, review threads, and CI/check status.
6. Review for correctness, regressions, architecture invariant violations, missing tests or fixtures, documentation drift, and CI/check risk.
7. Classify every concern as either PR-scoped, out-of-scope issue material, or not worth mentioning. Do not leave vague "follow-up later" items in the review.
8. Prefer concrete findings over general suggestions. Each finding must include the file path, line or diff location when available, severity, type, category, evidence, impact, and the minimal fix direction.
9. Run the final skeptical pass before publishing.
10. Publish the review through the `CodeAnalyzer Review Bot` GitHub Actions workflow unless the user explicitly requested no posting.
11. Report in chat what was posted and any CI/check gaps that matter.

Use GitHub connector tools, `gh pr view`, `gh pr diff`, and `gh pr checks` for PR inspection. Local git commands may inspect surrounding code only after the PR has been resolved and fetched from GitHub. Do not publish reviews with the user's GitHub identity unless the user explicitly asks for direct local posting.

Use repository-relative paths and portable command names in PR comments and summaries. Do not include local absolute paths such as a user's home directory.

## PR Resolution Gate

Before reviewing anything, establish a concrete GitHub PR identity:

- Repository full name.
- PR number.
- PR head SHA and base SHA.
- Changed files or PR diff from GitHub.
- PR head branch and base branch, when available.

If the user provides a branch, commit, or range, use it only to search for the corresponding PR. If multiple PRs match, ask which PR to review. If no PR matches, stop and report that no GitHub PR was identified.

Hard rules:

- Do not review the current checkout, local branch, local `git diff`, or local commit range as a fallback.
- Do not publish or draft a review when the PR number is unknown.
- Do not infer that the current branch is the PR unless GitHub confirms it.
- Do not proceed if the fetched PR head SHA differs from the checked-out code being inspected, unless the review relies only on the GitHub diff and surrounding code is version-compatible.
- `dry-run`, `chat only`, and `do not comment` disable publishing only; they do not allow replacing PR review with local branch review.

If PR resolution fails, return the exact blocker and the identifier needed next, such as `owner/repo#123` or a PR URL.

## CI And Re-Review

Treat CI as evidence to investigate, not as an automatic finding. When checks fail, inspect the failing job, relevant logs, and changed CodeAnalyzer path before deciding whether the PR introduced the failure. Distinguish deterministic product/test failures from flakes, infrastructure failures, missing secrets, stale base branches, or unrelated failures.

For re-reviews, do not repeat resolved findings. Start from prior comments and unresolved threads, then inspect the incremental diff since the last review when that commit range is available. State which prior findings appear resolved, still unresolved, or replaced by a different issue.

When re-reviewing through the bot workflow, prefer updating or superseding the existing CodeAnalyzer bot review if the workflow supports it. If the workflow creates a new comment, make the new review clear about the head commit and prior result so readers are not left comparing stale bot comments.

## CodeAnalyzer Review Checks

Check the repository-specific invariants before posting:

- No common AST or lowest-common-denominator shared syntax type.
- Sharing stops below IR: CFG, dataflow, and diagnostics can be shared; parser, AST, HIR, and type resolution stay per-language.
- Dependencies flow common to language. Reverse dependencies and cross-language dependencies are forbidden.
- AST, HIR, MIR and their checker tiers remain distinct.
- Decision-record docs are not edited without explicit agreement.
- Generated agent docs and rule mirrors are not edited directly; change `ai/fragments/` or `ai/rules/` and run `make agent-docs`.
- Behavior changes include focused tests or fixture updates.
- External crate dependency additions were discussed first.

Treat `cargo build --workspace` as the source-of-truth validation signal when local validation is feasible. Do not rely on `cargo check` or `cargo test` alone as proof the workspace builds.

## Review Content Model

Use a CodeRabbit-inspired content split:

- `Summary`: a compact table with the review outcome, reviewed scope, and main
  risk area. Use short cells, not long prose.
- `Findings`: actionable issues only, classified by severity, type, and category.
- `Checks`: optional. Include only when CI is failing, missing, stale, or when
  local/manual checks differ from CI.
- `Notes`: assumptions, open questions, or residual risks that are not findings
  or check gaps.
- `Issue candidates`: optional. Include only for actionable work that is outside
  the PR scope and should become a separate GitHub issue.

Finding types:

- `Potential issue`: likely bug, regression, invariant violation, dataflow mismatch, or behavior drift.
- `Refactor suggestion`: maintainability or simplification concern with clear review value.
- `Nitpick`: minor style or wording issue. Use only when explicitly requested or when it blocks docs/rule consistency.

Finding categories:

- `Functional correctness`
- `Architecture / invariants`
- `Test / fixture coverage`
- `Documentation drift`
- `Security / privacy`
- `Data integrity / API contract`
- `Performance / scalability`
- `Stability / availability`
- `Maintainability`

Severity guidance:

- `Critical`: likely exploit, data loss, severe privacy breach, production outage, irreversible migration failure, or a merge-blocking correctness issue with high confidence.
- `High`: likely user-visible regression, CodeAnalyzer invariant violation with broad blast radius, data corruption, broken public contract, or deterministic CI failure in a common or important path.
- `Medium`: plausible correctness, compatibility, fixture coverage, documentation drift, performance, scalability, or maintainability issue that can break realistic usage but is bounded in blast radius.
- `Low`: limited edge case, localized documentation drift, minor maintainability risk, or small test gap with low immediate impact.

For CodeAnalyzer roadmap slices, prefer `Potential issue` findings in
`Functional correctness`, `Architecture / invariants`, `Test / fixture
coverage`, or `Documentation drift`. Avoid generic praise, release notes, and
style-only comments unless the user requested them.

Do not file a finding solely because code could be cleaner. File it only when the current diff creates a realistic bug, regression, review blocker, CodeAnalyzer guardrail violation, project-rule violation, or material maintenance risk.

## Follow-up Handling

Do not use "non-blocking follow-up" as a vague middle ground. Classify each item
before posting:

- `PR-scoped`: Caused by the PR, required to keep the changed behavior coherent,
  needed for the PR's documented scope, or small enough to resolve in the same
  diff without changing the agreed design. Post it as a finding and recommend
  resolving it in the PR before merge, even if the severity is `Low`.
- `Issue candidate`: Pre-existing work, broader cleanup, future roadmap scope,
  design work needing discussion, or a change that would make the PR materially
  larger without being required for correctness. Do not present it as a finding.
  Mention it only if it is concrete enough to file as an issue.
- `Omit`: Interesting but speculative ideas, taste-based improvements, or work
  without a clear owner, impact, and acceptance criteria.

For issue candidates, prefer either creating a GitHub issue when the user
explicitly asked for issue creation, or including an issue-ready entry in the
review. Issue-ready entries should have a short title, problem, rationale, and
acceptance criteria. Avoid asking PR authors to "follow up" unless the next step
is clear enough to become an issue.

## Roadmap Slice Checks

For PRs that touch `docs/phase*-impl/`, language MIR lowerers, canary fixtures, or roadmap slice plans, also check:

- The implementation matches the authoritative plan's accepted and degraded scope. Treat undocumented scope widening as a finding.
- PR body, slice plan, boundary review, canary status, and fixture/test matrix agree after all fixups. Treat stale fixture counts, checklist items, "still deferred" entries, and contradictory implementation notes as documentation-drift findings.
- Every newly accepted language shape has positive coverage and every newly rejected or deliberately deferred boundary has negative coverage, preferably through both real-frontend fixtures and focused hand-built HIR tests when the PR uses both styles.
- New language-owned intrinsics stay in the language crate, are documented in the boundary review, and are not name-matched by common crates or checkers.
- Caller-callee and method receiver degrade boundaries remain intact when new expression forms can appear inside calls, receivers, multi-return destructuring, or comma-ok statement shapes.

## Final Skeptical Pass

Before publishing:

1. Re-read each finding and try to disprove it from the diff, surrounding code, tests, CI evidence, or CodeAnalyzer docs.
2. Check whether the finding is in scope for this PR and caused or exposed by the change.
3. Verify severity against the rubric; downgrade or remove overstated findings.
4. Re-check the highest-risk changed path for a missed correctness, architecture-invariant, fixture, documentation, or CI issue.
5. If there are no findings, confirm that the changed behavior, tests or fixtures, and CI evidence are sufficient for a no-blocking-findings bot review.

## Publishing Rules

Publish through `.github/workflows/codeanalyzer-review-bot.yml` by default so comments are attributed to the CodeAnalyzer GitHub App bot:

1. Write the final review Markdown to a temporary file.
2. Dispatch the workflow:

   ```bash
   gh workflow run codeanalyzer-review-bot.yml \
     -f pr_number=<PR_NUMBER> \
     -F review_body=@<REVIEW_FILE> \
     -f fallback_to_comment=true
   ```

3. Watch or inspect the run:

   ```bash
   gh run list --workflow codeanalyzer-review-bot.yml --limit 1
   gh run watch <RUN_ID>
   ```

The workflow reads these repository settings:

- Variable: `CODEANALYZER_REVIEW_APP_CLIENT_ID`
- Secret: `CODEANALYZER_REVIEW_APP_PRIVATE_KEY`

If the workflow cannot run because the variable, secret, GitHub App installation, or App permissions are missing, explain the failure and include the exact Markdown body that would have been posted.

Do not approve, merge, request changes, resolve threads, push commits, or modify files unless the user explicitly asks for that action.

If there are findings, put findings first, ordered by severity. If there are no findings, post a concise no-blocking-findings comment and mention only meaningful CI/check gaps.

Only use direct PR review/comment APIs from the local session when the user explicitly requests posting as the authenticated user instead of the bot.

## Comment Format

Use a CodeRabbit-inspired layout: a short visible summary first, compact tables
for scanning, and collapsible details for long rationale. Do not squeeze a full
finding into one list item; GitHub renders that as a dense paragraph block.

Formatting rules:

- Start with `## Review`.
- Put a compact `Summary` table before details. State whether blocking findings
  were found, what was reviewed, and the main risk or resolution status.
- Keep summary table cells short. Move long reasoning to findings, notes, or
  collapsible details.
- Put findings in a compact table first: number, severity, type/category,
  location, and concise title.
- Order findings by severity. Use consistent severity labels: `Critical`,
  `High`, `Medium`, `Low`.
- Follow the table with one `<details>` block per finding. The `<summary>` must
  be short and scannable, e.g. `<strong>1. Medium:</strong> concise issue
  title`.
- Inside each details block, use stable labels: `Classification`, `Location`,
  `Problem`, `Impact`, and `Suggested fix`.
- Keep each labeled explanation as plain prose, not as an indented continuation
  of a bullet.
- Use inline code for paths, commands, symbols, and literal snippets.
- Do not include a `Verification` section by default. Routine build, test, fmt,
  and clippy status belongs to CI and is already visible on the PR.
- Include `### Checks` only when it changes review interpretation: CI is
  failing, missing, stale relative to head, or local/manual checks found a result
  CI will not show.
- Include `### Issue Candidates` only for out-of-PR-scope work that is concrete
  enough to file. Put it after findings and checks, before notes. Do not mix
  issue candidates into `Notes`.
- For each issue candidate, provide `Title`, `Problem`, `Why outside this PR`,
  and `Acceptance criteria`. Keep it short enough to paste into a GitHub issue.
- Use `Notes` only for open questions, assumptions, or residual risk that do not
  belong in a finding, check gap, or issue candidate.
- Omit empty sections when they add no value.

Use this structure for reviews with findings:

```markdown
## Review

### Summary

| Area | Result |
|---|---|
| Outcome | 1 Medium finding |
| Reviewed scope | Go MIR defer lowering |
| Main risk | Accepted-scope drift in the MIR lowering path |

### Findings

| # | Severity | Type / category | Location | Finding |
|---|---|---|---|---|
| 1 | Medium | Potential issue / Functional correctness | `crates/path/to/file.rs:123` | Concise issue title |

<details>
<summary><strong>1. Medium:</strong> Concise issue title</summary>

**Location**
`crates/path/to/file.rs:123`

**Classification**
Potential issue / Functional correctness

**Problem**
What is wrong.

**Impact**
What can break or regress.

**Suggested fix**
Minimal correction direction.

</details>

### Issue Candidates

Only include out-of-scope work that should become a separate GitHub issue.

#### Title

**Problem**
Concrete problem statement.

**Why outside this PR**
Why it is not required for this PR's acceptance.

**Acceptance criteria**
What would make the issue complete.

### Notes

Open questions, assumptions, or residual risk.
```

Use this shorter structure when there are no findings. For re-reviews, state
what changed since the prior review and why the earlier finding is now resolved:

```markdown
## Review

### Summary

| Area | Result |
|---|---|
| Outcome | No blocking findings |
| Prior finding | Direct-local defer fallback accepted non-callable locals |
| Resolution | Direct-local defer now degrades instead of lowering as accepted MIR |
| Coverage | Hand-built HIR and real-frontend `defer x()` degradation tests |

### Findings

No blocking findings.
```

For short reviews with exactly one finding and no long rationale, a non-collapsed
variant is acceptable:

```markdown
## Review

### Summary

| Area | Result |
|---|---|
| Outcome | 1 Medium finding |
| Reviewed scope | Focused diff review |

### Findings

#### 1. Medium: Concise issue title

**Location**
`crates/path/to/file.rs:123`

**Classification**
Potential issue / Functional correctness

**Problem**
What is wrong.

**Impact**
What can break or regress.

**Suggested fix**
Minimal correction direction.

```
