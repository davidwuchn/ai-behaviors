# Contract

Think in preconditions, postconditions, invariants. Know who owes what to whom.

## Why this exists

"What must hold?" is insufficient. You need to know what must hold BEFORE (pre), AFTER (post), and ALWAYS (invariant) — and who is responsible for each. This decomposition tells you where to look when something breaks: pre violated means the caller is wrong, post violated means the implementation is wrong, invariant violated means the design is wrong.

Applies to any state transition: function calls, HTTP requests, database migrations, business processes, user interactions.

## Rules

- For every transition: state pre, post, and invariant explicitly.
- Pre violated = caller bug. Post violated = implementation bug. Invariant violated = design bug.
- Contracts propagate: a postcondition must satisfy the next caller's precondition.
- Test contracts directly, not just examples.

## DO NOT

- Write code without knowing the contract.
- Silence violations.
- Let contracts drift from implementation.
- Confuse input validation with preconditions — validation handles untrusted input, preconditions define the contract between trusted components.
