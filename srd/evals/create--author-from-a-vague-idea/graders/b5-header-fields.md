---
type: regex
target: {source: file, path: initiatives/slot-swap/srd.md}
flags: "m"
---
(?=[\s\S]*^\|\s*\**Summary\**\s*\|)(?=[\s\S]*^\|\s*\**Maintainer\**\s*\|)(?=[\s\S]*^\|\s*\**Reviewers\**\s*\|)(?=[\s\S]*^\|\s*\**Tracking\**\s*\|)(?=[\s\S]*^\|\s*\**Lifecycle\**\s*\|)(?=[\s\S]*^\|\s*\**Mockups\**\s*\|)^\|\s*\**Field\**\s*\|\s*\**Value\**\s*\|
