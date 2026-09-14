---
name: maximize-research-results
description: Investigate questions requiring reconciliation of competing evidence or hypotheses, broad verification of consequential claims, or explicitly deep research. Exclude focused lookups, routine diagnosis, simple comparisons, implementation, and PR review.
---

# Maximize Research Results

## Operating Contract

Turn the request into a decision-ready investigation. Inspect relevant local and external evidence without mutating the systems under study. Do not implement fixes, publish results externally, or expand scope unless the request authorizes it.

Infer the user's underlying decision and intended depth from context. Ask at most one concise question only when the answer would materially change the evidence path or judgment criteria; otherwise proceed with a visible assumption.

Do not complete an investigation, recommendation, root-cause claim, or no-findings result without at least one usable real subagent result. If subagents are unavailable, prohibited, or fail without usable evidence, report the critique-gate blocker instead of substituting local self-review.

## Define The Investigation

Create a compact brief:

- **Decision:** what the user should understand or do afterward.
- **Primary question:** the claim the investigation must resolve.
- **Scope:** target, time range, version, repository area, stakeholders, and exclusions.
- **Success:** required evidence, confidence, reproduction, citations, or comparison criteria.
- **Subquestions:** the smallest set that removes material uncertainty.
- **Stop condition:** enough evidence to answer responsibly.
- **Failure modes:** stale sources, selection bias, hidden dependencies, confounders, and plausible alternative causes.

Keep the brief internal unless exposing it helps coordinate a large task.

## Gather Evidence

Scan broadly enough to map the problem, then deepen only where evidence can change the answer:

- For code, inspect structure, execution paths, callers, tests, fixtures, docs, logs, and relevant history.
- For technical facts, prefer official documentation, specifications, source code, standards, release notes, and research papers.
- For current, legal, financial, medical, product, pricing, schedule, or policy claims, verify against current authoritative sources.
- Inspect user-provided artifacts directly and normalize comparison criteria before evaluating alternatives.

Record file references, source links, commands, observed outputs, dates, and concrete examples for material claims. Separate facts, inferences, assumptions, and recommendations when confusing them would change the decision.

## Subagent Critique Gate

Launch at least one focused subagent after the first evidence direction is credible and early enough to change the investigation. Use independent, self-contained questions rather than delegating the entire answer. Continue non-overlapping evidence work while agents run.

Give each agent the primary question, scope, evidence already found, one specific role, expected output, and failure modes to check. Require cited facts, inferences, counterevidence, confidence, and recommended next checks. Useful roles are strategy check, independent evidence check, alternative-root-cause review, adversarial critique, and draft-conclusion review.

Use read-only agents for research and critique. Use a write-capable worker only for a bounded reproduction or measurement in an isolated workspace when the request permits it.

Use the bounded role for evidence sweeps, the judgment role for synthesis and critique, and the mechanical role only for extraction or classification. Read [model selection](../../policies/model-selection.md) before choosing a model or reasoning effort.

Treat subagent output as evidence leads, not conclusions. Verify citations, resolve conflicts, and reconcile each material critique as adopted, rejected with reason, or unresolved with confidence impact.

## Iterate To The Answer

After each evidence and critique pass:

1. Identify the largest remaining uncertainty that could change the answer.
2. Run one bounded check to reduce it.
3. Resolve contradictions or expose them explicitly.
4. Stop when another pass is unlikely to change the decision within the task constraints.

Run one critique loop by default for substantial work. Add loops only for new contradictions, missing evidence, or unresolved high-impact uncertainty. Do not treat source count or subagent agreement as proof.

## Report

Lead with the result, then the evidence needed to assess it:

- Findings: impact, evidence, location or source, confidence, and action.
- Root cause: symptom, cause, mechanism, reproduction or verification, alternatives rejected, and fix direction.
- Comparison: normalized criteria, tradeoffs, recommendation, and confidence.
- Summary: what matters, what changed, remaining uncertainty, and next action.

Preserve material facts, decisions, caveats, and next steps. Omit process narration, generic reassurance, and interesting evidence that does not affect the user's decision.
