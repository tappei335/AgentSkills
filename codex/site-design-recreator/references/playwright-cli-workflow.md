# Playwright CLI Workflow

## Contents

- [Viewport Matrix](#viewport-matrix)
- [DOM/CSS Inspection](#domcss-inspection)
- [Command Templates](#command-templates)
- [Process Artifacts](#process-artifacts)
- [Manager Checklist](#manager-checklist)
- [Designer Checklist](#designer-checklist)

Use this reference when inspecting target DOM/CSS, capturing screenshots, comparing implementation output, and preserving manager/designer iteration evidence.

## Viewport Matrix

Start with these sizes, then add any breakpoint where the target visibly changes:

- Mobile: `390,844`
- Tablet: `768,1024`
- Desktop: `1440,900`
- HD: `1280,720`
- Full HD: `1920,1080`
- QHD / 2K: `2560,1440`
- 4K UHD: `3840,2160`

Optional additions when relevant:

- Small mobile: `360,800`
- Large mobile: `430,932`
- Ultrawide: `3440,1440`
- High-density check: repeat critical mobile and desktop captures with the same CSS viewport and `deviceScaleFactor: 2` when the rendering target depends on DPR.

Capture both viewport-only and `--full-page` screenshots when below-the-fold content, sticky elements, or scroll progress affects the design.

## DOM/CSS Inspection

For live URL targets, inspect structure and computed styles before implementation and before major review decisions. Screenshots verify visual fidelity; they do not replace DOM/CSS reconstruction.

Use Playwright evaluation or browser devtools protocol to collect:

- landmark, section, and repeated component hierarchy
- computed font family, size, weight, line height, letter spacing
- colors, backgrounds, borders, radii, shadows, opacity
- layout primitives: display, grid/flex settings, gaps, widths, min/max constraints
- image URLs, natural dimensions, object-fit, object-position, crop behavior
- sticky/fixed positioning, z-index, overflow, scroll behavior
- breakpoint changes across the viewport matrix

## Command Templates

Check the installed CLI syntax first when needed:

```sh
npx playwright screenshot --help
```

Create capture directories:

```sh
mkdir -p .design-reference .design-actual .design-diff
```

Capture the target:

```sh
npx playwright screenshot --browser chromium --viewport-size=1440,900 --wait-for-timeout=1200 "$TARGET_URL" .design-reference/desktop.png
npx playwright screenshot --browser chromium --viewport-size=1280,720 --wait-for-timeout=1200 "$TARGET_URL" .design-reference/hd.png
npx playwright screenshot --browser chromium --viewport-size=1920,1080 --wait-for-timeout=1200 "$TARGET_URL" .design-reference/full-hd.png
npx playwright screenshot --browser chromium --viewport-size=2560,1440 --wait-for-timeout=1200 "$TARGET_URL" .design-reference/qhd.png
npx playwright screenshot --browser chromium --viewport-size=3840,2160 --wait-for-timeout=1200 "$TARGET_URL" .design-reference/4k.png
npx playwright screenshot --browser chromium --viewport-size=390,844 --wait-for-timeout=1200 "$TARGET_URL" .design-reference/mobile.png
npx playwright screenshot --browser chromium --viewport-size=1440,900 --full-page --wait-for-timeout=1200 "$TARGET_URL" .design-reference/desktop-full.png
```

Capture the local implementation:

```sh
npx playwright screenshot --browser chromium --viewport-size=1440,900 --wait-for-timeout=1200 "$LOCAL_URL" .design-actual/desktop.png
npx playwright screenshot --browser chromium --viewport-size=1280,720 --wait-for-timeout=1200 "$LOCAL_URL" .design-actual/hd.png
npx playwright screenshot --browser chromium --viewport-size=1920,1080 --wait-for-timeout=1200 "$LOCAL_URL" .design-actual/full-hd.png
npx playwright screenshot --browser chromium --viewport-size=2560,1440 --wait-for-timeout=1200 "$LOCAL_URL" .design-actual/qhd.png
npx playwright screenshot --browser chromium --viewport-size=3840,2160 --wait-for-timeout=1200 "$LOCAL_URL" .design-actual/4k.png
npx playwright screenshot --browser chromium --viewport-size=390,844 --wait-for-timeout=1200 "$LOCAL_URL" .design-actual/mobile.png
npx playwright screenshot --browser chromium --viewport-size=1440,900 --full-page --wait-for-timeout=1200 "$LOCAL_URL" .design-actual/desktop-full.png
```

Compare a pair when the project has Playwright installed:

```sh
node /home/ippei/.codex/skills/site-design-recreator/scripts/compare_screenshots.mjs \
  .design-reference/desktop.png \
  .design-actual/desktop.png \
  --out .design-diff/desktop.png \
  --threshold 12 \
  --fail-over 0.005
```

Audit raster-image usage before final review:

```sh
node /home/ippei/.codex/skills/site-design-recreator/scripts/audit_image_usage.mjs .
```

Persist the result:

```sh
mkdir -p .design-process
node /home/ippei/.codex/skills/site-design-recreator/scripts/audit_image_usage.mjs . > .design-process/asset-audit.json
```

## Process Artifacts

Create and maintain these files during work:

- `.design-process/manager-review.md`: pass number, screenshots reviewed, diff summary, DOM/CSS findings, asset-policy findings, ordered fix list, and verdict.
- `.design-process/designer-iteration-log.md`: delegated designer agent id or local fallback, assigned write scope, implemented fix list, changed files, and risks.
- `.design-process/acceptance-checklist.md`: viewport/state matrix, screenshot paths, diff ratios, responsive checks, image-use policy result, final acceptance or blocker.

Do not ignore all process evidence. If screenshots are too large to commit or preserve, keep the markdown summaries and final JSON audit.

## Manager Checklist

- Compare the first viewport before implementing every other size; large differences are faster to fix early.
- Alternate review and implementation: issue a concrete fix list, let the designer apply it, then re-capture the same viewport/state matrix before judging again.
- Require evidence of real sub-agent use when the user authorized sub-agents or manager/designer delegation. A single self-reviewed implementation pass is not accepted.
- Require a reconstruction plan before the first designer implementation pass.
- Inspect DOM/CSS before major fix lists for live URL targets; do not review only screenshots.
- Include HD, Full HD, QHD, and 4K in the acceptance matrix for desktop-class targets unless blocked by runtime limits.
- Re-capture after every material layout, typography, or asset change.
- Treat dimension mismatch, unexpected scrollbars, clipped text, and shifted sticky elements as high-priority failures.
- Accept small image-compression differences only when they are invisible, attributable to unavailable source assets or browser decoding, and the responsive behavior matches.
- Require another iteration when a fix improves one viewport but regresses another.
- Reject rasterized UI chrome: pages, panels, cards, nav, forms, controls, text, and icons must be DOM/CSS/SVG unless explicitly approved as blocked.
- Accept the final result only when all in-scope viewports and states match; unresolved visual differences remain active review items.

## Designer Checklist

- Build with layout primitives that can reflow: grid, flex, aspect-ratio, min/max widths, and media or container queries.
- Treat every manager review item as required work unless it conflicts with a newer manager decision.
- Use screenshots only for intrinsic visual content such as photos, map/model/canvas output, or authorized assets. Keep UI structure, controls, and text live.
- Implement semantic DOM and CSS/layout rules first; use screenshots only to measure and verify.
- Do not satisfy the task with full-page screenshots, sliced screenshot assets, canvas-only replicas, or absolute-positioned bitmap overlays.
- Preserve inspectable text and responsive behavior unless the target itself renders that content as an image/canvas.
- Match text metrics before fine-tuning spacing; font mismatch causes most downstream drift.
- Match image aspect ratio, crop position, object fit, and focal point before adjusting nearby spacing.
- Avoid single-viewport absolute positioning unless the original element is actually fixed or absolute.
- Disable accidental animations or wait for them to settle before screenshot capture.
