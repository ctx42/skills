---
type: regex
target: last_message
flags: "i"
---
^(?=[\s\S]*[Tt]enant order(?:(?![Ii]solation)[\s\S])*?(acceptance|criteri|pass(es)?\b|verif))(?=[\s\S]*[Ii]solation(?:(?![Rr]ollback)[\s\S])*?(acceptance|criteri|pass(es)?\b|verif))(?=[\s\S]*[Rr]ollback(?:(?![Mm]onitoring)[\s\S])*?(acceptance|criteri|pass(es)?\b|verif))(?=[\s\S]*[Mm]onitoring(?:(?![Cc]oncurrency)[\s\S])*?(acceptance|criteri|pass(es)?\b|verif))
