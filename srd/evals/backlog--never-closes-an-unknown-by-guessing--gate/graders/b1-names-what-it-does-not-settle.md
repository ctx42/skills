---
type: regex
target: last_message
flags: "i"
---
^(?=[\s\S]*((default|single|one) (propagation )?speed|Standard-?\w*geschwindigkeit))(?=[\s\S]*((does(n.t| not)|not|never) (settle|answer|say|address|touch|cover|decide)|offen l(ä|ae)sst|kl(ä|ae)rt nicht))(?=[\s\S]*(sensor[- ]type|Sensortyp))
