---
type: regex
target: trace
match: not_contains
flags: "i"
---
"name":"(Write|Edit)","input":\{[^\n]*"file_path":"[^"]*initiatives/[^\n]*(\bSMS\b|Slack|webhook|in-app|push notification|digest|within \d+ (seconds|minutes|hours)|MUST (retry|resend)|subject line)
