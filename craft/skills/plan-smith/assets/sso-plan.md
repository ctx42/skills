# SSO plan

## Summary

| #  | Item              | Status |
|----|-------------------|--------|
| 1  | Provider config   | N      |
| 2  | Login flow        | N      |
| 3  | Session storage   | N      |
| 4  | Operator docs     | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Provider config — [ ]

Read the OIDC issuer, client ID, and client secret from the environment and
validate them at startup. The secret never appears in logs or in the config
dump endpoint.

Done when: the server refuses to start with a missing or malformed issuer, and
`GET /debug/config` redacts the secret.

## 2. Login flow — [ ]

Authorization-code flow with PKCE. `/login` redirects to the provider,
`/callback` exchanges the code and establishes a session.

Done when: a full round trip against the staging provider lands an
authenticated user on the post-login page, and a replayed code is rejected.

## 3. Session storage — [ ]

Sessions live in Redis, keyed by an opaque session ID, with a 12-hour TTL. The
cookie carries only the ID.

Done when: a session survives an app restart, expires on its own after 12
hours, and logout deletes the key.

## 4. Operator docs — [ ]

A page in the operator manual covering the environment variables, the redirect
URI the provider must whitelist, and how to rotate the client secret.

Done when: someone who has not seen this work can configure SSO from the page
alone.
