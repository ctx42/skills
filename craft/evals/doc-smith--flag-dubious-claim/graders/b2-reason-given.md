---
type: regex
target: last_message
flags: "i"
---
stateless[^\n]{0,200}(no (session |client )?state|keeps? no|stores? no|each request|between requests|self-contained|(does not|doesn't|never) (keep|store|remember|hold)|constraint|Fielding)
