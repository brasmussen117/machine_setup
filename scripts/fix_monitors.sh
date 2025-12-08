#!/bin/bash
# fix_monitors.sh
# Configure display layout with xrandr
# Layout (left → right): DP-1 | DP-3 | DP-2

# Apply rotations and positions in one command
echo "Configuring monitors: Home setup with DP-1 (left), DP-3 (center, primary), DP-2 (right)"
xrandr \
  --output DP-1 --rotate right --auto --pos 0x244 \
  --output DP-3 --primary --auto --pos 1440x731 \
  --output DP-2 --rotate left --auto --pos 4000x0
