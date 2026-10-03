---
type: regex
target: last_message
flags: "i"
---
(?<![\w:.\-–]|lines? |L)(([4-9]|1\d)|four|five|six|seven|eight|nine|ten|eleven|twelve)\b(?!\))[^\n.;]{0,40}(\bcolours?\b|British)|(\bcolours?\b|British)[^\n.;]{0,40}(×\s*([4-9]|1\d)\b|\(([4-9]|1\d)\)|\b([4-9]|1\d) (times|sites|uses|occurrences|places)\b)
