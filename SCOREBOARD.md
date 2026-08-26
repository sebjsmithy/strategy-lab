# Scoreboard

> ### ▶ NEXT ACTION
> **Run `strategies/v2a_trend_basket.py` in QuantConnect** and bring back:
> Compounding Annual Return · Drawdown · Sharpe Ratio · Total Orders.
> Also check Exposure and Portfolio Margin — gross should stay at or below 100%.
>
> First paper-faithful version: 10-ETF basket, signal is the sign of past return
> blended equally across 1/3/12-month lookbacks, long and short, monthly rebalance,
> **equal weight (no vol-scaling)**. New build window 2008–2016.
>
> **Claude's pre-registered prediction:** positive but unspectacular, Sharpe
> roughly 0.3–0.6, with v2b beating it. KEEP bar is Sharpe ≥ 0.50.
>
> **When reading the result:** the build window includes 2008, an exceptional year
> for trend-following. Check the equity curve, not just the summary — a strong
> number carried entirely by one year is not the same as a consistent one.
>
> Then `v2b` adds volatility scaling — the single clean attributable comparison.
> Do not skip ahead to v4/v5.
>
> *(Claude: keep this block updated at the end of every session. It is the first
> thing to read when Seb comes back after a gap.)*

---

**This file is the actual output of the project.** Not the code — the code is just how we got here.

Read this first to see where things stand. Rules for filling it in are in [README.md](README.md) §5 and §6.

- **Build window:** **2008-01-01 → 2016-12-31** (all development happens here)
- **Holdout window:** **2017-01-01 → today** (**untouched** — one look, at the end)
- **Instruments:** v0–v1s used QQQ. **v2a onward: a 10-ETF basket** —
  `GLD SLV DBC DBA` (commodity) · `SPY EFA EEM` (equity) · `TLT IEF` (bond) · `UUP` (currency)
- **Starting cash:** $100,000
- **Costs:** Interactive Brokers fee model, margin account — on in every version

> **Window changed 2026-08-26**, before any multi-asset run. Was 2010–2018 build /
> 2019+ holdout. Reasons: (1) HOP 2017 shows 2010–2016 is the weakest decade for
> trend-following in a 137-year sample, so the old build window lacked regime
> variety — the new one contains the GFC, the euro crisis and the 2015–16 selloff;
> (2) the new holdout contains the COVID crash and the 2022 inflation shock, a far
> better exam. **Legitimacy check:** changed before running anything new, old
> holdout never looked at, reason drawn from the literature rather than from
> disappointing results. See README §4.
>
> v0–v1s numbers below were measured on the **old** 2010–2018 window and are kept
> for the record. They are not directly comparable to v2a onward.

---

## Build window results

| v | Commit | Pre-reg: "this helps if…" | CAGR | Max DD | Sharpe | Trades | vs prev | Verdict |
|---|---|---|---|---|---|---|---|---|
| v0 | `2277fc1` | *(baseline — nothing to beat yet)* | 15.44% | -22.80% | 0.73 | 1 | — | **baseline** |
| v1 | `77a8ef9` | Sharpe ≥ 0.88 **and** drawdown no worse than 22.80% | 6.61% | -17.20% | 0.434 | 87 | Sharpe −0.30 | **CUT** |
| v1s | `f304583` | Sharpe ≥ 0.88. Claude predicts **worse** than v1@40d (0.400) | **-2.18%** | **-47.20%** | **-0.097** | 108 | Sharpe −0.50 | **CUT** |
| **v2a** | | Sharpe ≥ 0.50. Claude predicts 0.3–0.6, and that v2b beats it | | | | | | pending |
| v2b | | Beats v2a on Sharpe by ≥ 0.15 (vol-scaling earns its place) | | | | | | queued |
| v3 | | robustness checks on whatever survives | | | | | | — |
| v4 | | Markov conviction scaling | | | | | | — |
| v5 | | regime-based strategy selection | | | | | | — |

**Verdict** is one of: `KEPT` · `CUT` · `baseline` · `pending`

A version is `KEPT` only if **all four** criteria in README §5 hold: Sharpe +0.15 or better, drawdown no worse, trade count sane, and survives a ±25% parameter nudge.

---

## Holdout results

**Do not fill this in until the build-window ladder is finished.** One run, then it's spent.

| v | Commit | CAGR | Max DD | Sharpe | Trades | Held up? |
|---|---|---|---|---|---|---|
| | | | | | | |

---

## Log

Short notes on what happened and why — especially for anything cut. A cut component with a recorded reason is a real finding.

