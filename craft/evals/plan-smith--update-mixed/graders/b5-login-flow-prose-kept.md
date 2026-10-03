---
type: regex
target: {source: file, path: sso-plan.md}
flags: "m"
---
^## 2\.[^\n]*\n\nAuthorization-code flow with PKCE\. `\/login` redirects to the provider,\n`\/callback` exchanges the code and establishes a session\.\n\nDone when: a full round trip against the staging provider lands an\nauthenticated user on the post-login page, and a replayed code is rejected\.\n
