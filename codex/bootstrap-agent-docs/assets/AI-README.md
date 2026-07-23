# AI agent documentation sources

`AGENTS.md` and `CLAUDE.md` are generated from the fragments in `ai/fragments/`. Edit the fragments, not the generated outputs.

Path-specific rules live in `ai/rules/`. The generator mirrors those rules into `.claude/rules/` while preserving unrelated Claude rules. Managed outputs are recorded in the generated `ai/.agent-docs-manifest.json` file.

Keep this maintenance explanation here. Generated `AGENTS.md` and `CLAUDE.md` intentionally contain no generation banner or fragment-source notice. Their root context is reserved for non-obvious, always-relevant constraints.

## Commands

Run from the repository root:

```sh
python3 ai/manage-agent-docs.py build
python3 ai/manage-agent-docs.py check
```

`build` regenerates managed documents and rule mirrors. It refuses to overwrite a managed output changed independently of its source; move the intended edit into a fragment or rule before rebuilding. `check` performs no writes and exits nonzero when a managed output or manifest is missing, stale, or inconsistent.

During initial migration, the generator refuses to overwrite an unmanaged `AGENTS.md`, `CLAUDE.md`, or colliding Claude rule. After moving all authoritative content into `ai/fragments/` or `ai/rules/` and reviewing the migration, adopt the files once with:

```sh
python3 ai/manage-agent-docs.py build --adopt-existing
```

The generator also blocks when `AGENTS.override.md` would shadow a managed `AGENTS.md`, or when `.claude/CLAUDE.md` would coexist with a managed `CLAUDE.md` at the same scope. Migrate the active content and remove or rename the conflicting alternate file explicitly; the adoption flag does not bypass this check. Inventory any Codex fallback instruction filenames configured outside this repository separately.

## Fragment layout

Fragment directories mirror repository directories. Root fragments generate root documents; `ai/fragments/packages/api/*.md` generates `packages/api/AGENTS.md` and `packages/api/CLAUDE.md`. A fragment directory must map to an existing repository directory.

Fragments are concatenated in filename order:

| Suffix | Output |
|---|---|
| `NN-name.md` | Both documents |
| `NN-name.agents.md` | `AGENTS.md` only |
| `NN-name.claude.md` | `CLAUDE.md` only |

Keep shared instructions in unsuffixed fragments. Add nested fragments and tool-specific variants only when the local workflow or agent capability genuinely differs.

Prefer `ai/rules/` for Claude guidance that applies only to matching files or situations. Do not duplicate a mirrored rule's full text in `CLAUDE.md`. Use nested or AGENTS-only routing guidance only when other agents need to discover the same scoped constraint.

## Repository integration

Expose the build and check commands through the repository's existing task runner. Run the non-mutating check in CI so source and generated files cannot drift silently. Commit source fragments, generated documents, mirrored rules, and `ai/.agent-docs-manifest.json` together.
