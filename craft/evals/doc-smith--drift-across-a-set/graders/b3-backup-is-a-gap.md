---
type: regex
target: last_message
flags: "i"
---
backup[^\n]{0,200}(missing|does not exist|doesn't exist|no such|dangling|broken|not (found|present)|none of|absent|nowhere)|(missing|does not exist|doesn't exist|no such|dangling|broken|absent|nowhere)[^\n]{0,200}backup
