import argparse
import json
from pathlib import Path
from .engine import backtest, load_csv


def main():
    parser = argparse.ArgumentParser(description="Trading-R1 fork: offline research backtest")
    parser.add_argument("csv", help="CSV containing ISO date and close columns")
    parser.add_argument("--fast", type=int, default=3)
    parser.add_argument("--slow", type=int, default=5)
    parser.add_argument("--cash", type=float, default=10000)
    parser.add_argument("--fee-bps", type=float, default=10)
    parser.add_argument("--slippage-bps", type=float, default=5)
    parser.add_argument("--allocation", type=float, default=0.9)
    parser.add_argument("--output", type=Path, help="Save full JSON results")
    args = parser.parse_args()
    try:
        bars = load_csv(args.csv)
        config = dict(fast=args.fast, slow=args.slow, initial_cash=args.cash,
                      fee_bps=args.fee_bps, slippage_bps=args.slippage_bps,
                      allocation=args.allocation)
        results = {name: backtest(bars, strategy=name, **config)
                   for name in ("sma", "buy_hold")}
        if args.output:
            args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, KeyError) as error:
        parser.error(str(error))
    for name, result in results.items():
        print(f"{name}: equity={result['final_equity']:.2f}, "
              f"return={result['return_pct']:.2f}%, "
              f"max drawdown={result['max_drawdown_pct']:.2f}%, "
              f"fills={result['trade_count']}")


if __name__ == "__main__":
    main()
