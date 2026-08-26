# strategy-lab

A small, honest trading-strategy research project. Two people: **Seb** and **Akram**.

We build a simple trend-following strategy, backtest it properly on QuantConnect, and add one component at a time — measuring whether each one actually helped. The goal is not to get rich. The goal is to end up with a result we can defend, including if that result is *"this doesn't work."*

---

## Start here — what we're doing and why

*If you've been away, or you're new, read only this section. Everything below is detail.*

### The strategy in one paragraph

**We buy ten different things. Every month we look at each one and ask a simple
question: has the price been going up recently, or down? If it's been going up we
bet it keeps going up. If it's been going down we bet it keeps going down. We do
this for all ten independently, at the same time. Most of these bets are small
losers. A few catch a big move and pay for all the rest.**

That's the entire idea.

### What the ten things are

Each is an ETF — a fund you buy like a share, which owns a pile of something on
your behalf.

| Ticker | What you actually own |
|---|---|
| **GLD** | Gold bars in a vault. Owning gold without storing it. |
| **SLV** | Same, but silver. |
| **DBC** | A basket of commodity contracts — oil, petrol, metals, crops. Mostly energy. |
| **DBA** | Farm goods only — corn, wheat, soybeans, sugar, coffee. |
| **SPY** | The 500 biggest US companies. Essentially "the American stock market". |
| **EFA** | Big companies outside North America — Europe, Japan, Australia. |
| **EEM** | Big companies in developing countries — China, India, Brazil, Korea. |
| **TLT** | US government debt repaid in 20+ years. Moves a lot with interest rates. |
| **IEF** | Same, but repaid in 7–10 years. Moves less. |
| **UUP** | The US dollar against other currencies. Rises when the dollar strengthens. |

Four commodity-ish, three stock-ish, two bond-ish, one currency. That mix is
deliberate: it mirrors the papers, which are roughly 43% commodities.

### How these are normally used, and how we differ

Normally people buy these and hold for decades. A pension fund owns SPY and TLT
forever. Gold is held as insurance. Commodity funds are held as inflation
protection. Almost nobody bets *against* them.

We're doing something different. We have no opinion about gold, or oil, or China.
We aren't analysing anything. We just measure whether the price is higher than it
was a while ago. Yes → buy. No → bet against it. **We don't care what these assets
are, only which way they've been moving.**

### Why ten things instead of one

This is the part that matters most, and it's why the QQQ tests went nowhere.

Think of a football scout. They can't reliably tell which single 16-year-old will
turn pro — on any one kid their judgement is barely better than a coin flip. But
sign sixty using a consistent method and a handful become stars who more than pay
for everyone who didn't make it. **Judging that scout by one player tells you
nothing.** That is exactly what v1 and v1s did with QQQ.

The papers put a number on it: across 67 markets over 137 years, every single
market was profitable, at an average Sharpe of about **0.4**. Real, but far too
weak to detect in one asset over nine years. You only see it stacked.

### Why we bet against things here, when that failed on QQQ

QQQ goes up over time — that's what stock indexes do. Betting against it is
fighting gravity, which is why v1s lost 18%.

Gold, oil, currencies and bonds have no built-in upward drift. Over decades they
go up *and* down. So betting against them isn't fighting a tide, it's the other
half of a symmetric bet. **Shorting was wrong on QQQ specifically, not wrong in
general.**

### What "volatility scaling" means

Some of these swing wildly (silver, emerging markets). Some barely move
(medium-term bonds). Put £10,000 into each and silver alone drives nearly all your
results — the calm ones are inaudible.

So we put **less money into the jumpy ones and more into the calm ones**, so each
contributes roughly equally. Like setting the volume on ten speakers so no single
one drowns out the rest.

The papers treat this as part of the strategy, not an optional extra — which is
why v2a runs without it and v2b adds it, so we can *see* what it is worth.

### What you're doing, and how you got here

