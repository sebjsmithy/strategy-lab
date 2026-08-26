# Universe statistics — the 10-ETF basket

Measured over the build window (2008-01-01 → 2016-12-31) from adjusted daily
closes. Reference data for designing and interpreting v2a / v2b.

Generated with `yfinance`; the GARCH plugin (`garch-method`) was used to sanity
check current-day forecasts against these realised figures.

---

## Realised volatility and what vol-scaling does to each market

| ETF | Class | Ann. vol | Weight multiplier at a 10% target |
|---|---|---:|---:|
| IEF | bond | **7.3%** | **1.37×** ← scaled *up* |
| UUP | fx | 9.1% | 1.10× ← scaled *up* |
| TLT | bond | 15.7% | 0.64× |
| DBA | commodity | 19.3% | 0.52× |
| GLD | commodity | 19.9% | 0.50× |
| DBC | commodity | 20.8% | 0.48× |
| SPY | equity | 21.3% | 0.47× |
| EFA | equity | 25.8% | 0.39× |
| EEM | equity | 33.4% | 0.30× |
| SLV | commodity | **34.5%** | **0.29×** ← scaled *down* |

**Dispersion: 4.7×** (SLV 34.5% vs IEF 7.3%). Median 20.4%.

**This is the whole case for v2b.** Under v2a's equal-dollar weighting, silver and
emerging markets were contributing roughly **4–5× the risk** of the bond and
dollar positions. The portfolio's results were effectively driven by SLV, EEM and
EFA, while IEF and UUP were close to inaudible — regardless of whether their
signals were right.

Equal-risk weighting reverses that: bonds and the dollar get scaled up, silver and
emerging markets get cut to roughly a third.

### The actual weights v2b produces

Inverse-volatility weights normalised to sum to 1.0, so gross exposure is capped
at 100% — identical to v2a. Only the *distribution* changes.

| ETF | Ann. vol | v2a weight | v2b weight | Change | Risk contribution v2a | v2b |
|---|---:|---:|---:|---:|---:|---:|
| IEF | 7.3% | 0.100 | **0.226** | **2.26×** | 0.73% | 1.65% |
| UUP | 9.1% | 0.100 | **0.182** | **1.82×** | 0.91% | 1.65% |
| TLT | 15.7% | 0.100 | 0.105 | 1.05× | 1.57% | 1.65% |
| DBA | 19.3% | 0.100 | 0.086 | 0.86× | 1.93% | 1.65% |
| GLD | 19.9% | 0.100 | 0.083 | 0.83× | 1.99% | 1.65% |
| DBC | 20.8% | 0.100 | 0.079 | 0.79× | 2.08% | 1.65% |
| SPY | 21.3% | 0.100 | 0.078 | 0.78× | 2.13% | 1.65% |
| EFA | 25.8% | 0.100 | 0.064 | 0.64× | 2.58% | 1.65% |
| EEM | 33.4% | 0.100 | 0.049 | **0.49×** | 3.34% | 1.65% |
| SLV | 34.5% | 0.100 | 0.048 | **0.48×** | 3.45% | 1.65% |

Risk contribution is `weight × volatility`. Under v2a it ranges from 0.73% to
3.45% — a **4.7× spread**. Under v2b it is **1.65% for every market**, which is
precisely what "equal risk" means.

The practical effect: **bonds and the dollar roughly double in size, silver and
emerging markets roughly halve.**

---

## Correlations, and why nominal N ≠ effective N

| | DBA | DBC | EEM | EFA | GLD | IEF | SLV | SPY | TLT | UUP |
|---|---|---|---|---|---|---|---|---|---|---|
| **DBA** | 1.00 | 0.66 | 0.38 | 0.40 | 0.24 | −0.18 | 0.38 | 0.36 | −0.20 | −0.34 |
| **DBC** | 0.66 | 1.00 | 0.54 | 0.54 | 0.38 | −0.27 | 0.51 | 0.49 | −0.31 | −0.41 |
| **EEM** | 0.38 | 0.54 | 1.00 | **0.90** | 0.12 | −0.39 | 0.29 | **0.88** | −0.39 | −0.32 |
| **EFA** | 0.40 | 0.54 | **0.90** | 1.00 | 0.10 | −0.40 | 0.29 | **0.92** | −0.43 | −0.44 |
| **GLD** | 0.24 | 0.38 | 0.12 | 0.10 | 1.00 | 0.17 | **0.80** | 0.01 | 0.12 | −0.40 |
| **IEF** | −0.18 | −0.27 | −0.39 | −0.40 | 0.17 | 1.00 | 0.01 | −0.44 | **0.91** | −0.03 |
| **SLV** | 0.38 | 0.51 | 0.29 | 0.29 | **0.80** | 0.01 | 1.00 | 0.21 | −0.04 | −0.42 |
| **SPY** | 0.36 | 0.49 | **0.88** | **0.92** | 0.01 | −0.44 | 0.21 | 1.00 | −0.45 | −0.25 |
| **TLT** | −0.20 | −0.31 | −0.39 | −0.43 | 0.12 | **0.91** | −0.04 | −0.45 | 1.00 | 0.05 |
| **UUP** | −0.34 | −0.41 | −0.32 | −0.44 | −0.40 | −0.03 | −0.42 | −0.25 | 0.05 | 1.00 |

**Average pairwise correlation: 0.10**
**Effective N: 5.2** (against a nominal N of 10)

The earlier estimate of "5–6 effective bets" is confirmed empirically. The ten
markets collapse into roughly five blocks:

| Block | Members | Internal correlation |
|---|---|---|
| Equities | SPY, EFA, EEM | 0.88 – 0.92 |
| Bonds | TLT, IEF | 0.91 |
| Precious metals | GLD, SLV | 0.80 |
| Broad commodities | DBC, DBA | 0.66 |
| Dollar | UUP | — (negative to most others) |

**UUP is the most genuinely diversifying holding** — negatively correlated with
almost everything else (−0.25 to −0.44). It is also one of the two lowest-vol
markets, so v2a's equal-dollar weighting gave it almost no influence.

The low *average* correlation of 0.10 is misleading on its own: it arises because
strong positive correlations within blocks are offset by negative correlations
between blocks, not because the markets are independent.

---

## Implications

1. **v2b's re-weighting will be material, not cosmetic** — a 4.7× vol spread means
   position sizes change substantially.
2. **The √N ceiling is √5.2 ≈ 2.3, not √10 ≈ 3.2.** At the papers' ~0.4
   single-market Sharpe, the theoretical best case for this universe is roughly
   0.4 × 2.3 ≈ **0.9**, assuming everything goes right.
3. **Adding more equity ETFs would add nothing.** Any expansion should be toward
   uncorrelated blocks — more currencies, more distinct commodity groups — not
   more of what is already represented.
4. **DBA is the weakest link** — QuantConnect flagged it as the binding capacity
   constraint in v2a ($7.1M), and it is heavily correlated with DBC (0.66).
