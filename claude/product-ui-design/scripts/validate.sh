#!/usr/bin/env bash
# Deterministic validation checks on generated UI output
#
# Usage: validate.sh --output <path> --result <path>
#
# Runs grep/regex checks that don't require LLM judgment.
# These complement the LLM grader by catching issues deterministically.
# "Language is non-deterministic, code is deterministic."

set -euo pipefail

OUTPUT_PATH=""
RESULT_PATH=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --output) OUTPUT_PATH="$2"; shift 2 ;;
    --result) RESULT_PATH="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$OUTPUT_PATH" || -z "$RESULT_PATH" ]]; then
  echo "Usage: validate.sh --output <path> --result <path>" >&2
  exit 1
fi

# Read generated output text
TEXT_FILE="${OUTPUT_PATH%.json}.txt"
if [[ -f "$TEXT_FILE" ]]; then
  CODE="$(cat "$TEXT_FILE")"
else
  CODE="$(cat "$OUTPUT_PATH")"
fi

# Helper: count grep matches safely (returns clean integer)
count() {
  echo "$CODE" | grep -c "$@" 2>/dev/null | tr -d '[:space:]' || echo "0"
}

count_e() {
  echo "$CODE" | grep -cE "$@" 2>/dev/null | tr -d '[:space:]' || echo "0"
}

count_i() {
  echo "$CODE" | grep -ciE "$@" 2>/dev/null | tr -d '[:space:]' || echo "0"
}

# --- Checks ---
CHECKS=()

# 1-1/1-2: Hardcoded Tailwind palette colors
HARDCODED_COLORS="$(echo "$CODE" | grep -oE '(bg|text|border|ring|from|to|via)-(red|green|blue|yellow|orange|purple|pink|emerald|amber|violet|indigo|sky|cyan|teal|lime|rose|fuchsia|zinc|slate|gray|stone|neutral)-(50|100|200|300|400|500|600|700|800|900|950)' | sort -u || true)"
HARDCODED_COUNT="$(echo "$HARDCODED_COLORS" | grep -c '.' 2>/dev/null | tr -d '[:space:]' || echo "0")"
if [[ "$HARDCODED_COUNT" -gt 0 ]]; then
  SAMPLE="$(echo "$HARDCODED_COLORS" | head -5 | tr '\n' ', ' | sed 's/,$//')"
  CHECKS+=("{\"id\":\"v-color-hardcoded\",\"pass\":false,\"detail\":\"${HARDCODED_COUNT} hardcoded palette colors: ${SAMPLE}\"}")
else
  CHECKS+=("{\"id\":\"v-color-hardcoded\",\"pass\":true,\"detail\":\"No hardcoded Tailwind palette colors\"}")
fi

# 1-2: bg-white usage
BG_WHITE="$(count 'bg-white')"
if [[ "$BG_WHITE" -gt 0 ]]; then
  CHECKS+=("{\"id\":\"v-bg-white\",\"pass\":false,\"detail\":\"bg-white used ${BG_WHITE} times (use bg-background or bg-card)\"}")
else
  CHECKS+=("{\"id\":\"v-bg-white\",\"pass\":true,\"detail\":\"No bg-white usage\"}")
fi

# 1-2: dark: prefix
DARK_COUNT="$(echo "$CODE" | grep -oE 'dark:[a-z]+-[a-z]+-[0-9]+' 2>/dev/null | wc -l | tr -d '[:space:]' || echo "0")"
if [[ "$DARK_COUNT" -gt 0 ]]; then
  CHECKS+=("{\"id\":\"v-dark-prefix\",\"pass\":false,\"detail\":\"${DARK_COUNT} dark: color overrides (use semantic tokens)\"}")
else
  CHECKS+=("{\"id\":\"v-dark-prefix\",\"pass\":true,\"detail\":\"No dark: color overrides\"}")
fi

# 3-5: useState for filters without useSearchParams
FILTER_STATE="$(count_i 'useState.*filter|useState.*status|useState.*sort|filter.*useState|status.*useState')"
SEARCH_PARAMS="$(count_i 'useSearchParams|searchParams|nuqs')"
if [[ "$FILTER_STATE" -gt 0 ]] && [[ "$SEARCH_PARAMS" -eq 0 ]]; then
  CHECKS+=("{\"id\":\"v-url-state\",\"pass\":false,\"detail\":\"Filter state in useState without useSearchParams\"}")
