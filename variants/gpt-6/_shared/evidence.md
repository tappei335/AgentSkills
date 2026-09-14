# GPT-6 guidance adoption record

Status: official-guidance pilot, requested by the user on 2026-09-05. No task-quality, latency, or token improvement has been measured. This is an explicit, user-authorized exception to the common policy's measured-only rule for adding variants.

Updated at the user's request on 2026-09-15 using [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), accessed on that date. The article motivates shorter discovery descriptions, conditional reference loading, clearer decision boundaries, and explicit completion criteria. This update continues the pilot rather than asserting a measured behavioral improvement.

Source: [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model), accessed 2026-09-05. Relevant sections: Initiative and follow-through; Instruction following; Personality and writing style; Subagent delegation; Testing and verification; Update API and model parameters.

The guide recommends tuning autonomy, skill interpretation, writing, delegation, and verification. It recommends retaining an existing supported reasoning setting during migration. These recommendations motivate this pilot; they do not establish a repository-specific performance result.

## Repository application

- Bundle one shared adjustment into all nine GPT-6 skills, including bootstrap-agent-docs, which has no model-selection section. Load it immediately after frontmatter so it is available before workflow gates.
- Keep model-specific guidance out of the GPT-5.6 distribution. The September 15 common-source edits shorten discovery descriptions and move the CodeAnalyzer comment format into a conditionally loaded reference; both profiles receive those edits. Claude skills remain separate.
- Preserve root medium and judgment high from the existing profile. Bounded and mechanical workers retain their independent model choices.
- Keep strategy/research real-critic requirements, site reconstruction visual acceptance, and explicit publication authority. The new instruction distinguishes an actual gate from an inferred one; it does not waive required checks.
- Use delegation only where the existing skill and runtime allow it. Do not import an unconditional delegation policy into single-agent tasks.
- No Responses API adapter exists here. Async tool execution, configuration_update, and request parameter migration belong to a consuming harness and are outside this change.

## September 15 instruction audit

| Surface | Decision and reason |
| --- | --- |
| Nine Codex descriptions | Keep capability, triggering request, and useful exclusions; leave execution mechanics in the body. Preserve explicit planning and team-mode boundaries. |
| CodeAnalyzer review formatting | Move the existing format and examples intact into `references/comment-format.md`, loaded when composing a review. Preserve PR identity, bot publishing, evidence, and review gates. |
| GPT-6 shared instructions | Define completion beyond a first pass, reuse existing authority, load references for the current decision, and preserve the task through follow-up messages. |
| Strategy/research critique and site visual checks | Retain as substantive acceptance requirements, not obsolete scaffolding. |
| Bootstrap agent documentation | Retain its scoped documentation routing and generated-file invariants; no root AGENTS.md exists in this repository to trim. |

Description size and entrypoint length measure context reduction only, not skill-selection accuracy. The behavior of shortened triggers still needs representative model runs.

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
| Already-authorized action with a generic ask-first recommendation | Uses the existing authority without a second approval, while preserving explicit review checkpoints. |
| Follow-up correction during implementation | Applies the correction, retains the original completion criteria, and does not restart completed work. |
| Focused task with unrelated reference links | Reads applicable instructions and relevant references without loading every linked document. |
| Trigger boundaries | A routine plan, simple diagnosis, or backend edit does not load strategy, deep research, or product UI respectively; an explicit cross-system strategy, competing-evidence investigation, or product screen request does. |

For each run, record exact model/effort, completion and correctness, unsupported claims, avoidable questions, tool/check counts, latency, and token usage when exposed. Keep task-quality failures separate from packaging failures. Revise the pilot if it weakens an acceptance gate or adds overhead without a useful behavioral change.

Validation covers generation, links, and isolation of GPT-6 guidance. For the September 15 update, compare GPT-5.6 artifacts allowing only the common description edits and the moved CodeAnalyzer format. Behavioral A/B runs remain pending; packaging tests do not measure model behavior.

September 15 local validation: the repository validator passed for 16 skills; both profile builds succeeded. Comparing with the pre-edit distributions confirmed that GPT-5.6 changed only in nine entrypoints and the extracted formatting reference. The reference preserves the original format text exactly, and other workflow bodies are unchanged. Total description characters fell from 5,093 to 1,989 (60.9%; not a token measurement). The eight-test profile suite reported six passes and two failures because Windows resolved `bash` to a WSL launcher with no `/bin/bash`; successful sync behavior remains unverified in this environment. Tests expecting rejection are not evidence that the shell executed correctly.
