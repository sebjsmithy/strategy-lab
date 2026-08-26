# Scoreboard

> ### ▶ NEXT ACTION
> **THE HOLDOUT RUN — this is the final experiment. Read [HOLDOUT.md](HOLDOUT.md) first.**
>
> Run these three files in QuantConnect, **once each**, and record the numbers:
>
> 1. `strategies/v0b_buyhold_basket_holdout.py` — **H0**, the benchmark
> 2. `strategies/v2a_holdout.py` — **H1**, trend signal, equal dollars
> 3. `strategies/v2b_holdout.py` — **H2**, trend signal, equal risk
>
> For each take: Compounding Annual Return · Drawdown · Sharpe · Total Orders.
> Also grab the equity curve for H2 — the *shape* matters as much as the number,
> specifically whether 2022 carries it.
>
> **THE RULE, and it is the one that matters:** after these three runs, change
> nothing and re-run nothing. No adjusting the lookback, no adding markets, no
> tweaking the vol target "just to see". The holdout is spent the moment it is
> read, and every temptation afterwards converts an out-of-sample test into an
> in-sample one — destroying the only clean evidence this project has.
>
> **Predictions are already committed** in HOLDOUT.md, timestamped before the run.
> Claude's record so far: wrong on v2a, right on v1s and v2b.
>
> **After this: write up the project.** Six build-window experiments plus a clean
> out-of-sample test, a literature basis, reproducible code with commit hashes,
> and a measured universe analysis. Whatever the numbers say, that is a real
> piece of work and a legitimate outcome.
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
| **v2a** | `0dffed2` | Sharpe ≥ 0.50. Claude predicted 0.3–0.6 — **wrong** | 0.79% | -17.10% | **-0.015** | 870 | — (new window) | **CUT** |
| **v2b** | `b754ab8` | Sharpe ≥ 0.135. Claude predicted "beats v2a, under 0.3" — **correct** | 1.52% | -10.20% | **0.048** | 856 | Sharpe **+0.063** | **CUT** |
| v3 | | robustness checks on whatever survives | | | | | | — |
| v4 | | Markov conviction scaling | | | | | | — |
| v5 | | regime-based strategy selection | | | | | | — |

**Verdict** is one of: `KEPT` · `CUT` · `baseline` · `pending`

A version is `KEPT` only if **all four** criteria in README §5 hold: Sharpe +0.15 or better, drawdown no worse, trade count sane, and survives a ±25% parameter nudge.

---

## Holdout results

**Do not fill this in until the build-window ladder is finished.** One run, then it's spent.

**Window: 2017-01-01 → 2025-12-31.** Pre-registered in [HOLDOUT.md](HOLDOUT.md)
before any run. Three arms, one run each.

| Run | File | What it is | CAGR | Max DD | Sharpe | Trades |
|---|---|---|---|---|---|---|
| **H0** | `v0b_buyhold_basket_holdout.py` | benchmark — equal weight, always long | | | | |
| **H1** | `v2a_holdout.py` | trend signal, equal dollars | | | | |
| **H2** | `v2b_holdout.py` | trend signal, equal risk | | | | |

`H0 → H1` isolates **the signal**. `H1 → H2` isolates **the sizing**.

Claude's pre-registered predictions: H2 Sharpe 0.2–0.5 · H2 > H1 · H0 highest raw
return · H1/H2 lower drawdown than H0 · lumpy curve with a 2022 jump · 2020 mixed.
Flagged in HOLDOUT.md as informed rather than blind.

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

### v2a — 10-ETF basket, blended 1/3/12-month trend, equal weight
- **Status:** CUT — failed its bar. But the most *informative* run so far.
- **File:** `strategies/v2a_trend_basket.py` @ `0dffed2`
- **Window:** 2008-01-01 → 2016-12-31 (new build window)
- **Result:** CAGR **0.791%** · Max DD **17.10%** · Sharpe **−0.015** · 870 orders
- **$100,000 → $107,353.73** over nine years. Fees $1,345.89. Turnover 1.78%.
- **Claude's prediction (0.3–0.6 Sharpe) was wrong.** Recorded as a miss.

**1. Positive return, negative Sharpe — not a contradiction.**
Sharpe is *excess* return over the risk-free rate, divided by volatility. The
strategy earned 0.79%/yr while cash over 2008–2016 paid roughly the same. Excess
return ≈ 0, so Sharpe ≈ 0. **It did not lose money; it earned nothing above cash
while carrying a 17% drawdown.** For a risk asset that is a failure.

**2. Essentially all the profit came from 2008.**
Reading the equity curve: ~$100k → ~$120k through late 2008, then eight years of
chop and decline to $107k. So roughly **+20% in year one and −11% over the
following eight.** This is exactly the "carried by one year" trap flagged in the
pre-registration. Strip 2008 and the strategy is clearly negative.

