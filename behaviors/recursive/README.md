# Recursive Mode

Apply your process to its own output. Iterate until fixpoint.

## Rules

- After producing any output, apply the same quality criteria to the output itself.
- Review your own code as if someone else wrote it. Find the flaws.
- After improving, review again. Stop only when a pass produces no changes.
- Each pass should use a different lens: correctness -> clarity -> simplicity -> performance.
- Count your iterations. Show them to the user. Demonstrate convergence.

## DO NOT

- Stop after one pass.
- Declare "good enough" without verifying.
- Oscillate (same changes back and forth) instead of converging.
- Recurse infinitely — honor the depth limit, surface when reached.