### v0 — buy & hold baseline
- **Status:** DONE — this is the number to beat
- **File:** `strategies/v0_buy_hold.py` @ `2277fc1`
- **Result:** CAGR 15.44% · Max DD 22.80% · Sharpe 0.73 · 1 order
- **Detail:** bought 2,475 QQQ @ $40.27 on 2010-01-05, held to 2018-12-31.
  Start equity $100,000 → end equity $364,271.34. Total fees $12.38.
- **Notes:**
  - 2010–2018 was a strong bull run for the NASDAQ. A 15.4% CAGR here is the
    *market*, not skill. Any later version has to beat this to justify existing.
  - Sharpe 0.73 with a 22.8% drawdown is the honest cost of just owning the index.
  - `Alpha`, `Beta` and `Treynor Ratio` all report 0 — the benchmark comparison
    didn't populate. Cosmetic QC quirk; doesn't affect the four numbers we track.
  - `Win Rate` / `Loss Rate` / `Average Win` all show 0% because there are no
    *closed* trades. Expected for buy-and-hold, not a bug.
  - The runtime panel's "Net Profit" shows **-$12.38** (exactly the fees) because
    that field counts *realised* P&L only. Nothing was ever sold, so the entire
    $264,271.34 gain sits in "Unrealized". The Statistics panel's "Net Profit"
    of 264.271% is the real figure. Two different meanings, same label.

### v1 — Donchian 20/20, long only, binary size
- **Status:** CUT — failed its pre-registered bar
- **File:** `strategies/v1_donchian.py` @ `77a8ef9`
- **Raw result:** `Backtest recordings/v1_donchian.json`
- **Result:** CAGR 6.61% · Max DD 17.20% · Sharpe 0.434 · 87 orders
- **Pre-reg was:** Sharpe ≥ 0.88 and drawdown ≤ 22.80%. Sharpe came in at 0.434 —
  not just below the bar, below v0's 0.73. Clear fail on the primary criterion.
- **But read it properly — this is not a dead rule:**
  - **Drawdown did improve**, 22.80% → 17.20%. The strategy did exactly the job
    it was designed to do.
  - **Expectancy is positive (0.560).** Win rate 54%, average win 4.56% vs
    average loss −2.42%, profit-loss ratio 1.88. It wins more often than it
    loses, and its wins are bigger than its losses.
  - So the entry rule is **not noise**. The strategy underperformed on
    *opportunity cost* — sitting in cash through the strongest stretch of a
    historic bull market — not because the signal is meaningless.
- **The costs of trading became real:** fees $12.38 → $601.97, turnover
  0.03% → 2.07%, volume $99,670 → $8,427,349. This is why costs stay on.
- **Warning sign worth noting:** Drawdown Recovery 614 days vs v0's 238. The
  max drawdown was *smaller* but took far longer to climb out of — the
  signature of getting whipsawed in and out repeatedly.
- **PSR 1.929%** (v0: 13.135%). Probabilistic Sharpe Ratio — roughly, the
  confidence that the true Sharpe is above zero. Very low. Even this modest
  Sharpe is not statistically solid.

### v1s — Donchian 40/40, long AND short (the flip version)
- **Status:** CUT — the worst result in the project. It lost money.
- **File:** `strategies/v1s_donchian_long_short.py` @ `f304583`
- **Result:** CAGR **−2.177%** · Max DD **47.20%** · Sharpe **−0.097** · 108 orders
- **Start $100,000 → end $82,018.17.** Net profit −17.98%. Fees $492.77.
- **Prediction was correct, and then some.** Claude pre-registered "worse than v1
  long-only at 40d (0.400), far worse than v0 (0.730)". Actual: −0.097. The
  prediction did not anticipate an outright loss.

**Where the money went — the win rate collapse:**

| | v1 @ 40d (long only) | v1s @ 40/40 (long+short) |
|---|---|---|
| Sharpe | 0.400 | **−0.097** |
| CAGR | 7.01% | **−2.18%** |
| Max drawdown | 26.5% | **47.20%** |
| Win rate | **65%** | **37%** |
| Orders | 42 | 108 |
| Profit-loss ratio | 1.54 | 1.54 |

The per-trade edge is *unchanged* — profit-loss ratio is 1.54 in both. Average win
8.24% vs average loss −5.35% is still asymmetric in the right direction. What broke
is **frequency**: win rate fell from 65% to 37%. The ~66 extra trades the short leg
introduced were overwhelmingly losers, because they were shorting an index that
rose 264% over the window. Expectancy went from +0.560 (v1 @ 20d) to **−0.064**.

**Other observations:**
- **Drawdown 47.20%** — more than double v0's 22.80%. The flip mechanic means you
  are always fully exposed, so being wrong costs full freight with no cash buffer.
- **The equity curve peaked in early 2011 (~$120k) and never made a new high.**
  The "Drawdown Recovery: 184" figure is therefore not meaningful here — the
  strategy spent the entire remaining 8 years underwater.
