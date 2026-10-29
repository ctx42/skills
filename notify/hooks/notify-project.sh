#!/bin/bash
# notify-project.sh — ships with the ctx42 `notify` plugin (hooks/hooks.json).

INPUT=$(cat)

# Only the main agent asks for attention; `agent_id` is set only inside a subagent.
[ -n "$(echo "$INPUT" | jq -r '.agent_id // empty')" ] && exit 0

CWD=$(echo "$INPUT" | jq -r '.cwd // "Unknown project"')
MESSAGE=$(echo "$INPUT" | jq -r '.message // "Claude needs your attention"')
PROJECT_NAME=$(basename "$CWD")
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""' | cut -c1-8)

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERLAY="$HOOK_DIR/notify-monitors.py"
SOUND_FILE="/usr/share/sounds/freedesktop/stereo/message-new-instant.oga"
POPUP_SECONDS=6

# Play an attention sound (first available player wins).
play_sound() {
  [ -r "$SOUND_FILE" ] || return
  if command -v canberra-gtk-play >/dev/null; then canberra-gtk-play -f "$SOUND_FILE"
  elif command -v pw-play >/dev/null; then pw-play "$SOUND_FILE"
  elif command -v paplay >/dev/null; then paplay "$SOUND_FILE"
  elif command -v ffplay >/dev/null; then ffplay -nodisp -autoexit -loglevel quiet "$SOUND_FILE"
  elif command -v aplay >/dev/null; then aplay -q "$SOUND_FILE"
  fi
}

if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  osascript -e "display notification \"$MESSAGE\nProject: $PROJECT_NAME\" with title \"Claude [$PROJECT_NAME]\" sound name \"Glass\""
elif [ -n "$DISPLAY" ] && [ -r "$OVERLAY" ] && command -v python3 >/dev/null; then
  # Linux desktop: sound + a small card near the top of every monitor.
  # Detached (setsid) so the hook returns immediately and the popups outlive it.
  export SOUND_FILE
  setsid -f bash -c "$(declare -f play_sound); play_sound & \
    python3 \"\$1\" \"\$2\" \"\$3\" \"\$4\"; wait" \
    _ "$OVERLAY" "$MESSAGE" "$PROJECT_NAME" "$POPUP_SECONDS" </dev/null >/dev/null 2>&1
elif command -v notify-send >/dev/null; then
  # Linux fallback: single notification + sound.
  play_sound &
  notify-send -h int:transient:1 "Claude [$PROJECT_NAME]" "$MESSAGE" --icon=terminal
else
  echo "=== CLAUDE NEEDS ATTENTION IN: $PROJECT_NAME ===" >&2
  echo "$MESSAGE" >&2
fi
