---
date: 2026-05-05
entities:
  - id: elephant-money
    name: Elephant Money
    type: defi-protocol
  - id: elephant-token
    name: ELEPHANT Token
    type: cryptocurrency
  - id: binance-smart-chain
    name: Binance Smart Chain
    type: blockchain
title: "Elephant Money flash loan exploit on BSC: ELEPHANT/WBNB reserve manipulation and $11.2M treasury drain"
---

## Introduction

Elephant Money was a decentralized finance protocol on Binance Smart Chain (BSC) that operated a yield-generating ecosystem centered around the ELEPHANT token. The protocol offered several financial products including Elephant Treasury (a reserve-backed token buyback and burn mechanism), Stampede (a bond-style investment product paying fixed yields), and Elephant Futures (a leveraged synthetic product). The protocol's economic model relied on a flywheel where trading fees and Treasury operations provided yield to stakers and bond holders, funded by continuous buy pressure on the ELEPHANT token through automated buyback operations.

On April 13, 2022, an attacker exploited a vulnerability in Elephant Money's Treasury contract, using flash loans to manipulate the ELEPHANT/WBNB liquidity pool reserves and trick the Treasury into executing buybacks at artificially manipulated prices. The exploit drained approximately $11.2 million (27,416.46 WBNB) from the Elephant Treasury contract across two transactions. The vulnerability was in the Treasury's price calculation mechanism, which read spot reserves from the ELEPHANT/WBNB PancakeSwap pool rather than using manipulation-resistant price feeds, allowing the attacker to inflate the apparent value of ELEPHANT tokens relative to WBNB immediately before triggering a Treasury buyback.

## Background

### Elephant Money Economic Model

Elephant Money's economic model was built around a tax-and-redistribute mechanism common in "rebase" and "reflection" tokens on BSC. Every ELEPHANT token transfer incurred a tax (typically 10%), with the tax proceeds distributed across several sinks: a portion went to existing ELEPHANT holders as reflections, a portion was added to the ELEPHANT/WBNB PancakeSwap liquidity pool to deepen trading liquidity, and a portion was sent to the Elephant Treasury for buyback and burn operations.

The Elephant Treasury was the protocol's primary value accrual mechanism. It accumulated WBNB (wrapped BNB) from trading taxes and other protocol revenue, then used these WBNB reserves to periodically buy ELEPHANT tokens from the PancakeSwap pool and burn them. The buyback mechanism was designed to create sustained buy pressure on ELEPHANT, supporting its price and reducing the circulating supply over time. The Treasury held significant WBNB reserves (tens of millions of dollars at its peak) that were programmatically deployed for buyback operations.

### Treasury Buyback Mechanics

The Treasury contract's buyback function operated as follows: when triggered (either by an automated keeper or a manual call), the Treasury would determine how much WBNB to spend on ELEPHANT purchases, query the current ELEPHANT/WBNB price from the PancakeSwap pool, execute a swap of WBNB for ELEPHANT tokens through the PancakeSwap router, and burn the acquired ELEPHANT tokens (sending them to a dead address).

The critical design element was how the Treasury determined the swap parameters. Rather than using an external oracle (like Chainlink) or a time-weighted average price, the Treasury contract read the PancakeSwap pool's current reserve balances to calculate the expected swap output. This meant the Treasury relied on spot pool reserves — the same values that could be manipulated by anyone executing large swaps in the same pool within the same transaction.

### Flash Loan Availability on BSC

