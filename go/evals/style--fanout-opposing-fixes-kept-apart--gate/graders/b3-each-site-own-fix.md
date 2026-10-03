---
type: regex
target: last_message
match: not_contains
flags: "i"
---
(?:^|\n)[ \t]*\**\d+\.(?:(?=(?:(?!\n[ \t]*\**\d+\.)[\s\S])*?\b(delete|remove)\b)(?=(?:(?!\n[ \t]*\**\d+\.)[\s\S])*?\b(alpha|bravo|charlie|delta)_test\.go)|(?=(?:(?!\n[ \t]*\**\d+\.)[\s\S])*?\b(insert|add)\b)(?=(?:(?!\n[ \t]*\**\d+\.)[\s\S])*?\b(echo|foxtrot|golf|hotel)_test\.go))
