Finance should keep the case open. The closing export is CAD 55.00 lower, falling from CAD 167.00 to CAD 112.00. Three orders account for the full difference:

| Order | Change in exported order total |
|---|---|
| TRIAL-785 | −CAD 46.00. Appears only in the opening export. |
| TRIAL-784 | −CAD 21.00. Its total fell from CAD 91.00 to CAD 70.00. Both exports show `paid` and CAD 0.00 refunded. |
| TRIAL-787 | +CAD 12.00. Appears only in the closing export. |

Across the two orders present in both files, recorded refunds rose by CAD 6.50, all on TRIAL-786. It was already `partially_refunded` in the opening export, with CAD 1.00 refunded. The closing export shows the same status and CAD 7.50 refunded. Its order total stayed at CAD 30.00, so it contributed CAD 0.00 to the drop.

**Order Operations** should check both exports’ filters and cutoffs to explain why TRIAL-785 and TRIAL-787 appear only once, then verify what changed TRIAL-784’s total in the store. **Payments** should verify the status, amount, currency and date of the TRIAL-786 refund against the transaction record. Finance can close once those checks explain the order differences and confirm the refund outcome.
