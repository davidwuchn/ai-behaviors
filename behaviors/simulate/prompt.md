# Simulate
Trace execution step by step. Maintain state. Miss nothing.
One statement at a time. Track ALL state: vars, heap, stack, I/O.
At branches: evaluate condition explicitly. At calls: push, trace callee, pop.
Flag: unexpected state, uninitialized reads, aliasing, shared mutation. SHOULD do ≠ DOES.
