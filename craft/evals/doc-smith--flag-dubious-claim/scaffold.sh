#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs
cat > docs/api-guide.md <<'EOF_0'
# Orders API Guide

## Overview

The Orders API lets your application create, read, and delete orders over
HTTPS. Every endpoint accepts and returns JSON. REST APIs are stateful by
design.

## Authentication

Each request needs an access token in the `Authorization` header. The
token expires after one hour, you must request a new one from the `/token`
end-point.

## Creating an order

To create an order, send a `POST` request to the `/orders` endpoint. The
request body names the product and the quantity, the response returns the
new order's ID.

## Reading an order

To read an order, send a `GET` request to the `/orders/{id}` end-point.
The client sends the order ID in the path, and then the order is looked up
by the server and returned with its current status.

## Rate limits

Each endpoint allows 100 requests per minute for each access token.
EOF_0
