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

## Merchant operations review, 20 November 2026

Stars below were observed through GitHub's repository API. They apply to each repository; adoption by individual merchant teams is unknown.

| Original workflow | Repository stars | Adaptation |
|---|---:|---|
| [Stripe's Black Friday / Cyber Monday merchant dashboard](https://github.com/stripe/ai/blob/main/providers/agent-plugins/plugin/skills/stripe-bfcm-dashboard/SKILL.md) | 2,075 | Ask which payment account, live/test mode, event and comparison window a peak-season report measures before comparing it with orders. |
| [Anthropic Finance reconciliation](https://github.com/anthropics/knowledge-work-plugins/blob/main/finance/skills/reconciliation/SKILL.md) | 36,595 | Give the recipient all exception groups, their contribution, a suggested role and a specific evidence request. No adjustment or resolution is inferred. |
| [Shopify AI Toolkit](https://github.com/Shopify/Shopify-AI-Toolkit/blob/main/skills/shopify/SKILL.md) | 652 | Separate an aggregate reporting question from an individual order lookup. Keep the file calculation offline. |
| [Stripe integration in wshobson/agents](https://github.com/wshobson/agents/blob/main/plugins/payment-processing/skills/stripe-integration/SKILL.md) | 42,717 | A return or order-total change leaves the refund question open; request the corresponding payment evidence. |

The executable scenario uses two synthetic exports with equal totals. Ten changed amounts offset each other, one order has only a timestamp change, and two one-sided records cancel out. The CLI must expose all four categories although the English detail section displays only ten orders. This regression exercises the handoff someone would receive.
