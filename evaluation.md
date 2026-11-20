# What has been tested

The first user is an operator already responsible for explaining conflicting order exports to finance or a shop owner. The deliverable is a ranked list of records and source lines plus the next evidence check. This allows a colleague to open the relevant rows directly.

## Agent trial

On 20 November 2026 an independent Codex session received the skill, bundled input paths and an English finance question. It executed the CLI from another working directory. The agent located the largest difference on line 4 of the first file and correctly described the other two contributions. It treated the refund explanation as unknown and requested refund transactions. When asked about deposits, it identified a separate need for transaction-level payout data. All orders were fictional.

The trial exposed a handoff problem: the first CLI version relied on the agent to label the demonstration. Someone forwarding the text alone could lose that context. The CLI now labels output from the bundled example pair, including JSON. A regression test checks the standalone output.

## First merchant acceptance task

Use a shop's already-open discrepancy, with permission. Record the operator's usual method and a baseline they can substantiate. Ask them to use the tool and share only whether the suggested order and source line located the issue, what they still needed, and whether the recipient could take the next step. Record elapsed time only when actually observed. A second task requested by the merchant and a purchase decision are separate observations. Real merchant use, time savings and willingness to pay are unmeasured.

## Design sources

| Source | Decision in FolioDelta |
|---|---|
| [Agent Skills specification](https://github.com/agentskills/agentskills) | Package the entry point, bundled examples, script and on-demand contract in a portable directory. |
| [Vercel skills CLI](https://github.com/vercel-labs/skills) | Make the named skill selectable for a particular agent and project. |
| [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | Test with a plausible finance question and a neighboring task outside scope. Run the CLI and check observable outputs. |
| [Error Discovery](https://github.com/ai-evals-course/evals-skills/tree/main/skills/error-discovery) | Start from the actual claim, expose supporting or missing evidence, and preserve a concrete failing observation for regression. |
| [Shopify order export reference](https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders) | Distinguish order totals from item continuation rows and from settlement transactions. |

Implementation, skill text and fictional examples were written for this project.
