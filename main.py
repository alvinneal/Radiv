#!/usr/bin/env python3
"""
Radiv — Your Radar for Derivatives

Usage:
    python -m Radiv.main                              # defaults: Nifty 50, 1d, EMA 9/21
    python -m Radiv.main --interval 15m --period 60d  # 15-min candles, 60 days
    python -m Radiv.main --ema-fast 12 --ema-slow 26  # custom EMA periods
    python -m Radiv.main --backtest --capital 500000   # backtest with 5L capital
    python -m Radiv.main --all                         # show everything
"""

import argparse
from Radiv import data, signals, backtest, display


def parse_args():
    p = argparse.ArgumentParser(description="Radiv — Your Radar for Derivatives")

    # What to show
    p.add_argument("--recent", action="store_true", help="show recent signals table")
    p.add_argument("--stats", action="store_true", help="show signal distribution")
    p.add_argument("--backtest", action="store_true", help="run backtest")
    p.add_argument("--all", action="store_true", help="show everything")

    # Data
    p.add_argument("--period", default="1y", help="history length: 1y, 6mo, 2y, 5y (default: 1y)")
    p.add_argument("--interval", default="1d", help="candle size: 1d, 1h, 15m, 5m (default: 1d)")

    # EMA
    p.add_argument("--ema-fast", type=int, default=9, help="fast EMA period (default: 9)")
    p.add_argument("--ema-slow", type=int, default=21, help="slow EMA period (default: 21)")

    # Backtest
    p.add_argument("--capital", type=float, default=100000, help="starting capital (default: 100000)")
    p.add_argument("--sl", type=float, default=2.0, help="stop loss %% (default: 2.0)")
    p.add_argument("--tp", type=float, default=3.0, help="target profit %% (default: 3.0)")

    # Display
    p.add_argument("--days", type=int, default=10, help="days in recent table (default: 10)")

    return p.parse_args()


def main():
    args = parse_args()

    # Fetch data with user's chosen period and interval
    df = data.load(period=args.period, interval=args.interval)

    # Show header with active settings
    display.header(
        ema_fast=args.ema_fast,
        ema_slow=args.ema_slow,
        interval=args.interval,
        period=args.period,
    )

    # Generate signals with user's EMA periods
    df = signals.generate(df, config={
        "ema_fast": args.ema_fast,
        "ema_slow": args.ema_slow,
    })

    # Always show latest
    display.latest(df, ema_fast=args.ema_fast, ema_slow=args.ema_slow)

    # Optional sections
    if args.recent or args.all:
        display.recent(df, n=args.days)

    if args.stats or args.all:
        display.stats(df)

    if args.backtest or args.all:
        results = backtest.run(
            df,
            capital=args.capital,
            stop_loss_pct=args.sl,
            target_pct=args.tp,
        )
        backtest.display(results)

    display.disclaimer()


if __name__ == "__main__":
    main()