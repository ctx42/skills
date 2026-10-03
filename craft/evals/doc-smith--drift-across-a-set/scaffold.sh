#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs
cat > docs/install.md <<'EOF_0'
# Installing Tally

To install Tally, download the installer for your system from the
releases page and run it. When the installer finishes, Tally asks you to
create your first workspace.

## Creating your first workspace

A workspace holds your ledgers, your reports, and the people you share
them with. Enter a name for the workspace and select **Create**.
EOF_0
mkdir -p docs
cat > docs/config.md <<'EOF_1'
# Configuring Tally

Each project has its own settings. To open them, select the project name
in the sidebar and then select **Settings**.

## Currency

The currency applies to every ledger in the project. You can change it
until the first entry is posted.

## Members

To invite someone, enter their email address under **Members**. Members
see every ledger in the project.
EOF_1
mkdir -p docs
cat > docs/usage.md <<'EOF_2'
# Using Tally

## Posting an entry

To post an entry, open a ledger, select **New entry**, and fill in the
date, the amount, and the account.

## Running a report

To run a report, select **Reports** and choose the period. Reports are
saved automatically, and you can restore an older version from a backup;
see the Backup section.
EOF_2
