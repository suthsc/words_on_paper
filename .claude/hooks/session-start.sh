#!/bin/bash
NOTES=".claude/handoff-notes.md"
if [ -f "$NOTES" ]; then
  echo "<handoff-notes>"
  cat "$NOTES"
  echo "</handoff-notes>"
fi
