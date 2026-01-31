#!/bin/bash
# Claude Code Wrapper Script with pseudo-TTY and file-based output

export HOME=/root
export PATH="/usr/local/bin:$PATH"
export USER=root
export TERM=xterm-256color

# Claude API settings
export ANTHROPIC_BASE_URL="http://44.251.199.189:4000/"
export ANTHROPIC_AUTH_TOKEN="sk-mqNwjp4esKkasmgZQn_FKw"
export ANTHROPIC_API_KEY="sk-mqNwjp4esKkasmgZQn_FKw"
export ANTHROPIC_MODEL="claude-opus-4-5-20251101"

# Settings file location
SETTINGS_FILE="/root/.claude/settings_arash.json"

# Create a temp file for output
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

# Build properly quoted command
QUOTED_ARGS=""
for arg in "$@"; do
    # Escape single quotes in the argument and wrap in single quotes
    escaped_arg=$(printf '%s' "$arg" | sed "s/'/'\\\\''/g")
    QUOTED_ARGS="$QUOTED_ARGS '$escaped_arg'"
done

# Run claude with script for pseudo-TTY (using the original binary)
# Include --settings flag to use custom settings file
script -q /dev/null -c "/root/.local/bin/claude --settings $SETTINGS_FILE $QUOTED_ARGS" > "$TMPFILE" 2>&1

# Clean and output the result (remove ANSI codes, OSC sequences, and control chars)
cat "$TMPFILE" | tr -d '\r' | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\[[?][0-9]*[a-zA-Z]//g; s/\x1b\[<u//g; s/\x1b\][0-9]*;[^\x07]*\x07//g'
