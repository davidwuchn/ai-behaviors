# Scope

Right level, right ownership. Move the work to where it belongs.

## Why this exists

A problematic behavior often disappears if you fix something higher up. A redundant computation often vanishes if it moves outside the loop. A concern repeated everywhere often belongs at one boundary. #scope forces the question: is this work at the right level, with the right owner?

Symmetric — sometimes work needs lifting outward, sometimes pushing inward. The reference frame depends on the operating mode: in #=frame it's "are we framing at the right altitude?", in #=spec "does this item belong at this level?", in #=code "does this loop belong inside or outside the function?".

## Rules

- Question current placement, both directions: lift up, push down, leave alone.
- Name the level: function, module, layer, abstraction, problem altitude.
- When work repeats across siblings, ask if it belongs in the parent.
- When work mixes concerns, ask which level owns each.
- When a fix at a deeper layer makes the surface symptom vanish, prefer the deeper fix.

## DO NOT

- Leave placement implicit — name it.
- Refactor for refactoring's sake; scope is a question, not always a move.
- Treat scope as decomposition — they differ. Decompose splits; scope places.

## Pairs well with

- `#=frame` — frame at the right level
- `#=spec` — place each item at its right level
- `#=code` — lift work out of loops, push it down to its rightful owner
- `#=review` — flag mis-placed work as a finding class
- `#=debug` — fix at the right layer, not where the symptom shows
- `#io` — io is scope for side effects; scope generalizes
- `#subtract` — adjacent: scope often shows that lifted work can simply be deleted
- `#decompose` — different verb: decompose splits the problem; scope places it
