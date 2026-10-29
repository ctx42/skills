# CSV export plan

## Summary

| #  | Item              | Status |
|----|-------------------|--------|
| 1  | Filtered scope    | Y      |
| 2  | Row limit         | Y      |
| 3  | Audit log         | N      |
| 4  | Remove this plan  | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Filtered scope — [x]

The export covers the currently filtered view, not the whole dataset.

Done when: exporting from a filtered report yields exactly the filtered rows.

## 2. Row limit — [x]

Over 100k rows the export is refused with a message naming the filter as the
fix.

Done when: a 100,001-row selection is refused and names the filter as the fix.

## 3. Audit log — [ ]

Every export is logged with user, timestamp, and row count.

Done when: an export writes exactly one audit row carrying those three fields.

## 4. Remove this plan — [ ]

When every other item is `Y` or `X`, ask the user whether to delete this file.

Done when: the user has answered — yes deletes the file, no marks this item `X`.
