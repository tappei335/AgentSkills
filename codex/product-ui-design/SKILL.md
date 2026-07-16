---
name: product-ui-design
description: Design or implement operational product UI such as dashboards, settings, onboarding, internal tools, CRUD screens, tables, forms, admin panels, and app shells. Use when the user asks Codex to build, improve, fix, restyle, or redesign a product screen where clarity and workflow quality matter more than marketing spectacle. Preserve existing design systems while avoiding flashy AI-demo patterns and interchangeable SaaS defaults. Do not use for landing pages, marketing sites, brand exploration, or purely backend work.
---

# Product UI Design

## Operating Contract

Create product interfaces that are specific, usable, accessible, responsive, and realistic to maintain. Preserve the existing design system and user workflows unless the request explicitly authorizes a visual or interaction reset.

For change requests, inspect and edit the in-scope UI and run relevant non-destructive validation without asking first. Stop before external publication, dependency expansion, destructive actions, or material product-behavior changes outside the request.

Read [reference.md](reference.md) for detailed state, accessibility, token, component, and visual guidance before substantial design or implementation.

## Establish The Direction

Survey repository instructions, design tokens, shared components, layout patterns, typography, responsive conventions, and nearby screens before proposing a direction. Reuse existing primitives and semantic tokens before creating new ones.

Define only the anchors needed to keep the work coherent:

- **Mode:** existing product UI or new product surface.
- **Thesis:** one sentence describing hierarchy, density, tone, and product character.
- **Anchors:** typography, spacing density, color strategy, surfaces, and motion.
- **Signature move:** one memorable treatment that supports the product rather than competing with it.
- **Success:** user task, states, viewports, and evidence required for acceptance.

Infer these from the product and repository context. Ask only when an ambiguity would materially change workflow, information architecture, brand direction, or scope.

## Implement For The Task

Build navigation, hierarchy, state, and primary actions before decoration. Keep the signature move concentrated in one layer and let the rest remain disciplined.

- Use semantic HTML and accessible controls; do not simulate buttons or links with bare clickable containers.
- Handle applicable loading, empty, error, success, and destructive-action states with a recovery or next action.
- Preserve filters, sort, pagination, and other shareable view state in the URL when the screen exposes them.
- Add shortcuts only for frequent, discoverable actions where they improve the actual workflow.
- Make displayed metrics and alerts lead to an actionable detail or filtered view.
- Keep mobile and desktop behavior intentional, including focus, overflow, text wrapping, and reduced motion.

Avoid ornamental complexity, raw palette colors where semantic tokens exist, landing-page motifs inside operational screens, and new abstractions the codebase will not maintain.

## Model And Iteration

Prefer automatic model selection. When explicit selection is available, use `gpt-5.6` for ambiguous, high-polish, or visually judgment-heavy work and `gpt-5.6-terra` for bounded changes inside a mature design system. Do not use `gpt-5.6-luna` for subjective visual decisions; reserve it for mechanical inventories or transformations with objective acceptance criteria.

Evaluate the result against the thesis and user task. If it feels generic, strengthen product-specific hierarchy or the signature move. If it feels flashy, remove decoration. If conventions or responsive behavior broke, correct those before adding polish.

## Validate

Run repository-native lint, typecheck, tests, and visual or interaction checks proportional to the change. For applicable source files, also run the bundled validator:

```bash
bash ~/.codex/skills/product-ui-design/scripts/validate.sh --output <written-file> --result /tmp/product-ui-design-validate.json
```

When editing this skill from its source repository, use `codex/product-ui-design/scripts/validate.sh`. Treat validator failures as leads: inspect applicability, fix real gaps, and explain any intentional exception.

Before completion, verify task clarity, state coverage, accessibility, responsive behavior, destructive-action safeguards, actionable metrics, and design-system consistency.

## Output

For planning, report the mode, thesis, signature move, key layout or component decisions, state and responsive plan, and material risks. For implementation, lead with the user-visible result, changed files, checks, visual evidence when available, and remaining risks. Omit generic design narration.