elif [[ "$FILTER_STATE" -gt 0 ]] && [[ "$SEARCH_PARAMS" -gt 0 ]]; then
  CHECKS+=("{\"id\":\"v-url-state\",\"pass\":true,\"detail\":\"Filter state uses URL search params\"}")
else
  CHECKS+=("{\"id\":\"v-url-state\",\"pass\":true,\"detail\":\"No filter state detected (N/A)\"}")
fi

# 4-1: Empty state with CTA
EMPTY_STATE="$(count_i 'empty.?state|no .* yet|no .* found|nothing here|get started')"
EMPTY_CTA="$(count_i '<Button|<button|variant=|Create.*first|Get started')"
if [[ "$EMPTY_STATE" -gt 0 ]] && [[ "$EMPTY_CTA" -eq 0 ]]; then
  CHECKS+=("{\"id\":\"v-empty-cta\",\"pass\":false,\"detail\":\"Empty state found but no Button/CTA detected\"}")
else
  CHECKS+=("{\"id\":\"v-empty-cta\",\"pass\":true,\"detail\":\"Empty state has CTA or none present\"}")
fi

# 4-2: Loading state
LOADING="$(count_i 'isLoading|skeleton|Skeleton|Loader2|spinner|Spinner')"
if [[ "$LOADING" -eq 0 ]]; then
  CHECKS+=("{\"id\":\"v-loading-state\",\"pass\":false,\"detail\":\"No loading state detected\"}")
else
  CHECKS+=("{\"id\":\"v-loading-state\",\"pass\":true,\"detail\":\"Loading state present (${LOADING} indicators)\"}")
fi

# 4-2: Error state
ERROR="$(count_i 'isError|error.*retry|error.*state|ErrorBanner|error.*message|onError')"
if [[ "$ERROR" -eq 0 ]]; then
  CHECKS+=("{\"id\":\"v-error-state\",\"pass\":false,\"detail\":\"No error state detected\"}")
else
  CHECKS+=("{\"id\":\"v-error-state\",\"pass\":true,\"detail\":\"Error state present (${ERROR} indicators)\"}")
fi

# Accessibility: clickable div without role/button
CLICK_DIV="$(count_e '<div[^>]*onClick')"
CLICK_DIV_ROLE="$(count_e '<div[^>]*(role|tabIndex)[^>]*onClick|<div[^>]*onClick[^>]*(role|tabIndex)')"
BARE_CLICK=$(( CLICK_DIV - CLICK_DIV_ROLE ))
if [[ "$BARE_CLICK" -gt 0 ]]; then
  CHECKS+=("{\"id\":\"v-clickable-div\",\"pass\":false,\"detail\":\"${BARE_CLICK} clickable divs without role/tabIndex\"}")
else
  CHECKS+=("{\"id\":\"v-clickable-div\",\"pass\":true,\"detail\":\"No bare clickable divs\"}")
fi

# Accessibility: icon-only buttons without aria-label
ICON_BTN="$(count_e 'size=.icon')"
ICON_ARIA="$(count_e 'aria-label')"
if [[ "$ICON_BTN" -gt 0 ]] && [[ "$ICON_ARIA" -eq 0 ]]; then
  CHECKS+=("{\"id\":\"v-icon-aria\",\"pass\":false,\"detail\":\"Icon buttons found without any aria-label\"}")
else
  CHECKS+=("{\"id\":\"v-icon-aria\",\"pass\":true,\"detail\":\"Icon buttons have aria-label or none present\"}")
fi

# Build result JSON
PASS_COUNT=0
FAIL_COUNT=0
for check in "${CHECKS[@]}"; do
  if echo "$check" | grep -q '"pass":true'; then
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

TOTAL=$((PASS_COUNT + FAIL_COUNT))
CHECKS_JSON="$(printf '%s\n' "${CHECKS[@]}" | jq -s '.')"

jq -n \
  --argjson checks "$CHECKS_JSON" \
  --argjson pass_count "$PASS_COUNT" \
  --argjson fail_count "$FAIL_COUNT" \
  --argjson total "$TOTAL" \
  '{
    checks: $checks,
    pass_count: $pass_count,
    fail_count: $fail_count,
    total: $total,
    pass_rate: (if $total > 0 then ($pass_count / $total * 100 | round) else 0 end)
  }' > "$RESULT_PATH"

echo "  Validated: ${PASS_COUNT}/${TOTAL} checks passed (${FAIL_COUNT} failed)"
