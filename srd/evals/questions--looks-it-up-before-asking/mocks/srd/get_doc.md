---
type: agent
---
Answer with the full text of the document whose id or path the call names.

- `docs/srd-standard.md`: answer with exactly the text between the BEGIN and
  END marker lines below, verbatim and complete, the marker lines themselves
  left out.
- `1000000103` or `docs/concepts/part-kits.md`: answer with exactly the text
  between the PARTKITS-BEGIN and PARTKITS-END marker lines below.
- `docs/glossary/terms.md`: answer with exactly the text between the
  TERMS-BEGIN and TERMS-END marker lines below.
- `docs/glossary/ui-terms.md`: answer with exactly the text between the
  UI-BEGIN and UI-END marker lines below.
- `docs/glossary/ml-terms.md`: answer with exactly the text between the
  ML-BEGIN and ML-END marker lines below.
- Any other id or path that `list_docs` lists: answer with that document's
  title as a level-1 heading and one short paragraph on the page's own topic
  at Starforge Rocketworks; it says nothing about
  Part Kits, Launch Slots, or Assembly Bays.
- Any other id: answer `{"error":"no document with id <the id>"}`.

BEGIN
{{file:fixtures/srd-standard.md}}
END

PARTKITS-BEGIN
# Part Kits

A Part Kit is the set of parts picked for one Stage of one Build Order.

## Picking

Part kits are picked 5 working days before stage integration. Every Part Kit
carries a pick priority, one of `routine`, `expedite`, or `critical`; a Part
Kit cannot be created without one.
PARTKITS-END

TERMS-BEGIN
{{file:fixtures/glossary-terms.md}}
TERMS-END

UI-BEGIN
{{file:fixtures/glossary-ui-terms.md}}
UI-END

ML-BEGIN
{{file:fixtures/glossary-ml-terms.md}}
ML-END
