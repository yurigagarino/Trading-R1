# Trading-R1 — independent research fork

A runnable, dependency-free Python foundation for historical strategy research.
The upstream [TauricResearch/Trading-R1](https://github.com/TauricResearch/Trading-R1)
currently publishes only a terminal announcement. This fork's code is independently
written; it does not implement or reproduce the Trading-R1 paper or model.

## Run

Requires Python 3.10 or newer. From the repository root:

```bash
python -m trading_r1 examples/demo.csv --output results.json
python -m unittest discover -s tests -v
```

Supply your own CSV with `date,close` columns. Dates must be unique, ascending ISO
dates and prices must be finite and positive. The bundled data is synthetic.

```bash
python -m trading_r1 prices.csv --fast 10 --slow 30 --cash 10000 \
  --fee-bps 10 --slippage-bps 5 --allocation 0.9 --output results.json
```

## Included

- Long/cash moving-average baseline and a buy-and-hold benchmark using the same costs and allocation.
- Signals calculated after a close, filled at the following bar's close.
- Fees, directional slippage, fractional units, cash accounting, equity and maximum drawdown.
- Full JSON equity curves, execution ledger and configuration for inspection.
- Tests for timing, future-data independence, costs, accounting and invalid inputs.

## Modeling limits

This is an offline backtest, not a live paper broker. Next-close fills deliberately
use close-only data; there are no intrabar fills, liquidity constraints, funding,
taxes or corporate actions. Remaining positions are marked at the final close,
without liquidation costs. Drawdown is sampled at closes. Buy-and-hold enters on
bar two; SMA remains cash during warm-up, so their exposure periods differ.
Currencies and sampling frequency are determined by your input. Results are not
evidence that a strategy will work on unseen markets.

## Development direction

1. OHLCV adapters and next-open execution with explicit data provenance.
2. Out-of-sample evaluation, parameter sweeps and reproducible experiment reports.
3. A terminal interface for charts, execution history and strategy comparisons.
4. Optional model-generated research signals behind the same execution engine.

No upstream code or model weights were available to import, and this change does
not assign a license to the upstream project.
