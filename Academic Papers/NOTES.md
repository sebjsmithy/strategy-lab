# Notes on the two papers

Distilled from the PDFs in this folder. This is the theoretical basis for the
project — read this before designing any trend-following version.

- **MOP 2012** — Moskowitz, Ooi & Pedersen, "Time Series Momentum,"
  *Journal of Financial Economics* 104(2), pp. 228–250.
- **HOP 2017** — Hurst, Ooi & Pedersen, "A Century of Evidence on
  Trend-Following Investing," *Journal of Portfolio Management* 44(1), pp. 15–29.

---

## 1. What they actually traded

### MOP 2012 — 58 liquid futures/forwards, 1985–2009 (Appendix A)

| Class | N | Markets |
|---|---|---|
| Equity indices | 9 | SPI 200 (AU), CAC 40 (FR), DAX (DE), FTSE/MIB (IT), TOPIX (JP), AEX (NL), IBEX 35 (ES), FTSE 100 (UK), S&P 500 (US) |
| Bonds | 13 | Australia 3y & 10y, Euro Schatz, Euro Bobl, Euro Bund, Euro Buxl, Canada 10y, Japan 10y, Long Gilt, US 2y, US 5y, US 10y, US Long Bond |
| Currencies | 10 | AUD, CAD, EUR (spliced from DEM), JPY, NZD, NOK, SEK, CHF, GBP, USD |
| Commodities | 24 | Aluminium, Copper, Nickel, Zinc (LME); Brent Crude, Gas Oil, Cotton, Coffee, Cocoa, Sugar (ICE); Live Cattle, Lean Hogs (CME); Corn, Soybeans, Soy Meal, Soy Oil, Wheat (CBOT); WTI Crude, RBOB Gasoline, Heating Oil, Natural Gas (NYMEX); Gold, Silver (COMEX); Platinum (TOCOM) |

*(The appendix enumerates 56 by direct count; the paper states 58. Minor
discrepancy, probably splicing. Not material.)*

### HOP 2017 — 67 markets, 1880–2016

**29 commodities · 11 equity indices · 15 bond markets · 12 currency pairs**

### The headline for us

**Commodities are the largest block in both papers — roughly 43% of markets.**
Any basket we build should be commodity-heavy to reflect the evidence base.

---

## 2. Key findings

**Individual markets are positive but weak.** HOP: *"the strategy has delivered
positive average returns in each market, with an average Sharpe ratio of
approximately 0.4."* Every single one of 67 markets positive over 1880–2016.

This is the crucial number. A single-market Sharpe of ~0.4 is real but far too
noisy to detect in one 9-year sample. It is why single-asset tests of this
strategy are uninformative — and why v1/v1s failing on QQQ is weak evidence
against trend-following.

**Diversification is where the Sharpe comes from.** Uncorrelated return streams
stack roughly by √N: N strategies each at Sharpe *s*, mutually uncorrelated,
give a portfolio Sharpe of about *s*·√N. At 0.4 with 20 genuinely independent
markets that is ~1.8. MOP report portfolio Sharpe above 1.2.

**Effective N is smaller than nominal N.** Correlated markets do not each count
as a bet. Eight equity ETFs are close to one bet. Diversify *across* asset
classes, not within.

**It performs best in extreme markets.** HOP: profitable in 8 of the 10 largest
drawdowns for a 60/40 portfolio, and the return-vs-equity-market scatter shows a
"smile" — good in big up years *and* big down years, weak in the middle.

**The strategy has decayed.** Their per-decade table shows roughly 0.41 for
2010–2016 against 1.70 for the 1970s — the weakest decade in the 137-year
sample. **Our build window (2010–2018) sits inside the worst stretch this
strategy has had in over a century.** Worth remembering when judging results.

---

## 3. Methodology — how they actually construct it

This differs from what this project built in v1/v1s, in three ways that matter.

**Signal: the sign of past return, not a channel breakout.**
> *"the position taken in each market is determined by assessing the past return
> in that market over the relevant look-back horizon. A positive past excess
> return is considered an 'up' trend and leads to a long position; a negative
> past excess return is considered a 'down' trend and leads to a short position."*

Simpler than Donchian. No high/low channel involved.

**Always long or short — never flat.** Same structure as our v1s, not v1.

**Multiple lookbacks blended, not one chosen.** Equal-weighted combination of
**1-month, 3-month and 12-month** time series momentum. This sidesteps the
parameter-selection problem entirely — no lookback sweep, no plateau hunting.

**Volatility scaling is part of the strategy, not an add-on.**
> *"Each position is sized to target the same amount of volatility, both to
> provide diversification and to limit the portfolio risk from any one market.
> The positions across the three strategies are aggregated each month and scaled
> such that the combined portfolio has an annualized ex ante volatility target
> of 10%."*

They use three years of past data to estimate volatilities. **This means our
planned GARCH/vol-sizing component is not an optional later improvement — it is
constitutive of the strategy.** Without it, the wildest market dominates the
portfolio.

**Monthly rebalancing.** Not daily. Lower turnover, lower costs.

**Costs and fees are subtracted**, including a simulated 2% management fee and
20% performance fee.

---

## 4. Implications for this project

1. **Go multi-asset.** Single-asset tests cannot distinguish a 0.4-Sharpe edge
   from noise. v1 and v1s were structurally uninformative tests, not evidence
   against trend-following.
2. **Weight commodities heavily** — ~43% of markets in both papers.
3. **Diversify across asset classes, not within.** Effective N, not nominal N.
4. **Vol-scale positions** from the start rather than deferring it to v2.
5. **Consider the simpler signal** — sign of past return — and the blended
   1/3/12-month lookback, which removes the parameter-choice problem.
6. **Consider monthly rebalancing** rather than daily.
7. **Calibrate expectations to the era.** 2010–2018 is the weakest decade in the
   sample. A modest positive result in this window is more impressive than it
   looks; a spectacular one should raise suspicion.

---

## 5. Honest caveats

- Both papers are authored by AQR-affiliated researchers, and AQR sells
  trend-following products. Peer-reviewed in JFE and JPM, but worth knowing.
- There is a genuine academic replication debate about how robust time-series
  momentum is to methodology changes. Not yet reviewed here.
- Published edges get crowded. The decade table is direct evidence of decay.
