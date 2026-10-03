#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs
cat > docs/manual.md <<'EOF_0'
# Pulse Logger Manual

## Overview

Pulse Logger records pressure readings from field loggers and shows them
on a chart. In order to get started, you simply need an account and one
logger.

## Adding a logger

To add a logger, follow these steps.

1. Select **Add logger** and enter the serial number.
2. Select the site and select **Save**.

The device appears on the map within one minute.

## Reading the chart

The chart will be shown with the last 24 hours of readings. Please note
that readings older than 90 days are deleted.

## Alarm thresholds

The following table lists the default thresholds.

| Alarm | Default |
|---|---|
| Low pressure | 1.5 bar |
| High pressure | 8 bar |
EOF_0
