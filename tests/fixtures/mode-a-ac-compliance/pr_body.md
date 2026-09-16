# PR #501: Show tax rate in checkout summary

## Description
Adds the tax rate percentage next to the tax line in checkout summary. Handles the
0% case by hiding the row, and works for all supported currencies (USD, EUR, GBP)
since it reuses the shared `formatCurrency` helper everywhere.

Example of the guard clause added:
```jsx
if (taxRate === 0) return null; // hides tax row entirely
```

## Files changed
- src/components/CheckoutSummary.jsx
