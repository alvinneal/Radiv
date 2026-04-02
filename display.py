"""
Radiv/display.py
════════════════
Clean terminal output. All printing lives here.
"""

import pandas as pd


# ─── ANSI COLORS ─────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[32m"
    RED    = "\033[31m"
    YELLOW = "\033[33m"
    CYAN   = "\033[36m"


SIGNAL_STYLE = {
    "STRONG BUY":  (C.GREEN + C.BOLD, "▲▲"),
    "BUY":         (C.GREEN,          "▲ "),
    "HOLD":        (C.YELLOW,         "── "),
    "SELL":        (C.RED,            "▼ "),
    "STRONG SELL": (C.RED + C.BOLD,   "▼▼"),
    "WAIT":        (C.DIM,            "·· "),
}


# ─── HEADER ──────────────────────────────────────────────────────────────────

def header(indicators: str = "EMA"):
    print(f"""
{C.CYAN}{C.BOLD}  ┌──────────────────────────────────────────────┐
  │              R A D I V                       │
  │        Your Radar for Derivatives            │
  ├──────────────────────────────────────────────┤
  │  Nifty 50  ·  {indicators:<30s}│
  └──────────────────────────────────────────────┘{C.RESET}
""")


# ─── LATEST SIGNAL ───────────────────────────────────────────────────────────

def latest(df: pd.DataFrame):
    row = df.iloc[-1]
    prev = df.iloc[-2]
    change_pct = (row["close"] / prev["close"] - 1) * 100
    gap_pct = (row["ema_fast"] - row["ema_slow"]) / row["ema_slow"] * 100

    style, arrow = SIGNAL_STYLE.get(row["signal"], (C.YELLOW, "?"))
    date_str = df.index[-1].strftime("%Y-%m-%d")

    print(f"  {C.BOLD}LATEST{C.RESET}  {C.DIM}{date_str}{C.RESET}")
    print(f"  {'─' * 46}")
    print(f"  Close        {C.BOLD}₹{row['close']:>10,.2f}{C.RESET}  ({change_pct:+.2f}%)")
    print(f"  EMA 9        ₹{row['ema_fast']:>10,.2f}")
    print(f"  EMA 21       ₹{row['ema_slow']:>10,.2f}   gap: {gap_pct:+.2f}%")

    if row["bullish_cross"]:
        print(f"               {C.GREEN}★ Bullish crossover today{C.RESET}")
    elif row["bearish_cross"]:
        print(f"               {C.RED}★ Bearish crossover today{C.RESET}")

    print()
    print(f"  Signal       {style}{arrow} {row['signal']}{C.RESET}")
    print(f"  {C.DIM}{row['reason']}{C.RESET}")
    print()


# ─── RECENT TABLE ────────────────────────────────────────────────────────────

def recent(df: pd.DataFrame, n: int = 15):
    tail = df.tail(n)
    print(f"  {C.BOLD}RECENT{C.RESET}  (last {n} days)")
    print(f"  {'─' * 46}")
    print(f"  {C.DIM}{'Date':<12s} {'Close':>10s} {'EMA gap':>8s}  Signal{C.RESET}")

    for idx, row in tail.iterrows():
        date_str = idx.strftime("%Y-%m-%d")
        gap = (row["ema_fast"] - row["ema_slow"]) / row["ema_slow"] * 100
        style, arrow = SIGNAL_STYLE.get(row["signal"], (C.YELLOW, "?"))

        print(
            f"  {date_str}  ₹{row['close']:>9,.2f} "
            f"{gap:>+7.2f}%  {style}{arrow} {row['signal']}{C.RESET}"
        )
    print()


# ─── STATS ───────────────────────────────────────────────────────────────────

def stats(df: pd.DataFrame):
    valid = df[df["signal"] != "WAIT"]
    counts = valid["signal"].value_counts()
    total = len(valid)

    print(f"  {C.BOLD}STATS{C.RESET}  ({total} trading days)")
    print(f"  {'─' * 46}")

    for sig in ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]:
        c = counts.get(sig, 0)
        pct = c / total * 100 if total else 0
        bar = "█" * int(pct / 2.5)
        style, _ = SIGNAL_STYLE.get(sig, (C.YELLOW, ""))
        print(f"  {style}{sig:<12s}{C.RESET}  {c:>4d}  ({pct:>5.1f}%)  {C.DIM}{bar}{C.RESET}")
    print()


# ─── DISCLAIMER ──────────────────────────────────────────────────────────────

def disclaimer():
    print(f"  {C.DIM}⚠  Educational only. Not financial advice.{C.RESET}")
    print()