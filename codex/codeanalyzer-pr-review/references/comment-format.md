# Comment Format

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
