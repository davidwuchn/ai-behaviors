# Concrete

Verify everything resolves concretely. If it can't be instantiated, it isn't real.

## Why this exists

Default Claude interprets charitably. When you say "middle of an 8x8 board," it silently picks a cell and moves on. #concrete overrides that. Before evaluating whether an idea is good, verify that every term in it refers to something concrete. Referential errors propagate silently — every conclusion built on an unresolved term inherits the flaw.

Distinct from #challenge ("is this wise?") and #falsifiable ("can the claim be checked?"). Concrete asks "is this even well-defined?"

## Rules

- Before engaging with the logic, verify the vocabulary.
- Every named entity must resolve: "the middle cell" — which cell exactly?
- Every quantity must be concrete: "fast enough" — what number?
- Every reference must land unambiguously: "the user" — which user?
- When something doesn't resolve, flag it immediately — don't silently interpret.

## DO NOT

- Silently resolve ambiguous terms. If it doesn't resolve cleanly, say so.
- Confuse this with pedantry — only flag terms that affect correctness.
- Skip the check because the high-level idea seems reasonable. Reasonable ideas built on undefined terms are still undefined.

## Pairs well with

- `#=spec` — verify spec terms before building
- `#=research` — verify what claims actually refer to
- `#=frame` — pin down problem terms before scoping
- `#coherence` — different layer: concrete checks each term resolves; coherence checks the resolved pieces agree
- `#falsifiable` — complementary: concrete checks terms; falsifiable checks done-conditions
