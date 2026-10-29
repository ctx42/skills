#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs
cat > docs/guide.md <<'EOF_0'
# Getting started with Fieldbook

Fieldbook is an app that simply keeps your survey notes, photos, and maps
together in one workspace, and the workspace can be shared by you with
your team.

## Creating a workspace

To create a workspace, select **New** on the home screen and enter a
name. You become the owner of the workspace.

## Inviting your team

To invite a colleague, open the workspace and select **Invite**. Each
member can add notes and photos to the workspace but cannot delete it.

## Archiving a workspace

When a survey is finished, archive its workspace to make it read-only.
Archived workspaces stay searchable.
EOF_0
