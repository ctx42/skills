---
type: regex
target: last_message
flags: "i"
---
(?:workspace|project)[\s\S]{0,500}?(?:install\.md[\s\S]{0,400}?config\.md|config\.md[\s\S]{0,400}?install\.md)|(?:install\.md[\s\S]{0,400}?config\.md|config\.md[\s\S]{0,400}?install\.md)[\s\S]{0,500}?(?:workspace|project)
