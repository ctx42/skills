---
type: regex
target: {source: file, path: tmp/sso-plan.md}
---
^(?![\s\S]*\b(OIDC|OpenID|SAML)\b)|^(?=[\s\S]*\b(OIDC|OpenID)\b)(?=[\s\S]*\bSAML\b)
