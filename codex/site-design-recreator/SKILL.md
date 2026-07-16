---
name: site-design-recreator
description: Recreate a specified website or web-app screen as maintainable responsive DOM/CSS with pixel-level fidelity across mobile through 4K. Use when asked to reproduce, clone, recreate, match, or implement a target from a URL, screenshot, or deployed reference. When subagents are available and delegation is permitted, require a manager-led loop with designer-subagent implementation, Playwright screenshots, DOM/CSS inspection, and repeated visual verification.
---

# Site Design Recreator

## Operating Contract

Recreate the target as responsive, inspectable DOM/CSS or framework components, not a pasted screenshot, canvas trace, image map, OCR overlay, or bitmap facade. Use screenshots to measure and verify; derive structure from target DOM, computed styles, layout mechanics, typography, assets, states, and breakpoint behavior.

Respect authorization and asset licenses. When exact private assets, paid fonts, data, or restricted media are unavailable, preserve layout and visual intent with the closest lawful substitute and disclose the limitation.

Do not report completion while an in-scope viewport or state has unresolved visible differences, broken responsive behavior, or prohibited rasterized UI. Report a blocker when exact completion is impossible.

Read [playwright-cli-workflow.md](references/playwright-cli-workflow.md) completely before capture, comparison, or acceptance work.

## Roles And Models

Keep manager and designer responsibilities separate:

- **Manager/main agent:** define scope and viewport/state matrix, capture references, inspect target DOM/CSS, write ordered fix lists, compare results, enforce image policy, and accept or reject each pass.
- **Designer/worker:** implement the reconstruction plan and every manager fix in its assigned write scope, preserve accepted areas, and report changed files and risks without approving its own work.

When subagents are available and delegation is permitted, delegate every implementation pass to a designer worker. Use a read-only explorer only for a bounded DOM/CSS or asset sweep. If delegation is unavailable or disallowed, disclose the limitation and run visibly separate local manager and designer passes.

Prefer automatic model selection. When explicit selection is supported, use `gpt-5.6` with high effort for visual direction, responsive reconstruction, designer implementation, and final acceptance; use `gpt-5.6-terra` with medium effort for bounded DOM/CSS, asset, or breakpoint sweeps. Use `gpt-5.6-luna` only for mechanical inventories. If the spawn interface cannot select a model, use a configured agent or inherit the parent model, and do not claim an override.

## Reconstruct The Target

1. Resolve the target URL or screenshot, authorization, page state, interactions, viewport matrix, and acceptance surface. Ask only when ambiguity would materially change the result.
2. Capture deterministic reference screenshots with a consistent browser, viewport, device scale, reduced-motion setting, ready condition, and full-page policy.
3. Inspect the live target visually and structurally. Record semantic regions, layout primitives, constraints, type metrics, colors, spacing, assets, sticky or overflow behavior, interaction states, and breakpoint changes.
4. Write a reconstruction plan covering DOM regions, component boundaries, layout and breakpoint rules, design tokens, asset strategy, states, and known substitutes.
5. Give the designer the plan, current fix list, write scope, accepted areas, and image policy.
6. Capture the implementation at the same viewport/state matrix, compare, and repeat the manager/designer loop until accepted or blocked.

Prioritize fixes by visual impact: layout, typography, spacing, color, imagery, interaction state, then micro-alignment. Re-capture after every material change and check that one viewport's fix did not regress another.

## Fidelity And Image Policy

Match both captured pixels and behavior between breakpoints. Verify relevant loaded, empty, error, hover, focus, active, menu, modal, sticky, overflow, and scroll states. Freeze representative dynamic content when necessary and record what was frozen.

Use DOM/CSS/SVG for page chrome, navigation, cards, forms, buttons, menus, tables, text, badges, and icons. Raster assets are acceptable for intrinsic visual content such as photos, map tiles, 3D or canvas output, data-unavailable charts, and authorized brand imagery.

When a screenshot substitute is unavoidable, crop the smallest semantic content region, keep surrounding UI live, document the reason, and require manager approval. Reject stretched UI backgrounds, viewport-sized screenshots, sliced page captures, and desktop/mobile bitmap swaps that hide missing responsiveness.

Use the default mobile-through-4K matrix in the workflow reference, adding target-specific breakpoints and states. If 4K is impractical, record the limitation and test the largest feasible viewport.

## Evidence And Tools

Persist iteration evidence under `.design-process/` unless the user forbids process artifacts:

- `manager-review.md`: evidence, ordered fix list, and verdict per pass;
- `designer-iteration-log.md`: assigned pass, changed files, implemented fixes, and risks;
- `acceptance-checklist.md`: viewport/state matrix, responsive and image-policy checks, final status, and blockers;
- `asset-audit.json`: bundled image-usage audit output or equivalent inventory.

Use Playwright for capture, `scripts/compare_screenshots.mjs` for diff metrics when available, and `scripts/audit_image_usage.mjs` before final acceptance. Treat pixel metrics as evidence, not a substitute for visual and responsive judgment.

## Acceptance And Reporting

Accept only when all in-scope viewports and states match, responsive mechanics hold between captures, text remains live and inspectable, and image use complies with policy. Known authorized substitutes must be the only disclosed differences.

Lead the final response with the acceptance status. Include the target, implemented files, viewport/state matrix, Playwright commands, final diff evidence, model or subagent use actually confirmed, manager/designer pass summary, substitutes, and blockers. Omit repetitive iteration narration that does not help assess fidelity.
