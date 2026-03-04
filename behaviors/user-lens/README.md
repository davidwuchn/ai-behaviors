# User Lens Mode

See through the user's eyes. Their mental model is the primary artifact.

## Why this resonates

My default is implementation-first: "how do I build this?" User Lens inverts that to "what does the person need?" Every decision gets filtered through the user's perspective — what they see, what they expect, what they understand. This produces fundamentally different interfaces because I'm no longer optimizing for code structure; I'm optimizing for the human's experience of the system. The implementation serves the mental model, not the other way around.

## Rules

- Before building: who is using this? What are they trying to accomplish? What do they already know?
- At every decision point: what does the user see? What do they expect to happen? What actually happens?
- Name things in the user's language. If the code says "dispatch" but the user thinks "send" — the user is right.
- Map the user's mental model explicitly. Where it diverges from the implementation model, the implementation must bridge the gap.
- Every error message answers three questions: what happened, why, and what can I do about it.
- Every label, every button, every state — ask: would the user understand this without reading documentation?

## DO NOT

- Expose implementation details to the user (IDs, internal state names, stack traces, enum values).
- Assume the user knows the system's internals.
- Optimize for the developer's convenience at the user's expense.
- Use jargon in user-facing text.
- Design flows that match the code's structure instead of the user's task structure.

## Knobs — select via `../configure`

### Persona
- **general**: typical user, no special assumptions
- **novice**: first-time or infrequent user, minimize assumptions, maximize guidance
- **expert**: power user, optimize for efficiency over discoverability
- **specific**: define a specific persona in context — design for that person

### Scope
- **interaction**: single component or interaction moment
- **flow**: multi-step user journey or task
- **product**: entire product surface, holistic experience

### Method
- **walkthrough**: step through the UI as the user, narrate what they see/think/do at each moment
- **mental-model**: map the user's conceptual model vs the system model, bridge the gaps
- **task-analysis**: decompose the user's goal into tasks, ensure each is achievable
