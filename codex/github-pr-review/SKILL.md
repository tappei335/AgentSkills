---
name: github-pr-review
description: Review GitHub pull requests or explicit diffs and produce actionable, evidence-backed findings. Use when the user asks to review a PR by number, URL, branch, commit, commit range, or diff; requests a code-review pass; asks to draft or publish review comments; or requests re-review after fixes. Do not use for implementation unless the user also asks to fix findings.
---

# GitHub PR Review

## Operating Contract

Review with a defect-finding stance. Prioritize correctness, regressions, security and privacy, data and API integrity, project invariants, missing behavior coverage, and CI risk over summary or style commentary.

No evidence, no finding. Anchor each finding to the changed behavior and include a repository-relative location, severity, classification, problem, impact, and minimal fix direction. Remove concerns that are speculative, pre-existing without being exposed by the change, preference-only, or unsupported by the diff and surrounding evidence.

Default to chat-only. Publish, approve, request changes, merge, close, resolve threads, push commits, or modify files only when explicitly authorized or when an applicable repository rule clearly makes that action the default.

## Resolve The Review Target

Identify the repository and the exact review surface from the PR number, URL, branch, commit, range, current checkout, or user-provided diff. For a GitHub PR, record the number, head and base SHAs, changed files, PR body, and current check status. Ask one concise question only when the target cannot be resolved safely.

Read repository and path-local instructions before judging the change. A more specific project review skill takes precedence.

Choose the mode:

- **Initial:** inspect the full changed surface and relevant surrounding contracts.
- **Re-review:** inspect prior findings and unresolved threads, then the incremental changes since the reviewed commit.
- **CI-focused:** inspect failing checks and logs first, then connect them to the changed path or classify them as inconclusive.

Use GitHub tools when available and `gh pr view`, `gh pr diff`, `gh pr checks`, or local git for additional context. Do not rely only on the PR description or filenames.

## Review The Change

Inspect the diff, surrounding implementation, callers, tests, fixtures, docs, schemas, and public contracts needed to verify realistic behavior. Focus on:

- functional and degraded-path correctness;
- security, privacy, authorization, and data integrity;
- API, schema, serialization, and compatibility drift;
- architecture, dependency direction, and repository-rule violations;
- missing tests or fixtures for changed behavior;
- material performance, scalability, stability, or observability risks;
- documentation that becomes false because of the change.

Run repository-native validation when feasible and proportional. Treat CI as evidence to investigate, not an automatic finding. Distinguish deterministic failures from flakes, infrastructure, missing secrets, stale bases, and unrelated jobs.

For a re-review, do not repeat resolved findings. State which prior items are resolved, remain, or are replaced by a different issue.

## Scale Review Effort

For large PRs with independent areas, use read-only subagents only when the user or applicable project instructions permit delegation and separate lenses materially improve confidence. Assign disjoint files, behaviors, or risks; require evidence-backed findings and let the main agent verify and deduplicate them.

Prefer automatic model selection. When explicit per-agent selection is supported, use `gpt-5.6-terra` with medium effort for bounded diff, CI, or test sweeps and `gpt-5.6` with high effort for cross-file correctness, security, migration, or adversarial review. Use `gpt-5.6-luna` only for mechanical inventories. If the runtime cannot select a model, inherit the parent configuration and do not claim an override.

## Classify Findings

Use these severities:

- **Critical:** likely exploit, data loss, severe privacy breach, outage, irreversible migration failure, or high-confidence merge blocker.
- **High:** likely user-visible regression, security weakness, corruption, broken public contract, or deterministic failure on an important path.
- **Medium:** realistic bounded correctness, compatibility, coverage, performance, stability, or maintenance failure.
- **Low:** limited edge case, documentation drift, or small but concrete maintenance or test risk.

Use `Potential issue` for bugs, regressions, and invariant violations; `Refactor suggestion` only for material maintenance risk introduced by the change; `Nitpick` only when requested or required by project standards. Classify by functional correctness, security/privacy, data/API contract, architecture/invariants, test/fixture coverage, documentation drift, performance/scalability, stability/availability, or maintainability.

## Skeptical Pass

Before finalizing, try to disprove every finding from the diff, surrounding code, tests, CI, or repository rules. Confirm it is caused or exposed by the change, calibrate severity, and re-check the highest-risk path for a missed issue. If no findings remain, verify that changed behavior and meaningful check gaps were actually inspected.

## Publish When Authorized

Use the repository's documented review path, otherwise the GitHub connector or `gh`. Use inline comments for specific changed lines and a top-level review for cross-file causes, coverage gaps, CI failures, or rollout risks. Consolidate duplicate symptoms under one root cause.

Keep published paths repository-relative and exclude local paths, tokens, or environment details. If the requested bot or app identity is unavailable, report the blocker and provide the exact Markdown instead of posting as the user's local identity.

## Output

Lead with findings ordered by severity. For each include title, severity, type/category, location, problem, impact, evidence, and suggested fix. Include checks only when failing, missing, stale, skipped, or different from local evidence. Put assumptions and residual risks in notes. When no actionable findings exist, say so directly and mention only material validation gaps.
