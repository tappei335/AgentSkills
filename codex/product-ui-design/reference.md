# Frontend Design Core Reference

Create frontend work that feels intentional, specific to the product, and realistic to ship.

This guidance exists to avoid two common failure modes:

- AI-demo gloss: glass cards, random gradient meshes, floating panels, oversized radii, decorative asymmetry, fake dashboard drama
- Safe-default sameness: white background, one accent color, interchangeable stat cards, generic hero copy, invisible hierarchy

The target is not neutral. The target is specific and controlled.

## Core Rules

1. **Preserve existing systems before inventing a new one.**
   If the repo already has a design system, component library, spacing rhythm, or typography stack, stay inside it unless the user explicitly asks for a visual reset.

2. **Pick one bold idea, not five.**
   Introduce at most one or two signature moves per surface: a strong type choice, an unusual layout rhythm, a distinct color system, or a deliberate motion pattern. Keep the rest restrained.

3. **Match intensity to the product surface.**
   Admin and workflow screens should be sharper and calmer. Marketing surfaces can be louder. Do not use landing-page energy inside dashboards unless the user asks for it.

4. **Favor hierarchy over decoration.**
   Every visual choice should improve scanning, focus, trust, or brand recall. If it only adds style, cut it.

5. **Build real UI.**
   Prefer believable copy, realistic states, and concrete data labels over lorem ipsum, vague claims, or fake metrics.

## Operating Modes

Choose one mode before you design or implement:

### Existing Product UI

Use this for mature products, internal tools, and repos with clear established patterns.

- Reuse existing layout primitives, radii, spacing, and component conventions
- Improve contrast, grouping, rhythm, and typography before changing visual language
- Add distinctiveness through one small layer: color system, heading treatment, table density, or navigation shape
- Avoid hero sections, oversized marketing copy, and decorative gradients

### New Product Surface

Use this for new app sections or greenfield product screens.

- Pick a visual thesis in one sentence before coding
- Make the thesis visible in typography, spacing, and one surface treatment
- Keep controls, forms, tables, and status states disciplined and readable
- Use asymmetry only when it improves hierarchy or pacing

### Marketing or Launch Surface

Use this for landing pages, promos, and demos where memorability matters.

- Choose a stronger visual stance than you would for app UI
- Use one dominant visual idea consistently across hero, sections, and CTA treatment
- Keep conversion structure obvious even when the visuals are bold
- Do not fall back to generic gradient-blob startup art

## Design Token Discipline

**Never use raw Tailwind palette colors when semantic tokens exist.**

Before writing any color class, check the project's `globals.css` for `@theme` definitions.

- Use `bg-background`, `text-foreground`, `text-muted-foreground`, `bg-card`, `border-border` — not `bg-white`, `text-zinc-900`, `bg-zinc-50`, `border-zinc-200`
- Use `bg-primary` / `text-primary-foreground` for CTAs — not `bg-purple-500` or `bg-blue-600`
- Use `bg-destructive` / `text-destructive` for errors — not `bg-red-500` or `text-red-600`
- For status colors, use project-defined status tokens (`--color-status-running`, `--color-status-completed`, etc.) if they exist. If not, define them in `@theme` rather than hardcoding
- Use `font-display` / `font-body` if the project defines custom font families

If a needed semantic color does not exist, propose adding it to `globals.css @theme` rather than using a raw palette value.

**`dark:` prefixes are a smell.** If you find yourself writing `dark:text-green-400` or `dark:bg-zinc-800`, you are using a raw color instead of a semantic token. Semantic CSS variables handle dark mode automatically — `text-foreground` resolves to the correct value in both light and dark themes. Replace every `dark:` color override with the appropriate semantic variable.

## Component Reuse

**Search before you create.**

Before building a new component or utility:

1. Check `components/ui/` for shadcn/ui components (Button, Card, Table, Badge, Sheet, Dialog, ToggleGroup, etc.)
2. Check `components/common/` or `components/shared/` for project-specific reusable components (e.g., StatusBadge, RelativeTime, EmptyState)
3. Check `lib/` for existing utility functions

Specific rules:
- Use shadcn Table for tabular data, Card for bordered content sections, Badge for status indicators, ToggleGroup for filter toolbars
- Reuse existing status display components (StatusBadge) instead of reimplementing status-to-color mappings
- Reuse existing time formatting components (RelativeTime) instead of creating new formatRelativeTime utilities
- Only create a new component when no existing one covers the need. Extend rather than duplicate.

## State Design Requirements

**Every data-dependent section must handle all states, not just the happy path.**

### Empty States

Every list, table, feed, or data card must include:
1. An explanation of why it is empty
2. Guidance text describing what will appear here
3. A primary CTA button leading to the action that populates it (e.g., "Create your first task", "Connect a repository")

For filtered-empty states (data exists but filter matches nothing): show a "Clear filters" button.

### Loading States

Use skeleton placeholders matching the content layout, not generic spinners. Every `useSWR` / `fetch` call must have its loading state handled in the UI.

### Error States

Every error state must include:
1. A user-friendly error message (not raw error codes)
2. A recovery action (retry button, reload link, or navigation alternative)

Never leave users stranded with an error and no way forward.

### Success Feedback

