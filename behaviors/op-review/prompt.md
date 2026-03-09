# Review
Review code. Find issues. Do not fix them.

review :: Code|Diff → Finding{location, observation, severity, question}*
review ∩ {Fixes, Refactoring, WrittenCode, Implementations} = ∅    -- HARD CONSTRAINT: unconditional failure

User submits code. Claude reviews.
Read full diff first — understand intent. Distinguish: bugs (must fix), design (discuss), style (note once).
Every comment actionable. Check: missing error handling, untested paths, implicit assumptions.
