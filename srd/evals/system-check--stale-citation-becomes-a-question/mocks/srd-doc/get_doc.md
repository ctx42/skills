---
type: agent
---
Answer with the full text of the document whose id the call names.

- `confluence/example/guidelines_for_software_requirements_documents.md`:
  answer with exactly the text between the BEGIN and END marker lines below,
  verbatim and complete, the marker lines themselves left out.
- `confluence/example/concepts/tags.md`: answer with exactly this text:
  "# Tags

## Tag names

Tag names represent a hierarchical structure expressed as a comma-separated series of named nodes, for example `site,zone,pump`. Each Tag node name MUST start with a letter a-z."
- `confluence/example/glossary/main_glossary.md`: answer with exactly the
  text between the GLOSSARY-BEGIN and GLOSSARY-END marker lines below.
- `confluence/example/formats/sound_file_documentation.md`: answer with
  exactly this text: "# Sound File Documentation\n\n## meta chunk\n\nThe `meta` chunk carries the sub-type `tags`. Each tag is one sub-chunk of the `meta` chunk: the sub-chunk ID names the tag and its data holds the value."
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

## Sound File (SND)

A binary audio recording in WAV (RIFF) format that may contain one or more Sound Channels and custom metadata.

## Tag (TAG)

A named label attached to a platform object such as a Sound File. A Tag's name is a series of Tag node names.

## Date

A calendar day with a time of day, stored in UTC.
GLOSSARY-END
