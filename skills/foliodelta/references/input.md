# Input contract

Supply two UTF-8 CSV files from the same store. A UTF-8 BOM and quoted commas are supported. The command accepts either schema per file. All column names are case-sensitive and must be unique.

| Schema | Required columns | Row meaning |
|---|---|---|
| Shopify orders | `Name`, `Created at`, `Total`, `Currency` | One order summary. A following row with the same order name, a nonempty `Lineitem name` and all three summary values empty is an item continuation. Ambiguous rows stop the comparison. |
| Normalized | `order_id`, `created_at`, `total`, `currency` | One row per order. Keep the same identifier semantics in both files. |

Order names are case-sensitive. Use the same store and order naming scheme on both sides. Other fields, including contact details, are excluded from output. Order names, amounts, timestamps and source row numbers **are included**. A row number is the starting physical line in the original file including its header.

Amounts use a decimal point and no thousands separators. Supported currencies are USD, EUR, GBP, CAD, AUD, NZD, CHF, SGD, HKD and CNY at two decimal places, JPY at zero and KWD at three. Trailing zeroes may exceed the currency precision. Values with nonzero excess precision are rejected. The two files must use one currency. Creation times require a numeric UTC offset or Z; equal instants in different time zones match. A validated header-only file can be compared to a populated file; two empty files have no currency.

Output covers order presence, recorded total and creation time only. A change in item mix with the same order summary is outside this contract. Refund totals, payment settlements, fees and fulfillment require separate sources. Eligibility for payout and why a difference occurred remain open.

The English handoff shows up to ten orders ranked by absolute difference. The JSON includes every changed record, including time-only changes. Totals in both formats cover the entire input.

Shopify documents that additional line items appear on separate rows with many fields blank. Confirm the exported layout when a shop uses a custom reporting app. [Shopify order exports](https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders)
