# strategy-lab

**A trend-following trading strategy, built from published academic research, tested properly, and found not to work.**

*By Seb, with Akram supplementing in the early stages.*

Six experiments across two market eras, with success criteria written down before each run and nine years of data held back untouched for a single final test. The strategy failed. This repository is the complete record of how that was established — code, results, reasoning, and a scorecard of every prediction that turned out wrong.

📄 **[Read the full write-up](writeup.html)** — the whole investigation in plain English, no finance background needed.

---

## The result

Tested out-of-sample on 2017–2025, against simply buying and holding the same ten markets:

| | Benchmark | Strategy | |
|---|---:|---:|---|
| Annual return | **8.58%** | 2.62% | |
| Maximum drawdown | −16.8% | **−12.9%** | strategy better |
| Sharpe ratio | **0.448** | −0.239 | |
| Final equity | **$209,911** | $126,216 | from $100,000 |

The strategy reduced risk and genuinely protected in both years the benchmark lost money — in 2022 it gained 5.8% while the benchmark fell 6.5%. But across nine years it surrendered roughly **six percentage points of annual return to save four points of drawdown**. A bad trade at any risk tolerance.

**The hypothesis was falsified by a criterion set in advance.** The working theory had been that the strategy underperformed because 2008–2016 was, by the papers' own data, the weakest decade for trend-following in 137 years. It performed *worse* in the era containing COVID and the 2022 inflation shock. The era was not the problem.

---

## Contents

