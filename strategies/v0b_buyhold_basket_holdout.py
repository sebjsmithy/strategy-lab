# region imports
from AlgorithmImports import *
# endregion

# =============================================================================
#  H0 - HOLDOUT BENCHMARK. Pre-registered in HOLDOUT.md. Run ONCE.
# =============================================================================


class V0bBuyHoldBasketHoldout(QCAlgorithm):
    """
    H0 - THE BENCHMARK. Equal-weight, always 100% long all ten ETFs.

    No signal. No timing. No shorting. Buy 10% of each of the ten markets and
    rebalance back to equal weight once a month. That is the entire algorithm.

    WHY THIS RUN EXISTS
      Without it the holdout result is uninterpretable. If the trend strategy
      returns 8% a year, is that good? Only if simply owning the same ten markets
      returned less. 2017-2025 contained a long equity bull run; a strategy that
      spends time short will give a lot of that up. We need to know by how much.

      This is the same role v0 (buy & hold QQQ) played in the build window, but
      matched to the actual universe being traded.

    WHAT IT ISOLATES
      H0 -> H1 is the value of the TREND SIGNAL. Everything else is identical:
      same ten markets, same monthly rebalance, same fees, same starting capital.
      The only difference is that H0 is always long everything and H1 lets the
      1/3/12-month trend decide direction and conviction.

      H1 -> H2 is then the value of VOLATILITY SCALING.

    NOTE ON WHAT THIS BENCHMARK IS
      It is a naive equally-weighted multi-asset portfolio, not a sensible
      investment. Holding 10% in silver and 10% in an agriculture fund is not
      what anyone would advise. It is the right benchmark here precisely because
      it holds the universe constant - it answers "did the signal add anything to
      these ten markets", not "was this a good portfolio".

    Window:  HOLDOUT  (2017-01-01 -> 2025-12-31)   ** H0 - ONE RUN ONLY **
    Record:  CAGR, Max Drawdown, Sharpe, Trades  ->  SCOREBOARD.md

    HOW TO RUN
      1. QuantConnect -> paste this whole file over main.py
      2. Backtest
      3. Take: Compounding Annual Return, Drawdown, Sharpe Ratio, Total Orders
    """

    TICKERS = [
        "GLD", "SLV", "DBC", "DBA",   # commodities
        "SPY", "EFA", "EEM",          # equities
        "TLT", "IEF",                 # bonds
        "UUP",                        # currency
    ]

    def initialize(self):
        # --- HOLDOUT WINDOW. One-shot exam. See HOLDOUT.md.
        self.set_start_date(2017, 1, 1)
        self.set_end_date(2025, 12, 31)
        self.set_cash(100000)

        self.set_brokerage_model(
            BrokerageName.INTERACTIVE_BROKERS_BROKERAGE,
            AccountType.MARGIN,
        )

        self.symbols = [
            self.add_equity(ticker, Resolution.DAILY).symbol
            for ticker in self.TICKERS
        ]

        self.last_month = -1

    def on_data(self, data: Slice):
        # Monthly rebalance, matching the strategy versions so the comparison is
        # like-for-like on trading cadence.
        if self.time.month == self.last_month:
            return
        self.last_month = self.time.month

        weight = 1.0 / len(self.symbols)

        for symbol in self.symbols:
            # Skip a market with no bar this slice rather than guessing.
            if not data.contains_key(symbol) or data[symbol] is None:
                continue
            # Always fully long, equal weight. set_holdings takes a target, so
            # this simply rebalances back to 10% each month.
            self.set_holdings(symbol, weight)
