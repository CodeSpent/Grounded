# MOCK-101: Add rate display to checkout summary

## Acceptance Criteria
1. Checkout summary page must display the tax rate as a percentage next to the tax line item.
2. If the tax rate is 0%, the tax line item must be hidden entirely (not shown as "0%").
3. Tax rate display must work for all supported currencies (USD, EUR, GBP).

## Definition of Done
- Unit tests covering the tax display component, including the 0% hidden case.
