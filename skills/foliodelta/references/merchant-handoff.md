# Which colleague can answer this?

Use the operator's actual question to pick the next source. The CLI provides evidence from two files. The roles below are suggestions for a small merchant team; the operator decides who takes the case.

| Colleague's question | What to check next | What would settle this question? |
|---|---|---|
| Operations: “Did we lose an order?” | Use the reported order name and line, confirm the same store and check each export's date window, timezone and status filters. Look up that order in the original order system. | A source record plus the export settings can explain an exclusion. Presence on one side alone leaves the explanation open. |
| Support: “The customer returned it. Was money sent back?” | Look for the return event in the order timeline and a separate successful refund transaction. Match order/payment reference, currency, amount and date. Allow for partial or multiple refunds. | A return authorization establishes a return request. Report a refund only to the extent supported by the matched payment evidence. To explain the file delta also verify the export's amount definition and timing. |
| Finance: “Why was our bank deposit smaller?” | Ask for the processor's payout ID and included balance transactions, fees, adjustments and posting dates. Match that payout to the bank deposit. | Two order exports can identify candidate orders. The deposit comparison needs settlement evidence in the same currency. |
| Trading team: “Our Black Friday orders and payment dashboard disagree. Which is right?” | Ask which store and payment account the dashboard covers, live or test mode, timezone, comparison window and metric. An order created before midnight may be paid after midnight. Request the relevant payment reference and timestamp for the disputed order. | Match the account, mode, currency and event window first. Order creation time alone leaves payment success and its date unknown. |
| Reporting: “Totals match. Can we close this?” | Read every populated review group. Offsetting increases and decreases or time-only differences may survive a zero net change. Inspect the indicated source rows and check creation times against the report cutoff. | Describe the file comparison as reconciled only for the fields actually checked. Record a colleague's acceptance only after they confirm it. |

For an English handoff, give the observed amount and direction, affected orders and source lines, one specific evidence request, and the suggested role. If the cause is unknown, state what is missing. Keep a draft's recipient decision open.
