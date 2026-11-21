# Input contract

Supply two UTF-8 CSV files from the same store. A UTF-8 BOM and quoted commas are supported. The command accepts either schema per file. All column names are case-sensitive and must be unique.

| Schema | Required columns | Row meaning |
|---|---|---|
| Shopify orders | `Name`, `Created at`, `Total`, `Currency` | One order summary. A following row with the same order name, a nonempty `Lineitem name` and all three summary values empty is an item continuation. Ambiguous rows stop the comparison. |
| Normalized | `order_id`, `created_at`, `total`, `currency` | One row per order. Keep the same identifier semantics in both files. |

Order names are case-sensitive. Use the same store and order naming scheme on both sides. Other fields, including contact details, are excluded from output. Order names, amounts, timestamps and source row numbers **are included**. A row number is the starting physical line in the original file including its header.

Amounts use a decimal point and no thousands separators. Supported currencies are USD, EUR, GBP, CAD, AUD, NZD, CHF, SGD, HKD and CNY at two decimal places, JPY at zero and KWD at three. Trailing zeroes may exceed the currency precision. Values with nonzero excess precision are rejected. The two files must use one currency. Creation times require a numeric UTC offset or Z; equal instants in different time zones match. A validated header-only file can be compared to a populated file; two empty files have no currency.

Default output covers order presence, recorded total and creation time. A change in item mix with the same order summary is outside this contract.

With `--review-refunds`, both native exports need the `Refunded Amount` column. The additional `recorded_refunds` JSON section compares the field on shared order names when both values are numeric. A blank is unknown, an explicit zero is known, and one-sided orders are excluded. A nonempty refund on a continuation row is ambiguous and stops the review. The net change covers comparable orders only; with none it is null. Positive and negative changes describe right minus left. The text shows up to ten changed refund values; JSON includes every changed value and both source lines for matched orders with blanks. Payment success, timing, settlement and the reason for a difference require transaction evidence.

The English handoff shows up to ten orders ranked by absolute difference. The JSON includes every changed record, including time-only changes. Totals in both formats cover the entire input.

`review_groups` covers all changed orders once. One-sided rows are grouped by side even if their amount is zero. For orders present on both sides an amount change takes precedence over a simultaneous timestamp change. Within each group, `increase_minor` is nonnegative and `decrease_minor` is signed and nonpositive. Their sum across groups is the reported right-minus-left delta. Suggested roles are unassigned.

Shopify documents that additional line items appear on separate rows with many fields blank. Confirm the exported layout when a shop uses a custom reporting app. [Shopify order exports](https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders)
