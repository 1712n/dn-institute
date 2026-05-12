---
title: "Four.Meme Launch Liquidity Sandwich Attack"
date: 2025-03-18
entities:
  - Four.Meme
  - PancakeSwap
  - BNB Chain
  - BNB
  - SBL
---

## Summary

The March 2025 Four.Meme incident is a useful market-health case because the loss came from launch-market structure, transaction visibility, and liquidity-pool initialization rather than a normal post-launch trading loss. Public reports describe an attacker pre-calculating the PancakeSwap pair address, using Four.Meme functionality to obtain or position tokens before launch, and then sandwiching the official add-liquidity transaction when Four.Meme seeded the pool.

The reported facts converge on the same market pattern:

- Four.Meme temporarily suspended and then resumed its launch function on March 18, 2025.
- PANews, BTCC/99Bitcoins, and CyberMaterial describe the loss as roughly $120,000.
- BTCC/99Bitcoins reports that the attacker left with at least 192 BNB and sent funds to FixedFloat.
- CertiK's cited SBL example described a 21.1 BNB profit from sandwiching the add-liquidity transaction at launch.
- PANews, citing SlowMist commentary, described the root cause as leakage of Four.Meme's add-liquidity transaction to PancakeSwap rather than a vulnerability in all contracts.
- ExVul's cited analysis described the attack as a market manipulation technique using a pre-calculated liquidity-pair address and token transfer restriction bypass.

For market-health analysis, this incident is important because the official launch transaction became a predictable price anchor. If an attacker can see or infer the launch liquidity transaction before final ordering, seed an imbalanced future pair, and bracket the liquidity addition, the first tradable price is not a fair launch price. It is an attacker-shaped state.

## Market-health surface

Four.Meme is a BNB Chain memecoin launch platform. Its critical market-health surface is the transition from pre-launch token restrictions to a live PancakeSwap pool. In that transition, a small number of state changes determine whether the first public price is neutral:

- the future pair address;
- balances already sitting at that future pair address;
- the official add-liquidity transaction;
- the first executable swap path;
- token transfer restrictions before launch;
- private or semi-private transaction visibility through builders, relays, or mempool infrastructure.

Reports describe the attacker exploiting this launch boundary. The attacker did not need a long-lived price oracle or a large after-market position. The attack was concentrated around the first liquidity event, when pool balances and initial price are most fragile.

That makes the incident different from routine MEV on an existing pool. Existing pools usually have observable liquidity depth, historical volatility, and arbitrage paths. A launch pool can have almost no market history. If a pair address can be predicted and seeded before launch, and if the official liquidity transaction can be observed or bundled against, then the market opens already manipulated.

## Attack mechanics

The public reports support the following replay:

1. The attacker pre-calculated the future PancakeSwap pair address for a Four.Meme-launched token.
2. The attacker used a Four.Meme function or launch-path behavior to obtain or position some pre-launch tokens despite transfer restrictions.
3. The attacker sent an imbalanced quantity of tokens to the future pair address before the legitimate pool was created.
4. Four.Meme prepared or submitted its official add-liquidity transaction to seed the PancakeSwap pool.
5. That add-liquidity transaction became visible or leaked through transaction-ordering infrastructure.
6. The attacker bundled transactions around the liquidity addition, sandwiching the launch and extracting value as the initial pool price was distorted.
7. The attacker withdrew at least 192 BNB, worth about $120,000 according to BTCC/99Bitcoins, and moved the funds onward.

In the SBL example cited by CertiK and reported by BTCC/99Bitcoins, the attacker sent a small amount of SBL to the pre-calculated pair address and profited 21.1 BNB by sandwiching the add-liquidity transaction. The number is smaller than the overall incident estimate, but it is a useful concrete replay of the mechanism: a future pair address held an unexpected token balance before the official launch path created the market.

## Evidence table

