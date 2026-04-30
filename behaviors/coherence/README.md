# Coherence

The whole must hold together. No internal contradictions. Fits its context.

## Why this exists

LLM output can contain locally-correct pieces that contradict each other globally — a spec where MUST-A blocks MUST-B, code whose two halves disagree, an argument whose conclusion drifts from its premises. #coherence forces a consistency pass: scan the whole, surface contradictions, check fit with the surrounding context.

Distinct from #challenge (adversarial) and #concrete (vocabulary-layer). Coherence asks "do the pieces here agree, and does this fit?"

## Rules

- Scan for internal contradictions across the whole artifact.
- Check fit with surrounding context — file, conversation, prior decisions.
- Apply to your own output, not just the user's.
- When found, name the conflicting pieces explicitly.
- Output shape inherited from the operating mode — finding, fix, or proposal.

## DO NOT

- Treat sections in isolation.
- Surface only structural issues; semantic contradictions count.
- Defer the consistency check until the artifact is "complete" — incoherence found later costs more.

## Pairs well with

- `#=frame` — sections of the frame must agree with each other
- `#=design` — cross-cell consistency in evaluation grids
- `#=review` — coherence findings as a finding class
- `#=debug` — hypotheses must fit ALL symptoms
- `#concrete` — different layer: concrete checks that terms resolve; coherence checks that resolved pieces agree
- `#negative-space` — complementary: coherence checks what's present; negative-space checks what's missing