- **PSR 0.004%** — effectively zero confidence the Sharpe is above zero.
- **Shorts were free in this test** (no borrow costs modelled). Real costs would
  make it worse still, so the rejection holds a fortiori — exactly the reasoning
  used to justify running it without the cost model.
- Research Guide moved to "10 Parameters — Possible Overfitting", up from 8,
  because two lookback variables were declared instead of one. Cosmetic.

**Conclusion:** the Donchian rule family is now rejected on QQQ in both
configurations — long/flat and long/short. The problem is not the parameter and not
the direction logic. See "Where next" below.

---

## Parameter sweeps

When testing a range of values, record the **shape**, not just the winner. A plateau means the idea is real; a lone spike means it's noise.

### v1-sweep — Donchian lookback, 5 to 50 days

- **Raw data:** `Backtest recordings/V1Sweep.xlsx`
- **Held constant:** QQQ, long only, binary sizing, entry and exit both use the
  same lookback, 2010–2018, IB fees.

| Lookback | Sharpe | CAGR | Max DD | DD Recovery | Win rate | P/L ratio | Orders |
|---|---|---|---|---|---|---|---|
| 5 | 0.253 | 4.25% | 18.2% | 1285 | 45% | 1.61 | 343 |
| 10 | 0.087 | 2.07% | 17.3% | 645 | 39% | 1.95 | 191 |
| 15 | 0.158 | 3.00% | 24.4% | 1143 | 45% | 1.73 | 132 |
| **20** | **0.434** | **6.61%** | **17.2%** | **614** | **54%** | **1.88** | **87** |
| 30 | 0.279 | 4.83% | 23.5% | 914 | 58% | 1.41 | 67 |
| 40 | 0.400 | 7.01% | 26.5% | 816 | 65% | 1.54 | 42 |
| 45 | 0.419 | 7.39% | 27.2% | 875 | 65% | 1.61 | 39 |
| 50 | *n/a* | ~6.89%¹ | *n/a* | *n/a* | *n/a* | *n/a* | *n/a* |
| **v0** | **0.730** | **15.44%** | **22.80%** | **238** | — | — | **1** |

¹ 50-day stats panel would not load (free-tier UI issue). CAGR derived from the
reported end equity of $182,162.59 on $100,000 over 9 years. Treat as approximate.

**Shape — read it as a spike plus a plateau, not a single winner:**

```
 5d  0.253  ##########
10d  0.087  ###
15d  0.158  ######
20d  0.434  #################   <- lone spike, neighbours much worse
30d  0.279  ###########
40d  0.400  ################ }
45d  0.419  ################# }  <- genuine plateau, adjacent values agree
```

**Findings:**

1. **No lookback beats v0.** Best Sharpe in the family is 0.419 vs buy-and-hold's
   0.730; best CAGR is 7.39% vs 15.44%. The *idea* failed, not the parameter.
   This is a clean rejection, not an inconclusive result.
2. **v1's 0.434 at 20 days was partly luck.** It is a lone spike between 15 (0.158)
   and 30 (0.279). Had we defaulted to 15 or 30, v1 would have looked far worse.
   A cautionary note about trusting any single un-swept result.
3. **40/45 is the only trustworthy region** — adjacent values agree, and the
   estimated 50-day rolls back over, so it is a real hill rather than noise.
4. **There is no cell that wins on either axis.** Short lookbacks beat v0 on
   drawdown (17–18% vs 22.8%) but return almost nothing. Long lookbacks recover
   some return but their drawdown (26–27%) is *worse* than v0. The strategy's only
   advantage over buy-and-hold disappears exactly where its returns become
   tolerable.
5. **Win rate is the one clean monotonic relationship:** 39% → 45% → 54% → 58% →
   65% as lookback lengthens. Longer lookbacks genuinely produce fewer, better
   signals. Real effect, insufficient to rescue the strategy.
6. **Every variant recovers from drawdown far slower than v0** — 614 to 1,285 days
   versus 238. No exceptions. Whipsaw is systemic across the whole family.
7. **The 10-day hypothesis was rejected.** Predicted to reduce opportunity cost by
   staying invested more; came in worst of all (Sharpe 0.087). Whipsaw cost
   exceeded opportunity cost.
8. **Exposure charts confirm the v1 opportunity-cost diagnosis.** 5-day zips in and
   out constantly (343 orders); 45-day holds for long stretches (39 orders), and
   CAGR rises with holding period.

**Chosen:** nothing. No setting is carried forward. Plain long-only Donchian on a
single index is rejected for 2010–2018.

**Holdout status:** untouched. Nothing here earned a holdout run.
