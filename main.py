#!/usr/bin/env python3

import sys

from Radiv import data, signals, backtest, display


def main():
    df = data.load()

    display.header(indicators="EMA")

    df = signals.generate(df)

    display.latest(df)
    display.recent(df, n=15)
    display.stats(df)

    if "--backtest" in sys.argv:
        results = backtest.run(df)
        backtest.display(results)

    display.disclaimer()


if __name__ == "__main__":
    main()