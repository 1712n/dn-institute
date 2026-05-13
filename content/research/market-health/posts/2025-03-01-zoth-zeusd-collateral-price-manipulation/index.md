---
title: "Zoth ZeUSD Collateral Price Manipulation and LTV Mismatch"
date: 2025-03-01
entities:
  - Zoth
  - ZeUSD
  - Uniswap V3
  - USDC
  - Ethereum
---

## Summary

The March 2025 Zoth ZeUSD incident is a useful market-health case because the loss did not depend only on a broken access-control check. Public analyses describe an attacker using Uniswap V3 price manipulation to make Zoth's `mintWithStable()` flow record more collateral than was actually received after an internal swap. The protocol then allowed ZeUSD minting and later withdrawal against that overstated collateral record.

The reported numbers are small compared with later 2025 DeFi exploits, but the mechanism is important:

- SolidityScan and Verichains describe a March 1, 2025 attack transaction against Zoth's ZeUSD minting path.
- The reported profit was about $285,000, while Nominis lists the impact at $286,000.
- SolidityScan reports that the manipulated swap returned only 7,669 collateral tokens while Zoth recorded 330,979 collateral tokens.
- The root accounting mismatch was that LTV validation used the initial stablecoin `amount`, not the actual `collateralReceived` after the swap.
- Nominis classifies the incident as lack of slippage protection and a smart-contract vulnerability.

For market-health analysis, the important lesson is that a DeFi protocol can turn a temporary liquidity distortion into a balance-sheet event if it lets a manipulated swap output become a trusted collateral input. This is not only a contract-bug story. It is a case where market depth, slippage controls, collateral accounting, and stablecoin backing were one risk surface.

## Market-health surface

Zoth's ZeUSD product was built around a minting path where a user could deposit a stablecoin such as USDC, have that stablecoin swapped into a collateral asset, and receive ZeUSD based on the resulting collateral value. In a healthy design, the minting limit should depend on the actual collateral received after the swap, plus an independent check that the execution price and received quantity are within acceptable bounds.

The exploit path inverted that relationship. Public writeups say the protocol validated loan-to-value limits against the input amount instead of the post-swap collateral quantity. When the attacker distorted the relevant Uniswap V3 pool, the swap returned much less collateral than the protocol expected, but Zoth still credited the attacker as if the full collateral value had arrived.

That made the market surface broader than the `mintWithStable()` function itself:

- the external Uniswap V3 pool supplied the executable price path;
- the Zoth minting contract converted that path into collateral metadata;
- ZeUSD minting created a claim against the protocol;
- burning ZeUSD later converted the inflated metadata into withdrawable collateral.

The useful surveillance boundary is therefore not "is the contract audited" or "is the pool liquid" in isolation. The boundary is whether a one-transaction price distortion can move a protocol's collateral ledger enough to create underbacked stablecoin supply.

## Attack mechanics

The public attack flow can be expressed as a replay of a manipulated collateral accounting path:

1. The attacker distorted the relevant Uniswap V3 pool before using Zoth's stablecoin minting path.
2. The attacker called `mintWithStable()` with a large stablecoin deposit.
3. Because the pool price had been moved, the swap returned far fewer collateral tokens than the protocol should have required.
4. Zoth's validation logic checked the input `amount` instead of the actual `collateralReceived`.
5. Zoth recorded the position as if it had received 330,979 collateral tokens, while public analyses report an actual received quantity of 7,669 collateral tokens.
6. The attacker minted ZeUSD against the overstated collateral record.
7. The attacker burned ZeUSD and withdrew collateral that had not been economically deposited.

The difference between the recorded and actual collateral values is the market-health signal. A protocol-local ledger accepted a price-impacted execution result without verifying the output amount or imposing a slippage bound. Once that ledger value was accepted, the exploit no longer required a persistent market price. The attacker only needed the manipulated state to survive long enough to mint and redeem.

## Evidence table

