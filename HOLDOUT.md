# Holdout pre-registration

**Written and committed BEFORE any holdout backtest was run.** That is the entire
point of this document: predictions recorded in advance cannot be rationalised
after the fact.

- **Date registered:** 2026-08-27
- **Holdout window:** 2017-01-01 → 2025-12-31 (9 years, matching the 9-year build window)
- **Status when written:** holdout never looked at. Zero backtests run on it.

---

## What question this answers

Every version so far was tested on 2008–2016 and every one was CUT. The diagnosis
throughout has been that **the era, not the method, was the problem**: Hurst, Ooi
& Pedersen show 2010–2016 is the weakest decade for trend-following in a 137-year
sample, plausibly because QE suppressed volatility and truncated trends.

The holdout tests that diagnosis. It contains the COVID crash, the 2020
V-recovery, and the 2022 inflation shock — a period when trend-followers publicly
had some of their best years in decades.

### What a good result would and would not mean

**Would mean:** the era hypothesis has support. Trend-following behaved
differently in a different regime, consistent with the literature.

**Would NOT mean:** we have a validated trading strategy. The era was chosen
knowing broadly what happened in it. A CUT strategy does not become a KEPT one by
being run on a period selected for being favourable. This is an experiment about
*regimes*, not a strategy validation.

Stating that now so it cannot be blurred later.

---

## The experiment

Three runs, all specified here in advance, each run **exactly once**. They form a
single experiment with three arms, not three chances to iterate.

| Run | File | What it is | Isolates |
|---|---|---|---|
| **H0** | `v0b_buyhold_basket_holdout.py` | Equal-weight, always 100% long all ten ETFs, rebalanced monthly | the benchmark |
| **H1** | `v2a_holdout.py` | v2a exactly — trend signal, equal dollars | H0→H1 = **the signal** |
| **H2** | `v2b_holdout.py` | v2b exactly — trend signal, equal risk | H1→H2 = **the sizing** |

Everything else is held constant: same ten ETFs, same monthly rebalance, same IB
fee model, same $100,000, same margin account.

**H0 is not optional.** Without a benchmark the result is uninterpretable — if the
strategy returns 8%/yr but buying and holding the same ten returns 12%, that is a
failure, and there would be no way to tell without measuring it.

---

## Pre-registered predictions

Recorded before running. Claude's track record so far: **wrong on v2a**
(predicted Sharpe 0.3–0.6, actual −0.015), **right on v1s and v2b**.

### Claude's predictions

1. **H2 (vol-scaled) beats its build-window Sharpe of 0.048.** Expected range
   **0.2 – 0.5**.
2. **H2 beats H1**, replicating the vol-scaling result from the build window.
   This is the prediction most likely to be informative, because it is a
   replication rather than a fresh guess.
3. **H0 (buy and hold) beats both on raw return.** 2017–2021 and 2023–2024 were
   strong for equities, and a strategy that goes short will give that up.
4. **H1 and H2 beat H0 on maximum drawdown**, principally because of 2022.
5. **The equity curve will be lumpy, not smooth** — weak or flat 2017–2021, a
   pronounced jump in 2022, mixed thereafter.
6. **2020 will be mixed, not good** — the March crash favours trend, but the
   violent V-shaped recovery is the same shape that hurt every trend-follower in
   2009 and hurt v2a in this project.

### Honesty flag on these predictions

**These are not blind.** It is public knowledge that 2022 was an exceptional year
for managed futures and that equities ran hard through most of this window.
Predictions 3, 4 and 5 are informed by that. They are mechanism hypotheses, not
forecasts made in ignorance, and should be discounted accordingly.

Prediction 2 is the cleanest of the six, because it is a replication of an effect
measured in a different period.

### What would falsify the era hypothesis

If H2 lands near zero again — Sharpe below roughly 0.1 — then the era explanation
fails and the more likely reading is that this implementation does not capture
whatever the papers captured. That is a legitimate and reportable outcome.

---

## Rules for this run

1. **Run each of the three files exactly once.** Record the numbers.
2. **Do not tune anything afterwards.** No "what if we changed the lookback",
   no adding markets, no adjusting the vol target. The holdout is spent the
   moment it is read.
3. **Record the result whether or not it is flattering**, including if it
   contradicts every prediction above.
4. **Then write up the project.** This is the final experiment.

Point 2 is the one that matters. Every temptation after this run will be to
adjust something and re-run "just to see". That converts an out-of-sample test
into an in-sample one and destroys the only clean evidence the project has.
