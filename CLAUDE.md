# Instructions for Claude

Short version. The full reasoning is in [README.md](README.md) — read it before doing real work here, especially §5 (what earns a row), §6 (workflow) and §7 (design decisions already made).

## What this project is

A two-person strategy research project (Seb, Akram). We build a breakout strategy on QuantConnect/LEAN and add **one component at a time**, measuring whether each addition actually helped. Progress lives in `SCOREBOARD.md`, not in the git log.

## Non-negotiables

1. **Never fabricate backtest results.** You cannot run QuantConnect. If a number is needed, ask Seb to run it and report back. Never estimate, guess, or "illustrate" a plausible result — one fake number in the scoreboard poisons every decision after it.
2. **Never edit an existing `vN_*.py` file** to make the next version. Copy it to a new file. Old versions are immutable records of what produced a recorded number.
3. **Never change the build window** (2010-01-01 → 2018-12-31) to the holdout (2019 →) unless Seb explicitly asks. The holdout is a one-shot exam and every peek spends it.
4. **Never suggest branches or pull requests here.** Everything goes on `main`. The Horizon repo has the opposite rules — do not carry them over.
5. **Never remove the brokerage/fee model** from a strategy file to make a number look better.
6. **Don't skip rungs.** If Seb asks for v4 and v2 has no recorded result, say so first.
7. **Report bad results plainly.** A cut component is a real finding. Do not soften it, and do not look for a reading of the numbers that rescues it.

## Conventions

- **LEAN API style:** PascalCase (`self.SetStartDate`, `self.OnData`). QuantConnect's current docs show snake_case; both work. Stay consistent with the existing files, don't mix styles within a file.
- **Every strategy file** opens with a docstring giving: version, what changed from the previous one, the pre-registered *"this helps if…"*, and which window it runs on.
- **Commit messages** carry the numbers:
  `vN: <what it is>. CAGR x%, MaxDD -y%, Sharpe z, N trades`

## The loop

When Seb returns with backtest numbers:

1. Add the row to `SCOREBOARD.md`, **including the commit hash** of the code that produced it (`git log -1 --pretty=%h`).
2. Apply the four keep/cut criteria from README §5 honestly.
3. Write the next version as a **new file**, with its pre-registered hypothesis in the docstring.
4. Remind Seb to commit and push.

## Where things stand

Check `SCOREBOARD.md`. If every row is empty, the project is at v0 and has not been run yet.
