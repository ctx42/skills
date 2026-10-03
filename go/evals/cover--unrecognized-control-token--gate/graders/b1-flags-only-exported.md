---
type: regex
target: last_message
flags: "i"
---
only=exported[^\n]*(not (a )?(recogni[sz]ed|known|supported|valid|control)|unrecogni[sz]ed|unknown|isn't|is not)|(unrecogni[sz]ed|unknown|not recogni[sz]ed|(didn't|did not|don't|do not) recogni[sz]e)[^\n]*only=exported
