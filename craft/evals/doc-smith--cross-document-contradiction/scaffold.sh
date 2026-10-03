#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs
cat > docs/manual.md <<'EOF_0'
# Acme User Manual

## Overview

Acme is a hosted web platform for planning maintenance work on water
networks. Your work orders, crews, and schedules are stored on Acme's
servers, so everyone on your team sees the same plan.

## Signing in

To sign in, open the address your administrator sent you and enter your
email address and password. After three failed attempts, your account is
locked for 15 minutes.

## Creating a work order

To create a work order, follow these steps.

1. Select **New work order** on the dashboard.
2. Enter a title and choose the asset that needs work.
3. Select **Save**.

The work order appears in the backlog of the crew you assigned it to.

## System requirements

Acme runs entirely in your web browser. You need a current version of
Chrome, Firefox, or Edge, and there is nothing to install.

## Assigning crews

To assign a crew, open a work order and choose a crew from the **Crew**
list. The crew lead receives an email with the details of the job.
Please note that you can simply reassign the work order later if plans
change.

## Working offline

Remember that Acme runs entirely in your web browser. When your
connection drops, Acme shows a banner and retries until it is back.

## Exporting schedules

To export a schedule, select **Export** on the schedule page and choose
CSV or PDF. Acme runs entirely in your web browser, so the file is saved
to your browser's download folder.
EOF_0
