I can sign off on the $29.50 decrease in exported order totals. The cause remains open. I matched the order IDs in both CSVs and counted CASE-541’s total once per file because its second line is an item with a blank total. Each export contains four orders. The earlier total is $184.40 and the later total is $154.90, all in USD.

Three orders explain the difference. CASE-542 appears only in the earlier file (−$52.00), where it shows `paid` and $0.00 refunded. CASE-545 appears only in the later file (+$35.00). CASE-541 fell from $78.40 to $65.90 (−$12.50) and shows `paid` with $0.00 refunded in both files.

The only recorded refund change among matched orders was on CASE-543. Its refunded amount rose from $5.00 to $13.25, but its status was already `partially_refunded` in the earlier file and its order total stayed at $34.00. That $8.25 increase contributes $0.00 to the change in exported totals.

Please keep the case open. Order Operations should start with CASE-542 in the store and check the later export’s filters and cutoff, then check CASE-545 against the earlier export’s settings and review CASE-541’s edit history. Payments should verify successful refund transactions for CASE-541 and CASE-543 by order ID, amount, currency and date. The packet contains neither the store history and export settings nor the payment records needed to close the case.
