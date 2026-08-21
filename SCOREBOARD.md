# Scoreboard

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
| v0 | | *(baseline — nothing to beat yet)* | | | | | — | — |
| v1 | | | | | | | | |
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
- **Status:** pending — not yet run
- **File:** `strategies/v0_buy_hold.py`
- **Notes:**

---

## Parameter sweeps

When testing a range of values, record the **shape**, not just the winner. A plateau means the idea is real; a lone spike means it's noise.

### (none yet)

| Version | Parameter | Values tested | Shape | Chosen | Why |
|---|---|---|---|---|---|
| | | | | | |
