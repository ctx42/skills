- Grep `contract.json` for single words, never whole phrases: a stored phrase
  can escape its spaces, so a phrase grep misses it and only lint catches the
  break.
