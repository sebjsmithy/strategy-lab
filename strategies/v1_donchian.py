# region imports
from AlgorithmImports import *
from collections import deque
# endregion


class V1Donchian(QCAlgorithm):
    """
    v1 - DONCHIAN BREAKOUT, LONG ONLY, FIXED SIZE.

    What changed from v0: v0 bought once and held forever. v1 tries to be in
    the market only when price is making new highs, and in cash otherwise.

    THE RULE
      - Go LONG (100%) when today's close is above the highest close of the
        previous 20 days.
      - Go FLAT (0%)   when today's close is below the lowest close of the
        previous 20 days.
      - Otherwise do nothing - hold whatever we already have.

    Note there are three states, not two: long, flat, short. This version never
    goes short. Closing a long puts us in FLAT (cash), not short. Shorting is
    tested separately as v1s and has to earn its place.

    Sizing is BINARY - 100% in or 0% in. Because set_holdings takes a target
    weight, a repeat buy signal on day 2, 3, 4... of an uptrend just re-asserts
    "still want 100%" and buys nothing more. That is what stops repeat signals
    accidentally levering us up. See README.md section 7.

    PRE-REGISTERED HYPOTHESIS
      This helps if sidestepping large drawdowns produces a better risk-adjusted
      return than simply owning the index. Concretely, v1 is KEPT only if:
          Sharpe >= 0.88          (v0 was 0.73, need +0.15)
      AND Max drawdown <= 22.80%  (v0's drawdown, must not get worse)
      AND the trade count is sane (not 4, not 5000)

      Note the likely failure mode: 2010-2018 was a near-uninterrupted bull run.
      A rule that sits in cash part of the time may well LOSE to buy-and-hold
      over this window. That is a legitimate result, not a broken strategy.

    Window:  BUILD  (2010-01-01 -> 2018-12-31)
    Record:  CAGR, Max Drawdown, Sharpe, Trades  ->  SCOREBOARD.md

    HOW TO RUN
      1. QuantConnect -> paste this whole file over main.py
      2. Backtest
      3. Take: Compounding Annual Return, Drawdown, Sharpe Ratio, Total Orders
      4. Put them in SCOREBOARD.md with the commit hash (git log -1 --pretty=%h)
    """

    def initialize(self):
        # --- Build window. Do not change to the holdout period (2019 onward)
        # --- without reading README.md section 4 first.
        self.set_start_date(2010, 1, 1)
        self.set_end_date(2018, 12, 31)
        self.set_cash(100000)

        # Realistic fees and fill assumptions. Never turn this off.
        self.set_brokerage_model(
            BrokerageName.INTERACTIVE_BROKERS_BROKERAGE,
            AccountType.MARGIN,
        )

        self.qqq = self.add_equity("QQQ", Resolution.DAILY).symbol

        # The one parameter of this strategy. When we test robustness later we
        # nudge this +/-25% (so 15 and 25) and check the result does not collapse.
        self.lookback = 20

        # Holds the previous N closes. maxlen makes it drop the oldest
        # automatically, so it is always exactly the trailing window.
        self.closes = deque(maxlen=self.lookback)

    def on_data(self, data: Slice):
        if not data.contains_key(self.qqq) or data[self.qqq] is None:
            return

        close = data[self.qqq].close

        # Warm-up: we need a full window before we can compare against anything.
        if len(self.closes) < self.lookback:
            self.closes.append(close)
            return

        # IMPORTANT: compare today's close against the window BEFORE adding
        # today to it. If we appended first, today's close would be part of its
        # own high/low band and the rule could never trigger. That is also how
        # look-ahead bias sneaks into hand-rolled backtests.
        highest = max(self.closes)
        lowest = min(self.closes)

        if close > highest:
            # New 20-day high -> be fully long. Idempotent if already long.
            self.set_holdings(self.qqq, 1.0)
        elif close < lowest:
            # New 20-day low -> go to cash. Not short. Flat.
            self.liquidate(self.qqq)

        self.closes.append(close)
