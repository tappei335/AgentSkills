# Agent Skills Repository

This repository manages Codex and Claude skills.

## Layout

- `codex/<skill-name>/` - Codex skills. Each skill should include `SKILL.md`; Codex skills should also include `agents/openai.yaml`.
- `claude/<skill-name>/` - Claude skills. Claude-specific tool names and frontmatter may live here.
- `<skill>/references/` - Optional reference material loaded only when the skill needs it.
- `<skill>/scripts/` - Optional deterministic helpers used by the skill.
- `policies/model-selection.md` - Shared model-selection rules, bundled into each Codex skill on build.
- `profiles/<profile>.json` - Root model/effort and independent candidate models for worker roles.
- `variants/<profile>/<skill-name>/` - Optional measured instruction additions, with `instructions.md` and `evidence.md`.
- `variants/<profile>/_shared/` - Profile-wide guidance using the same two-file format, bundled into every skill.

## Conventions

- Keep `SKILL.md` concise and procedural. Put detailed variants, examples, or long reference material in `references/`.
- Put trigger guidance in the `description` frontmatter because the body is loaded only after the skill triggers.
- Keep Codex frontmatter to `name` and `description`.
- Name skill directories exactly the same as the `name` field.
- Prefer copying a skill to both `codex/` and `claude/` only when the workflow is useful in both agents; adapt tool names separately.

## Japanese documentation

[`write-japanese-docs`](codex/write-japanese-docs/SKILL.md) creates and revises Japanese READMEs, design documents, procedures, technical articles, and reports. A [Claude version](claude/write-japanese-docs/SKILL.md) is also available. It includes revision examples and optional textlint guidance.

After syncing, invoke it with a request such as:

```text
$write-japanese-docs 実装を確認し、新規利用者向けの README を日本語で作成してください。
```

## Sync

Copy repository skills into the local agent skill directories:

```sh
scripts/sync_skills.sh
```

Preview changes without copying:

```sh
scripts/sync_skills.sh --dry-run
```

Sync only one agent:

```sh
scripts/sync_skills.sh --agent codex
scripts/sync_skills.sh --agent claude
```

The script replaces destination skill directories with the same name, such as `~/.codex/skills/<skill-name>` or `~/.claude/skills/<skill-name>`. Skills that exist only in the destination are left untouched. Codex builds without a profile inherit the runtime model and effort. They honor an existing `CODEX_HOME`; Claude sync is unchanged.

## GPT-6 and GPT-5.6 side by side

Install each distribution into a separate Codex home:

```sh
scripts/sync_skills.sh --agent codex --profile gpt-6
scripts/sync_skills.sh --agent codex --profile gpt-5.6
```

The defaults are `~/.codex-profiles/gpt-6` and `~/.codex-profiles/gpt-5.6`. Add `--dry-run` to preview, or `--codex-home /absolute/path` to select another home. Sync refuses profile installation into the shared Codex home, mixing profiles in one destination, or adopting a home containing unmanaged skills.

Start separate CLI sessions, including simultaneous sessions in the same repository:

```sh
python3 scripts/codex_profile.py gpt-6
python3 scripts/codex_profile.py gpt-5.6
python3 scripts/codex_profile.py gpt-6 -- --cd /path/to/project
```

The launcher uses the installed profile snapshot, sets `CODEX_HOME` only for the child process, and passes the root model and effort through Codex's `-c` option. Everything after `--` is forwarded literally to Codex; model overrides there take precedence and do not select a different skill variant. Start a new session with the matching launcher when changing profiles. Use `--dry-run` before `--` to inspect the command without starting Codex. When using a custom home, pass the same `--codex-home` to sync and the launcher.

Authentication, config, plugins, and session history belong to each home. Existing credentials and settings are not copied. If authentication is required, run `python3 scripts/codex_profile.py gpt-6 -- login` (and likewise for `gpt-5.6`); configure needed MCP servers and other preferences in that home's `config.toml`.