**3. The 2008-up / 2009-down shape is the textbook trend-following signature.**
Long trends into the 2008 crash, then run over by the violent V-shaped reversal in
March 2009. Every CTA had a bad 2009 for this reason. **This is mechanically
reassuring** — the strategy is behaving like a real trend-follower rather than
like noise. 2015–16 was weak for the same documented reason: choppy, directionless
markets with no sustained trends.

**4. Diversification worked — on risk, not on return.**

| | v1s (1 market) | v2a (10 markets) |
|---|---|---|
| Max drawdown | 47.20% | **17.10%** |
| Annual std dev | 14.9% | **7.4%** |
| Sharpe | −0.097 | −0.015 |

Risk fell by roughly two-thirds. The equity curve is far smoother. What
diversification did not do is manufacture return that was not there.

**5. Realised volatility is only 7.4% against the paper's 10% target.**
The portfolio is *under-risked* — long and short positions across markets offset
each other, so net exposure often sits near zero (visible in the Exposure chart,
long and short ratios both oscillating around 0.2–0.6). Relevant to v2b.

**6. Per-trade statistics collapsed, but are not comparable to v1/v1s.**
Win rate exactly 50%, average win 0.26% vs average loss −0.24%, profit-loss ratio
1.09, expectancy 0.036. Each market holds at most 10% of the book so trades are
small, and the blended signal produces frequent *partial* adjustments (+1 → +⅓)
rather than round trips. These numbers measure something different from the
Donchian versions — do not read the drop from 1.88 to 1.09 as a like-for-like
deterioration.

**7. Estimated strategy capacity fell to $7.1M** (v0: $130M, v1s: $490M), with
**DBA** named as the binding constraint. DBA is a thinly traded agriculture ETF.
Irrelevant at $100k, but it flags DBA as the weakest link in the universe.

**8. PSR 0.012%** — effectively zero confidence the Sharpe is above zero.

**What this does and does not tell us.** It does not reject trend-following: the
strategy behaved correctly, and 2010–2016 is the weakest decade in the papers'
137-year sample. It does say that **an equal-dollar-weighted version of it earned
nothing above cash in this era**, and that its one good year was the one crisis in
the window.

### v2b — same basket and signal, volatility-scaled sizing
- **Status:** CUT — improved on every metric, but fell short of the bar.
- **File:** `strategies/v2b_trend_basket_volscaled.py` @ `b754ab8`
- **Result:** CAGR **1.518%** · Max DD **10.20%** · Sharpe **0.048** · 856 orders
- **$100,000 → $114,527.38.** Fees $1,326.48. Turnover 1.76%.
- **Pre-reg bar was Sharpe ≥ 0.135.** Actual 0.048 — a real improvement of +0.063,
  but less than half the required 0.15. **CUT on the rule as written.**
- **Claude's prediction was correct this time:** "beats v2a, but probably still
  under 0.3." (Claude was wrong on v2a.)

**Vol scaling worked. It improved literally every metric:**

| | v2a (equal $) | v2b (equal risk) | Change |
|---|---|---|---|
| Sharpe | −0.015 | **0.048** | +0.063 |
| CAGR | 0.791% | **1.518%** | **+92%** |
| Max drawdown | 17.10% | **10.20%** | **−40%** |
| Annual volatility | 7.4% | **5.5%** | −26% |
| Expectancy | 0.036 | **0.104** | **+189%** |
| Profit-loss ratio | 1.09 | **1.24** | +14% |
| End equity | $107,354 | **$114,527** | +$7,173 |
| PSR | 0.012% | 0.029% | — |

Nearly double the return on a quarter less risk, with a 40% smaller drawdown.
That is not noise — it is a systematic improvement in exactly the direction
predicted from the measured 4.7× volatility spread (see `UNIVERSE.md`).

**The clearest way to see it:** raw return per unit of volatility went from
0.791/7.4 = **0.107** to 1.518/5.5 = **0.276** — roughly **2.6× better**. Sharpe
understates this because it subtracts the risk-free rate, which over 2008–2016
consumed most of a 1.5% return.

**So why is it still CUT?** Because vol scaling fixed the *sizing*, and the
sizing was never the main problem. **A better-sized version of a strategy with no
edge is still a strategy with no edge.** 1.518% a year is roughly what cash paid.

**On the win rate being below 50%** (49% win / 51% loss): this is normal and
expected for trend-following, not a warning sign. Real trend-followers typically
win 35–45% of the time. What matters is that average win (0.23%) exceeds average
loss (0.18%), giving a profit-loss ratio of 1.24 and **positive expectancy that
nearly tripled** from v2a. You win less often and win bigger. Win rate read alone
is meaningless.

**One metric got worse: Drawdown Recovery 1,218 days** (v2a: 206). Smaller
drawdowns, but far longer to climb out of them — a mechanical consequence of
lower volatility, since a calmer strategy grinds back more slowly. Worth noting
as the cost of the improvement.

**2015 onward is a genuine bleed.** Equity peaked around $122k in early 2015 and
finished at $114.5k. This matches the documented weakness of trend-following in
choppy, trendless markets, and matches the papers' per-decade table showing
2010–2016 as the weakest stretch in 137 years.

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
