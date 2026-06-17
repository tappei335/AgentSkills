---
name: site-design-recreator
description: Recreate a specified website or web app screen as real responsive DOM/CSS with pixel-level fidelity across mobile, tablet, HD, Full HD, QHD, and 4K breakpoints. Use when asked to reproduce, clone, recreate, match, or implement a target site from a URL, screenshot, or deployed reference. When sub-agent tools are available and delegation is permitted, this skill requires implementation by a designer sub-agent, manager review between passes, Playwright screenshots for verification, and DOM/CSS inspection for reconstruction.
---

# Site Design Recreator

## Overview

Recreate the target as real responsive DOM/CSS UI, not as a pasted screenshot, canvas trace, image map, or screenshot-backed facade. Use Playwright screenshots for measurement and verification, but derive the implementation from DOM inspection, computed styles, layout mechanics, typography, assets, and responsive behavior.

Respect authorization and asset licenses. If exact brand assets, paid fonts, private data, or restricted media are not available or authorized, preserve layout, proportions, behavior, and visual intent with clearly disclosed substitutes.

## Operating Model

Run separate manager and designer execution contexts. Keep the roles separate in reasoning, implementation, and reporting.

- **Manager**: define scope, choose target URLs/states/breakpoints, capture reference screenshots, decide whether questions are needed, review each iteration, produce ordered fix lists, judge diffs, and stop only when the reproduction completely matches.
- **Designer**: implement the UI with HTML/CSS/framework code, preserve responsive layout mechanics, select assets, apply every manager fix item, and never replace the page with one static bitmap.

## Sub-Agent Protocol

When sub-agent tools are available (in Claude Code, the `Agent` tool) and the user request invokes this skill or otherwise permits delegation, the main agent MUST act as manager and MUST delegate implementation to a designer worker sub-agent for every implementation pass. Do not silently collapse the workflow into one self-reviewed pass. If the runtime has no sub-agent capability or the harness policy does not permit delegation for the request, state that limitation before proceeding and still perform distinct manager and designer passes locally.

- The **main agent/manager** critiques screenshots, diffs, DOM/CSS reconstruction, responsive behavior, and image-use policy. The manager must not implement a pass that should be delegated.
- Spawn a **designer/worker** sub-agent (via the `Agent` tool) to implement fixes from the manager's review list. The designer must edit files in its assigned write scope and must not approve its own work.
- The main agent coordinates captures, passes artifacts and fix lists to the designer, integrates or reviews returned changes, and enforces acceptance gates.
- For each iteration, obtain a manager review before the designer starts the next fix pass, then re-capture with Playwright before manager re-review.
- If a separate reviewer sub-agent is useful and available, use it for independent final critique, but do not use that as a substitute for the manager/designer loop.

## Acceptance Goal

The goal is complete visual and responsive match for all in-scope viewports and states. Known differences are failures, not acceptable follow-up notes, unless exact reproduction is blocked by authorization, unavailable private assets, paid fonts, third-party data, or a browser/runtime limitation. In that case, state the blocker and use the closest lawful substitute.

Never report the task as implemented, done, accepted, or complete while any required viewport/state has unresolved visual differences, broken responsive behavior, or a screenshot substitute that violates the image-use policy.

Default viewport coverage includes mobile, tablet, desktop, HD, Full HD, QHD, and 4K. If runtime or hardware limits make 4K capture impractical, state the limitation and still test the largest feasible viewport.

## Review-Implementation Loop

Repeat this loop until the manager accepts the result:

1. Manager captures or refreshes reference and actual screenshots with Playwright CLI.
2. Manager reviews the screenshots, diff output, target DOM structure, computed styles, layout measurements, asset usage, and responsive behavior. For live targets, inspect the target DOM/CSS before issuing each major fix list unless access is blocked.
3. Manager writes a concrete fix list ordered by visual impact: layout, typography, spacing, color, imagery, interaction state, then micro-alignment.
4. Designer implements the full fix list without changing accepted areas unless required by the fix.
5. Designer reports changed files and any suspected risk.
6. Manager re-captures the same viewport/state matrix, compares again, and either accepts or issues the next fix list.

Persist iteration evidence under `.design-process/` in the target project, unless the user explicitly forbids writing process artifacts:

- `manager-review.md`: each pass's manager verdict, screenshot/diff evidence, fix list, and acceptance decision.
- `designer-iteration-log.md`: each delegated designer pass, changed files, and implemented fix list.
- `acceptance-checklist.md`: viewport/state matrix, final diff status, responsive checks, image-use policy result, and blockers.
- `asset-audit.json`: output from `scripts/audit_image_usage.mjs` or an equivalent runtime image inventory.

