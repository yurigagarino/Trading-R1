import unittest
from trading_r1.engine import Bar, backtest


def bars(prices):
    return [Bar(f"2026-01-{i+1:02d}", p) for i, p in enumerate(prices)]


class EngineTests(unittest.TestCase):
    def test_signal_executes_next_bar(self):
        result = backtest(bars([1, 2, 3, 4, 5]), fast=1, slow=2,
                          fee_bps=0, slippage_bps=0, allocation=1)
        self.assertEqual(result["trades"][0]["date"], "2026-01-03")
        self.assertAlmostEqual(result["final_equity"], 10000 * 5 / 3)

    def test_future_prices_do_not_change_earlier_decisions(self):
        config = dict(fast=1, slow=2)
        a = backtest(bars([1, 2, 3, 4, 5]), **config)
        b = backtest(bars([1, 2, 3, 400, 500]), **config)
        self.assertEqual(a["equity_curve"][:3], b["equity_curve"][:3])
        self.assertEqual(a["trades"][0], b["trades"][0])

    def test_flat_round_trip_costs_and_accounting(self):
        result = backtest(bars([100, 100, 100]), strategy="buy_hold",
                          allocation=1, fee_bps=100, slippage_bps=100)
        self.assertAlmostEqual(result["final_equity"], 10000 / 1.01 / 1.01)
        self.assertAlmostEqual(result["equity_curve"][1]["cash"], 0)

    def test_sell_and_drawdown(self):
        result = backtest(bars([1, 2, 3, 2, 1]), fast=1, slow=2,
                          allocation=1, fee_bps=0, slippage_bps=0)
        self.assertEqual([t["side"] for t in result["trades"]], ["buy", "sell"])
        self.assertEqual(result["open_units"], 0)
        self.assertAlmostEqual(result["max_drawdown_pct"], 100 * 2 / 3)

    def test_invalid_data_and_configuration(self):
        for prices in ([1, float("nan"), 3], [1, 0, 3], [1]):
            with self.assertRaises(ValueError):
                backtest(bars(prices), fast=1, slow=2)
        for config in ({"allocation": 2}, {"fee_bps": -1}, {"initial_cash": float("inf")},
                       {"fast": 3, "slow": 2}):
            with self.assertRaises(ValueError):
                backtest(bars([1, 2, 3, 4, 5, 6]), **config)
        with self.assertRaises(ValueError):
            backtest([Bar("2026-01-01", 1), Bar("2026-01-01", 2)])


if __name__ == "__main__":
    unittest.main()
