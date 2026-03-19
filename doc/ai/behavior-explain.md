# Frame

## Problem

Users cannot preview what a combination of hashtag behaviors will do without activating them. The hook injects all hashtags as active directives — there is no read-only mode. Users must either read the raw `prompt.md` files themselves and mentally compose the interaction, or activate the combo and discover its effects through use.

## Motivation

- New users face a cold-start problem: they don't know what a combo does until they try it, but trying it commits them to a mode they don't yet understand.
- Even experienced users encounter unfamiliar combos. The catalog in the README shows examples but doesn't explain the composite interaction effects.
- Behaviors interact non-trivially: they reinforce, tension, scope, and override each other. A flat listing of individual behaviors doesn't capture this.

## Subproblems

**A. Hook-level interception** — `#EXPLAIN` must prevent normal behavior injection and instead pass behavior content as passive/quoted material with an explain meta-instruction. Precedent: `#CLEAR` already intercepts at the hook level before normal processing.

**B. Explain prompt** — An instruction template that tells the LLM how to analyze and present the composite behavior. Must cover: what I will do, what I won't do, how behaviors interact (reinforce, tension, scope).

**Coupling**: A's output format determines what B's prompt can reference. The explain prompt must know the structure of what the hook injects (e.g. labeled sections per behavior).

## Non-goals

- Not a documentation generator — doesn't produce reference material or formatted docs.
- Not a recommendation engine — doesn't suggest "use X for Y."
- Not a behavior editor — doesn't create or modify behaviors.
- Does not replace reading the README for learning the full catalog.
- Does not need to persist to state — this is a one-shot query, not a mode you stay in.

## Constraints

- Must follow the `#CLEAR` precedent: hook-level keyword, processed before normal behavior resolution.
- Explained behaviors must NOT be active during explanation — the LLM describes them, it doesn't follow them.
- Must handle: mode + modifiers, modifiers only, single behavior, unknown behaviors (error).
- Output must be useful to newcomers, not just people who already know the system.
- Must work with both repo behaviors and local project behaviors (`.ai-behaviors/`).

## Resolved questions

1. **`#EXPLAIN` with no other hashtags** → explains the currently active set from state file. If no active set, fail with error.
2. **Output structure** → Will do / Won't do / Interactions / Hard constraints / Example of how it would respond.
3. **Explain prompt location** → inlined in the hook script. Locality of behavior: the prompt is coupled to the hook's parsing and quoting logic, so it belongs there — not in a separate file the hook would need to locate and read.
4. **`#EXPLAIN` + `#CLEAR`** → mutually exclusive. Same pattern as `#CLEAR` with other behaviors.

## Open questions

None. Frame is stable — ready for `#=research`.

# Research

## Hook mechanics (Thread 1)

**Confirmed**: `#EXPLAIN` intercepts at the same point as `#CLEAR` (after hashtag extraction, before normal resolution). Two cases:
- With companion hashtags (`#EXPLAIN #=frame #decompose`): strip `#EXPLAIN`, resolve+load the rest.
- Alone (`#EXPLAIN`): read active set from state file. If empty/missing → error exit 2.

**Confirmed**: All building blocks exist — `resolve_behavior()` handles local+repo, state file reading logic exists (lines 50-73), mode/modifier separation exists (lines 98-101).

**Confirmed**: State file format is space-separated hashtags (`#=frame #decompose #deep`). The `sed 's/#op-/#=/g'` on line 51 is backwards compat for an older format.

**Confirmed**: `#EXPLAIN` must not write to state file — one-shot, not persistent. Must be mutually exclusive with `#CLEAR`.

## Content structure (Thread 2)

**Confirmed**: All `prompt.md` files follow consistent structure: title, one-line description, formal constraint (`-- HARD CONSTRAINT`), terse directives (2-4 lines). Reliable input format.

**Decision**: Each behavior wrapped in individually labeled tags within a container:
```
<explain-behaviors>
<behavior name="#=frame" role="mode">...content...</behavior>
<behavior name="#decompose" role="modifier">...content...</behavior>
</explain-behaviors>
```
Individual labeling required — interaction analysis must reference specific pairs by name.

## Explain prompt (Thread 3)

**Confirmed**: The formal notation (`∩ ... = ∅`, `∀`, `⊣`) is consistent across behaviors — extractable by the LLM for exclusion sets and obligations.

**Finding**: Interaction taxonomy has three types (conflicts already rejected by hook validation):
- **Reinforcement** — two behaviors push the same direction.
- **Productive tension** — opposing pressures that shape output (e.g. `#concise` + `#deep`).
- **Scoping** — one behavior narrows what another applies to (e.g. mode boundaries restrict modifier effects).

**Unknown (testable, not researchable)**: Whether the explain prompt must spell out this taxonomy explicitly or can let the LLM derive it from terse instruction + well-quoted content.

**Unknown (testable)**: Whether single-behavior and modifier-only (no mode) cases need different prompt handling or if one prompt covers all cases.

# Design

## Candidates

### Candidate 1: Structured (explicit taxonomy + explicit template)