## Workflow

1. Confirm the target and scope. Capture the URL, page state, viewport set, and any required interactions. Ask only when the target, authorization, or expected surface is ambiguous enough to change the result.
2. Capture references with Playwright CLI. Use the same browser engine, viewport sizes, and wait strategy for the target and local implementation. Read `references/playwright-cli-workflow.md` for command templates.
3. Inspect the target visually and structurally. Record typography, spacing, colors, imagery, grid behavior, sticky elements, overflow, interaction states, and breakpoint changes.
4. Produce a reconstruction plan before implementation: semantic DOM regions, layout primitives, breakpoint rules, typography tokens, color tokens, spacing scale, image/assets strategy, and interaction states. The designer must implement from this plan, not from screenshot placement alone.
5. Implement the reproduction as maintainable responsive DOM/CSS or framework components. Use real text, semantic regions, reusable CSS, stable layout constraints, media/container queries, and extracted or substituted assets. Do not use a full-page screenshot, sliced screenshots, absolutely positioned screenshot fragments, canvas-only rendering, or OCR text overlays as the implementation.
6. Start the review-implementation loop. Re-capture the local implementation with Playwright CLI at every reference viewport and state.
7. Compare screenshots. Use visual inspection first, and use `scripts/compare_screenshots.mjs` for pixel-diff metrics and diff PNGs when Playwright is available. Use `scripts/audit_image_usage.mjs` to surface screenshot-heavy implementation risk before final review.
8. Iterate through manager review and designer fixes until the manager accepts a complete match. Do not stop after one viewport if other widths or states remain visibly wrong.

## Image-Use Policy

Default to real DOM/CSS/SVG/canvas implementation. Screenshots and raster crops are allowed only for visual content that is itself the product content or cannot be lawfully or practically reconstructed.

Allowed raster use:

- Photos, product thumbnails, map tiles, orthomosaics, 3D/WebGL render output, charts whose data is unavailable, or other intrinsically visual source content.
- Minimal crops of dynamic canvas/map/model content when live reconstruction is out of scope.
- Brand marks or icons only when the asset is public, authorized, and not reasonably represented by text or vector drawing.

Prohibited raster use:

- Entire pages, full panels, nav bars, cards, forms, buttons, menus, sidebars, tables, text blocks, badges, icons, or layout chrome that can be built with DOM/CSS/SVG.
- Screenshots containing readable UI text that should be live text.
- Stretching captured UI with `background-size: 100% 100%`, `object-fit: fill`, or viewport-sized background images to hide layout differences.
- Hiding missing responsive behavior by swapping large desktop/mobile screenshots.

When a screenshot substitute is unavoidable, crop the smallest semantic content region, keep surrounding UI chrome as DOM/CSS, document the reason, and get manager approval before final acceptance.

## Fidelity Rules

- Treat pixel-level match as a required measurement aid, not the whole goal. The page must also reflow like the target between captured breakpoints.
- Capture at least mobile, tablet, desktop, HD, Full HD, QHD, and 4K. Add target-specific breakpoints, ultrawide, and high-density device scale factors when the layout changes or the target is expected to support them.
- Compare viewport screenshots and full-page screenshots when scrollable content matters.
- Match loaded state, hover/focus/active states, modals, menus, sticky headers, and empty/error/loading states when they are in scope.
- Prefer measured values from screenshots and DOM inspection over guesses: colors, font sizes, line heights, border radii, shadows, gutters, and image crop positions.
- Preserve text wrapping at each viewport. Do not let labels, buttons, cards, or nav items overflow or overlap.
- If the target uses dynamic content, freeze representative content for comparison and document what was frozen.
- Treat image-use violations as review failures even when pixel diff improves.

## Playwright Requirements

- Use Playwright CLI for screenshots unless impossible; if CLI syntax differs in the installed version, run `npx playwright screenshot --help` and adapt.
- Save reference and actual screenshots in separate directories with names that include viewport and state.
- Use deterministic waits: prefer app-ready selectors when using a temporary script, otherwise use a short fixed CLI wait after network/layout settles.
- Keep browser, viewport, device scale factor, full-page setting, and reduced-motion settings consistent between reference and actual captures.

## Reporting

Finish with the target URL or screenshot source, implemented files, viewport matrix, Playwright commands used, final diff status, and whether the manager accepted the reproduction as a complete match. If not accepted, do not call the work done; report the blocker or next required fix list.

Include the manager/designer iteration log: sub-agent used or unavailable, each manager fix list, each designer implementation pass, and the acceptance decision. If sub-agent tools were available and delegation was permitted but not used, report that as a skill violation.
