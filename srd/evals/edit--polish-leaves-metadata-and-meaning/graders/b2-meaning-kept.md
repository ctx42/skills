---
type: regex
target: {source: file, path: specs/login.md}
flags: "s"
---
^(?=.*carries\s+no\s+Login\s+Token\s+with\s+HTTP\s+status\s+401)(?=.*whose\s+Login\s+Token\s+has\s+expired)(?=.*signature\s+is\s+invalid)(?=.*was\s+revoked)(?=.*5\s+consecutive\s+failed)(?=.*15\s+minutes\s+after)