| Signal                                                                                       | Source                                                                                                                                                                                  | Market-health value                                                                     |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Reported exploit loss of about $285,000                                                      | [SolidityScan](https://blog.solidityscan.com/zoth-hack-analysis-80ba3ac5076b/), [Verichains](https://blog.verichains.io/p/anatomy-of-a-hack-how-a-simple-logic)                         | Establishes the direct economic impact of the collateral accounting mismatch.           |
| Nominis impact estimate of $286,000                                                          | [Nominis](https://www.nominis.io/insights/crypto-security-incidents-march-2025)                                                                                                         | Provides an independent incident-summary estimate and classification.                   |
| Attack transaction `0xc3f70057e261af554c6acf6a372389899f0c2d7d1ebd27311e39525dee88fb39`      | [Etherscan](https://etherscan.io/tx/0xc3f70057e261af554c6acf6a372389899f0c2d7d1ebd27311e39525dee88fb39), [SolidityScan](https://blog.solidityscan.com/zoth-hack-analysis-80ba3ac5076b/) | Anchors the case to an on-chain transaction for replay and trace reconstruction.        |
| Actual collateral received reported as 7,669 tokens                                          | [SolidityScan](https://blog.solidityscan.com/zoth-hack-analysis-80ba3ac5076b/), [Verichains](https://blog.verichains.io/p/anatomy-of-a-hack-how-a-simple-logic)                         | Shows the low post-swap collateral outcome after price manipulation.                    |
| Recorded collateral reported as 330,979 tokens                                               | [SolidityScan](https://blog.solidityscan.com/zoth-hack-analysis-80ba3ac5076b/), [Verichains](https://blog.verichains.io/p/anatomy-of-a-hack-how-a-simple-logic)                         | Shows the ledger value used for minting and withdrawal did not match actual collateral. |
| Root cause described as LTV validation using input `amount` rather than `collateralReceived` | [SolidityScan](https://blog.solidityscan.com/zoth-hack-analysis-80ba3ac5076b/)                                                                                                          | Identifies the invariant that a detector or test should enforce.                        |
| Incident type classified as lack of slippage protection                                      | [Nominis](https://www.nominis.io/insights/crypto-security-incidents-march-2025)                                                                                                         | Connects the contract bug to an executable market-depth and slippage problem.           |

## Replay packet

A useful replay packet for this incident should include `tx_hash`, `block_number`, `attacker`, `zoth_contract`, `mint_function`, `input_stablecoin`, `input_amount`, `swap_pool`, `pool_price_before`, `pool_price_after`, `pool_liquidity_before`, `pool_liquidity_after`, `collateral_expected`, `collateral_received`, `collateral_recorded`, `zeusd_minted`, `zeusd_burned`, `collateral_withdrawn`, `profit_usd`, and `downstream_fund_movements`.

The companion `incident-metrics.csv` is shaped as this replay packet so the row can be joined directly against Etherscan traces, the SolidityScan/Verichains collateral mismatch, and Zoth ledger effects. The most important join is between swap execution data and Zoth's internal collateral metadata. Looking only at the Uniswap pool would show price impact, but not necessarily protocol loss. Looking only at ZeUSD minting would show token issuance, but not necessarily why it was underbacked. The exploit becomes visible when the replay joins:

- the manipulated pool state;
- the actual collateral quantity returned by the swap;
- the collateral quantity recorded by Zoth;
- the ZeUSD amount minted and later burned;
- the final collateral withdrawal.

That replay packet turns the incident into a reusable market-health test: every mint path that depends on a swap should prove that recorded collateral is less than or equal to verified received collateral after slippage checks.

## Detection controls

### Post-swap collateral invariant

The first detector is a simple invariant check:

`recorded_collateral &lt;= collateral_received_after_swap`

If units differ, the comparison should be made in a normalized collateral-value unit with a trusted reference price. The key point is that the ledger cannot credit a user based on the pre-swap input amount when the minting asset is the post-swap collateral. Any positive gap between recorded collateral and received collateral is a direct undercollateralization signal.

For a live protocol, this should not be only an off-chain alert. The minting function should reject the transaction if the received collateral is below the minimum required amount for the ZeUSD being minted. The detector is still useful off-chain because it can find existing positions whose recorded collateral exceeds verified incoming assets.

### Slippage and liquidity-depth gate

The second detector compares the expected swap output with the actual output. For any stablecoin-to-collateral mint path, the protocol should set a minimum acceptable collateral output before the swap executes. Off-chain surveillance can mirror this by tracking:

- current pool liquidity;
- recent realized volatility;
- expected output for the submitted input amount;
- actual output returned by the swap;
- percent shortfall between expected and actual collateral.

If a ZeUSD mint path accepts a large shortfall and still mints against the input amount, the monitor should classify the transaction as a collateral-accounting failure, not merely a high-slippage trade. High slippage is the market symptom; the dangerous state transition is the protocol crediting unreceived collateral.

### Same-transaction mint and redeem stress signal

The exploit path matters because the attacker could transform a short-lived pool distortion into permanent extraction. A generic detector should flag transactions or tightly linked transaction groups where the same actor:

- creates or benefits from a large pool price distortion;
- calls a minting function that depends on the distorted price path;
- receives stablecoin or collateral credit above actual delivered value;
- burns or redeems the minted asset shortly afterward;
- exits with collateral or stable assets.

This signal does not require proving intent. It identifies a structural market-health risk: a temporary execution price was allowed to become a trusted collateral state and then a withdrawal claim.

### Stablecoin backing monitor

ZeUSD's risk surface was larger than the individual attacker profit because the minting path could create underbacked supply. A stablecoin market-health monitor should therefore track:

- total ZeUSD minted through swap-backed flows;
- aggregate recorded collateral backing those mints;
- verified on-chain collateral received by the backing contracts;
- slippage-adjusted collateral value;
- deviations between internal collateral records and independently reconstructed balances.

If recorded backing grows faster than verified collateral inflows, the stablecoin should be treated as balance-sheet stressed even before market price moves. In this incident, the attacker exploited the gap quickly, but the same invariant would also catch slower leakage.

### Repeated-incident context

Gate Research reported that Zoth later suffered a separate March 21, 2025 incident involving admin control and a malicious upgrade. That later incident should not be merged with the ZeUSD collateral-price manipulation case, but it is useful context for risk scoring. A protocol that experiences a market-driven collateral-accounting exploit and then a separate privileged-upgrade loss in the same month should receive a higher operational-risk score until controls, keys, upgrade paths, and minting invariants are all revalidated.

## Lessons

The Zoth ZeUSD case shows why market-health systems need to watch the handoff between execution markets and protocol accounting. A manipulated Uniswap V3 price was not enough by itself to create the loss. The loss came from a minting system that trusted the wrong variable after the swap.

For surveillance, the durable invariant is straightforward: if a protocol mints a stablecoin against collateral obtained through a swap, the minting limit must be based on verified post-swap collateral, not on the user's input amount or on an assumed execution path. Slippage, liquidity depth, and collateral metadata should be analyzed together because an attacker only needs one accepted mismatch to turn temporary price manipulation into permanent protocol loss.

## References

- SolidityScan, [Zoth Hack Analysis](https://blog.solidityscan.com/zoth-hack-analysis-80ba3ac5076b/), March 2025.
- Verichains, [Anatomy of a Hack: How a Simple Logic Flaw Led to a $285k Exploit on Zoth](https://blog.verichains.io/p/anatomy-of-a-hack-how-a-simple-logic), July 28, 2025.
- Nominis, [Crypto Security Incidents: March 2025 Overview](https://www.nominis.io/insights/crypto-security-incidents-march-2025), 2025.
- Gate Research, [Security Incident Summary for March 2025](https://www.gate.com/research/article/gate-research-security-incident-summary-for-march-2025), 2025.
- Etherscan, [Zoth attack transaction](https://etherscan.io/tx/0xc3f70057e261af554c6acf6a372389899f0c2d7d1ebd27311e39525dee88fb39).
