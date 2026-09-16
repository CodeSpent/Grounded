# Answer key — Mode A (AC Compliance)

Planted so a correct run of the skill must catch **4 problems**, including one
hallucinated code snippet in the PR description.

| Criterion | Expected status | Why |
|---|---|---|
| AC1: show tax rate % next to tax line | ✅ Met | `taxRatePercent` is computed and rendered |
| AC2: hide tax line entirely at 0% | ❌ Not met | No `taxRate === 0` guard exists anywhere in `pr.diff` — the row always renders |
| AC3: works for USD, EUR, **and GBP** | ❌ Not met | The diff's ternary only checks `currency === 'USD' \|\| currency === 'EUR'` — GBP silently gets no `%` suffix |
| DoD: unit tests incl. 0% case | ❌ Not met | Diff touches only `CheckoutSummary.jsx`; no test file is added |
| Description cross-check | ❌ Flagged as false | `pr_body.md` shows a guard clause `if (taxRate === 0) return null;` that **does not appear anywhere in `pr.diff`** — a fabricated/hallucinated example |

**Expected verdict:** Not compliant — send back (quote AC2, AC3, and the DoD line).

A correct run must not accept the PR description's "works for all currencies" or
"handles the 0% case" claims at face value — it must trace the actual diff.
