# region imports
from AlgorithmImports import *
from collections import deque
# endregion

# =============================================================================
#  H2 - HOLDOUT RUN. Identical to the build-window version except the dates.
#  Pre-registered in HOLDOUT.md. Run ONCE. Do not tune anything afterwards -
#  the holdout is spent the moment it is read.
# =============================================================================


class V2bHoldout(QCAlgorithm):
    """
    v2b - MULTI-ASSET TREND FOLLOWING, VOLATILITY SCALED.

    Identical to v2a in every respect except how position sizes are set. This is
    the cleanest single-variable comparison in the project: same universe, same
    signal, same window, same costs, same rebalance schedule. Only the sizing
    changes.

    WHAT CHANGED FROM v2a
      v2a gave every market the same number of DOLLARS:
          weight_i = position_i x 0.10

      v2b gives every market the same amount of RISK:
          weight_i = position_i x (1/vol_i) / sum_j(1/vol_j)

      Quiet markets get more capital, jumpy markets get less, so each contributes
      roughly equally to portfolio risk instead of the loudest one dominating.

    WHY THIS MATTERS HERE - measured, not assumed (see UNIVERSE.md)
      Realised annualised volatility over 2008-2016:

          IEF   7.3%  -> scaled UP   (1.37x)
          UUP   9.1%  -> scaled UP   (1.10x)
          TLT  15.7%
          DBA  19.3%   GLD 19.9%   DBC 20.8%   SPY 21.3%
          EFA  25.8%
          EEM  33.4%  -> scaled DOWN (0.30x)
          SLV  34.5%  -> scaled DOWN (0.29x)

      A 4.7x spread. Under v2a, silver and emerging markets were carrying 4-5x
      the risk of the bond and dollar positions - so the portfolio's results were
      effectively decided by SLV, EEM and EFA while IEF and UUP were inaudible
      no matter how right their signals were.

    WHAT IS DELIBERATELY *NOT* INCLUDED
      The papers also scale the whole book to a 10% annualised volatility target.
      That is omitted here on purpose. Portfolio-level scaling is pure leverage:
      it multiplies returns AND risk by the same factor, so it CANNOT change the
      Sharpe ratio. Including it would inflate the CAGR and make v2b look better
      than v2a for a reason that has nothing to do with skill.

      v2a realised 7.4% volatility, so the paper's target would imply about 1.35x
      leverage. If we want to see the levered version it belongs in a separate
      v2c, clearly labelled as leverage rather than improvement.

      Weights here are normalised to sum to 1.0, so maximum gross exposure is
      100% - identical to v2a. Gross exposure is held constant and only the
      DISTRIBUTION changes. That is what isolates the effect.

    VOLATILITY ESTIMATE
      Simple realised volatility: standard deviation of the last 252 daily
      returns, annualised by sqrt(252). This is the paper's approach (they use a
      longer three-year window; 252 days is used here because it is already in
      the rolling buffer and needs no extra warm-up).

      A GARCH(1,1) forecast would in principle be a better volatility estimate
      because it captures volatility clustering. That is a genuine v2c question -
      "does a better volatility forecast improve the strategy?" - and should be
      tested separately rather than bundled in here. One change at a time.

    PRE-REGISTERED HYPOTHESIS
      v2b is KEPT if its Sharpe beats v2a's -0.015 by at least 0.15, i.e.
      Sharpe >= 0.135.

      Claude's prediction: v2b beats v2a, but probably still lands below 0.3.
      Reasoning - the 4.7x vol spread is large enough that re-weighting should
      matter, and it shifts capital toward bonds, which trended cleanly and
      persistently through 2008-2016.

      HONESTY FLAG ON THAT PREDICTION: it is informed by knowing 2008-2016 was a
      secular bond bull market. It is a mechanism hypothesis, not a blind
      forecast, and should be discounted accordingly.

      Claude was wrong about v2a (predicted 0.3-0.6, actual -0.015), so treat
      this prediction with appropriate scepticism.

    Window:  HOLDOUT  (2017-01-01 -> 2025-12-31)   ** H2 - ONE RUN ONLY **
    Record:  CAGR, Max Drawdown, Sharpe, Trades  ->  SCOREBOARD.md

    HOW TO RUN
      1. QuantConnect -> paste this whole file over main.py
         (keep only ONE algorithm file in the project)
      2. Backtest
      3. Take: Compounding Annual Return, Drawdown, Sharpe Ratio, Total Orders
      4. Compare directly against v2a - same everything except sizing
    """

    TICKERS = [
        "GLD", "SLV", "DBC", "DBA",   # commodities
        "SPY", "EFA", "EEM",          # equities
        "TLT", "IEF",                 # bonds
        "UUP",                        # currency
    ]

    # ~1, 3 and 12 months in trading days.
    LOOKBACKS = [21, 63, 252]

    # Trading days used to estimate realised volatility.
    VOL_WINDOW = 252

    def initialize(self):
        # --- HOLDOUT WINDOW. This is the one-shot exam. Run once, record,
        # --- change nothing afterwards. See HOLDOUT.md.
        self.set_start_date(2017, 1, 1)
        self.set_end_date(2025, 12, 31)
        self.set_cash(100000)

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
            self.closes[symbol] = deque(maxlen=self.max_lookback + 1)

        self.set_warm_up(self.max_lookback + 1, Resolution.DAILY)
        self.last_month = -1

    def on_data(self, data: Slice):
        for symbol in self.symbols:
            if data.contains_key(symbol) and data[symbol] is not None:
                self.closes[symbol].append(data[symbol].close)

        if self.is_warming_up:
            return

        if self.time.month == self.last_month:
            return
        self.last_month = self.time.month

        self.rebalance()

    # --- signal: identical to v2a ------------------------------------------

    def compute_position(self, prices):
        """Blended 1/3/12-month trend. Returns -1.0, -0.33, +0.33 or +1.0."""
        today = prices[-1]
        signals = []
        for lookback in self.LOOKBACKS:
            past = prices[-1 - lookback]
            if past <= 0:
                continue
            signals.append(1.0 if today / past - 1.0 > 0 else -1.0)
        if not signals:
            return None
        return sum(signals) / len(signals)

    # --- sizing: the only thing that differs from v2a ----------------------

    def realised_vol(self, prices):
        """Annualised stdev of the last VOL_WINDOW daily returns."""
        window = prices[-(self.VOL_WINDOW + 1):]
        returns = []
        for i in range(1, len(window)):
            if window[i - 1] > 0:
                returns.append(window[i] / window[i - 1] - 1.0)

        if len(returns) < 2:
            return None

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        vol = (variance ** 0.5) * (252 ** 0.5)

        # Guard against a degenerate estimate producing an enormous weight.
        return vol if vol > 1e-6 else None

    def rebalance(self):
        positions = {}
        inverse_vols = {}

        for symbol in self.symbols:
            prices = list(self.closes[symbol])
            if len(prices) < self.max_lookback + 1:
                continue

            position = self.compute_position(prices)
            vol = self.realised_vol(prices)
            if position is None or vol is None:
                continue

            positions[symbol] = position
            inverse_vols[symbol] = 1.0 / vol

        total_inverse_vol = sum(inverse_vols.values())
        if total_inverse_vol <= 0:
            return

        for symbol, position in positions.items():
            # Risk weights sum to 1.0 across whatever markets have data, so
            # gross exposure is capped at 100% exactly as in v2a. If a market
            # drops out, the rest re-normalise automatically.
            risk_weight = inverse_vols[symbol] / total_inverse_vol
            self.set_holdings(symbol, position * risk_weight)