Codex also discovers repository skills and shared `~/.agents/skills`. Those remain shared: avoid putting a second model-specific copy of these skills there. This launcher controls CLI sessions; it does not switch profiles in an already running desktop or IDE session.

| Profile | Root (medium) | Judgment (high) | Bounded (medium) | Mechanical (low) |
| --- | --- | --- | --- | --- |
| `gpt-6` | `gpt-6-astra` | `gpt-6-astra` | `gpt-5.6-terra` | `gpt-5.6-luna` |
| `gpt-5.6` | `gpt-5.6-sol` | `gpt-5.6-sol` | `gpt-5.6-terra` | `gpt-5.6-luna` |

These are initial settings using model IDs available in the development runtime, not benchmark results or a guarantee of availability in every account. Worker settings are guidance for a justified, supported override, not automatic agent creation or enforced routing. Runtime permissions still apply. Editing a profile requires another sync to update its installed snapshot.

## Build and tune

Build a portable distribution without installing it (Python 3.10+; standard library only):

```sh
python3 scripts/build_skills.py --profile gpt-6 --output build/gpt-6
python3 scripts/build_skills.py --profile gpt-5.6 --output build/gpt-5.6
python3 scripts/validate_skills.py --root build/gpt-6
```

Omit `--profile` for common skills. Outputs contain `skills/` and `profile.json`; builds require a fresh output directory and validate links before publishing it. Edit source files, then rebuild into a new directory. The builder copies helpers/assets, converts the shared policy link to a bundled relative link, adds profile-wide guidance immediately after frontmatter, and appends a reference to any skill-specific variant. Directly copying `codex/` does not bundle the shared policy; use the build or sync command.

Keep model IDs in `profiles/`, acceptance criteria in common skills, and model-specific additions in `variants/`. To add a variant, create `variants/<profile>/<skill-name>/instructions.md` and `evidence.md`; use `_shared` instead of a skill name for profile-wide guidance. The first contains only the adjustment and is loaded at workflow start. The second stays in this repository and records the representative task, exact model/effort, baseline versus candidate results, correctness/completeness, latency/token use when available, and why the adjustment is retained. Both files must be nonempty. Links in instructions must resolve from the generated skill's `references/` directory.

GPT-6 includes a user-requested official-guidance pilot. Its [adoption record](variants/gpt-6/_shared/evidence.md) maps the sources to this repository, records the exception to measured-only adoption, and defines behavioral evaluation cases. The September 15 update applies [OpenAI's skills and prompts article](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra): shorter Codex descriptions and conditional review-format loading are shared across profiles; completion, permission, and context-use adjustments apply only to GPT-6. Model-quality improvements remain unmeasured. Build or sync with `--profile gpt-6` to include those adjustments; a common install does not include them.

Use the same task inputs and acceptance criteria for both models. First compare common instructions, then test one adjustment at a time; retain only demonstrated improvements. Root and worker models are independent, so adopting GPT-6 at the root does not force every worker to use it.

On Windows, import only Codex skills with PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\import_codex_skills.ps1
```

Preview changes without copying:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\import_codex_skills.ps1 -DryRun
```

Import selected skills:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\import_codex_skills.ps1 -SkillName product-ui-design,github-pr-review
```

The PowerShell script copies `codex/*` to `$env:CODEX_HOME\skills` when `CODEX_HOME` is set, otherwise to `$HOME\.codex\skills`.

## Validation

Run the repository checks after editing skills:

```sh
python3 scripts/validate_skills.py
python3 -m unittest discover -s scripts/tests -v
```

The validator checks required frontmatter, directory/name consistency, Codex `agents/openai.yaml`, broken relative markdown links, and executable bits for shebang scripts. Profile tests cover common and model-specific builds, variants, portable links, destination isolation, repeated sync, dry-run behavior, and launch arguments.
