# region imports
from AlgorithmImports import *
from collections import deque
# endregion

# =============================================================================
#  H1 - HOLDOUT RUN. Identical to the build-window version except the dates.
#  Pre-registered in HOLDOUT.md. Run ONCE. Do not tune anything afterwards -
#  the holdout is spent the moment it is read.
# =============================================================================


class V2aHoldout(QCAlgorithm):
    """
    v2a - MULTI-ASSET TREND FOLLOWING, EQUAL WEIGHT (no volatility scaling).

    The first version in this project that follows the academic literature rather
    than a YouTube video. See `Academic Papers/NOTES.md`.

    WHAT CHANGED FROM v1s
      Three things, deliberately, because we are switching to the paper's method:
        1. Ten markets instead of one.
        2. Signal is the SIGN OF PAST RETURN, not a Donchian channel breakout.
        3. Three lookbacks blended equally instead of one chosen lookback.
      Rebalancing also moves from daily to monthly.

      This breaks our usual one-change-at-a-time rule. It is done knowingly: v1/v1s
      tested a rule the papers do not use, on a universe that cannot detect the
      effect. Porting one piece at a time would mean several more uninformative
      runs. v2a is a fresh baseline for the paper's method, and v2b then makes the
      single clean comparison that matters (vol-scaling on/off).

    THE RULE, per market, at each monthly rebalance
        S1  = sign(return over past  21 trading days)   ~  1 month
        S3  = sign(return over past  63 trading days)   ~  3 months
        S12 = sign(return over past 252 trading days)   ~ 12 months

        position = (S1 + S3 + S12) / 3      -> one of -1.0, -0.33, +0.33, +1.0
        weight   = position / 10            -> equal notional per market

      Each signal is binary. Because the three are equal-weighted, position size
      scales with how much the timescales AGREE. All three pointing the same way
      gives a full position; two-against-one gives a third. When horizons disagree
      - exactly when trends are ambiguous and whipsaw is most costly - exposure is
      small automatically.

      Max gross exposure is 10 x 0.10 x 1.0 = 100%. No leverage by construction.

    WHY THERE IS NO LOOKBACK TO TUNE
      Blending 1/3/12 months removes parameter selection entirely. There is no
      sweep to run and no plateau to hunt for. The weights are equal by design;
      optimising them would drag the overfitting problem straight back in.

      Note this project's v1 sweep only tested 5-50 days. The paper's primary
      signal is 252 days - five times longer than anything previously tried here.

    THE UNIVERSE - 4 commodity, 3 equity, 2 bond, 1 currency
      Mirrors the papers' ~43% commodity weighting. Diversified ACROSS asset
      classes, not within: nominal N is 10 but effective N is more like 5-6,
      since SPY/EFA/EEM move together and TLT/IEF nearly duplicate.

    WHY LONG AND SHORT IS FINE HERE WHEN IT FAILED ON QQQ
      QQQ has structural upward drift, so shorting it fights gravity - that is why
      v1s lost 18%. Gold, commodities, bonds and currencies have no such drift.
      Shorting them is the symmetric other half of the bet, not a losing lean.

    PRE-REGISTERED HYPOTHESIS
      v2a is KEPT if Sharpe >= 0.50 over the build window.

      Reasoning for that bar rather than the usual 0.88: the papers report an
      average single-market Sharpe of ~0.4, and with maybe 5-6 effective
      independent bets the theoretical ceiling is around 0.4 x sqrt(5) ~ 0.9 -
      but that assumes vol-scaling, which v2a deliberately lacks, and assumes
      correlations behave. v2a is the deliberately handicapped version.

      Also note the build window includes 2008, which was an exceptional year for
      trend-following. A strong result may be carried by that one year - check the
      equity curve, not just the summary number.

      Claude's prediction: positive but unspectacular, Sharpe roughly 0.3-0.6,
      with v2b beating it. Recorded in advance.

    Window:  HOLDOUT  (2017-01-01 -> 2025-12-31)   ** H1 - ONE RUN ONLY **   
    Record:  CAGR, Max Drawdown, Sharpe, Trades  ->  SCOREBOARD.md

    HOW TO RUN
      1. QuantConnect -> paste this whole file over main.py
         (keep only ONE algorithm file in the project)
      2. Backtest
      3. Take: Compounding Annual Return, Drawdown, Sharpe Ratio, Total Orders
      4. Also check the Exposure and Portfolio Margin charts - gross exposure
         should stay at or below 100%
      5. Put the numbers in SCOREBOARD.md with the commit hash
    """

    TICKERS = [
        "GLD", "SLV", "DBC", "DBA",   # commodities
        "SPY", "EFA", "EEM",          # equities
        "TLT", "IEF",                 # bonds
        "UUP",                        # currency
    ]

    # ~1, 3 and 12 months in trading days.
    LOOKBACKS = [21, 63, 252]

    def initialize(self):
        # --- Build window. Do NOT change to the holdout (2017 onward) without
        # --- reading README.md section 4 first. The holdout is a one-shot exam.
        self.set_start_date(2017, 1, 1)
        self.set_end_date(2025, 12, 31)
        self.set_cash(100000)

        # Margin account is required to hold short positions.
        # Models commissions. Does NOT model short borrow costs - see NOTES.
        self.set_brokerage_model(
            BrokerageName.INTERACTIVE_BROKERS_BROKERAGE,
            AccountType.MARGIN,
        )

        self.max_lookback = max(self.LOOKBACKS)

        self.symbols = []
        self.closes = {}
        for ticker in self.TICKERS:
            symbol = self.add_equity(ticker, Resolution.DAILY).symbol
            self.symbols.append(symbol)
            # +1 so that prices[-1 - 252] is a valid index once full.
            self.closes[symbol] = deque(maxlen=self.max_lookback + 1)

        # Feed a year of history before the start date so the 12-month signal is
        # live from day one. Without this the strategy would sit idle through
        # 2008 - the single most important year in the build window.
        self.set_warm_up(self.max_lookback + 1, Resolution.DAILY)

        self.last_month = -1

    def on_data(self, data: Slice):
        # Record closes every day, including during warm-up.
        for symbol in self.symbols:
            if data.contains_key(symbol) and data[symbol] is not None:
                self.closes[symbol].append(data[symbol].close)

        if self.is_warming_up:
            return

        # Monthly rebalance: act on the first trading day of a new month.
        # Done this way rather than via the scheduler to keep the API surface
        # small - fewer calls, fewer things to get wrong.
        if self.time.month == self.last_month:
            return
        self.last_month = self.time.month

        self.rebalance()

    def rebalance(self):
        weight_per_market = 1.0 / len(self.symbols)

        for symbol in self.symbols:
            prices = list(self.closes[symbol])

            # Not enough history yet (e.g. an ETF that started late). Skip it
            # rather than guessing - it will join once it has a full window.
            if len(prices) < self.max_lookback + 1:
                continue

            today = prices[-1]

            signals = []
            for lookback in self.LOOKBACKS:
                past = prices[-1 - lookback]
                if past <= 0:
                    continue
                past_return = today / past - 1.0
                # Binary: up trend -> long, down trend -> short.
                signals.append(1.0 if past_return > 0 else -1.0)

            if not signals:
                continue

            # Equal-weighted blend. Position scales with agreement across horizons.
            position = sum(signals) / len(signals)

            # set_holdings takes a TARGET weight, so calling it repeatedly is
            # idempotent and cannot accidentally accumulate leverage.
            self.set_holdings(symbol, weight_per_market * position)
