#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs
cat > docs/guide.md <<'EOF_0'
# Customising the Map View

The map view shows every asset in your network on one screen, and you can customise how it looks so
that the information you need stands out. This guide explains the colour settings, the label
options, and the way the map remembers your choices between sessions.

Each asset type has its own colour. Pipes are drawn in blue by default, valves in orange, and
hydrants in red, but your organisation can change these colours centrally so that every user sees
the same scheme. If your administrator has locked the colour scheme, the **Colour** menu is greyed
out and shows a short note instead.

To change the color of an asset type, open **Settings**, select **Map**, and pick a new colour from
the palette. The change applies at once, and the map remembers it the next time you sign in from the
same browser on the same computer.

The following table lists the default colour for each asset type.

| Asset type | Default colour | Can be changed |
|------------|----------------|----------------|
| Pipe       | Blue           | Yes            |
| Valve      | Orange         | Yes            |
| Hydrant | Red | Only by an administrator |

Labels show the asset ID next to each symbol. When the map is zoomed out, labels are hidden
automatically to keep the view readable, and they reappear as soon as you zoom in to street level
again.

Colour-blind users can switch to the high-contrast palette, which replaces the default colors with shapes and patterns
that remain distinct without relying on colour at all, and the palette applies to printed maps as well as to the screen.
EOF_0
