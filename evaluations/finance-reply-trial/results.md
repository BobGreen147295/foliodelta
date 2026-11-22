# Can Finance reopen the source rows from the first reply?

Two independent AI recipients each received two fictional CSVs and a generated English draft. Each was asked to check the CSVs, including their financial status fields, and answer Finance’s closure question. The recipients were given only their respective packets. The rubric was written before each trial. The scores below use the first substantive answer, with no coaching or follow-up.

| Check | First draft, CAD | Revised draft, GBP |
|---|---|---|
| Prioritize the first order and locate it | Partial. Identified TRIAL-785 but omitted its file and line. | Pass. Prioritized WAVE-819 and cited morning.csv line 3. |
| Explain the complete order-total change | Pass. Three changes sum to −55.00. | Pass. Three changes sum to −60.00. |
| Trace the refund in both files and verify statuses | Partial. Verified both statuses and amounts but omitted both lines. | Pass. Cited morning.csv line 2 and afternoon.csv line 4 for WAVE-817. Verified both statuses, the 4.00 increase and the unchanged order total. |
| Distinguish export evidence from closure | Pass. Kept the case open. | Pass. Kept the case open. |
| Assign the next check and request evidence | Pass. Requested source-store and payment checks. | Pass. Specified filters, cutoffs, order histories and the processor record. |

The first draft put source locations beside the individual examples. The revised draft also put the highest-priority order and the displayed refund references together on one line for forwarding. The first recipient preserved 0 of 3 required locations. The second preserved all 3 in the body of its reply. Its initial invocation ended at a service quota limit before producing an answer. Resuming the same assignment produced the first substantive reply.

These are two different fictional cases with different AI recipients. They show that the revised handoff worked once. They do not measure merchant adoption, time saved or the independent effect of changing the draft.

| Trial materials | Fixed criteria | Input and generated draft | First reply |
|---|---|---|---|
| Initial format | [Criteria](criteria.md) | [CAD packet](packet/) | [Reply](first-reply.md) |
| Revised format | [Criteria](v2/criteria.md) | [GBP packet](v2/packet/) | [Reply](v2/first-reply.md) |

To reproduce the revised draft from the repository root, run:

```sh
python skills/foliodelta/scripts/compare.py evaluations/finance-reply-trial/v2/packet/morning.csv evaluations/finance-reply-trial/v2/packet/afternoon.csv --finance-reply --review-refunds
```
