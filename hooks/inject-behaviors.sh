#!/bin/bash
set -euo pipefail

INPUT=$(cat)
PROMPT=$(jq -r '.prompt // empty' <<< "$INPUT")

if [ -z "$PROMPT" ]; then
  exit 0
fi

BEHAVIORS_DIR="$HOME/.claude/behaviors"
HASHTAGS=$(grep -oE '#[a-zA-Z0-9_-]+' <<< "$PROMPT" | sort -u) || true

if [ -z "$HASHTAGS" ]; then
  exit 0
fi

CONTEXT=""
MISSING=""

while IFS= read -r TAG; do
  NAME="${TAG#\#}"
  FILE="$BEHAVIORS_DIR/$NAME.md"
  if [ -f "$FILE" ]; then
    if [ -n "$CONTEXT" ]; then
      CONTEXT+=$'\n\n'
    fi
    CONTEXT+="$(cat "$FILE")"
  else
    MISSING+=" $TAG"
  fi
done <<< "$HASHTAGS"

if [ -n "$MISSING" ]; then
  echo "Unknown behaviors:$MISSING" >&2
fi

if [ -n "$CONTEXT" ]; then
  WRAPPED="<claude-behaviors>
$CONTEXT
</claude-behaviors>
The above directives between <claude-behaviors> tags apply to all your responses until superseded by a newer <claude-behaviors> block. When a new <claude-behaviors> block appears, stop following all previous ones — only the most recent set applies. During compaction, preserve the most recent <claude-behaviors> block verbatim. Discard all older ones."
  jq -n --arg ctx "$WRAPPED" '{
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: $ctx
    }
  }'
fi

exit 0
