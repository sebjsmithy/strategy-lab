# region imports
from AlgorithmImports import *
from collections import deque
# endregion


class V1sDonchianLongShort(QCAlgorithm):
    """
    v1s - DONCHIAN BREAKOUT, LONG AND SHORT (the "flip" version).

    This is the strategy as originally described: go long at the N-day high,
    go SHORT at the N-day low. It is not v1 with shorts bolted on - it is a
    structurally different system.

        v1  (long only):   long --> FLAT  --> long --> FLAT
        v1s (this one):    long --> SHORT --> long --> SHORT

    The key difference: v1s is NEVER IN CASH after the first signal. That means
    the failure mode we diagnosed in v1 - money lost sitting flat while the
    market rose - cannot happen here. Instead the risk is losing money on bad
    shorts. Different strategy, different way to fail.

    THE RULE
      - Go LONG  (+100%) when today's close is above the highest close of the
        previous 40 days.
      - Go SHORT (-100%) when today's close is below the lowest close of the
        previous 40 days.
      - Otherwise hold the current position.

    WHY 40/40 SYMMETRIC
      One change at a time. The variable under test is long-only vs long/short.
      Using a different short lookback would add a second free parameter and
      make any change in the result un-attributable. 40 comes from the v1 sweep,
      where 40 and 45 formed the only trustworthy plateau.

      Caveat worth stating: 40 was chosen AFTER seeing the sweep results. That
      is post-hoc selection. Defensible (a plateau, not a spike) but not
      pre-registered - which is what the untouched holdout is for.

    IMPORTANT - SHORT BORROW COSTS ARE NOT MODELLED
      LEAN's default margin interest model (NullMarginInterestRateModel) charges
      nothing for borrowing shares to short. Real shorting is not free. So treat
      this result as an OPTIMISTIC UPPER BOUND for the short leg.

      The logic for running it anyway: if the strategy fails with free shorts,
      real borrow costs can only make it worse, so the rejection holds either
      way. Only if it succeeds is it worth adding
      ShortMarginInterestRateModel + InteractiveBrokersShortableProvider
      and re-testing.

    LEVERAGE WATCH
      Flipping from +1.0 to -1.0 is a 200% swing in exposure. Check the
      Portfolio Margin chart after running - it should touch 100% but not
      exceed it. If it goes above, something is wrong.

    PRE-REGISTERED HYPOTHESIS
      Claude's prediction, written before running: this will be WORSE than
      v1 long-only at 40 days (Sharpe 0.400, CAGR 7.01%), and far worse than
      v0 (Sharpe 0.730, CAGR 15.44%). Shorting an index that rose 264% over
      the window should be punitive, and the flip doubles exposure to being
      wrong.

      Formal KEEP bar, consistent with the ladder: Sharpe >= 0.88.
      The more informative comparison is against v1 at 40 days (0.400) - that
      isolates what the short leg actually contributed.

      If this beats long-only, the prediction was wrong and the short side
      deserves serious attention. Recording it in advance so neither outcome
      can be rationalised after the fact.

    Window:  BUILD  (2010-01-01 -> 2018-12-31)
    Record:  CAGR, Max Drawdown, Sharpe, Trades  ->  SCOREBOARD.md

    HOW TO RUN
      1. QuantConnect -> paste this whole file over main.py
         (keep only ONE algorithm file in the project - extra .py files inflate
          the Research Guide's parameter count)
      2. Backtest
      3. Take: Compounding Annual Return, Drawdown, Sharpe Ratio, Total Orders
      4. Also glance at the Portfolio Margin and Exposure charts
      5. Put the numbers in SCOREBOARD.md with the commit hash
    """

    def initialize(self):
        # --- Build window. Do not change to the holdout period (2019 onward)
        # --- without reading README.md section 4 first.
        self.set_start_date(2010, 1, 1)
        self.set_end_date(2018, 12, 31)
        self.set_cash(100000)

        # Margin account is required to hold a short position.
        # NOTE: this models commissions but NOT short borrow costs. See above.
        self.set_brokerage_model(
            BrokerageName.INTERACTIVE_BROKERS_BROKERAGE,
            AccountType.MARGIN,
        )

        self.qqq = self.add_equity("QQQ", Resolution.DAILY).symbol

        # Kept as two names so a later asymmetric sweep is a one-line change.
        # Both 40 for now - see "WHY 40/40 SYMMETRIC" above.
        self.long_lookback = 40
        self.short_lookback = 40

        # Holds the previous N closes, where N is the longer of the two.
        self.window = max(self.long_lookback, self.short_lookback)
        self.closes = deque(maxlen=self.window)

    def on_data(self, data: Slice):
        if not data.contains_key(self.qqq) or data[self.qqq] is None:
            return

        close = data[self.qqq].close

        # Warm-up: need a full window before any comparison is meaningful.
        if len(self.closes) < self.window:
            self.closes.append(close)
            return

        # Compare against the window BEFORE adding today to it. If today's close
        # were part of its own high/low band the rule could never trigger, and
        # that is also how look-ahead bias creeps into hand-rolled backtests.
        recent = list(self.closes)
        highest = max(recent[-self.long_lookback:])
        lowest = min(recent[-self.short_lookback:])

        if close > highest:
            # New 40-day high -> fully long. Closes any short and reverses.
            self.set_holdings(self.qqq, 1.0)
        elif close < lowest:
            # New 40-day low -> fully short. Closes any long and reverses.
            # This is the line that makes v1s a different strategy from v1,
            # where this was self.liquidate() and we went to cash instead.
            self.set_holdings(self.qqq, -1.0)

        self.closes.append(close)
