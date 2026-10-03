---
type: regex
target: {source: file, path: sso-plan.md}
flags: "m"
---
^## 1\.[^\n]*\n\nRead the OIDC issuer, client ID, and client secret from the environment and\nvalidate them at startup\. The secret never appears in logs or in the config\ndump endpoint\.\n\nDone when: the server refuses to start with a missing or malformed issuer, and\n`GET \/debug\/config` redacts the secret\.\n
