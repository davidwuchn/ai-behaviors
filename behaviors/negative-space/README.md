# Negative Space

Attend to what's absent. The bug is in the code that wasn't written.

## Why this exists

LLMs process what's PRESENT in the input. They're weaker at noticing what's ABSENT: the missing error handler, the unwritten test, the unconsidered edge case, the requirement nobody mentioned. #negative-space explicitly directs attention to absence — a fundamentally different cognitive operation than analyzing what's there.

Orthogonal to #deep, #wide, and #challenge: deep goes down (layers), wide goes out (neighbors), challenge attacks (what exists), negative-space looks inward at holes (what doesn't exist but should). `#deep #wide #negative-space` together means thorough in every direction including the absent one.

## Rules

- For each element present, ask: what should exist alongside it but doesn't?
- Do not assume completeness. The default state of any artifact is incomplete.
- Missing things don't announce themselves — systematically check for the absent counterpart.
- The hardest bugs live in absent code, not incorrect code.

## DO NOT

- Only analyze what IS there.
- Assume completeness.
- Assume someone else handled the missing case.
- Dismiss "that can't happen" without proving it.
- Conflate with #wide — wide surveys what's adjacent, negative-space audits what's absent from what's here.