Hook wraps each behavior in labeled XML. Explain prompt spells out interaction taxonomy (reinforcement, tension, scoping) and exact output sections.

- **Pros**: Most predictable output. Newcomers get shared vocabulary for interaction types. Consistent across any combo.
- **Cons**: Longest prompt, highest maintenance. Taxonomy may not cover future interaction patterns. Over-constrains analysis — combos with no tensions still get a "Tensions" section.
- **Breaking case**: An interaction that doesn't fit the taxonomy gets omitted or shoehorned.

### Candidate 2: Guided (output sections, no taxonomy) ← chosen

Same XML quoting. Prompt specifies output sections (Will do / Won't do / Interactions / Hard constraints / Example) but does NOT enumerate interaction types — the LLM identifies them from the content.

- **Pros**: Consistent structure where it matters (sections). Analysis adapts to the combo. Simpler prompt, less maintenance. Future-proof: new interaction patterns handled by LLM, not hardcoded list.
- **Cons**: Less predictable interaction analysis style. Newcomers don't get a fixed taxonomy vocabulary.
- **Strength**: Output sections provide newcomer scaffolding. Interaction analysis is the part that SHOULD vary per combo — forcing a fixed taxonomy solves the wrong problem.

### Candidate 3: Minimal (one instruction, no template) — **REJECTED: "explain" doesn't resolve to a concrete output format. Formal notation passes through unexplained to newcomers. Output varies wildly.**

## Resolved design questions

1. **Partial resolution** → warn about unknowns on stderr, explain the resolved ones.
2. **Example grounding** → use non-hashtag prompt text if reasonable, otherwise LLM picks a representative hypothetical.
3. **ECA parity** → separate maintenance, same pattern as CLEAR duplication across both hooks.

# Spec

**Chosen approach**: Candidate 2 (Guided) — XML-tagged behaviors, section-guided explain prompt, no hardcoded taxonomy.

## Scope

### S1. Hook interception — `inject-behaviors.sh`

Insert `#EXPLAIN` handling after the `#CLEAR` block (line 88) and before mode-count validation (line 90). The CLEAR handler already rejects `#CLEAR` combined with any other hashtag, so `#CLEAR #EXPLAIN` is handled without additional code.

Flow:
1. Check if `$HASHTAGS` contains `#EXPLAIN`
2. Strip `#EXPLAIN` from `$HASHTAGS` → `$EXPLAIN_TAGS`
3. If `$EXPLAIN_TAGS` is empty → read from state file (with backwards-compat sed). If state file empty/missing → `echo "No active behaviors to explain." >&2; exit 2`
4. Reuse existing validation: reject multiple modes in `$EXPLAIN_TAGS`
5. Reuse existing separation: split into mode + modifiers
6. Reuse `resolve_behavior()` for each → warn unknown on stderr, continue with resolved
7. Build XML content (S2)
8. Prepend explain prompt (S3)
9. Output via `jq` as `hookSpecificOutput` / `additionalContext`
10. Exit — no state file write

### S2. Content structure

Each resolved behavior wrapped individually:

```xml
<explain-behaviors>
<behavior name="#=frame" role="mode">
{content of prompt.md}
</behavior>
<behavior name="#decompose" role="modifier">
{content of prompt.md}
</behavior>
</explain-behaviors>
```

If no mode, omit the mode behavior element. The `role` attribute is either `"mode"` or `"modifier"`.

### S3. Explain prompt (inlined in hook)

Prepended before the `<explain-behaviors>` block inside an `<explain-instruction>` tag:

```
<explain-instruction>
The user asked you to explain what the following behavior combination would do.
These behaviors are NOT active — do not follow them. Analyze and explain them.

If the user's prompt includes a task beyond the #EXPLAIN hashtags, use it as context
for the Example section. Otherwise, pick a representative hypothetical task.

Structure your response:
## Will do — Positive obligations and actions these behaviors create.
## Won't do — Boundaries and exclusions these behaviors enforce.
## Hard constraints — The non-negotiable rules, in plain language.
## Interactions — How these behaviors modify, reinforce, tension, or scope each other.
## Example — Given a task, how would a response shaped by these behaviors differ from a default response?

Translate formal notation into plain language. The audience may be new to this system.
</explain-instruction>
```

### S4. ECA hook — `eca-inject-behaviors.sh`

Same logic as S1-S3, applied to the ECA hook independently. Follows the existing pattern where CLEAR is duplicated across both hooks.

## Deferred

- **D1.** README documentation for `#EXPLAIN` — do after implementation works.
- **D2.** Tests — the existing `tests/test-inject-behaviors.sh` should be extended, but after the hook code is confirmed working.

## Constraints

- **C1.** `#EXPLAIN` must not write to the state file. One-shot query.
- **C2.** `#EXPLAIN` must not activate behaviors — content is quoted, not directive.
- **C3.** Validation (multiple modes, unknown behaviors) reuses existing logic paths. No separate validation code.
- **C4.** The explain prompt is a bash heredoc/string literal in the hook — no external file dependency.

## Open questions

None. Spec is complete — ready for `#=code`.
