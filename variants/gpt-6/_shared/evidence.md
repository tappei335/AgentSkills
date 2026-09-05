# GPT-6 guidance adoption record

Status: official-guidance pilot, requested by the user on 2026-09-05. No task-quality, latency, or token improvement has been measured. This is an explicit, user-authorized exception to the common policy's measured-only rule for adding variants.

Source: [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model), accessed 2026-09-05. Relevant sections: Initiative and follow-through; Instruction following; Personality and writing style; Subagent delegation; Testing and verification; Update API and model parameters.

The guide recommends tuning autonomy, skill interpretation, writing, delegation, and verification. It recommends retaining an existing supported reasoning setting during migration. These recommendations motivate this pilot; they do not establish a repository-specific performance result.

## Repository application

- Bundle one shared adjustment into all eight GPT-6 skills, including bootstrap-agent-docs, which has no model-selection section. Load it immediately after frontmatter so it is available before workflow gates.
- Keep shared source skills and GPT-5.6 artifacts intact. Model-specific guidance must not reach the GPT-5.6 distribution.
- Preserve root medium and judgment high from the existing profile. Bounded and mechanical workers retain their independent model choices.
- Keep strategy/research real-critic requirements, site reconstruction visual acceptance, and explicit publication authority. The new instruction distinguishes an actual gate from an inferred one; it does not waive required checks.
- Use delegation only where the existing skill and runtime allow it. Do not import an unconditional delegation policy into single-agent tasks.
- No Responses API adapter exists here. Async tool execution, configuration_update, and request parameter migration belong to a consuming harness and are outside this change.

## Evaluation cases

Use the previous generated GPT-6 distribution as the baseline and the new distribution as the candidate, with identical model settings, repository state, prompts, and tool permissions. Keep the GPT-5.6 build as a separation control, not an interchangeable causal baseline.

| Case | Acceptance evidence |
| --- | --- |
| Small, explicit local documentation correction | Completes the edit and applicable checks without an unnecessary confirmation or unrelated test suite. |
| Review with ambiguous but resolvable scope | Uses supplied diff/context, reports evidence-backed findings, and does not modify product code. |
| Requested team implementation with independent ownership | Starts useful workers when available, integrates evidence, and preserves write boundaries. |
| Required strategy critic unavailable | Identifies the exact applicable gate and limitation; does not fabricate a critic. |
| Site recreation with a viewport mismatch | Continues necessary visual correction rather than treating test proportionality as permission to skip acceptance. |
| Authorized preparation followed by an unapproved publication step | Completes reviewable local work and requests only the remaining publication authority. |

For each run, record exact model/effort, completion and correctness, unsupported claims, avoidable questions, tool/check counts, latency, and token usage when exposed. Keep task-quality failures separate from packaging failures. Revise the pilot if it weakens an acceptance gate or adds overhead without a useful behavioral change.

Validation for this change covers generation, links, profile isolation, and unchanged GPT-5.6 bytes. Behavioral A/B runs remain pending; packaging tests do not measure model behavior.
