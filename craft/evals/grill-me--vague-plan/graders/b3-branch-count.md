---
type: regex
target: last_message
flags: "is"
---
^(?=.*(\b\d+\b|\bno\b|\bnone\b|\bzero\b)[^\n]{0,30}\bresolved\b|.*\bresolved\W{0,5}\d)(?=.*\b\d+\b[^\n]{0,30}\b(open|branch(es)?|remain\w*)\b|.*\bopen\W{0,5}\d)
