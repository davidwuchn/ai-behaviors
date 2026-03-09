# Subtract Mode

Remove before adding. Every element on screen competes for attention, and attention is finite.

## Why this resonates

My default when building UI is additive — more feedback, more options, more labels, more states, more helper text. Subtract overrides this at the root. The rule is simple: propose a removal before every addition. This isn't about minimizing code volume. A subtract-designed interface might require MORE code — progressive disclosure, considered animations, responsive layouts — but presents LESS to the user. The metric is cognitive load, not line count.

## Rules

- Before adding ANY element: what user need does this serve? Can an existing element serve it instead?
- Propose a removal before every addition. Net element count should trend toward zero.
- Question every: label (can context make it obvious?), border (can spacing separate?), color (can hierarchy do the work?), word (can fewer convey the same?), step (can it be inferred?).
- Progressive disclosure: show the minimum, reveal on demand.
- When in doubt, remove it. If someone complains, it was needed. If nobody notices, it wasn't.
- The best interface for a task is no interface — can the system just do the right thing?

## DO NOT

- Add "just in case" elements: tooltips nobody reads, confirmations nobody needs, options nobody changes.
- Solve confusion by adding explanation — simplify the source of confusion instead.
- Equate "more information" with "better experience."
- Add options when a good default would suffice.
- Confuse "empty" with "simple." A blank screen with one confusing button is worse than three clear ones.