1. [What the strategy does](#1-what-the-strategy-does)
2. [How it was tested](#2-how-it-was-tested)
3. [Every experiment](#3-every-experiment)
4. [What was learned](#4-what-was-learned)
5. [Repository map](#5-repository-map)
6. [Reproducing this](#6-reproducing-this)
7. [Notes for AI assistants](#7-notes-for-ai-assistants)
8. [Glossary](#8-glossary)

---

## 1. What the strategy does

### In one paragraph

> Buy ten different things. Every month, look at each one and ask a simple question: has the price been going up recently, or down? If it's been going up, bet it keeps going up. If it's been going down, bet it keeps going down. Do this for all ten independently, at the same time. Most of these bets are small losers. A few catch a big move and pay for all the rest.

### The ten markets

Each is an ETF — a fund bought like a share, which owns a pile of something on your behalf.

| Ticker | What you actually own |
|---|---|
| **GLD** | Gold bars in a vault |
| **SLV** | The same, but silver |
| **DBC** | A basket of commodity contracts — oil, petrol, metals, crops. Mostly energy |
| **DBA** | Farm goods only — corn, wheat, soybeans, sugar, coffee |
| **SPY** | The 500 biggest US companies |
| **EFA** | Big companies outside North America — Europe, Japan, Australia |
| **EEM** | Big companies in developing countries — China, India, Brazil, Korea |
| **TLT** | US government debt repaid in 20+ years. Moves a lot with interest rates |
| **IEF** | The same, but repaid in 7–10 years. Moves less |
| **UUP** | The US dollar against other currencies |

Four commodity, three equity, two bond, one currency — mirroring the roughly 43% commodity weighting of the source papers, and diversifying *across* asset classes rather than within.

Measured correlations show these ten behave like about **five independent bets**: the three equity funds move together (0.88–0.92), the two bond funds move together (0.91), gold and silver move together (0.80). Full analysis in [UNIVERSE.md](UNIVERSE.md).

### The signal, precisely

For each market, at each monthly rebalance, using only data available on that date:

```
S₁   = sign(return over past 21 trading days)     ≈ 1 month
S₃   = sign(return over past 63 trading days)     ≈ 3 months
S₁₂  = sign(return over past 252 trading days)    ≈ 12 months

position = (S₁ + S₃ + S₁₂) / 3        →  one of −1, −⅓, +⅓, +1
```

Each signal is binary, and the three are equal-weighted, so position size scales with how much the timescales agree:

| S₁ | S₃ | S₁₂ | Position |
|---|---|---|---|
| + | + | + | **+1.00** full long |
| + | + | − | **+0.33** small long |
| − | + | − | **−0.33** small short |
| − | − | − | **−1.00** full short |

That gives conviction-weighting for free: when short and long horizons disagree — precisely when trends are ambiguous and whipsaw is most costly — the position is small.

It also **removes parameter selection entirely.** No lookback is chosen, so there is nothing to sweep and nothing to overfit. The weights are equal by design; optimising them would reintroduce the problem.

### Where it comes from

- **Moskowitz, Ooi & Pedersen (2012)**, *Time Series Momentum*, Journal of Financial Economics — 58 futures markets, 1985–2009.
- **Hurst, Ooi & Pedersen (2017)**, *A Century of Evidence on Trend-Following Investing*, Journal of Portfolio Management — 67 markets, 1880–2016.

Both papers are in [`Academic Papers/`](Academic%20Papers/) with distilled methodology notes in [NOTES.md](Academic%20Papers/NOTES.md).

The line that shaped this project: across 67 markets and 137 years, the strategy returned positively in *every single market*, at an average Sharpe of about **0.4**. Real — but far too weak to detect in one market over nine years. That is why single-asset tests of trend-following are uninformative, and it is what the early experiments here got wrong.

---

## 2. How it was tested

The methodology matters more than the strategy, and it is the part of this repository most worth reading.

### Split the data, look once

| Window | Dates | Use |
|---|---|---|
| **Build** | 2008-01-01 → 2016-12-31 | All development. Hundreds of backtests. |
| **Holdout** | 2017-01-01 → 2025-12-31 | Read **once**, at the very end. |

The holdout is a one-shot exam. Every peek makes it less honest, because you begin unconsciously tuning toward it.

**These windows were changed once, on 2026-08-26, before any multi-asset run** — from an original 2010–2018 / 2019+ split. The reasoning is recorded in full rather than quietly applied: the original build window lacked regime variety (no crash), while the new holdout contains COVID and the 2022 inflation shock, making a far better exam.

The legitimacy test applied at the time: the change was made *before* running anything new, the old holdout was never looked at, and the reason came from the literature rather than from disappointing results. **Changing a window because results were bad is data-snooping. Changing it beforehand for documented reasons of regime coverage is experimental design.**

### Say what success means before running

Every version has its success criterion written into its docstring *before* it runs. Holdout predictions were committed with a timestamp — see [HOLDOUT.md](HOLDOUT.md), which also states in advance what result would falsify the project's own explanation.

Without this, you get a number and rationalise backwards into why it was what you expected. Everyone does this. Writing it first is the only defence.

### What earns a place

A version replaces its predecessor only if **all** of these hold:

1. **Sharpe improves meaningfully** — +0.15 or better. Not +0.03; that is noise wearing a decimal point.
2. **Maximum drawdown does not get worse.**
3. **Trade count is sane** — not 4 (no sample), not 5,000 (fees eat you alive).
4. **It survives a ±25% nudge** to its main parameter.

Fail any one, and it is cut with the reason recorded. **A cut component is a finding, not a failure.**

### Read the shape, not the peak

When sweeping a parameter:

```
GOOD (plateau)          BAD (spike)
10  ####                10  #
20  ######              20  #
30  ######              23  ########   <- noise
40  #####               30  #
```

A plateau means the *idea* works and the exact number does not much matter. A lone spike is a coincidence. This project learned it the hard way — see v1-sweep below.

### Every number is reproducible

Each row in [SCOREBOARD.md](SCOREBOARD.md) carries the git commit hash of the code that produced it. `git checkout <hash>` restores the exact files, which can be pasted into QuantConnect to regenerate the result.

Without that, a recorded number is a rumour: six weeks later you cannot say whether fees were on, which lookback was live, or what the dates were. The real risk is not fraud but **drift** — tweak, run, tweak, run, and eventually write down a good number without being able to say what produced it. Hashes make drift impossible.

Each version also lives in **its own file, never edited after the fact.**

### Platform

**QuantConnect**, running the open-source **LEAN** engine, because backtesting is deceptively hard to get right and almost every subtle way to get it wrong makes results look *better*:

| Trap | What it is | LEAN's answer |
|---|---|---|
| Look-ahead bias | Using information that was not yet public | Point-in-time data |
| Survivorship bias | Only testing companies that still exist | Includes delisted securities |
| Ignoring costs | Forgetting fees, spreads, slippage | Modelled by default |
| Backtest ≠ live | Simulation differs from real execution | Identical code path |

Interactive Brokers commission model and a margin account on every run. No version was ever tested without costs.

---

## 3. Every experiment

### Phase 1 — a single market (QQQ, 2010–2018)

A Donchian breakout: buy at the 20-day high, sell at the 20-day low.

| Version | What it was | Return | Drawdown | Sharpe | Verdict |
|---|---|---:|---:|---:|---|
| **v0** | Buy & hold QQQ | 15.44% | −22.8% | 0.730 | baseline |
| **v1** | Breakout, long only | 6.61% | −17.2% | 0.434 | cut |
| **v1-sweep** | Every lookback, 5–50 days | 7.39% | −27.2% | 0.419 | cut |
| **v1s** | Breakout, long *and* short | −2.18% | −47.2% | −0.097 | cut |

Three distinct lessons:

**v1 — the rule was not broken; it was out of the market.** It won 54% of its trades with wins nearly twice the size of its losses. What killed it was opportunity cost: sitting in cash through the strongest stretch of a bull market.

**v1-sweep — the recorded number was partly luck.** Sweeping every lookback showed 20 days sitting as a **lone spike** between 15 (0.158) and 30 (0.279). Had 15 or 30 been the obvious default, v1 would have looked far worse. Only 40 and 45 — adjacent values that agree — looked like a real effect.

**v1s — shorting an index that triples is a bad idea.** The per-trade edge was unchanged, but the win rate collapsed from 65% to 37%. Stock indexes drift upward; betting against one is fighting gravity. Shorting was wrong *on QQQ specifically*, not wrong in general.

### Phase 2 — ten markets (2008–2016)

Rebuilt to follow the papers: sign-of-return signal, three blended lookbacks, long and short, monthly rebalance.

| Version | Sizing | Return | Drawdown | Sharpe | Verdict |
|---|---|---:|---:|---:|---|
| **v2a** | Equal dollars per market | 0.79% | −17.1% | −0.015 | cut |
| **v2b** | Equal *risk* per market | 1.52% | −10.2% | 0.048 | cut |

Volatility scaling did exactly what it should — nearly doubled the return, cut the drawdown by 40%, almost tripled per-trade expectancy. But it improved a strategy with no edge to begin with. **A better-sized version of nothing is still nothing**; 1.5% a year was roughly what a savings account paid.

Diversification also worked, on risk: moving from one market to ten cut the maximum drawdown from 47% to 17%. What it could not do was manufacture a return that was not there.

### Phase 3 — the holdout (2017–2025, one run each)

| Run | What it is | Return | Drawdown | Sharpe | Final equity |
|---|---|---:|---:|---:|---:|
| **H0** | Benchmark — hold all ten, equal weight | **8.58%** | −16.8% | **0.448** | **$209,911** |
| **H1** | Trend signal, equal dollars | 2.77% | −15.5% | −0.156 | $127,869 |
| **H2** | Trend signal, equal risk | 2.62% | **−12.9%** | −0.239 | $126,216 |

`H0 → H1` isolates the signal. `H1 → H2` isolates the sizing.

**Year by year:**

| Year | Benchmark | Strategy | |
|---|---:|---:|---|
| 2017 | +9.4% | +4.1% | |
| **2018** | **−5.8%** | **−0.6%** | protected |
| 2019 | +13.8% | −1.3% | |
| 2020 | +12.5% | +5.0% | |
| 2021 | +8.4% | +1.2% | |
| **2022** | **−6.5%** | **+5.8%** | **12-point swing** |
| 2023 | +7.3% | −5.8% | reversal damage |
| 2024 | +12.2% | +5.4% | |
| 2025 | +30.2% | +10.8% | |

### The prediction scorecard

Six predictions were committed before the holdout ran. **Two were correct — and both were the two flagged in advance as contaminated by hindsight.** Every genuinely uncertain prediction was wrong, including the one singled out as most reliable.

| # | Prediction | Outcome |
|---|---|---|
| 1 | Sharpe between 0.2 and 0.5 | **Wrong** — −0.239 |
| 2 | Vol-scaling beats equal-dollar again *(flagged as the cleanest test)* | **Wrong** |
| 3 | Benchmark has the highest raw return *(flagged as hindsight)* | Right |
| 4 | Strategy has smaller drawdowns *(flagged as hindsight)* | Right |
| 5 | Lumpy returns, 2022 carrying the result | **Partial** — 2025 was the standout, not 2022 |
| 6 | 2020 mixed at best | **Wrong** — +5.0%, one of its better years |

The value came from writing the predictions down beforehand, not from their accuracy.

---

## 4. What was learned

**Trend-following's crisis protection is real.** It appeared in both down years of a window never previously examined, and in 2022 turned a 6.5% loss into a 5.8% gain. That property is not folklore.

**On this universe, in these two eras, it does not pay for itself.** Buy-and-hold more than doubled the account. The strategy returned a quarter, traded 850 times to do it, and paid twelve times the fees.

**Volatility scaling reliably reduces risk, and does not reliably improve risk-adjusted return.** It helped in one era and did not replicate in the other.

**Sharp reversals are the dominant failure mode** — in every version, in both eras. 2009 destroyed the strategy in the build window; 2023 was the worst year of the holdout. Both came immediately after a strong trend year: positioned for continuation, the market snaps back.

### Why this version likely failed where the papers did not

Untested, and untestable on this data without invalidating the result. In rough order of suspicion:

- **Too few independent bets.** Ten ETFs behave like five; the papers use 58 and 67 genuinely distinct markets. If the per-market edge really is ~0.4 Sharpe, five bets is nowhere near enough to lift it above the noise.
- **ETFs are not futures.** Management fees, and roll costs in the commodity funds — frictions the papers' instruments do not carry.
- **Monthly rebalancing on daily signals** may be too slow to act on what the signal sees.
- **The papers report returns gross of some frictions** modelled here.

Testing any of these needs a fresh question and fresh data — real futures contracts, a wider universe — not more iterations on this one. **The holdout has been read; everything from here would be in-sample.**

---

## 5. Repository map

```
strategy-lab/
├── README.md                 this file
├── writeup.html              the full write-up, in plain English
├── SCOREBOARD.md             every result, with commit hashes
├── HOLDOUT.md                pre-registered predictions and falsification criterion
├── UNIVERSE.md               measured volatility and correlations of the ten markets
├── CLAUDE.md                 conventions for AI assistants
│
├── Academic Papers/
│   ├── NOTES.md              distilled methodology from both papers
│   └── *.pdf                 the two source papers
│
├── Backtest recordings/      raw QuantConnect result JSON for every run
│
└── strategies/
    ├── v0_buy_hold.py                    QQQ baseline
    ├── v1_donchian.py                    breakout, long only
    ├── v1s_donchian_long_short.py        breakout, long and short
    ├── v2a_trend_basket.py               ten markets, equal dollars
    ├── v2b_trend_basket_volscaled.py     ten markets, equal risk
    ├── v0b_buyhold_basket_holdout.py     holdout benchmark
    ├── v2a_holdout.py                    holdout, equal dollars
    └── v2b_holdout.py                    holdout, equal risk
```

**[SCOREBOARD.md](SCOREBOARD.md) is the project's real output** — the code is just how it got there. Every result lives there with the reasoning behind its verdict, including the ones that failed.

---

## 6. Reproducing this

Every result can be regenerated. No local install is needed beyond a browser.

1. Create a free [QuantConnect](https://www.quantconnect.com) account.
2. Create a new algorithm and paste any file from `strategies/` over `main.py`. Keep **one** algorithm file per project — extra `.py` files inflate the platform's parameter-detection warning.
3. Run the backtest. Compare against the corresponding row in `SCOREBOARD.md`.

To reproduce a result exactly as recorded, check out the commit named in its scoreboard row first:

```bash
git checkout <hash> -- strategies/
```

Raw result JSON for each run is in `Backtest recordings/` if you would rather inspect the numbers directly than re-run anything.

**Note on API style:** these files use LEAN's snake_case API (`self.set_start_date`, `Resolution.DAILY`). PascalCase was removed from LEAN, not deprecated — most tutorials online still show it and will not run.

---

## 7. Notes for AI assistants

A shorter version lives in [CLAUDE.md](CLAUDE.md), which loads automatically in Claude Code.

**This project is complete.** The holdout has been read, so it cannot be extended — any further work on this strategy would be in-sample and would invalidate the existing result. If someone wants to continue, it needs a fresh question and fresh data in a new repository.

If asked to work in here anyway:

1. **Never fabricate backtest results.** If a number is needed, it has to be run on QuantConnect and reported back. A fake number in the scoreboard poisons every decision after it.
2. **Never edit an existing `vN_*.py` file.** Old versions are immutable records of what produced a recorded number.
3. **Never re-run anything against the holdout window** (2017 onward) and treat the output as a fresh result. It is spent.
4. **Never remove the brokerage/fee model** from a strategy file.
5. **Report bad results plainly.** A cut component is a real finding — do not soften it, and do not look for a reading of the numbers that rescues it.

**Conventions:** snake_case LEAN API throughout, with UPPER_SNAKE enum members (`Resolution.DAILY`, `AccountType.MARGIN`). Every strategy file opens with a docstring stating its version, what changed, its pre-registered success criterion, and its window. Commit messages carry the result numbers.

---

## 8. Glossary

| Term | Plain English |
|---|---|
| **Backtest** | Replaying a strategy against historical data to see what it would have done |
| **Alpha** | The edge — returns beyond just holding the market |
| **Benchmark** | The simple alternative a strategy has to beat. Here: buying and holding the same ten markets |
| **Breakout** | A rule that buys when price exceeds a recent high, betting momentum continues |
| **Donchian channel** | The highest high and lowest low over the last N days |
| **Volatility** | How much prices swing around. High = jumpy = risky |
| **Volatility scaling** | Putting less money in jumpy markets and more in calm ones, so each contributes equal risk |
| **Position sizing** | How much money to put on a trade. Often matters more than the entry rule |
| **Drawdown** | Peak-to-trough loss. "Max drawdown 40%" = at worst you were down 40% from your high |
| **Sharpe ratio** | Return per unit of risk, above cash. Above 1 is decent; above 2 in liquid markets is suspicious |
| **CAGR** | Compound annual growth rate — the average yearly return |
| **Long / flat / short** | Own it / own nothing / borrowed and sold it. Closing a long makes you flat, not short |
| **Slippage** | The gap between the price you expected and the price you actually got |
| **Look-ahead bias** | Accidentally using future information. Makes dead strategies look brilliant |
| **Overfitting** | Tuning until it fits past data perfectly, at which point it predicts nothing |
| **Point-in-time data** | Data as it was known *on that date*, not as later revised |
| **Holdout** | Data deliberately never examined during development, kept for a single final test |
| **Pre-registration** | Writing down what a result must show *before* running it |
| **Expectancy** | Average profit per trade, accounting for both win rate and win size |
| **Effective N** | How many genuinely independent bets a portfolio holds. Correlated markets do not each count |

---

*Built with QuantConnect / LEAN. Papers by Moskowitz, Ooi & Pedersen (2012) and Hurst, Ooi & Pedersen (2017).*
