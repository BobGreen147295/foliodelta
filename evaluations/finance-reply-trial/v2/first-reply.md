We can account for the full £60.00 decrease in exported order totals, from £152.50 in `morning.csv` to £92.50 in `afternoon.csv`. Please keep the reconciliation open until we verify the export scope and payment records.

- WAVE-819 accounts for −£85.00. It appears only in the morning export and is marked `paid` (morning.csv, line 3).
- WAVE-821 accounts for +£30.00. It appears only in the afternoon export and is marked `paid` (afternoon.csv, line 3).
- WAVE-820 accounts for −£5.00. Its total fell from £27.50 to £22.50, with `paid` and £0.00 refunded in both files (morning.csv, line 5 and afternoon.csv, line 2).

WAVE-817 stayed at £40.00 and was marked `partially_refunded` in both exports. Its recorded refund rose from £2.00 to £6.00, contributing £0.00 to the order-total difference (morning.csv, line 2 and afternoon.csv, line 4).

Order Operations should start with WAVE-819, verify both exports’ filters and cutoffs, and check the source order histories for WAVE-821 and WAVE-820. Payments should match WAVE-817’s £4.00 refund increase to the processor record and confirm its status, amount, currency and date before Finance confirms any money moved.