**What you're doing:** building the simplest honest version of a well-documented
strategy, testing it carefully, and writing down what happened — including when it
doesn't work.

1. Tested a trend rule on QQQ. It lost. Tested it in both directions. It lost worse.
2. Rather than tweaking numbers until something looked good, asked *why*.
3. The answer, from two peer-reviewed papers: this has never been a single-asset
   strategy. We were running one line of a sixty-line portfolio.
4. So now we run it the way the evidence says it is actually built — many markets,
   both directions, sized by risk.

**The discipline throughout:** decide what "it worked" means *before* running.
Change one thing at a time. Never look at the holdout years. Record the result
whether we like it or not. That last part is the actual skill.

---

## Table of contents

0. [**Start here** — what we're doing and why](#start-here--what-were-doing-and-why)
1. [Why this project exists](#1-why-this-project-exists)
2. [What we're building](#2-what-were-building)
3. [The ladder](#3-the-ladder)
4. [Two rules we don't break](#4-two-rules-we-dont-break)
5. [What earns a row](#5-what-earns-a-row)
6. [How we work — the git workflow](#6-how-we-work--the-git-workflow)
7. [Design decisions already made](#7-design-decisions-already-made)
8. [For Claude and other AI assistants](#8-for-claude-and-other-ai-assistants)
9. [Glossary](#9-glossary)

---

## 1. Why this project exists

This replaces an earlier project that tried to extract trading signals from financial news sentiment. We stopped that one for three structural reasons:

- **Speed.** When market-moving news breaks, professional firms react in milliseconds using feeds that arrive before public ones. By the time a story reaches a free RSS feed or a standard news API, the price has already moved. We were entering a latency race we cannot fund.
- **Data quality.** The news dataset we had was ~2,800 Zacks articles, ~1,000 paid press releases, and ~900 Motley Fool pieces. No Reuters, no Bloomberg, no FT. Retail content written *after* the move, for clicks. Tier-1 sources cost real money per month.
- **Redundancy.** The dataset already shipped LLM-generated sentiment labels, which our pipeline deliberately ignored in order to re-derive them less accurately.

None of that was a coding problem. It was a budget and physics problem. So we picked something we can actually finish and actually test.

The full write-up of that decision lives in the Horizon repo as `STRATEGY_REPIVOT.md`.

---

## 2. What we're building

Plain-English version is in [Start here](#start-here--what-were-doing-and-why).
This section is the technical statement of the same thing.

### The strategy, precisely

For each market *i*, at each monthly rebalance, using only data available on that date:

```
S₁   = sign(return over past 21 trading days)     ≈ 1 month
S₃   = sign(return over past 63 trading days)     ≈ 3 months
S₁₂  = sign(return over past 252 trading days)    ≈ 12 months

raw position_i = (S₁ + S₃ + S₁₂) / 3        →  one of −1, −⅓, +⅓, +1
```

Each signal is binary (+1 long, −1 short) and the three are **equal-weighted** —
so the position size scales with how much the timescales agree:

| S₁ | S₃ | S₁₂ | Position |
|---|---|---|---|
| + | + | + | **+1.00** full long |
| + | + | − | **+0.33** small long |
| − | + | − | **−0.33** small short |
| − | − | − | **−1.00** full short |

That is conviction-weighting for free: when short and long horizons disagree —
precisely when trends are ambiguous and whipsaw is most costly — the position is
small. It also removes parameter selection entirely. We do not pick a lookback,
so there is nothing to sweep and nothing to overfit. The weights are equal by
design; optimising them would reintroduce the problem.

### The two versions

| | Sizing |
|---|---|
| **v2a** | Equal notional per market: `weight_i = 0.10 × position_i`. Max gross exposure 100%. |
| **v2b** | Volatility-scaled: quiet markets get more, jumpy markets get less, portfolio targeting ~10% annualised volatility. |

v2a exists purely so v2b has something to be measured against. The papers treat
vol-scaling as constitutive of the strategy, so we expect v2b to win — but
"expect" is not "know", which is the whole point of running both.

### The universe

Ten ETFs — four commodity, three equity, two bond, one currency:

`GLD` `SLV` `DBC` `DBA` · `SPY` `EFA` `EEM` · `TLT` `IEF` · `UUP`

Chosen to mirror the papers' roughly 43% commodity weighting, and to diversify
**across** asset classes rather than within. Nominal N is 10, but effective N is
more like 5–6 — SPY/EFA/EEM move together, TLT/IEF nearly duplicate each other.
Correlated markets do not each count as a separate bet.

All ten have price history from early 2007 or earlier, so the 2008–2016 build
window and the 2017+ holdout both work without gaps.

**On oil specifically:** exposure comes via `DBC` rather than `USO`. USO is badly
distorted by roll decay — in 2020 it broke so severely the fund restructured. If
pure oil is ever wanted as its own line, add USO separately and treat its result
with suspicion.

**We are explicitly not** using a basket of AI-adjacent stocks. Picking that in
2026 means already knowing which ones won — data leakage in the choice of
universe rather than in the code, which makes it nearly invisible.

### Platform

**QuantConnect** (which runs the open-source **LEAN** engine). We use it because backtesting is deceptively hard to get right, and almost every subtle way to get it wrong makes results look *better*:

| Trap | What it is | LEAN's answer |
|---|---|---|
| Look-ahead bias | Using information that wasn't public yet | Point-in-time data — you physically cannot see tomorrow |
| Survivorship bias | Only testing companies that still exist | Includes delisted securities |
| Ignoring costs | Forgetting fees, spreads, slippage | Models them by default |
| Backtest ≠ live | Simulation differs from real execution | Same code path for both |

**Accounts:** we each have our own **free** QuantConnect account. Their free tier only allows single-member organisations, so real in-platform collaboration needs the $20/month Team tier — not worth it. Two free accounts costs nothing and doubles our backtest throughput. **Collaboration happens in this repo, not inside QuantConnect.**

---

## 3. The ladder

We never build the whole system and then evaluate it. We build the dumbest possible version, record its numbers, then add **one** component at a time.

| v | What changes | The question it answers | Overfit risk | Status |
|---|---|---|---|---|
| **v0** | Buy & hold QQQ, no strategy | What am I trying to beat? | — | baseline |
| **v1** | Donchian 20d on QQQ, **long only** | Does the entry rule do anything at all? | low | CUT |
| **v1-sweep** | Donchian lookback 5–50 on QQQ | Is it the parameter or the idea? | low | CUT |
| **v1s** | Donchian 40/40 on QQQ, **long + short** | Do shorts help on an index? | low | CUT |
| **v2a** | **10-market basket**, blended 1/3/12-month trend, long+short, equal weight | Does the strategy work when run as a *portfolio*? | low | **next** |
| **v2b** | + **volatility scaling** to a 10% portfolio vol target | Does risk-based sizing earn its place? | low | queued |
| **v3** | Parameter/robustness checks on whatever survives | Is it a plateau or a spike? | medium | — |
| **v4** | + Markov conviction scaling | Does regime *scaling* help? | **medium** | — |
| **v5** | Regime-based strategy *selection* | Which rule wins in which regime? | **HIGH** | — |

**The v1 family is closed.** Donchian on QQQ was rejected in every configuration —
long/flat, long/short, and across every lookback from 5 to 50 days. The diagnosis
is in `SCOREBOARD.md`: single-asset tests cannot detect a ~0.4-Sharpe edge, so
those runs were structurally uninformative rather than evidence against trend
following. See `Academic Papers/NOTES.md`.

**v2a and v2b are paper-faithful**, following Hurst, Ooi & Pedersen (2017):

- **Signal** is the *sign of the past return*, not a channel breakout.
- **Three lookbacks blended equally** — 1, 3 and 12 months — so position size
  scales with how much the timescales agree. This removes the parameter-selection
  problem entirely: no sweep, no plateau hunting.
- **Always long or short**, never flat.
- **Monthly rebalancing**, not daily.

**v0 matters more than it sounds.** If the clever strategy cannot beat buying QQQ and going to sleep, that is the result. Most strategies can't.

### Why v5 is the danger zone

v5 asks *"which strategy works best in which regime?"* Sounds smart, is a trap.

Over 15 years, "bear market" days do not come from thousands of independent events — they come from maybe **5 to 8 distinct crashes** (2008, 2011, 2018, 2020, 2022…), and days within one crash are near-identical. We would be comparing strategies across a handful of real samples while it *feels* like thousands. We will find a split that looks brilliant. It will probably mean nothing.

Note the distinction: **detecting** regimes is fine — with ~3,800 daily transitions the 3×3 transition table is well-supported. It is using regimes to **pick between strategies** that's fragile. Same model, wildly different sample sizes underneath.

So v5 goes last, and gets judged on the holdout only.

---

## 4. Two rules we don't break

### Rule A — Split the data, and only look once

| Window | Dates | Use |
|---|---|---|
| **Build** | 2008-01-01 → 2016-12-31 | Tune here. Run 500 backtests if you want. |
| **Holdout** | 2017-01-01 → today | Touch **once**, at the end. |

**These windows were changed on 2026-08-26, before any multi-asset run.** The
original split was 2010–2018 build / 2019+ holdout. Two reasons for the change,
both recorded here so it is on the record rather than quietly done:

1. **Regime coverage.** Hurst, Ooi & Pedersen show 2010–2016 is the *weakest
   decade for trend-following in their 137-year sample* (roughly 0.41 versus 1.70
   in the 1970s), plausibly because QE suppressed volatility and truncated trends.
   Testing only there risks rejecting a strategy that works in normal conditions.
   The new build window contains the GFC, the euro crisis and the 2015–16 selloff.
2. **A better exam.** The new holdout contains the COVID crash and the 2022
   inflation shock — the best natural experiment available, and a period when
   trend-followers did famously well. A strategy tuned on 2008–2016 that survives
   those untouched is a genuinely strong result. One tuned *on* 2020–21 tells us
   nothing.

**The legitimacy test that was applied:** the change was made *before* running
anything on the new basket, the old holdout was never looked at, and the reason
comes from the literature rather than from disappointing results. Changing a
window because results were bad is data-snooping. Changing it beforehand for
documented reasons of regime coverage is experimental design.

The holdout is a one-shot exam. Every peek makes it less honest, because you start unconsciously tuning toward it. All development happens in the build window.

### Rule B — Say what success means *before* you run it

Before each version, write one sentence in the scoreboard: *"This helps if ___."* Then check.

Without this you get a number and rationalise backwards into why it is what you expected. Everyone does this. Writing it first is the only defence.

---

## 5. What earns a row

A version replaces the previous one only if **all** of these hold:

1. **Sharpe improves meaningfully** — +0.15 or better. Not +0.03; that's noise wearing a decimal point.
2. **Max drawdown doesn't get worse.**
3. **Trade count is sane** — not 4 trades (no sample), not 5,000 (fees eat you alive).
4. **It survives a ±25% nudge** to its main parameter. If 20 works but 15 and 25 collapse, we found a coincidence, not a strategy.

Fail any one → cut it, record *why* in the scoreboard, move on.

**A cut component is a real finding, not a failure.** "GARCH sizing did not improve risk-adjusted returns on QQQ" is a legitimate, writeable-up result.

### On optimising parameters

When searching for the best lookback period, **read the shape, not the peak**:

```
GOOD (plateau)          BAD (spike)
10  ####                10  #
20  ######              20  #
30  ######              23  ########   <- noise
40  #####               30  #
```

A plateau means the *idea* works and the exact number doesn't much matter. A lone spike means a coincidence. **Pick from the middle of a plateau**, and prefer round numbers (20, 50) over 23.

---

## 6. How we work — the git workflow

Deliberately low-tech. This is a two-person research repo, not production software.

### Repo layout

```
strategy-lab/
├── README.md              <- this file, the single source of truth
├── CLAUDE.md              <- instructions for AI assistants
├── SCOREBOARD.md          <- the results table (the actual output of this project)
└── strategies/
    ├── v0_buy_hold.py
    ├── v1_donchian.py
    └── ...
```

### The four rules

**Rule 1 — Everything goes on `main`. No branches, no pull requests.**

Branches and PR approvals are for production code where a bad merge breaks something live. Here the worst case is a bad backtest. Not worth the ceremony. (This is deliberately the opposite of the Horizon repo's rules. Don't copy those here.)

**Rule 2 — A new version means a new *file*. Never edit an old one.**

When v1 works, copy `v1_donchian.py` → `v2_donchian_garch.py` and edit *that*. Yes, it duplicates code. That is the point: v1's exact code stays on disk forever, so it can always be re-run. It is a safety net for when git habits slip.

**Rule 3 — Commit the moment you have a result, with the numbers in the message.**

```
v1: donchian 20d long-only. CAGR 8.2%, MaxDD -22%, Sharpe 0.61, 47 trades
```

**Rule 4 — `git pull` before you start, `git push` when you stop.**

### The commands

Before working:

```bash
git pull
```

After you have a result:

```bash
git add -A && git commit -m "v1: donchian 20d. CAGR 8.2%, Sharpe 0.61" && git push
```

Then get the commit hash for the scoreboard:

```bash
git log -1 --pretty=%h
```

That prints something like `7d10b4e`. Paste it into the scoreboard row. **Git generates this hash automatically on every commit — you never invent it.**

### Why the commit hash matters

Picture it is six weeks later. The scoreboard says *v2 — Sharpe 0.88*. You want to build on it. You open the file and:

- Was the lookback 20 or 25 when that ran?
- Were fees turned on?
- Was it 2010–2018, or did it accidentally run to 2019?

You cannot answer. **The 0.88 is now a rumour, not a result** — and you cannot even re-run it, because you don't know what "it" was.

With a hash, `git checkout 7d10b4e` restores the files to exactly how they were when 0.88 was recorded. Paste into QuantConnect, run, get 0.88 again.

The number alone is a claim. The number plus the code is an experiment someone can repeat.

The real risk here is not fraud, it is **drift**: tweak, run, tweak, run twenty times, and eventually write down a good number without being able to say what produced it. Then build on sand. The hash makes drift impossible.

### The QuantConnect loop

The free tier has no API access, so syncing is manual. That is fine at this stage:

```
write code here (git)  ->  paste into QuantConnect Algorithm Lab  ->  run
       ^                                                              |
       |                                                              v
   commit + push  <-  paste result numbers into SCOREBOARD.md  <-  read results
```

The `$8/month Researcher tier` unlocks the API and the LEAN CLI, which syncs local code to the cloud properly and kills the copy-paste. Worth it once the manual step becomes the annoying part — not before.

### The working setup

Deliberately minimal — one tool, not three.

| Tool | Used for |
|---|---|
| **Claude desktop app**, opened on this folder | Everything: editing files, writing strategies, running the git commands |
| **QuantConnect Algorithm Lab** (browser) | Running backtests |
| **Terminal** | Rarely needed — Claude runs git |

An editor like Cursor or VS Code is optional. This repo is a handful of files; it isn't worth the setup cost yet.

### Picking the work back up after a break

Open the Claude app on this folder and ask:

> Where are we and what's next?

`CLAUDE.md` loads automatically, so no re-briefing is needed. The answer comes from the **`▶ NEXT ACTION`** block at the top of `SCOREBOARD.md`, which gets updated at the end of every session.

That block is the handoff mechanism. Chats run out of context eventually; the repo does not.

---

## 7. Design decisions already made

Recording these so we don't relitigate them, and so anyone joining knows the reasoning.

### There are three states, not two

| State | What you hold | You profit when |
|---|---|---|
| **Long** | You own the asset | Price goes **up** |
| **Flat** | Nothing. Just cash. | — no exposure at all |
| **Short** | You borrowed it and sold it | Price goes **down** |

**Closing a long does not make you short. It makes you flat.** Not betting and betting against are different things.

We start **long-only**. Shorting adds borrow costs, adds theoretically unlimited downside, and fights the upward drift of equity indices. It gets tested separately as `v1s` and has to earn its place.

### The exit is a separate decision from the entry

A strategy is not an entry rule. It is **entry + exit + size**. The exit frequently matters more than the entry.

"Buy at the 20-day high" says nothing about when to leave. Options:

| Exit rule | What it does |
|---|---|
| **Opposite channel** — exit at the 20-day low | Simplest, symmetric. Holds through big pullbacks. |
| **Faster channel** — exit at the 10-day low | Exits sooner, keeps more profit. The classic Turtle setup (20 in, 10 out). |
| **Trailing stop** — exit if price falls X ATR from its peak | Locks in gains |
| **Time-based** — exit after N days | Rarely good alone |

**v1 uses the simplest:** long when close > 20-day high, flat when close < 20-day low. One parameter, symmetric. Testing 20-in/10-out afterwards is a good scoreboard row.

### Repeat signals and pyramiding

With a "close > 20-day high" rule, a strong uptrend fires a signal **almost every single day**. So the repeat-signal behaviour must be a deliberate choice:

| Approach | What happens |
|---|---|
| **Binary** *(what we use)* | Either 100% in or 0% in. Repeat signals change nothing. |
| **Pyramiding** | Add more on each signal. What the original Turtles did (up to 4 units). |

Naively buying on every signal would put you fully invested within a week and then borrowing — **accidental leverage**, which eventually wipes you out.

Pyramiding is genuinely interesting and worth testing later, but it adds a parameter (how many units, how far apart) and it amplifies both gains and losses. It is a scoreboard row, not a default.

**How LEAN handles this:** positions are expressed as **targets**, not actions.

```python
self.set_holdings(self.qqq, 1.0)   # "I want to be 100% long QQQ"
self.liquidate(self.qqq)           # "I want to be flat"
```

`set_holdings` sets a target, so calling it repeatedly just re-asserts "still want 100%" and nothing more is bought. Pyramiding only happens if written deliberately.

### Costs stay on, always

Every version sets a brokerage model so fees and slippage are included. A backtest without costs is a fantasy. Do not turn this off to make a number look better.

---

## 8. For Claude and other AI assistants

**Read this section before doing anything in this repo.** There is a shorter version in `CLAUDE.md`.

### Non-negotiables

1. **Never fabricate backtest results.** You cannot run QuantConnect. If a number is needed, ask Seb to run it and report back. Never estimate, guess, or "illustrate" what a result might be — a fake number in the scoreboard poisons every decision after it.
2. **Never edit an existing `vN_*.py` file** to create the next version. Copy it to a new file. Old versions are immutable records.
3. **Never change the build window** (2010-01-01 → 2018-12-31) to the holdout period without Seb explicitly asking. The holdout is a one-shot exam.
4. **Never suggest branches or pull requests** in this repo. Everything goes on `main`. (The Horizon repo has the opposite rules — do not carry them over.)
5. **Never remove the brokerage/fee model** from a strategy file.
6. **Do not skip rungs on the ladder.** If Seb asks for v4 and v2 isn't recorded yet, say so.

### Conventions

- **LEAN API style: snake_case, always.** `self.set_start_date`, `self.add_equity`, `self.portfolio.invested`, `data.contains_key`. Method overrides are `def initialize(self)` and `def on_data(self, data)`.

  Enum members are **UPPER_SNAKE**: `Resolution.DAILY`, `AccountType.MARGIN`, `BrokerageName.INTERACTIVE_BROKERS_BROKERAGE`.

  **PascalCase (`SetStartDate`, `Resolution.Daily`) does not work.** Older tutorials, forum posts and blog articles are full of it because LEAN used to use it — it has since been removed, not deprecated. If you find a PascalCase example online, translate it before using it. Verified against LEAN master v18024 (August 2026) via the Algorithm Lab linter.
- **Every strategy file starts with a docstring** stating: which version it is, what changed from the previous one, the pre-registered "this helps if…", and which window it runs on.
- **Commit messages** carry the result numbers. Format: `vN: <what it is>. CAGR x%, MaxDD -y%, Sharpe z, N trades`.

### The loop you are supporting

When Seb comes back with numbers from a backtest:

1. Add the row to `SCOREBOARD.md` — including the commit hash of the code that produced it.
2. Apply the [What earns a row](#5-what-earns-a-row) criteria honestly. If the component failed, say so plainly and record it as cut. Do not soften a bad result.
3. Write the next version as a **new file**, with its pre-registered hypothesis in the docstring.
4. Commit and push — Seb generally wants the git commands run for him, not handed to him.
5. **Update the `▶ NEXT ACTION` block** at the top of `SCOREBOARD.md` before the session ends.

### Context for a cold start

If you are picking this up with no prior conversation:

1. Read the **`▶ NEXT ACTION`** block at the top of `SCOREBOARD.md`. That is the single source of truth for what to do next.
2. Read the scoreboard's results table for what has already been measured.
3. Read this README for the reasoning behind the rules.

The scoreboard is the source of truth for progress — not the file list, not the git log.

**Always leave the `▶ NEXT ACTION` block accurate when a session ends.** Chats run out of context; that block and the scoreboard are what survive.

---

## 9. Glossary

| Term | Plain English |
|---|---|
| **Backtest** | Replaying a strategy against historical data to see what it would have done |
| **Alpha** | The edge — returns beyond just holding the market |
| **QQQ** | A fund tracking the NASDAQ-100; buying it ≈ buying the 100 biggest non-financial NASDAQ companies |
| **Breakout** | A rule that buys when price exceeds a recent high, betting momentum continues |
| **Donchian channel** | The highest high and lowest low over the last N days |
| **Bollinger Bands** | A band around the average price, widening when the market is jumpy |
| **Volatility** | How much prices swing around. High = jumpy = risky |
| **GARCH** | A model forecasting tomorrow's volatility from recent volatility. Jumpy periods cluster together |
| **Position sizing** | How much money to put on a trade. Often matters more than the entry rule |
| **Drawdown** | Peak-to-trough loss. "Max drawdown 40%" = at worst you were down 40% from your high |
| **Sharpe ratio** | Return per unit of risk. Higher is better. Above 1 is decent, above 2 is suspicious |
| **CAGR** | Compound annual growth rate — the average yearly return |
| **Markov chain** | A model where the next state depends only on the current one. Here: bull/sideways/bear |
| **Slippage** | The gap between the price you expected and the price you actually got |
| **Look-ahead bias** | Accidentally using future information. Makes dead strategies look brilliant |
| **Overfitting** | Tuning until it fits past data perfectly, at which point it predicts nothing |
| **Point-in-time data** | Data as it was known *on that date*, not as later revised |
| **Long / flat / short** | Own it / own nothing / borrowed and sold it |
| **Pyramiding** | Adding to a winning position as it keeps going your way |
| **ATR** | Average True Range — a measure of how much an asset typically moves in a day |
