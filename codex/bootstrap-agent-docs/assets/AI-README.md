# AI agent documentation sources

`AGENTS.md` and `CLAUDE.md` are generated from the fragments in `{{AGENT_DOCS_DIR}}/fragments/`. Edit the fragments, not the generated outputs.

Path-specific rules live in `{{AGENT_DOCS_DIR}}/rules/`. The generator mirrors those rules into `.claude/rules/` while preserving unrelated Claude rules. Managed outputs are recorded in the generated `{{AGENT_DOCS_DIR}}/.agent-docs-manifest.json` file.

`{{AGENT_DOCS_DIR}}/.agent-docs-layout.json` binds the manager to this repository-relative source directory. Choose the directory during scaffolding; do not edit the layout file or relocate individual maintenance artifacts afterward.

Keep this maintenance explanation here. Generated `AGENTS.md` and `CLAUDE.md` intentionally contain no generation banner or fragment-source notice. Their root context is reserved for non-obvious, always-relevant constraints.

## Commands

Run from the repository root:

```sh
python3 {{AGENT_DOCS_DIR}}/manage-agent-docs.py build
python3 {{AGENT_DOCS_DIR}}/manage-agent-docs.py check
```

`build` regenerates managed documents and rule mirrors. It refuses to overwrite a managed output changed independently of its source; move the intended edit into a fragment or rule before rebuilding. `check` performs no writes and exits nonzero when a managed output or manifest is missing, stale, or inconsistent.

During initial migration, the generator refuses to overwrite an unmanaged `AGENTS.md`, `CLAUDE.md`, or colliding Claude rule. After moving all authoritative content into `{{AGENT_DOCS_DIR}}/fragments/` or `{{AGENT_DOCS_DIR}}/rules/` and reviewing the migration, adopt the files once with:

```sh
python3 {{AGENT_DOCS_DIR}}/manage-agent-docs.py build --adopt-existing
```

The generator also blocks when `AGENTS.override.md` would shadow a managed `AGENTS.md`, or when `.claude/CLAUDE.md` would coexist with a managed `CLAUDE.md` at the same scope. Migrate the active content and remove or rename the conflicting alternate file explicitly; the adoption flag does not bypass this check. Inventory any Codex fallback instruction filenames configured outside this repository separately.

## Fragment layout

Fragment directories mirror repository directories. Root fragments generate root documents; `{{AGENT_DOCS_DIR}}/fragments/packages/api/*.md` generates `packages/api/AGENTS.md` and `packages/api/CLAUDE.md`. A fragment directory must map to an existing repository directory.

Fragments are concatenated in filename order:

| Suffix | Output |
|---|---|
| `NN-name.md` | Both documents |
| `NN-name.agents.md` | `AGENTS.md` only |
| `NN-name.claude.md` | `CLAUDE.md` only |

Keep shared instructions in unsuffixed fragments. Add nested fragments and tool-specific variants only when the local workflow or agent capability genuinely differs.

Prefer `{{AGENT_DOCS_DIR}}/rules/` for Claude guidance that applies only to matching files or situations. Do not duplicate a mirrored rule's full text in `CLAUDE.md`. Use nested or AGENTS-only routing guidance only when other agents need to discover the same scoped constraint.

## Repository integration

Expose the build and check commands through the repository's existing task runner. Run the non-mutating check in CI so source and generated files cannot drift silently. Commit the selected maintenance directory—including its manager, layout file, README, sources, and manifest—together with generated documents and mirrored rules.
