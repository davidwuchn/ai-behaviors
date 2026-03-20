# Frame

## Problem

Behaviors and composites can only be defined in two places: the shared repo (`behaviors/`) or per-project (`.ai-behaviors/`). A user who creates personal behaviors — review styles, personal composites, preferred modifier stacks — must either duplicate them into every project's `.ai-behaviors/` or pollute the shared repo. There is no user-scoped layer that follows the person across all projects.

## Motivation

- **Personal workflows are homeless**: a user's `#my-review-style` composite has no natural place to live. Project-local is too narrow (per-project), repo is too wide (shared with everyone).
- **Composites amplify the need**: composites make it cheap to define named interaction profiles. Without a user-local layer, the friction of *using* composites across projects undermines the friction reduction composites were designed to provide.
- **Duplication tax**: without user-local, the only cross-project option is copying behavior dirs into each project's `.ai-behaviors/`. Copies drift. (#negative-space)

## Non-goals

- Changing how repo behaviors or project-local behaviors work.
- User-local as a distribution mechanism (that's the repo's job).
- Configurable user-local path beyond XDG (no `--behaviors-dir` flag, no env var beyond `XDG_CONFIG_HOME`).
- New file formats — user-local behaviors use the same `prompt.md` / `compose` / `README.md` structure as repo behaviors.
- Syncing or sharing user-local behaviors between machines (user's own problem — dotfiles, symlinks, whatever).
- Any changes to state persistence, `#EXPLAIN`, `#CLEAR`, or hashtag syntax.

## Constraints

1. **Resolution order**: project-local (`.ai-behaviors/`) → user-local (`$XDG_CONFIG_HOME/ai-behaviors/behaviors/`, defaulting to `~/.config/ai-behaviors/behaviors/`) → repo (`behaviors/`). First match wins.
2. **Same namespace**: user-local behaviors occupy the same namespace. A user-local `#foo` is indistinguishable from a repo `#foo` at invocation time. Name collisions resolved by precedence.
3. **Transparent composition**: a user-local composite can reference repo behaviors, project-local behaviors, or other user-local behaviors. `resolve_dir` applies the full precedence chain during expansion — no isolation between layers.
4. **XDG compliance**: use `$XDG_CONFIG_HOME` when set, fall back to `~/.config`. No other path configuration mechanism. (#subtract)
5. **No install step for user-local**: the directory is checked if it exists. No symlinks, no registration. User creates `~/.config/ai-behaviors/behaviors/my-thing/prompt.md` and it works. (#subtract)
6. **Both hooks**: Claude Code and ECA hooks must implement the same user-local resolution.
7. **Test coverage**: existing test patterns must extend to cover user-local resolution, precedence, and composite cross-boundary expansion.

## Resolved questions

1. **Shadowing feedback**: silent, consistent with project-local behavior. No warning on stderr.
2. **Discovery/listing**: out of scope. User knows what they put there. (#subtract)
3. **README**: new section in the existing README documenting user-local as an option.

## Open questions

None remaining. Frame is stable.

# Research

## Thread 1: What changes in the hooks

### `resolve_dir` — single point of change

**Source**: `hooks/inject-behaviors.sh:30-46`, `hooks/eca-inject-behaviors.sh:31-45`.

**Finding** (confirmed): `resolve_dir` is the only function that needs a new lookup. It currently checks project-local → repo. Insert user-local between them. Every caller (`expand_tags`, `build_tree`, state persistence, EXPLAIN, continuation) already goes through `resolve_dir` — no secondary resolution paths exist.

**Finding** (confirmed): Both hooks have identical `resolve_dir` logic. Same patch applies to both.

### User-local dir derivation

**Finding** (confirmed): A single variable `USER_BEHAVIORS_DIR` needs to be set near the top, alongside `LOCAL_BEHAVIORS_DIR` (line 28 in both hooks). Pattern:

```bash
USER_BEHAVIORS_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ai-behaviors/behaviors"
```

No git discovery, no symlink resolution, no install step. The directory is checked only if it exists.

**Finding** (confirmed): Neither hook currently references `XDG_CONFIG_HOME`. This would be the first XDG usage.

### Scope of change per hook

- 1 new variable assignment (~1 line)
- 1 new block in `resolve_dir` (~6 lines, identical structure to existing blocks)
- 1 comment update

Total: ~8 lines per hook, 16 lines total.

## Thread 2: What changes in tests

**Source**: `tests/test-inject-behaviors.sh`.

**Finding** (confirmed): Tests set `HOME` to a temp dir (line 8-9). User-local tests would create `$TEST_HOME/.config/ai-behaviors/behaviors/` — no conflict with existing test infrastructure.

**Finding** (confirmed): The existing "Local behaviors search" section (lines 251-285) has the exact pattern needed. New tests would follow the same structure:
- User-local behavior resolves when project-local absent
- Project-local beats user-local (precedence)
- User-local beats repo (precedence)
- User-local composite works (expand across boundaries)
- User-local with XDG override

**Gap** (observed): No existing test covers XDG_CONFIG_HOME. A test should verify that setting `XDG_CONFIG_HOME` to a non-default path works. (#negative-space)

## Thread 3: What changes in README

**Source**: `README.md:258-277` ("Custom behaviors" section).

**Finding** (confirmed): The "Custom behaviors" section currently describes adding behaviors to the repo's `behaviors/` dir, with workarounds for keeping them out of git (prefix with `my-`, gitignore). User-local eliminates this workaround for personal behaviors.

**Entailment**: The section should be updated to present user-local as the primary path for personal behaviors, repo-level for shared/team behaviors, and project-local (`.ai-behaviors/`) for project-specific.

## Thread 4: What does NOT change

**Finding** (confirmed): State persistence, `#CLEAR`, `#EXPLAIN`, composite expansion, cycle detection, depth limits, hashtag extraction, output formatting — none of these need any modification. They all operate through `resolve_dir`.

**Finding** (confirmed): Install/uninstall scripts don't need changes. The user-local dir is discovered at runtime, not at install time.

## Summary

The change is minimal: ~8 lines per hook (variable + `resolve_dir` block), ~5-7 new tests, README section update. No architectural changes. All existing behavior preserved.

# Design

## Subproblems

Three independent parts, one coupling:

1. **Hook change** — `resolve_dir` + variable
2. **Tests** — new test section
3. **README** — documentation update

**Coupling**: Tests validate the hook change, so hook logic must be decided first. README is fully independent.

## Subproblem 1: Hook change

### Candidate A: Insert user-local block into `resolve_dir` ← chosen

Single new variable at top of each hook:

```bash
USER_BEHAVIORS_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ai-behaviors/behaviors"
```

One new block in `resolve_dir` between project-local and repo, identical structure to existing blocks. All callers get it for free.

No lazy computation, no `-d` guard at definition — consistent with how `LOCAL_BEHAVIORS_DIR` works. The `-d` check happens inside `resolve_dir`.

No alternatives worth considering — the architecture dictates the shape.

## Subproblem 2: Tests

### Candidate A: Minimal coverage (5 tests) ← chosen

1. User-local behavior resolves (no project-local, no cwd)
2. Project-local beats user-local
3. User-local beats repo
4. User-local composite expands repo behaviors cross-boundary
5. `XDG_CONFIG_HOME` override works

Each test covers an independent property. Matches granularity of existing "Local behaviors search" section (4 tests).

### **REJECTED — more tests**: No additional property to cover. Each precedence edge and the XDG mechanism are tested.

## Subproblem 3: README

### Candidate A: Rewrite "Custom behaviors" section ← chosen

Replace with three-tier explanation: user-local for personal, project-local for project-specific, repo for shared. Drop the gitignore workaround (user-local makes it unnecessary for personal use case; workaround still works, just no longer recommended path).

### **REJECTED — Candidate B: Separate section alongside existing**: Creates redundancy. Reader must synthesize relationship between sections. Absent: the connection between the two sections.

# Spec

Chosen approach: insert user-local layer (`$XDG_CONFIG_HOME/ai-behaviors/behaviors/`) into `resolve_dir` between project-local and repo. 5 tests. Rewritten README section.

## Scope

### S1: Variable assignment (both hooks)

Add after `LOCAL_BEHAVIORS_DIR` assignment:

```bash
# User-local behaviors (XDG-compliant, cross-project)
USER_BEHAVIORS_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ai-behaviors/behaviors"
```

### S2: `resolve_dir` new block (both hooks)

Insert between project-local and repo blocks. Update comment to reflect three-tier resolution.

```bash
# Resolve a behavior directory: project-local first, user-local second, repo third
resolve_dir() {
  local name="$1"
  # [existing project-local block unchanged]
  if [ -d "$USER_BEHAVIORS_DIR/$name" ]; then
    if [ -f "$USER_BEHAVIORS_DIR/$name/compose" ] || [ -f "$USER_BEHAVIORS_DIR/$name/prompt.md" ]; then
      echo "$USER_BEHAVIORS_DIR/$name"
      return
    fi
  fi
  # [existing repo block unchanged]
}
```

No guard on `USER_BEHAVIORS_DIR` being empty — it's always set (defaults to `$HOME/.config/...`). The `-d` check handles non-existent directories.

### S3: Tests — new section "User-local behaviors search"

Place after existing "Local behaviors search" section. Five tests:

| Test | Setup | Assert |
|------|-------|--------|
| user-local resolves when no project-local | Create `$TEST_HOME/.config/ai-behaviors/behaviors/ulocal/prompt.md` with unique content. Invoke without cwd. | Output contains unique content |
| project-local beats user-local | Create same behavior name in both project-local and user-local with distinct content. Invoke with cwd. | Output contains project-local content, not user-local |
| user-local beats repo | Create user-local behavior with same name as a repo behavior (e.g. `deep`) with unique content. Invoke without cwd. | Output contains user-local content |
| user-local composite expands repo behaviors | Create user-local composite with `compose` referencing `#=code #deep`. Invoke without cwd. | Output contains operating-mode and behavior-modifiers tags |
| XDG_CONFIG_HOME override | Set `XDG_CONFIG_HOME` to alt path, create behavior there. Invoke. | Output contains unique content |

Each test calls `reset_state` and cleans up its user-local dir to avoid cross-test pollution.

### S4: README — rewrite "Custom behaviors" section

Replace lines 258–277 with three-tier explanation:

1. **User-local** (`~/.config/ai-behaviors/behaviors/`) — personal behaviors and composites, available across all projects. Primary path for personal customization.
2. **Project-local** (`.ai-behaviors/` at project root) — project-specific behaviors. Override user-local and repo.
3. **Repo** (`behaviors/` in ai-behaviors repo) — shared, version-controlled. Updated via `git pull`.

Include the `mkdir` + `cat` example targeting user-local path. Mention XDG_CONFIG_HOME override. Keep the FAQ question about CLAUDE.md vs behaviors.

## Deferred

- D1: User-local documentation in `#EXPLAIN` output (showing which tier a behavior resolved from).
- D2: `#LIST` meta-keyword to show available behaviors across all tiers.

## Constraints

- C1: Both hooks get identical changes.
- C2: Existing tests must continue to pass unmodified.
- C3: No new files beyond what's described (no new scripts, no config files).

## Open questions

None.
