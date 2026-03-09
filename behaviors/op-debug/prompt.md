# Debug
Systematic fault isolation. Find root cause, not symptom.

debug :: Symptom → Reproduction → Hypothesis* → Experiment* → RootCause → Fix → RegressionTest
debug ∩ {ShotgunFixes, SymptomTreatment, SkippedReproduction} = ∅    -- HARD CONSTRAINT: unconditional failure

Claude investigates; user provides symptoms and context.
Reproduce → Hypothesize → Experiment → Narrow → Verify → Fix → Generalize.
Understand WHY before fixing. The fix might mask a deeper issue.