| Signal                                                                                                                   | Source                                                                                                                                                      | Market-health value                                                                              |
| ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Four.Meme resumed operations after a reported $120,000 sandwich attack                                                   | [BTCC/99Bitcoins](https://www.btcc.com/en-US/square/99bitcoinsEN/183333), [CyberMaterial](https://cybermaterial.com/four-meme-attack-results-in-120k-loss/) | Establishes the loss estimate and confirms the attack was tied to launch operations.             |
| SlowMist-linked report says the add-liquidity transaction leaked and was bundled into a sandwich attack                  | [PANews](https://www.panewslab.com/en/articles/sfh2sqa9)                                                                                                    | Identifies transaction privacy and ordering as core market-health controls.                      |
| ExVul-linked report says the attacker pre-calculated the liquidity-pair address and bypassed token transfer restrictions | [BTCC/99Bitcoins](https://www.btcc.com/en-US/square/99bitcoinsEN/183333)                                                                                    | Connects predictable pair creation to pre-launch manipulation.                                   |
| CertiK-linked SBL example reports 21.1 BNB profit from sandwiching an add-liquidity transaction                          | [BTCC/99Bitcoins](https://www.btcc.com/en-US/square/99bitcoinsEN/183333)                                                                                    | Provides a concrete token-level example of the launch manipulation sequence.                     |
| Attacker proceeds reported as at least 192 BNB, worth about $120,000                                                     | [BTCC/99Bitcoins](https://www.btcc.com/en-US/square/99bitcoinsEN/183333)                                                                                    | Quantifies the extracted value and links it to BNB rather than only USD reporting.               |
| Four.Meme had a prior February 2025 exploit with about $183,000 in losses                                                | [BTCC/99Bitcoins](https://www.btcc.com/en-US/square/99bitcoinsEN/183333)                                                                                    | Shows repeated launch/liquidity risk and raises the monitoring priority for subsequent launches. |

## Replay packet

A useful replay packet for this incident should include `launch_token`, `token_contract`, `factory`, `predicted_pair_address`, `pair_creation_tx`, `official_add_liquidity_tx`, `add_liquidity_submit_time`, `add_liquidity_inclusion_time`, `builder_or_relay_path`, `prelaunch_token_balance_at_pair`, `prelaunch_base_balance_at_pair`, `token_transfer_restriction_state`, `attacker_prefund_tx`, `attacker_buy_tx`, `attacker_sell_tx`, `attacker_profit_bnb`, `attacker_profit_usd`, `post_attack_destination`, and `affected_user_compensation_status`.

The key join is between a future pair-address balance and the official liquidity transaction. Looking only at the final swap trace would label the event as a sandwich. Looking only at the launch transaction would miss the fact that the pair was already poisoned. The market-health failure is visible when the replay shows unexpected token inventory at the future pair address before Four.Meme's legitimate liquidity addition.

## Detection controls

### Future pair-address balance monitor

Launchpads should calculate the future pair address before launch and monitor it as a protected surface. Before adding liquidity, the launch controller can check:

- whether the predicted pair address already holds the launch token;
- whether it already holds the base token;
- whether any address other than the launch controller transferred assets there;
- whether balances differ from the expected zero or initialization values.

If the future pair address is already imbalanced, the launch should abort and rotate parameters where possible. This is a cheap pre-flight check and directly targets the mechanism described in the SBL example.

### Add-liquidity transaction privacy

The official add-liquidity transaction is a high-value target because it reveals the timing and size of the first tradable market. A market-health control should treat that transaction as sensitive orderflow:

- avoid broadcasting it through public paths where possible;
- simulate builder or private-relay leakage scenarios;
- monitor whether the transaction is observed before inclusion;
- use commit-reveal or delayed activation when feasible;
- reject launch if a competing bundle appears around the same pair and token.

The goal is not to eliminate all MEV. The goal is to prevent an attacker from turning the platform's own launch transaction into the middle leg of a sandwich.

### Pre-launch transfer restriction audit

Reports describe the attacker bypassing token transfer restrictions by using a function path and a pre-calculated pair address. A launchpad should test transfer restrictions against future pair addresses, not only against ordinary user-to-user transfers. Useful test cases include:

- transferring launch tokens to a pair address before the pair exists;
- buying through launch functions and then routing tokens to the predicted pair;
- creating a pair with dust or imbalanced inventory;
- checking whether token restrictions still apply when the receiver is a future liquidity pool.

The relevant invariant is simple: before official launch, no non-controller account should be able to seed the future trading pair with launch tokens or base assets.

### Initial price sanity check

At launch, the pool's initial price should be determined only by the official liquidity ratio. A launch monitor can reconstruct:

- expected token/base ratio from the official add-liquidity parameters;
- actual pool balances immediately after pair creation;
- first swap price;
- deviation between expected and realized first executable price.

If the first executable price materially differs from the official ratio because of pre-existing balances, the launch should be paused and the pool treated as contaminated. This check is especially important for memecoin launches, where early price movement can attract traders before they understand the launch state.

### Repeated-platform risk signal

Four.Meme had a separate February 2025 exploit before the March sandwich incident. A market-health system should increase platform-level risk when similar launch or liquidity failures repeat within a short window. The signal should not assume the same attacker or exact root cause. It should indicate that the platform's launch controls, transaction-ordering assumptions, and compensation processes need renewed scrutiny before new tokens are allowed to rely on the same launch path.

## Lessons

The Four.Meme incident shows that market manipulation can happen before a market is fully live. Launchpads often focus on post-launch trading controls, but the first price can already be compromised if the pair address is predictable, pre-launch transfer restrictions can be bypassed, and the official liquidity transaction is visible to searchers or builders.

For surveillance, the durable invariant is that a future launch pair should be empty and controlled until the official launch transaction initializes it. Any unexpected pre-funding, pair-address dusting, or transaction bundle around the add-liquidity event should be treated as a launch integrity failure, not merely ordinary MEV.

## References

- PANews, [Four.Meme loses around $120,000 in hacker attack](https://www.panewslab.com/en/articles/sfh2sqa9), March 18, 2025.
- BTCC/99Bitcoins, [BNB Chain's Four.Meme Resumes Operations After $120K Sandwich Attack](https://www.btcc.com/en-US/square/99bitcoinsEN/183333), March 19, 2025.
- CyberMaterial, [Four Meme Attack Results in $120K Loss](https://cybermaterial.com/four-meme-attack-results-in-120k-loss/), March 21, 2025.
