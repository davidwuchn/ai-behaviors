#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK="$REPO_DIR/hooks/inject-behaviors.sh"

TEST_HOME=$(mktemp -d)
export HOME="$TEST_HOME"
STDERR_FILE="$TEST_HOME/stderr"

PASS=0
FAIL=0

cleanup() { rm -rf "$TEST_HOME"; }
trap cleanup EXIT

# --- Helpers ---

invoke() {
  local prompt="${1:-}"
  local session_id="${2:-test-session}"
  jq -n --arg p "$prompt" --arg s "$session_id" \
    '{prompt: $p, session_id: $s}' \
    | "$HOOK" 2>"$STDERR_FILE"
}

invoke_no_session() {
  local prompt="$1"
  jq -n --arg p "$prompt" '{prompt: $p}' \
    | "$HOOK" 2>"$STDERR_FILE"
}

context_of() { jq -r '.hookSpecificOutput.additionalContext // empty'; }

reset_state() { rm -rf "$TEST_HOME/.claude/behaviors-state"; }

run_test() {
  reset_state
  : > "$STDERR_FILE"
  printf "  %-55s " "$1"
}

pass() { PASS=$((PASS + 1)); echo "OK"; }

fail() {
  FAIL=$((FAIL + 1))
  echo "FAIL"
  echo "    $1" >&2
}

assert_empty() {
  if [ -n "$1" ]; then
    fail "expected empty output, got: ${1:0:80}"
  else
    pass
  fi
}

assert_contains() {
  if [[ "$1" == *"$2"* ]]; then
    return 0
  else
    fail "expected to contain: $2"
    return 1
  fi
}

assert_not_contains() {
  if [[ "$1" == *"$2"* ]]; then
    fail "expected NOT to contain: $2"
    return 1
  else
    return 0
  fi
}

assert_eq() {
  if [ "$1" = "$2" ]; then
    return 0
  else
    fail "expected '$2', got '$1'"
    return 1
  fi
}

# === Input gating ===

echo "Input gating:"

run_test "empty_prompt_produces_no_output"
OUT=$(invoke "")
assert_empty "$OUT"

run_test "no_hashtags_no_state_produces_no_output"
OUT=$(invoke "hello world")
assert_empty "$OUT"

run_test "no_hashtags_empty_state_file_produces_no_output"
mkdir -p "$TEST_HOME/.claude/behaviors-state"
touch "$TEST_HOME/.claude/behaviors-state/test-session"
OUT=$(invoke "hello world")
assert_empty "$OUT"

# === Validation ===

echo ""
echo "Validation:"

run_test "multiple_op_modes_exits_2_with_error"
invoke "#op-code #op-assess" >/dev/null && EXIT_CODE=$? || EXIT_CODE=$?
STDERR=$(cat "$STDERR_FILE")
assert_contains "$STDERR" "multiple operating modes" && \
  assert_eq "$EXIT_CODE" "2" && pass

# === Full injection: structure ===

echo ""
echo "Full injection — structure:"

run_test "op_mode_wraps_in_operating_mode_tags"
OUT=$(invoke "do stuff #op-code" | context_of)
assert_contains "$OUT" "<operating-mode>" && \
  assert_contains "$OUT" "</operating-mode>" && \
  assert_not_contains "$OUT" "</behavior-modifiers>" && pass

run_test "modifiers_wrap_in_behavior_modifiers_tags"
OUT=$(invoke "do stuff #deep" | context_of)
assert_contains "$OUT" "</behavior-modifiers>" && \
  assert_not_contains "$OUT" "</operating-mode>" && pass

run_test "op_mode_with_modifiers_has_within_preamble"
OUT=$(invoke "do stuff #op-code #deep" | context_of)
assert_contains "$OUT" "WITHIN the operating mode" && pass

run_test "modifiers_only_omits_within_preamble"
OUT=$(invoke "do stuff #deep" | context_of)
assert_not_contains "$OUT" "WITHIN the operating mode" && pass

run_test "modifiers_include_marker_instruction"
OUT=$(invoke "do stuff #deep" | context_of)
assert_contains "$OUT" "mark it: (#name)" && pass

run_test "op_mode_only_omits_marker_instruction"
OUT=$(invoke "do stuff #op-code" | context_of)
assert_not_contains "$OUT" "mark it: (#name)" && pass

run_test "output_includes_compaction_instruction"
OUT=$(invoke "do stuff #op-code" | context_of)
assert_contains "$OUT" "During compaction, preserve" && pass

run_test "no_final_reminder_in_output"
OUT=$(invoke "do stuff #op-code #deep" | context_of)
assert_not_contains "$OUT" "FINAL REMINDER" && pass

# === Full injection: unknown behaviors ===

echo ""
echo "Full injection — unknown behaviors:"

run_test "unknown_hashtag_warns_on_stderr"
invoke "do stuff #nonexistent" >/dev/null || true
STDERR=$(cat "$STDERR_FILE")
assert_contains "$STDERR" "Unknown behaviors" && \
  assert_contains "$STDERR" "#nonexistent" && pass

run_test "mixed_known_unknown_injects_known_warns_unknown"
OUT=$(invoke "do stuff #op-code #nonexistent" | context_of)
STDERR=$(cat "$STDERR_FILE")
assert_contains "$OUT" "<operating-mode>" && \
  assert_contains "$STDERR" "#nonexistent" && pass

# === State persistence ===

echo ""
echo "State persistence:"

run_test "persists_valid_hashtags"
invoke "do stuff #op-code #deep" >/dev/null
STATE=$(cat "$TEST_HOME/.claude/behaviors-state/test-session")
assert_contains "$STATE" "#op-code" && \
  assert_contains "$STATE" "#deep" && pass

run_test "excludes_unknown_from_state"
invoke "do stuff #op-code #nonexistent" >/dev/null 2>/dev/null
STATE=$(cat "$TEST_HOME/.claude/behaviors-state/test-session")
assert_contains "$STATE" "#op-code" && \
  assert_not_contains "$STATE" "#nonexistent" && pass

run_test "no_session_id_skips_state_file"
rm -rf "$TEST_HOME/.claude/behaviors-state"
invoke_no_session "do stuff #op-code" >/dev/null
if [ -d "$TEST_HOME/.claude/behaviors-state" ]; then
  fail "state dir should not exist"
else
  pass
fi

# === Continuation path ===

echo ""
echo "Continuation path:"

run_test "continuation_attributes_constraints_to_hashtags"
invoke "do stuff #op-code #deep" >/dev/null
OUT=$(invoke "next question" | context_of)
assert_contains "$OUT" "Active: " && \
  assert_contains "$OUT" "HARD CONSTRAINTs in force:" && \
  assert_contains "$OUT" "#op-code:" && \
  assert_contains "$OUT" "#deep:" && pass

run_test "continuation_includes_constraint_text"
invoke "do stuff #op-code" >/dev/null
OUT=$(invoke "next question" | context_of)
assert_contains "$OUT" "-- HARD CONSTRAINT" && pass

run_test "continuation_skips_deleted_behavior"
invoke "do stuff #op-code" >/dev/null
echo "#op-code #deleted-fake" > "$TEST_HOME/.claude/behaviors-state/test-session"
OUT=$(invoke "next question" | context_of)
assert_contains "$OUT" "#op-code:" && \
  assert_not_contains "$OUT" "#deleted-fake:" && pass

# === Summary ===

echo ""
TOTAL=$((PASS + FAIL))
echo "$PASS/$TOTAL passed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
