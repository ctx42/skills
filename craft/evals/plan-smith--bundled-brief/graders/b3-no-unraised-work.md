---
type: regex
target: {source: file, path: tmp/agent-plan-export.md}
match: "not_contains"
flags: "im"
---
^## \d+\.[^\n]*\b(rewrite|rewriting|scheduler|cron|airflow|language|port\b|tests?\b|monitoring|dashboards?\s+for)
