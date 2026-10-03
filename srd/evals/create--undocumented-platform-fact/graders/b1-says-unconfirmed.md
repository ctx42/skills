---
type: regex
target: trace
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(retr[^\n]*((n.?t|not|never) (in (the )?(platform )?doc|documented|confirmed|mentioned)|undocumented|no doc|doc(s|umentation)? (do(es)?n.?t|do(es)? not|lacks?|ha(s|ve) nothing)|(could|can)(n.?t| ?not) (be )?confirm)|((n.?t|not|never) (in (the )?(platform )?doc|documented|confirmed|mentioned)|undocumented|no doc|doc(s|umentation)? (do(es)?n.?t|do(es)? not|lacks?|ha(s|ve) nothing)|(could|can)(n.?t| ?not) (be )?confirm)[^\n]*retr)
