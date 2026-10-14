"""Close-only, long/cash backtest with signals executed on the next bar."""
import csv
import math
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Bar:
    date: str
    close: float


def load_csv(path):
    bars = []
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not {"date", "close"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires date and close columns")
        for row in reader:
            bars.append(Bar(date.fromisoformat(row["date"]).isoformat(), float(row["close"])))
    validate_bars(bars)
    return bars


def validate_bars(bars):
    if len(bars) < 2:
        raise ValueError("At least two bars are required")
    for i, bar in enumerate(bars):
        date.fromisoformat(bar.date)
        if not math.isfinite(bar.close) or bar.close <= 0:
            raise ValueError("Prices must be finite and positive")
        if i and bar.date <= bars[i - 1].date:
            raise ValueError("Dates must be unique and strictly increasing")


def backtest(bars, fast=3, slow=5, initial_cash=10000.0,
             fee_bps=10.0, slippage_bps=5.0, allocation=0.9, strategy="sma"):
    validate_bars(bars)
    if not isinstance(fast, int) or not isinstance(slow, int) or not 0 < fast < slow:
        raise ValueError("Windows must be integers with 0 < fast < slow")
    if strategy not in {"sma", "buy_hold"}:
        raise ValueError("Unknown strategy")
    if not all(math.isfinite(v) for v in (initial_cash, fee_bps, slippage_bps, allocation)):
        raise ValueError("Configuration must be finite")
    if initial_cash <= 0 or not 0 < allocation <= 1:
        raise ValueError("Cash must be positive; allocation must be in (0, 1]")
    if not 0 <= fee_bps < 10000 or not 0 <= slippage_bps < 10000:
        raise ValueError("Costs must be in [0, 10000) basis points")
    if strategy == "sma" and len(bars) <= slow:
        raise ValueError("Need more bars than the slow window to execute a signal")
    cash, units = initial_cash, 0.0
    fee, slip = fee_bps / 10000, slippage_bps / 10000
    pending = False
    trades, curve, closes = [], [], []
    peak, max_drawdown = initial_cash, 0.0
    for i, bar in enumerate(bars):
        # pending was computed using only the preceding bar's information.
        if pending and units == 0:
            price = bar.close * (1 + slip)
            budget = cash * allocation
            units = budget / (price * (1 + fee))
            cost = units * price
            cash -= cost * (1 + fee)
            trades.append({"date": bar.date, "side": "buy", "units": units,
                           "price": price, "fee": cost * fee})
        elif not pending and units > 0:
            price = bar.close * (1 - slip)
            proceeds = units * price
            cash += proceeds * (1 - fee)
            trades.append({"date": bar.date, "side": "sell", "units": units,
                           "price": price, "fee": proceeds * fee})
            units = 0.0
        equity = cash + units * bar.close
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, 1 - equity / peak)
        curve.append({"date": bar.date, "equity": equity, "cash": cash, "units": units})
        closes.append(bar.close)
        pending = strategy == "buy_hold" or (i + 1 >= slow and
            sum(closes[-fast:]) / fast > sum(closes[-slow:]) / slow)
    return {"strategy": strategy, "initial_cash": initial_cash,
            "final_equity": curve[-1]["equity"],
            "return_pct": (curve[-1]["equity"] / initial_cash - 1) * 100,
            "max_drawdown_pct": max_drawdown * 100,
            "trade_count": len(trades), "trades": trades, "equity_curve": curve,
            "open_units": units,
            "config": {"fast": fast, "slow": slow, "fee_bps": fee_bps,
                       "slippage_bps": slippage_bps, "allocation": allocation}}
