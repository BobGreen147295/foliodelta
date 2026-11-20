# FolioDelta

**Trace an order export discrepancy to the rows an operator should check first.** FolioDelta compares two same-store CSVs locally, ranks changes by their absolute contribution to the difference, and produces an English handoff or structured JSON. It works with a coding agent or directly in a terminal.

For an example, a finance colleague notices that two exports each contain three orders, yet the second total is $46.50 lower. Which records should someone open? Is there enough evidence to attribute the difference to refunds?

## Try the fictional case

Clone the repo and run from its root with Python 3.10 or later. On Windows, `py -3` can replace `python`. The comparison uses the Python standard library.

```sh
git clone https://github.com/BobGreen147295/foliodelta.git
cd foliodelta
python skills/foliodelta/scripts/compare.py skills/foliodelta/examples/before.csv skills/foliodelta/examples/after.csv
```

| First checks | File evidence | Contribution |
|---|---|---:|
| DEMO-721 | Before, line 4 only | −60.00 USD |
| DEMO-723 | After, line 5 only | +18.50 USD |
| DEMO-720 | Line 2 in both files, total falls from 84.75 to 79.75 | −5.00 USD |

The totals are 169.75 and 123.25 USD. Those three changes account for the −46.50 USD file difference. To investigate a refund claim, check the export filters and consult the order's refund transactions. The exports alone leave that explanation open.

## Use with Codex

```sh
npx skills add BobGreen147295/foliodelta --skill foliodelta -a codex
```

Open the target project in a new agent session and ask:

> Use $foliodelta on the bundled example. Finance thinks refunds explain the lower total. Give me an English handoff with source lines and the next check.

For a manual project install, copy the complete `skills/foliodelta` directory into your project's `.agents/skills/`. The installed directory includes the executable script, input contract and demo. [Skill definition](skills/foliodelta/SKILL.md)

## Use on a business task

Start with two exports you are authorized to compare. The files can be outside this repository. Keep their order explicit. To produce a report for local review, run:

```sh
python skills/foliodelta/scripts/compare.py "first export.csv" "second export.csv" > handoff.txt
python skills/foliodelta/scripts/compare.py "first export.csv" "second export.csv" --json
```

1. The operator checks store identity, time window and zone, order status filters, order ID meaning, and amount definition. Leave scope unconfirmed until these agree. Add `--scope-confirmed` to record the operator's declaration.
2. Open the listed source lines, starting with the largest differences. Follow up on time-only changes even if the grand total matches. A comparison error exits with status 2 and emits no report to stdout.
3. Use the next check in the handoff to ask the responsible colleague for the missing evidence. Keep the actual acceptance and outcome in your team's own task system.

Shopify order exports and four-column normalized files are supported. Money is compared in currency minor units; no exchange rate is inferred. CSVs with an ambiguous repeated order summary stop with a source line. The CLI runs locally without accounts or network access. Output contains order identifiers; review it before sharing. A cloud agent reading the output has its own data handling. [Input contract and supported currencies](skills/foliodelta/references/input.md)

## Evidence and design

Run `python -m unittest discover -s tests -v`. Tests exercise the command a user runs, including a 10,000-order synthetic case, mixed currency, duplicate summaries, timezone-equivalent timestamps, an empty export, and offsetting changes. An independent agent also completed the fictional finance handoff from outside the repo. [Evaluation and product decisions](evaluation.md)

中文使用场景：同店两份 Shopify 订单导出的金额对不上，先用本地脚本定位哪几单、哪几行贡献了差额，再由运营核查导出口径和源订单。可要求代理用中文解释，并保留英文交接单给海外同事。

Distributed under the [MIT license](LICENSE).