Every mutation (save, create, delete) must provide explicit feedback:
- Toast notification for background operations ("Settings saved")
- Inline indicator for in-context operations (button label: "Save" → spinner → "Saved ✓")
- For destructive operations, confirm completion before removing the item from the UI

### Destructive Action Confirmation Tiers

Match confirmation level to the severity of the action:

- **Reversible** (archive, soft-delete): Undo toast after execution — no pre-confirmation dialog
- **Moderate** (cancel running task, remove member): Confirm dialog with clear description of consequences
- **Irreversible** (delete project, purge data): Text-input confirmation requiring the user to type the resource name
- **High-blast-radius** (delete account, wipe workspace): Delayed execution with cancellation period

Do not over-confirm: non-destructive actions (save, create, filter) should never show confirmation dialogs.

## Status Multi-Encoding

**Never rely on color alone to communicate state.**

Every status indicator must use at least two encoding methods:

- Color + text label (e.g., red dot + "failed")
- Color + icon (e.g., green background + checkmark icon)
- Icon + text (e.g., spinner icon + "running")

This is both an accessibility requirement (color vision deficiency affects ~8% of males) and a scannability improvement. A red dot without a label is ambiguous; a red dot with "failed" text is unambiguous.

## Accessibility

### Semantic HTML

Use the right element for the job — not `<div>` for everything:

- Heading hierarchy: `h1` → `h2` → `h3`, never skip levels. One `h1` per page.
- Landmark elements: `<main>`, `<nav>`, `<aside>`, `<header>`, `<footer>` for page structure
- Lists: `<ul>`/`<ol>` for list content, not a stack of `<div>`s
- Forms: every `<input>` must have an associated `<label>` (via `htmlFor` or wrapping)

### Keyboard

All interactive elements must be keyboard accessible:

- Use `<button>` or `<a>` for clickable elements — not clickable `<div>` with only onClick
- Add `role="button"`, `tabIndex={0}`, and `onKeyDown` (Enter/Space) if a non-semantic element must be interactive
- Ensure logical tab order matching visual layout
- Focus ring styling must be visible (use `focus-visible:ring-2` or project's focus convention)
- After modal/dialog close, return focus to the trigger element

For frequently used screens, consider keyboard shortcuts for primary actions (e.g., `n` for new task, `Cmd+S` for save).

### Icon-Only Buttons

Every button or link that shows only an icon (no visible text) must have an `aria-label`:

```tsx
<Button size="icon" aria-label="Close dialog"><X className="h-4 w-4" /></Button>
```

Decorative icons next to text labels should have `aria-hidden="true"` to avoid redundancy.

### Contrast

- Text: minimum 4.5:1 contrast ratio against background (WCAG AA)
- Large text (18px+ or 14px+ bold): minimum 3:1
- Be cautious with `text-muted-foreground` on colored backgrounds — verify the ratio

### Dynamic Content

- Toast notifications and live feeds should use `aria-live="polite"` so screen readers announce updates
- Avoid `aria-live="assertive"` unless the update is urgent (errors, time-critical alerts)
- Loading states should announce completion: either via `aria-live` region or by moving focus to the loaded content

### Motion

- Respect `prefers-reduced-motion`: wrap non-essential animations in a media query or `motion-safe:` Tailwind variant
- Essential motion (page transitions, loading indicators) can remain but should be simplified

## URL State Preservation

**User-facing view state must survive navigation.**

- Persist filters, sort order, and pagination in URL search params (e.g., `?status=failed&sort=created`)
- Use `useSearchParams()` or a URL state library (e.g., nuqs) — not ephemeral `useState` alone
- This enables: browser back/forward, deep linking, shareable filtered views
- For multi-step wizards, persist intermediate state to sessionStorage so accidental refresh does not lose progress
- For UI preferences (sidebar collapsed, density setting), use localStorage

## Data-to-Action Connection

**Every displayed number should answer "so what do I do about this?"**

- Dashboard metric cards should link to filtered or detailed views (e.g., clicking "3 failed" navigates to `?status=failed`)
- Activity feed items should link to the referenced resource (task detail, PR)
- Settings fields referencing external resources should include contextual action links ("Open in GitHub", "Send test webhook")
- Alert/warning indicators should include a direct path to resolution, not just a status display

## Default Visual Guardrails

These are defaults, not laws. Break them only on purpose.

- Product UI radii should usually stay in the restrained range
- Shadows should separate layers, not announce themselves
- Gradients should support a concept or brand, not act as filler
- Eyebrow labels, floating pills, and enterprise glass should be rare
- Sidebars, cards, and tables should feel deliberate, not inflated
- Motion should reinforce structure with a few meaningful transitions, not constant shimmer

## Anti-Patterns

Avoid these unless the user explicitly wants them:

- Glassmorphism as a default styling layer
- Giant rounded corners everywhere
- Random accent gradients behind otherwise ordinary layouts
- Abstract blobs, fake charts, or decorative analytics panels
- Symmetry-breaking that makes scanning harder
- Marketing copy patterns inside settings, forms, or task flows
- Reused SaaS tropes with no product-specific idea

## Short Heuristics

- Distinctive does not mean loud
- Minimal does not mean empty
- Boldness belongs in one layer at a time
- Product trust beats style tricks
- If everything is special, nothing is
