---
type: regex
target: {source: file, path: docs/guide.md}
flags: "m"
---
^(?:\|\ Asset\ type\ \|\ Default\ colour\ \|\ Can\ be\ changed\ \ \ \ \ \ \ \ \ \ \ \||\|\ Pipe\ \ \ \ \ \ \ \|\ Blue\ \ \ \ \ \ \ \ \ \ \ \|\ Yes\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \||\|\ Valve\ \ \ \ \ \ \|\ Orange\ \ \ \ \ \ \ \ \ \|\ Yes\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \||\|\ Hydrant\ \ \ \ \|\ Red\ \ \ \ \ \ \ \ \ \ \ \ \|\ Only\ by\ an\ administrator\ \|)$(?:[\s\S]*?^(?:\|\ Asset\ type\ \|\ Default\ colour\ \|\ Can\ be\ changed\ \ \ \ \ \ \ \ \ \ \ \||\|\ Pipe\ \ \ \ \ \ \ \|\ Blue\ \ \ \ \ \ \ \ \ \ \ \|\ Yes\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \||\|\ Valve\ \ \ \ \ \ \|\ Orange\ \ \ \ \ \ \ \ \ \|\ Yes\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \||\|\ Hydrant\ \ \ \ \|\ Red\ \ \ \ \ \ \ \ \ \ \ \ \|\ Only\ by\ an\ administrator\ \|)$){3}
