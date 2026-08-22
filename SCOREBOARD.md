# Scoreboard

> ### ▶ NEXT ACTION
> **Open decision — not yet resolved.** v1 was CUT (Sharpe 0.434 vs the 0.88 bar).
> But it *did* cut drawdown 22.8% → 17.2% and has positive expectancy
> (54% win rate, 1.88 profit-loss ratio), so the entry rule is not noise —
> it is simply out of the market too much during a historic bull run.
>
> The choice to make:
> **(a)** sweep v1's lookback to see whether the failure is the *parameter* or the
> *idea* — cheap, and the plateau shape is informative either way; or
> **(b)** accept trend-following underperforms a raging bull market on a single
> long-only index, and change something structural instead.
>
> *(Claude: keep this block updated at the end of every session. It is the first
> thing to read when Seb comes back after a gap.)*

---

**This file is the actual output of the project.** Not the code — the code is just how we got here.

Read this first to see where things stand. Rules for filling it in are in [README.md](README.md) §5 and §6.

- **Build window:** 2010-01-01 → 2018-12-31 (all development happens here)
- **Holdout window:** 2019-01-01 → today (**untouched so far** — one look, at the end)
- **Instrument:** QQQ
- **Starting cash:** $100,000
- **Costs:** Interactive Brokers fee model, margin account — on in every version

---

## Build window results

| v | Commit | Pre-reg: "this helps if…" | CAGR | Max DD | Sharpe | Trades | vs prev | Verdict |
|---|---|---|---|---|---|---|---|---|
| v0 | `2277fc1` | *(baseline — nothing to beat yet)* | 15.44% | -22.80% | 0.73 | 1 | — | **baseline** |
| v1 | `77a8ef9` | Sharpe ≥ 0.88 **and** drawdown no worse than 22.80% | 6.61% | -17.20% | 0.434 | 87 | Sharpe −0.30 | **CUT** |
| v1s | | | | | | | | |
| v2 | | | | | | | | |
| v3a | | | | | | | | |
| v3b | | | | | | | | |
| v4 | | | | | | | | |
| v5 | | | | | | | | |

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

---

## Parameter sweeps

When testing a range of values, record the **shape**, not just the winner. A plateau means the idea is real; a lone spike means it's noise.

### (none yet)

| Version | Parameter | Values tested | Shape | Chosen | Why |
|---|---|---|---|---|---|
| | | | | | |
