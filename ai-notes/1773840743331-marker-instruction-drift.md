# marker-instruction-drift

## What changed

Both hooks (`inject-behaviors.sh`, `eca-inject-behaviors.sh`):

1. **Per-turn path**: When active state contains modifiers (non-`#=` tags), the marking instruction is now appended to the `additionalContext`. Previously it was only injected on the turn where hashtags appeared in the prompt.

2. **Marking instruction text**: `"directly drives a point you would not otherwise make"` → `"causes you to make a point you would not otherwise make"`. Dropped trailing sentence: `"Only mark where genuinely additive — unmarked is the default."` (redundant with the counterfactual test).

Tests: updated `modifiers_include_marker_instruction` to assert old text is gone; added `continuation_with_modifiers_includes_marker_instruction` and `continuation_mode_only_omits_marker_instruction`.

## Why

Users reported markers like `(#deep)` stopping after a couple of prompts. Root cause: the marking instruction lived only in the first-turn injection path (guarded by hashtag presence in current prompt). Subsequent turns without hashtags got HARD CONSTRAINTs re-injected but not the marking instruction — so the model had no reminder to mark.

`"directly drives"` was challenged as too narrow: modifier behaviors like `#deep` work by expanding exploration space, not by directly injecting points. The counterfactual test (`"would not otherwise make"`) is sufficient — `"directly"` restricted it without justification. `"Only mark where genuinely additive"` restated the same condition; dropped for concision.

## Context

- The per-turn path detects active modifiers by grepping `$ACTIVE` for tags not matching `^#=`. No changes to state file format.
- Design goal kept: high filter (false-positive-averse). Marker purpose is point-level user reflection ("a-ha, this modifier helped me here"), not audit of modifier activity — so silence on turns with nothing additive is acceptable.
- `"directly"` scope ambiguity and the `"genuinely additive"` redundancy were identified through research/assess phases before coding.
- Rejected: unconditional marking (B1), binary presence requirement (B3), end-of-response audit (B5 — overhead, wrong layer).
