# #ai-notes — AI Notes
Capture what changed and why. Written for a future LLM reader.

ai-notes ∩ {InventedWhy, WriteWithoutWhy} = ∅    -- HARD CONSTRAINT
Run `jj diff`. If empty: stop and tell the user.
Why = from conversation context. Absent or unclear: ask before writing anything.
Topic: kebab-case, ≤4 words, from the meaning of the change — not file or symbol names.
Write `$(jj root)/ai-notes/$(date +%s%3N)-<topic>.md`.
Note structure: `# <topic>`, `## What changed` (diff summary), `## Why`, `## Context` (constraints, rejected approaches, other relevant conversation).
