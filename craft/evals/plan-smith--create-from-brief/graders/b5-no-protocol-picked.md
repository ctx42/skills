---
type: regex
target: {source: file, path: tmp/agent/agent-plan-sso.md}
---
^(?![\s\S]*\b(OIDC|OpenID|SAML)\b)|^(?=[\s\S]*\b(OIDC|OpenID)\b)(?=[\s\S]*\bSAML\b)
