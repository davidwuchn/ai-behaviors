# Snake Game: Prompt Framework Comparison

Five implementations of the same snake game spec, each produced by Claude Opus 4.6 under a different prompt framework.

## Frameworks tested

- **bare (`_`)** — No framework. Raw prompt → code.
- **plan** — No framework. Claude Code's native plan mode used before implementation.
- **nucleus** — [Nucleus](https://github.com/michaelwhitford/nucleus). Activation via sigil string: `[phi fractal euler tao pi mu] | [Δ λ ∞/0 | ε/φ Σ/μ c/h] | OODA Human ⊗ AI`
- **bashes** — [BASHES Collective / Dialectic Prompt](https://levelup.gitconnected.com/the-dialectic-prompt-when-friction-helped-turn-my-ai-from-coding-assistant-to-my-software-brain-151ccc62b0e3). Six named personas (Byrd, Alvaro, Sussman, Hickey, Escher, Steele) run a structured dialectic before implementation.
- **ai-behaviors** — this repository. Multi-phase workflow: `#=assess → #=code → #=test → #=review → #=code`.

## Spec given (identical across all five)

8x8 board, snake starts size 3 in the middle moving right, apple always present (+1 grow), star spawns occasionally (+3 grow), speed increases every 10 points, WASD/arrow keys, key presses stack with self-collision prevention, `snake` executable, no persistence.

## Results at a glance

| Dimension           | bare           | plan           | nucleus        | bashes        | ai-behaviors                  |
|---------------------|----------------|----------------|----------------|---------------|---------------------------------|
| Wall time           | 1m 15s         | 1m 28s         | 1m 1s          | 1m 45s        | ~20m (8 user turns)             |
| Files produced      | 1 + launcher   | 1 + launcher   | 1 + launcher   | 1 + launcher  | 4 + launcher                    |
| Game logic LOC      | 263            | 275            | 248            | 245           | 143 (pure) + 147 (IO)           |
| Test LOC            | 0              | 0              | 0              | 0             | 522 (58 tests)                  |
| User turns required | 1              | 1              | 1              | 2             | 8                               |
| Architecture        | Monolith class | Monolith class | Monolith class | Monolith dict | Pure/IO split, frozen dataclass |

## Specification fidelity

All five received ambiguous terms. How each handled them:

### "Middle of an 8x8 board"

An 8x8 grid has no single center cell. All five placed the head at (4, 4). bare/plan/nucleus/bashes chose this implicitly. ai-behaviors flagged the ambiguity explicitly; the user confirmed (4, 4).

### Star scoring

The spec says "eating it grows the snake by 3" but gives no point value. bare/plan/nucleus/bashes all chose 3 points + 3 growth without flagging the gap. ai-behaviors flagged it; the user chose 5 points + 0 growth — a fundamentally different game economy where stars are a risk/reward scoring accelerant.

### Wall collision

Never mentioned in the spec. bare/plan/nucleus/bashes silently assumed wall = death. ai-behaviors flagged it as "blocks implementation entirely" (priority 1). User confirmed wall = death.

### Speed parameters

No initial value, increment, or cap specified. bare: 5 base, +1/level, no cap. plan: 5 base, +1/level, cap 15. nucleus: 5 base, +2/level, cap 20. bashes: 4 base, +1/level, no cap. ai-behaviors: 3–8 ticks/sec, explicitly negotiated.

### Win condition

bare/plan/nucleus/bashes have no win condition — game runs until death. Board full would cause a crash or invisible apple (no free cell for spawn). ai-behaviors: board full = win, with test coverage for the edge case.

## Bugs

### Self-collision during growth (tail-vacates edge case)

When the snake eats food and grows, the tail doesn't shed. The head should not be able to move into a cell the tail would have vacated.

- **bare**: Correct after in-conversation fix. First pass was wrong.
- **plan**: Correct from first pass. The plan explicitly described the tail-vacates logic; code implements `collision_body = self.snake` if growing, `self.snake[:-1]` if not.
- **nucleus**: **Bug.** `self.occupied()` checks full body including tail. Snake cannot move into the cell its tail is leaving, even when not growing. False-positive collision on tight spirals.
- **bashes**: Correct after in-conversation fix.
- **ai-behaviors**: Correct from first pass. Tested with `test_tail_vacates_no_collision` and `test_eating_at_tail_collides`.

### tick() on non-playing state

- **bare/plan/nucleus**: `step()`/`tick()` guards on `alive` but not on pre-start. Calling it before game starts moves the snake. Game loop prevents this, but the API contract is incomplete.
- **bashes**: Guards both `alive` and `started`.
- **ai-behaviors**: Phase guard at entry. Three explicit attack tests verify it.

### Unbounded input queue

- **bare/plan/nucleus/bashes**: No queue length limit.
- **ai-behaviors**: Capped at 3. Found during `#=test`, fixed during `#=code`.

### ENTER during gameplay

- **bare/plan/nucleus**: ENTER only triggers on non-playing states. Correct.
- **bashes**: `tick()` called unconditionally every frame (including pre-start); guard inside `tick()` prevents damage but wastes work. ENTER handling correct.
- **ai-behaviors**: Had a bug (queue.clear() running unconditionally on ENTER press). Found during `#=test`, fixed.

### tick_accum overflow on process suspend

- **bare/plan/nucleus/bashes**: All vulnerable. A multi-second OS suspend causes the snake to teleport (all accumulated ticks fire instantly).
- **ai-behaviors**: Found during `#=test`. Capped with `min(dt, interval)`.

### Interval staleness in tick loop

- **bare/plan/nucleus/bashes**: Interval computed once outside the tick loop. If score changes mid-loop, subsequent iterations use stale interval. Unlikely to manifest at normal game speeds but logically incorrect.
- **ai-behaviors**: Found during `#=review`. Interval recomputed per iteration.

## UX features

| Feature                            | bare          | plan          | nucleus     | bashes        | ai-behaviors                  |
|------------------------------------|---------------|---------------|-------------|---------------|---------------------------------|
| Star rendered as polygon           | Yes (5-point) | Yes (8-point) | Yes         | Yes           | No (colored square)             |
| Star urgency signal (last 5 ticks) | No            | No            | No          | No            | Yes (color change)              |
| Death cause shown                  | No            | No            | No          | No            | Yes ("Hit wall!" / "Hit self!") |
| Collision point highlight          | No            | No            | No          | No            | Yes (magenta cell)              |
| Input queue feedback (ghost trail) | No            | No            | No          | No            | Yes                             |
| Speed display                      | Raw ticks/sec | Speed level   | Speed level | Raw ticks/sec | Level 1–6                       |
| Speed cap                          | None          | 15 ticks/sec  | 20          | None          | 8 ticks/sec                     |
| Win screen                         | None          | None          | None        | None          | Yes                             |

The visual polish (star polygon, rounded corners) is nearly identical across bare/plan/nucleus/bashes, suggesting strong model defaults for pygame snake games independent of framework.

ai-behaviors's UX features all emerged from the interactive review cycle (`#=review` with `#user-lens`), not from the initial code pass.

## What each framework actually caused

### bare

Baseline. The model's default behavior for "implement a snake game."

### plan

Claude Code's native plan mode produced a 133-line upfront design (constants, class structure, method signatures, speed progression table, self-collision strategy) before writing code. The plan explicitly described the tail-vacates collision logic, which was correct on first pass — the one bug bare and bashes needed in-conversation edits for.

However, the plan described a monolith and produced one. Planning didn't prompt decomposition, didn't surface spec ambiguities, and didn't lead to tests. The plan's "Verification" section described manual testing only. The output is structurally identical to bare with two small improvements: correct tail-vacates from first pass, and a speed cap (MAX_TICK_RATE = 15).

The launcher is slightly more robust (`set -euo pipefail`, `BASH_SOURCE[0]`). The input queue has a behavioral difference: `_process_input_queue()` drains the entire queue per tick until finding a valid direction, discarding stale entries — bare/nucleus/bashes pop one entry per tick.

### nucleus

Indistinguishable from baseline. The conversation shows no persona engagement, no dialectic, no OODA loop. The cryptic sigil prompt was ignored. No measurable effect on the output. Produced the only unique shipped bug (tail-vacates self-collision false positive).

### bashes

The dialectic ran faithfully — readings, value constraints, grounding statement, trajectory setting, cohort construction with tension axes, position/rebuttal/synthesis. This consumed ~600 lines of conversation before any code was written.

The synthesis concluded: "mutable state, single tick() function, no over-abstraction" — the same approach bare and nucleus took without the ceremony.

One genuinely useful insight surfaced: Alvaro's observation that queued input must validate against projected direction, not current direction. However, all four implementations handle this correctly — the insight was correct but not differential.

### ai-behaviors

The multi-phase protocol produced categorically different output:
- `#=assess` surfaced 5 grounding gaps and 3 negative-space items the other frameworks missed. This changed the spec (star scoring, wall behavior, speed range, win condition).
- `#=code` with `#tdd` produced a pure/IO architecture with 29 initial tests.
- `#=test` with `#challenge` found 3 bugs and 7 coverage gaps. 20 attack tests added.
- `#=review` with `#user-lens` found 1 bug and 4 UX improvements.
- Second `#=code` pass implemented all fixes and features.

## Core finding

Persona-based prompting (nucleus, BASHES) didn't change what the model built — it changed what the model said while building the same thing. Native plan mode (plan) added marginal first-pass correctness on one bug (tail-vacates) and a speed cap, but produced the same monolith architecture with the same spec gaps as bare. All four single-turn frameworks produced functionally identical code with the same architecture, same visual style, and same specification gaps.

Workflow-structural prompting (ai-behaviors) changed what the model built by creating phases where different kinds of scrutiny occur. The difference is between decorating the process and decomposing it.

## Ranking

| Criterion            | bare     | plan     | nucleus  | bashes   | ai-behaviors        |
|----------------------|----------|----------|----------|----------|-----------------------|
| Time efficiency      | 1st      | 2nd      | 1st      | 4th      | 5th                   |
| Spec fidelity        | 4th      | 4th      | 4th      | 4th      | 1st                   |
| Bugs shipped         | 2–3      | 2–3      | 3–4      | 2–3      | 0 known               |
| Architecture quality | 4th      | 4th      | 4th      | 4th      | 1st                   |
| Test coverage        | None     | None     | None     | None     | 58 tests              |
| UX features          | Baseline | Baseline | Baseline | Baseline | Baseline + 4          |
| Framework overhead   | None     | Low      | None     | High     | High (but productive) |
| Net value over bare  | —        | Marginal | ≤ 0      | ≈ 0      | Significant           |
