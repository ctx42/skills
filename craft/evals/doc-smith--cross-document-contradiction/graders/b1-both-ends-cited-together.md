---
type: regex
target: last_message
flags: "i"
---
(?:Overview|(?:\blines?\s*|\bL|\.md:)(?:[\d\s,–-]|\bvs\b\.?|\band\b|\bL(?=\d)){0,40}?(?<!\d)(?:5|6|7)\b)[\s\S]{0,400}?(?:System requirements|Working offline|Exporting schedules|(?:\blines?\s*|\bL|\.md:)(?:[\d\s,–-]|\bvs\b\.?|\band\b|\bL(?=\d)){0,40}?(?<!\d)(?:27|39|45)\b)|(?:System requirements|Working offline|Exporting schedules|(?:\blines?\s*|\bL|\.md:)(?:[\d\s,–-]|\bvs\b\.?|\band\b|\bL(?=\d)){0,40}?(?<!\d)(?:27|39|45)\b)[\s\S]{0,400}?(?:Overview|(?:\blines?\s*|\bL|\.md:)(?:[\d\s,–-]|\bvs\b\.?|\band\b|\bL(?=\d)){0,40}?(?<!\d)(?:5|6|7)\b)
