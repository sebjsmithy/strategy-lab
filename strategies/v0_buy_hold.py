# region imports
from AlgorithmImports import *
# endregion


class V0BuyHold(QCAlgorithm):
    """
    v0 - BASELINE.

    Buy QQQ on the first day, hold to the end. There is no strategy here.
    That is the whole point.

    This is the number every later version has to beat. If v1..v5 cannot beat
    simply owning the index and going to sleep, that IS the finding - and it is
    a more honest result than most of what gets posted online.

    Pre-registered hypothesis: none. This is the thing to be measured against.

    Window:  BUILD  (2010-01-01 -> 2018-12-31)
    Record:  CAGR, Max Drawdown, Sharpe, Trades  ->  SCOREBOARD.md

    HOW TO RUN
      1. QuantConnect -> Create New Algorithm
      2. Paste this whole file over main.py
      3. Backtest
      4. From the results page take: Compounding Annual Return, Drawdown,
         Sharpe Ratio, Total Orders
      5. Put them in SCOREBOARD.md with the commit hash (git log -1 --pretty=%h)
    """

    def Initialize(self):
        # --- Build window. Do not change these dates to the holdout period
        # --- (2019 onward) without reading README.md section 4 first.
        self.SetStartDate(2010, 1, 1)
        self.SetEndDate(2018, 12, 31)
        self.SetCash(100000)

        # Realistic fees and fill assumptions. Keep this in EVERY version.
        # A backtest without costs is a fantasy.
        self.SetBrokerageModel(
            BrokerageName.InteractiveBrokersBrokerage,
            AccountType.Margin,
        )

        self.qqq = self.AddEquity("QQQ", Resolution.Daily).Symbol

    def OnData(self, data: Slice):
        # Already fully invested - nothing to do for the rest of the backtest.
        if self.Portfolio.Invested:
            return

        # Guard against a missing bar on the very first day.
        if not data.ContainsKey(self.qqq) or data[self.qqq] is None:
            return

        # SetHoldings takes a TARGET WEIGHT, not an order.
        # 1.0 means "I want 100% of the portfolio in QQQ".
        # Because it is a target, calling it repeatedly does not buy more -
        # which is why repeat signals cannot accidentally leverage us up.
        # See README.md section 7, "Repeat signals and pyramiding".
        self.SetHoldings(self.qqq, 1.0)
