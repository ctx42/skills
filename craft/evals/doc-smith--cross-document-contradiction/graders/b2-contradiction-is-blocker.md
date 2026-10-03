---
type: regex
target: last_message
flags: "i"
---
Blockers?\b(?=(?:(?!Should[- ]?fix)[\s\S])*?(?:hosted))(?=(?:(?!Should[- ]?fix)[\s\S])*?(?:browser))(?=(?:(?!Should[- ]?fix)[\s\S])*?(?:Overview|(?:\blines?\s*|\bL|\.md:)(?:[\d\s,–-]|\bvs\b\.?|\band\b|\bL(?=\d)){0,40}?(?<!\d)(?:5|6|7)\b))(?=(?:(?!Should[- ]?fix)[\s\S])*?(?:System requirements|Working offline|Exporting schedules|(?:\blines?\s*|\bL|\.md:)(?:[\d\s,–-]|\bvs\b\.?|\band\b|\bL(?=\d)){0,40}?(?<!\d)(?:27|39|45)\b))
