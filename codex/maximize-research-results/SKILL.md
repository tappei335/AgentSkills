---
name: maximize-research-results
description: Improve investigation and research tasks by inferring the user's real intent, decision context, success criteria, constraints, and expected deliverable, then iterating with evidence gathering, mandatory subagent consultation when available and permitted, critique, and synthesis. Use when the user asks Codex to investigate, research, look into, analyze, audit, compare, diagnose, find root cause, summarize findings, or "調査して", especially when the request is broad, ambiguous, high-impact, or would benefit from structured inquiry before answering.
---

# Maximize Research Results

## Overview

Turn a research request into a precise investigation brief, then iterate until the answer is useful, well-supported, and hard to improve within the task constraints. Treat investigations as iterative: gather initial evidence, consult focused subagents whenever they are available and permitted, reconcile critique, then finalize. If subagents cannot be used, run equivalent skeptical review locally and disclose that fallback. Prefer moving forward with explicit assumptions over blocking on clarification unless a missing answer would materially change the investigation path.

## Workflow

### 1. Infer the Real Task

Start by identifying:

- The decision, action, or understanding the user needs after the investigation.
- The target object: code path, PR, issue, product, incident, paper, market, person, policy, or concept.
- The scope boundary: time range, repository area, geography, version, stakeholder, or comparison set.
- The deliverable: concise answer, findings list, root-cause analysis, options, recommendation, implementation plan, or source-backed memo.
- The quality bar: completeness, speed, citations, reproduction, tests, confidence level, or risk focus.

Ask at most one concise clarification question only when the missing information would substantially change what to inspect or how to judge success. Otherwise, state the assumption and proceed.

### 2. Create an Investigation Brief

Before deep work, form a short internal brief:

- Primary question: the one question that must be answered.
- Subquestions: the 2-5 supporting questions that reduce uncertainty.
- Evidence plan: local files, tests, logs, git history, official docs, primary sources, web search, or domain references.
- Consultation plan: which required subagent role or roles to use, what each should independently check, and what disagreement would change the answer.
- Stop condition: what evidence is enough to answer responsibly.
- Failure modes: likely ways the investigation could be misleading, stale, incomplete, or overfit to one source.

Do not expose this brief unless it helps the user understand the plan or the task is large enough to benefit from a visible plan.

### 3. Use Subagents for Iteration

Subagent consultation is required for every invocation of this skill when subagent tools are available and user/tool policy allows delegation. Use at least one focused subagent before finalizing. Do not skip subagents merely because the task is narrow, low-risk, or the direct evidence seems sufficient; for small requests, assign a compact adversarial review or final-answer review.

Use one skeptical subagent by default for broad, high-impact, ambiguous, or uncertain investigations. Add specialized subagents only when they reduce distinct uncertainty. Do not finalize until the required subagent result has been considered, unless the subagent is unavailable, blocked, or stale enough that waiting would no longer be useful; in that case, state the reason and run the equivalent role locally.

Prefer these consultation roles:

- Strategy check: ask whether the investigation brief targets the user's real decision and whether the evidence plan is sufficient.
- Independent evidence check: assign a bounded subquestion, source family, code path, or comparison criterion.
- Adversarial review: ask for counterexamples, missing assumptions, alternative root causes, and weak claims.
- Final answer review: ask whether the draft conclusion is supported, actionable, and missing anything material.

Every subagent prompt must include the primary question, scope boundary, evidence already found, the subagent's specific role, expected output format, and failure modes to check. Ask subagents to separate facts, inferences, and recommendations, and to cite files, commands, sources, or concrete observations for material claims.

Delegate only concrete, self-contained tasks with a requested output shape. Avoid asking multiple subagents the same vague question unless independent consensus is the goal. Continue local work while subagents run. Treat subagent results as leads and critique inputs, not conclusions.

The main agent remains responsible for synthesis, verification, and final judgment. Verify cited evidence, resolve conflicts, reject unsupported claims, and update the investigation path when new evidence changes the answer.

If subagents are unavailable or delegation is prohibited by active policy, run the same loop as a self-review: strategy check, evidence gap check, adversarial critique, then final answer review. State this limitation in the final answer when the investigation was nontrivial or when subagent use would normally have been visible.

### 4. Gather Evidence Broad-to-Deep

Use a broad scan first, then deepen selectively:

- For codebase investigations, inspect repository structure, relevant symbols, call sites, tests, fixtures, documentation, and recent changes before concluding.
- For technical facts, prefer primary sources: official docs, specifications, source code, release notes, standards, or research papers.
- For current, legal, financial, medical, product, pricing, schedule, or policy information, verify with up-to-date sources before answering.
- For user-provided artifacts, inspect the artifact directly instead of relying on memory or summaries.
- For comparisons, normalize criteria before comparing options.

Record enough evidence to support the final answer with file references, source links, commands, observed outputs, or concrete examples.

### 5. Iterate Until the Marginal Value Drops

After the first evidence pass, compare findings against the brief and any subagent critique:

- If a material subquestion remains unanswered, run another targeted evidence pass.
- If evidence conflicts, resolve the conflict or clearly explain why it remains unresolved.
- If a subagent identifies a plausible gap, investigate it before finalizing unless it is outside scope.
- Reconcile each substantive critique as adopted, rejected with reason, or unresolved with confidence impact.
- If additional work is unlikely to change the answer, stop and state the remaining uncertainty.

Run one critique loop by default for substantial investigations. Run additional loops only when new contradictions, missing evidence, or unresolved high-impact uncertainty remain. Do not stop at the first plausible answer when a stronger answer is reachable with a bounded second pass.

### 6. Maximize Signal

Actively look for:

- Counterexamples and edge cases.
- Conflicting evidence or stale assumptions.
- Missing tests, missing data, or hidden dependency paths.
- Root causes instead of only symptoms.
- Constraints that change the recommendation.
- The smallest next action that would remove the largest remaining uncertainty.
- Subagent agreement is not evidence by itself; verify it against primary sources, code, tests, logs, or direct artifacts.

Avoid shallow completion signals such as reading one file, checking one source, or finding one plausible explanation when the user's request implies a stronger answer.

### 7. Report Findings

Lead with the answer, then show the evidence. Use the deliverable shape the user needs:

- For findings: severity or impact first, then location/source, reasoning, and suggested action.
- For root cause: symptom, cause, evidence, reproduction or verification, and fix direction.
- For options: criteria, tradeoffs, recommendation, and confidence.
- For summaries: what matters, what changed, what remains uncertain, and why.
- For code research: include clickable file references and the commands or tests used when relevant.

Explicitly separate facts, inferences, and recommendations when confusion would be costly. State uncertainty clearly, but do not dilute well-supported conclusions.

## Quality Checks

Before finalizing, verify:

- The answer addresses the user's likely underlying goal, not only the literal wording.
- The investigation scope and assumptions are visible if they affect the conclusion.
- Evidence quality matches the stakes and recency requirements.
- A focused subagent challenged the conclusion, or subagents were unavailable/prohibited and an equivalent local skeptical pass was disclosed where material.
- Material critique was adopted, rejected with reason, or disclosed as unresolved with confidence impact.
- Important alternatives or counterevidence were considered.
- The answer still matches the requested deliverable; interesting but irrelevant findings were discarded.
- The final response contains a concrete result, not just a process summary.
