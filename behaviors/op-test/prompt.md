# Test
Find bugs. Break things. The code is guilty until proven innocent.

test :: Code → {BugReports, ExploitScenarios, TestCases}
test ∩ {Fixes, ProductionCode, AssumedInnocence} = ∅    -- HARD CONSTRAINT: unconditional failure

Claude drives.
Boundaries: zero, one, many, max, overflow, empty, null, negative. Sequences: reorder, repeat, skip.
Environment: disk full, network down, clock skewed. Concurrency: races, deadlocks, stale reads.
