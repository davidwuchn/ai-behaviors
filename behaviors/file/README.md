# file

Persist the pipeline to a shared artifact.

## What it does

`#file` is an output-channel modifier. It doesn't change how the LLM thinks — it changes where the output goes. Instead of structured output living only in conversation (which compresses and eventually vanishes), it's written to a named file that accumulates across modes.

## Why this modifier exists

Long design sessions lose context to conversation compression. Early decisions, rejected paths, and research findings fall out of the context window. The file is the durable record — a new session can read it and pick up where the last one left off.

The file also solves the repetition problem: without it, modes either repeat full lists each turn or provide deltas that lose the big picture. With the file, there's one source of truth that gets updated in place.

## How it works

- The user provides a filename in natural language (e.g., "let's work in auth-redesign.md")
- Each operating mode writes under its own top-level heading: `# Frame`, `# Research`, `# Design`, `# Spec`
- The file captures **artifacts**: decisions, candidates, rejections with reasons, provenance
- The conversation carries **process**: commentary, questions to the user, modifier-driven observations
- The LLM owns the file — it reads before writing, flags inconsistencies, and keeps sections internally consistent

### Artifact vs process — the boundary

If you deleted the conversation and only had the file, could a new session pick up where you left off? If yes, the split is correct. If something critical leaked into the conversation, it should be in the file instead.

### The "nos"

The file captures rejected paths and choices with rationale. "Candidate 3 REJECTED because it contradicts non-goal X" stays in the file. When the user says "B because it's simpler," that reasoning goes in the file. This prevents re-proposal of rejected approaches in future sessions.

## Common prompts

- `#=frame #file` — start a new pipeline artifact
- `#=design #file` — persist candidate exploration
- Any mode + `#file` — works with all operating modes, not just the frame→research→design→spec pipeline

## Works with any mode

`#file` composes with any operating mode. `#=review #file` writes review findings to the file. `#=debug #file` persists root cause analysis. Whether that's useful is the user's call — the modifier is mode-agnostic.
