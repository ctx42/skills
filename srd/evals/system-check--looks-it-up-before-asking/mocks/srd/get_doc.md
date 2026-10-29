---
type: agent
---
Answer with the full text of the document whose id or path the call names.

- `docs/srd-standard.md`:
  answer with exactly the text between the BEGIN and END marker lines below,
  verbatim and complete, the marker lines themselves left out.
- `1774485611` or `docs/concepts/tags.md`: answer with exactly this text:
  "# Tags

## Tag names

Tag names represent a hierarchical structure expressed as a dot-separated series of Tag node names, for example `travel.europe.lisbon`. Each Tag node name MUST start with a letter a-z. Every Tag Definition carries a Tag Kind besides its name: `string`, `number`, or `boolean`; a Tag cannot be created without one."
- `docs/glossary/main_glossary.md`: answer with exactly the
  text between the GLOSSARY-BEGIN and GLOSSARY-END marker lines below.
- `docs/formats/photo_format.md`: answer with
  exactly this text: "# Photo Format\n\n## meta block\n\nThe `meta` block carries the sub-type `tags`. Each tag is one entry of the `meta` block: the entry key names the tag and its data holds the value."
- Any other id: answer `{"error":"no document with id <the id>"}`.

BEGIN
{{file:fixtures/srd-standard.md}}
END

GLOSSARY-BEGIN
# Main Glossary

## Asset (AST)

Any user-defined, identifiable entity or record that holds value within a project.

## Device (DEV)

Uniquely identifiable hardware unit identified by a UUID (DEV_ID) and typically capable of sensing, processing, actuating, and/or transmitting data.

## Sensor

Hardware component that detects and measures a physical quantity and converts it into a readable signal or value.

## Project (PRJ)

A self-contained organizational unit that serves as a grouping and access-control boundary. Each Project belongs to a Customer.

## Customer

A paying organization with access to the platform. A Customer has zero or more Projects.

## EXAMPLE Instance

A single, self-contained deployment of the EXAMPLE platform operating independently with its own data store, services, and configuration.

## Photo (PHO)

A still image in JPEG format that may carry one or more Layers and custom metadata.

## Namespace (NS)

A named grouping that scopes Tag Definitions within a Project. Each Namespace has a short code that prefixes the names of the Tags it holds.

## Tag (TAG)

A named label attached to a platform object such as a Photo. A Tag's name is a series of Tag node names.

## Date

A calendar day with a time of day, stored in UTC.
GLOSSARY-END
