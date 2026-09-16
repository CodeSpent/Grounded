# Answer key: Mode D (Mid-build Drift Check)

Planted so a correct run catches drift in both directions: a missing
requirement and two instances of invented scope the ticket explicitly forbade.

| Requirement | Expected tag | Why |
|---|---|---|
| Req 1: "Export CSV" button | expected, met | Button is present in `current_diff.patch` |
| Req 2: export respects the date-range filter | expected, missing | `handleExportCsv` calls `allOrdersFromStore()` (unfiltered), not the filtered `orders` state. The diff's own comment admits this |
| Req 3: CSV columns (Order ID, Date, Status, Total) | expected, met | Columns array matches exactly |
| Email export button/handler | unrequested, scope creep | Ticket explicitly says "do not add ... email delivery ... tracked separately in MOCK-204" |
| Schedule dropdown/handler | unrequested, scope creep | Ticket explicitly says "do not add ... scheduling ... tracked separately in MOCK-203" |

Expected behavior: the skill should stop and flag drift plainly (per Step 5 of
Mode D) rather than silently continuing. Both the missing filter behavior and
the two invented features should be named explicitly, quoting the ticket's own
"do not add" line.