By April 2022, flash loans were readily available on BSC through PancakeSwap (forked from Uniswap V2's flash swap mechanism), Venus Protocol, and various other lending platforms. The combination of flash loan capital availability and the Treasury's reliance on spot pool reserves created a classic oracle manipulation vulnerability.

## The Attack

### Vulnerability: Spot Reserve-Based Price in Treasury Buyback

The core vulnerability was that the Elephant Treasury contract used the PancakeSwap pool's spot reserves (queried via `getReserves()` on the pair contract) to determine the parameters for its buyback swap. When the Treasury initiated a buyback, it calculated the expected output based on the current pool state — not a historical average or an external oracle feed.

This created a manipulation vector: if an attacker could change the pool's reserve ratio immediately before triggering the Treasury's buyback function, the Treasury would calculate its swap based on the manipulated reserves. If the attacker inflated the price of ELEPHANT relative to WBNB in the pool (by buying large amounts of ELEPHANT), the Treasury's buyback calculation would determine that WBNB was undervalued relative to ELEPHANT, and would spend its WBNB reserves on a swap that received fewer ELEPHANT tokens than it should at the true market price.

However, the actual exploit path was more subtle. The attacker manipulated the pool to make it appear that ELEPHANT was cheap relative to WBNB, causing the Treasury to spend more WBNB on the buyback than it would at fair value. The key insight was that the attacker could profit by being on the other side of the Treasury's overpayment — selling ELEPHANT at the inflated price that the Treasury was buying at.

### Attack Execution

The attack was executed across two transactions on April 13, 2022:

**Step 1: Flash loan acquisition.** The attacker obtained a large flash loan of WBNB from PancakeSwap. The borrowed WBNB provided the capital needed to significantly manipulate the ELEPHANT/WBNB pool reserves.

**Step 2: Pool reserve manipulation.** The attacker used the flash-loaned WBNB to buy a massive amount of ELEPHANT tokens from the PancakeSwap pool. This dramatically shifted the pool's reserves — the WBNB reserve decreased and the ELEPHANT reserve increased, making ELEPHANT appear cheap (low price in terms of WBNB) according to the pool's constant-product invariant.

**Step 3: Treasury buyback trigger.** With the pool in a manipulated state (ELEPHANT appearing artificially cheap), the attacker triggered the Treasury's buyback function. The Treasury read the manipulated reserves, concluded that ELEPHANT was trading at a bargain price, and executed a large buyback — spending a significant portion of its WBNB reserves to buy ELEPHANT at what it calculated to be a favorable rate.

**Step 4: Reverse manipulation.** After the Treasury's buyback pushed WBNB into the pool (partially restoring the reserve ratio), the attacker sold the ELEPHANT tokens they had purchased in Step 2 back to the pool. Because the Treasury had just added WBNB to the pool (through its buyback), the pool now had more WBNB available for the attacker to extract.

**Step 5: Flash loan repayment and profit extraction.** The attacker repaid the WBNB flash loan and retained the profit — the difference between what the Treasury spent from its reserves and what the attacker's manipulation cost. The net extraction from the Treasury was approximately 27,416 WBNB (roughly $11.2 million at the time).

**Step 6: Second transaction.** The attacker repeated the process in a second transaction, extracting additional value from the Treasury's remaining reserves. The combined extraction across both transactions totaled approximately $11.2 million.

### Transaction Details

The two exploit transactions consumed significant gas and involved complex multi-step swap sequences within each transaction. On-chain analysis confirmed that the attacker's wallet was funded with a small amount of BNB from a privacy-enhanced source, and the stolen WBNB was subsequently converted and laundered through multiple intermediary wallets and cross-chain bridges.

## Impact

### Financial Losses

The Elephant Treasury lost approximately 27,416 WBNB ($11.2 million), representing a significant portion of its total reserves. These reserves were the protocol's primary mechanism for supporting the ELEPHANT token price and generating yield for stakers and bond holders. The loss of Treasury reserves meant that the protocol's buyback mechanism was severely impaired, reducing the buy pressure that supported ELEPHANT's price.

### Token Price Collapse

The ELEPHANT token price dropped approximately 90% following the exploit, from roughly $0.000000094 to below $0.000000010. The collapse was driven by several factors: the immediate loss of Treasury buyback support (removing the protocol's primary price floor mechanism), panic selling by ELEPHANT holders who lost confidence in the protocol, and cascading liquidations in the Stampede and Futures products that depended on ELEPHANT price stability.

The Stampede bond product, which promised fixed yields to depositors funded by Treasury operations, became insolvent as the Treasury's WBNB reserves were drained. Stampede depositors faced losses on both their principal (denominated in ELEPHANT, which had lost 90% of its value) and their expected yields (which could no longer be funded without Treasury reserves).

### Impact on BSC Tax Token Ecosystem

The Elephant Money exploit reinforced concerns about the security model of "tax token" protocols on BSC, which typically relied on automated Treasury operations that interacted with PancakeSwap pools. Many similar projects (SafeMoon forks, reflection tokens with buyback mechanisms) used analogous designs where a Treasury contract read spot pool reserves to execute buybacks. The Elephant Money exploit demonstrated that this entire category of protocols was potentially vulnerable to the same flash loan manipulation vector.

Several competing protocols preemptively modified their Treasury contracts to use TWAPs or external oracles following the Elephant Money incident, though the decentralized and largely unaudited nature of the BSC tax token ecosystem meant that many vulnerable contracts remained deployed.

## Response and Remediation

### Immediate Response

The Elephant Money team acknowledged the exploit within hours and paused all Treasury operations. They published an initial post-mortem identifying the spot reserve manipulation vector and confirmed the total losses. The team communicated through their official channels that the core ELEPHANT token contract and PancakeSwap liquidity pool were not compromised — users could still trade ELEPHANT, but the Treasury-funded yield products were impaired.

### Treasury Redesign

The team implemented a comprehensive redesign of the Treasury's buyback mechanism. Key changes included replacing spot reserve-based price calculations with a time-weighted average price (TWAP) that tracked the ELEPHANT/WBNB price over a 15-minute window, making single-transaction manipulation ineffective; implementing a maximum buyback size per transaction, capped as a percentage of the pool's total liquidity to prevent outsized swaps that would move the price significantly; adding a price deviation circuit breaker that paused buyback operations if the current spot price deviated more than 5% from the TWAP (indicating potential manipulation); and implementing a cooldown period between buyback operations to prevent rapid sequential buybacks within the same block or time window.

### Recovery Efforts

The Elephant Money team launched a phased recovery plan that included rebuilding Treasury reserves through protocol fee accumulation (a slow process given the reduced TVL), implementing a "recovery mode" for the Stampede product that reduced yield payments to match available funding, and gradually restoring buyback operations at reduced scale as Treasury reserves recovered.

The recovery was slow — months of fee accumulation were required to rebuild a fraction of the lost reserves — and the protocol never fully recovered to its pre-exploit scale. TVL remained at approximately 10-20% of pre-exploit levels, reflecting both the direct losses and the lasting damage to user confidence.

## Technical Analysis

### Spot Reserve Manipulation in Buyback Mechanisms

The Elephant Money exploit demonstrates a specific vulnerability pattern that affects any protocol with an automated buyback mechanism that reads spot pool reserves. The pattern requires three conditions: a Treasury or reserve contract that holds significant value (WBNB in this case), a buyback function that uses spot pool reserves to determine swap parameters, and the ability for any external caller to trigger the buyback function (or the function being triggered automatically via a keeper).

When all three conditions are met, a flash loan attacker can manipulate the pool, trigger the buyback (causing the Treasury to overpay), and profit from the mispricing. The defense is to break any of the three conditions: use manipulation-resistant price feeds instead of spot reserves, restrict who can trigger buybacks (reducing to authorized keepers), or implement rate limits that bound the maximum value at risk in any single buyback operation.

### TWAP as a Defense for Automated Operations

Time-weighted average prices offer a strong defense against flash loan manipulation because they require the manipulated price to be sustained over the averaging window — something that is impossible within a single transaction (flash loans must be repaid within the same transaction). A 15-minute TWAP means an attacker would need to sustain the price manipulation for 15 minutes while continuously paying for the manipulation (through arbitrage losses), making the attack economically infeasible for any reasonable Treasury size.

However, TWAPs are not a perfect defense. They can be slowly manipulated over multiple blocks by a well-capitalized attacker willing to sustain losses (multi-block attacks, recently demonstrated on Ethereum L2s). They also introduce latency — the TWAP lags behind the true market price during rapid moves, which can cause the Treasury to execute buybacks at stale prices during volatile markets. Despite these limitations, TWAPs represent a significant improvement over spot reserves for automated Treasury operations.

### Comparison with Similar Treasury Exploits

The Elephant Money exploit belongs to a category of attacks targeting automated Treasury or buyback mechanisms. Similar incidents include the BUNNY token flash loan exploit (May 2021, approximately $45 million) on PancakeBunny, where the attacker manipulated the BUNNY/BNB pool price to trick the protocol's yield distribution mechanism into minting an excessive number of BUNNY tokens; the Beanstalk governance exploit (April 2022, approximately $182 million), where a flash loan was used to acquire governance voting power to drain the protocol's Treasury through a malicious governance proposal (a different mechanism but similar economic outcome); and various smaller BSC tax token Treasury drains throughout 2021-2022, most of which went unreported due to the projects' small size and anonymous teams.

## Lessons Learned

### Never Use Spot Reserves for Value-Sensitive Operations

The most direct lesson is that spot AMM pool reserves must never be used as price inputs for operations involving significant protocol funds. This applies to Treasury buybacks, liquidation calculations, NAV computations, and any other operation where a manipulated price can cause the protocol to transfer value in a direction favorable to the manipulator. TWAP oracles, Chainlink feeds, or multi-source price aggregation are minimum requirements for any such operation.

### Rate Limit Automated Fund Operations

Even with manipulation-resistant price feeds, automated Treasury operations should be rate-limited to bound the maximum value at risk in any single operation or time window. A Treasury that can only spend 1% of its reserves per hour limits the maximum extraction from any single manipulation attempt to 1% of reserves, regardless of how severe the price manipulation is.

### Separate Price Discovery from Execution

A more robust Treasury design separates the price determination from the execution: the Treasury determines the buyback price in one transaction (or over multiple blocks), and executes the swap in a subsequent transaction only if the price has remained stable. This two-phase approach prevents single-transaction flash loan manipulation entirely, as the manipulation cannot be sustained between the price determination and execution phases.

### Audit Tax Token Treasury Mechanisms

The proliferation of tax tokens with automated buyback mechanisms on BSC created a large category of potentially vulnerable protocols. Many of these projects launched without formal audits, assuming that the simplicity of the buyback logic (read reserves, execute swap) did not warrant audit-level scrutiny. The Elephant Money exploit demonstrated that even simple automated operations can be catastrophically vulnerable when they rely on manipulable inputs.

## Conclusion

The Elephant Money flash loan exploit of April 13, 2022, drained approximately $11.2 million (27,416 WBNB) from the protocol's Treasury contract on BSC through manipulation of the ELEPHANT/WBNB PancakeSwap pool reserves used by the Treasury's automated buyback function. The attacker used flash-loaned WBNB to distort the pool's reserve ratio, triggered the Treasury's buyback at the manipulated price, and profited from the Treasury's overpayment by reversing the manipulation after the buyback executed. The vulnerability — reliance on spot AMM reserves for a value-sensitive automated operation — was a well-documented attack vector that had affected numerous other protocols. The fix required migrating to a TWAP-based price feed with rate limits and circuit breakers, eliminating the single-transaction manipulation window. The incident reinforced that any automated protocol operation involving significant fund transfers must use manipulation-resistant price inputs, and demonstrated the systemic vulnerability of the BSC tax token ecosystem's widespread reliance on spot pool reserves for Treasury buyback calculations.
