# strategy-lab

A small, honest trading-strategy research project. Two people: **Seb** and **Akram**.

We build a simple breakout strategy, backtest it properly on QuantConnect, and add one component at a time — measuring whether each one actually helped. The goal is not to get rich. The goal is to end up with a result we can defend, including if that result is *"this doesn't work."*

---

## Table of contents

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

**The whole idea in one paragraph:**

> When a stock's price climbs above the highest price it has hit in the last 20 days, that is often a sign it will keep climbing — so we buy. When it drops below its 20-day low, we get out. Separately, we measure how *jumpy* the market is right now: when things are calm we put more money in, when things are wild we put less in. Then we check whether the market is in a calm-upward phase or a panicky phase, and see whether our rule works better in one than the other.

### The four components

| # | Component | What it does | Answers |
|---|---|---|---|
| 1 | **Donchian breakout** | Buy at a 20-day high, exit at a 20-day low | *Which way?* |
| 2 | **GARCH volatility model** | Forecasts how jumpy prices will be; size down when jumpy | *How much?* |
| 3 | **Bollinger breakout** | A second, different entry rule to compare against #1 | *Is there a better rule?* |
| 4 | **Markov regime model** | Labels each day bull / sideways / bear, tracks transitions | *Does context matter?* |

### What we trade

**QQQ** — the NASDAQ-100 tracker. Boring, enormously liquid, decades of clean free data. Deliberately unglamorous.

We are explicitly **not** starting with a basket of AI-adjacent stocks. Picking that basket in 2026 means we already know which ones won — the backtest would look spectacular and prove nothing. That is data leakage in the choice of universe rather than in the code, which makes it nearly invisible. It can come back later as a "does this generalise" test.

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

| v | What changes | The question it answers | Overfit risk |
|---|---|---|---|
| **v0** | Buy & hold QQQ, no strategy | What am I trying to beat? | — |
| **v1** | Donchian 20d, **long only**, fixed size | Does the entry rule do anything at all? | low |
| **v1s** | *side test:* add short trades | Do shorts pay for their borrow cost? | low |
| **v2** | + GARCH volatility-based sizing | Does risk-based sizing beat fixed size? | low |
| **v3a** | Bollinger breakout **instead of** Donchian | Is a different entry rule better? | low |
| **v3b** | Both rules combined | Are they additive, or redundant? | **medium** |
| **v4** | + Markov conviction scaling: size × (P(bull) − P(bear)) | Does regime *scaling* help? | **medium** |
| **v5** | Regime-based strategy *selection* | Which rule wins in which regime? | **HIGH** |

`v1s` is a side test, not a rung — it branches off `v1` and either earns its way in or doesn't.

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
| **Build** | 2010-01-01 → 2018-12-31 | Tune here. Run 500 backtests if you want. |
| **Holdout** | 2019-01-01 → today | Touch **once**, at the end. |

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
