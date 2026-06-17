---
name: product-ui-design
description: >
  Use when designing or implementing product UI such as dashboards, settings,
  onboarding, internal tools, or app shells. TRIGGER when the user says things
  like "make a settings page", "build a dashboard", "implement the admin panel",
  "redesign this CRUD screen", "add an onboarding flow", "create a form view",
  "build an app shell", or asks to improve, fix, or restyle an existing product
  screen. Steers away from flashy AI-demo patterns and bland default SaaS layouts
  while preserving existing design systems. Use this instead of the broader
  frontend-design skill when operational clarity matters more than visual spectacle.
  DO NOT trigger for landing pages, marketing sites, or brand explorations.
argument-hint: [surface-type]
---

# Product UI Design

Create product interfaces that feel intentional and specific — not AI-demo glossy, not interchangeably bland.

## When to Use This Skill

- Dashboard, settings page, onboarding flow, app shell, CRUD surface, or product redesign
- The repo already has UI conventions worth preserving
- The result should look like a real product, not a design demo

## When to Use the Broader frontend-design Skill Instead

- Landing page, launch page, campaign site, or brand-first exploration
- Visual experimentation matters more than operational clarity

## Workflow

1. **Classify and survey** — choose operating mode (existing / new product / marketing). Check the repo's existing design tokens (`globals.css @theme`), component library (`components/ui/`, `components/common/`), and layout patterns before writing any code
2. **Write a one-line visual thesis** — e.g. `calm technical workspace with dense data hierarchy`
3. **Lock five anchors** — typography, spacing density, color strategy, surface treatment, motion style
4. **Identify one signature move** — the single thing a reviewer would remember
5. **Implement around task clarity** — primary actions, navigation, state, hierarchy first. Then wire at least one keyboard shortcut for the primary action and persist filters/sort in URL searchParams (not ephemeral useState)
6. **Validate** — after writing the file, run `./scripts/validate.sh --output <written-file> --result /tmp/validate-result.json` and fix any failures it reports. The script checks: hardcoded palette colors, bg-white usage, dark: prefixes, useState-only filters, missing empty state CTAs, missing loading/error states, bare clickable divs, and icon buttons without aria-label
7. **Check completeness** — verify: empty states have CTA buttons, every fetch has loading/error/success, destructive actions have tier-matched confirmation, every metric links to an actionable view. Then check the opposite failure: too flashy → remove decoration; too generic → strengthen signature move

## Constraints

- Do not chase novelty across every layer of the interface
- Keep one signature move; let the rest stay disciplined
- Improve hierarchy, pacing, and typography before inventing new visual motifs
- Treat anti-slop as a constraint, not as a reason to make the design bland
- Preserve the repo's design system, component usage, and layout patterns
- Keep desktop and mobile working
- Do not introduce ornamental complexity the codebase will not maintain

## Output Shape

When planning, provide:

- operating mode (existing / new product / marketing)
- one-line visual thesis
- signature move
- key layout and component changes
- main risks to avoid

Example:

> **Mode:** Existing Product UI
> **Thesis:** Dense, technical workspace — information-forward with minimal chrome
> **Signature move:** Monospace headings with tight letter-spacing in the sidebar nav
> **Changes:** Collapse stat cards into a single summary bar; replace card grid with a compact table view; tighten vertical spacing by 25%
> **Risks:** Over-densifying mobile layout; losing visual breathing room in empty states

When implementing, make changes directly and keep the result realistic to ship.
Run relevant lint, typecheck, or test commands for behavior changes.

## After Implementation

If the result missed the mark, identify which of these caused it:

- Signature move was too subtle → strengthen it
- Signature move dominated the surface → dial it back
- Existing conventions were broken → check repo patterns more carefully
- Output felt generic → revisit the visual thesis
- Mobile or responsive broke → verify breakpoints before finishing

Report the finding so the skill can be refined over time.

## Detailed Guidelines

For the full design philosophy, anti-patterns, and visual guardrails, see [reference.md](reference.md).
