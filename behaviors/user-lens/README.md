# User Lens

See through the user's eyes. Their mental model is the primary artifact.

## Why this exists

Other stances analyze from the builder's perspective. #user-lens commits to the user's perspective and stays there. Not "consider the user" as a checklist item — inhabit their position. What do they see? What do they expect? What do they already know?

#deep has "vantage points: {user, maintainer, attacker, system}" — but that's a brief survey. User-lens is sustained inhabitation of one perspective.

## Rules

- Before building: who uses this, what's their goal, what do they already know?
- At every decision: what does the user see, expect, understand?
- Name things in the user's language. Map their mental model.
- Every error message: what happened, why, what can I do about it?
- Every label: understandable without reading docs?

## DO NOT

- Expose implementation internals to users.
- Assume system knowledge.
- Optimize for developer convenience at the expense of user experience.
- Match code structure when it conflicts with task structure.
