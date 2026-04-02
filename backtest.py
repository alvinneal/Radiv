"""
Radiv/backtest.py
═════════════════
Backtesting engine. Simulates trades based on signals.
Completely separate from signal generation.
"""

import pandas as pd
import numpy as np

from Radiv.display import C


def run(
    df: pd.DataFrame,
    capital: float = 100_000.0,
    stop_loss_pct: float = 2.0,
    target_pct: float = 3.0,
) -> dict:
    """
    Simulate trades based on signals.

    Rules:
        • Enter on BUY / STRONG BUY at next day's open.
        • Exit on SELL / STRONG SELL, or when stop/target hit.
        • One position at a time.

    Returns dict with: trades, summary, equity.
    """
    valid = df[df["signal"] != "WAIT"].copy()
    if len(valid) < 2:
        return {"trades": [], "summary": _empty(capital), "equity": pd.Series()}

    trades = []
    equity = []
    cash = capital
    pos = None

    for i in range(1, len(valid)):
        row = valid.iloc[i]
        prev = valid.iloc[i - 1]
        date = valid.index[i]

        if pos is not None:
            hit_stop = row["low"] <= pos["stop"]
            hit_target = row["high"] >= pos["target"]

            exit_price = exit_reason = None

            if hit_stop:
                exit_price, exit_reason = pos["stop"], "stop-loss"
            elif hit_target:
                exit_price, exit_reason = pos["target"], "target"
            elif prev["signal"] in ("SELL", "STRONG SELL"):
                exit_price, exit_reason = row["open"], "signal"

            if exit_price:
                pnl = (exit_price - pos["entry"]) * pos["shares"]
                pnl_pct = (exit_price / pos["entry"] - 1) * 100
                cash += exit_price * pos["shares"]
                trades.append({
                    "entry_date": pos["date"], "exit_date": date,
                    "entry_price": pos["entry"], "exit_price": exit_price,
                    "shares": pos["shares"],
                    "pnl": round(pnl, 2), "pnl_pct": round(pnl_pct, 2),
                    "exit_reason": exit_reason,
                })
                pos = None

        if pos is None and prev["signal"] in ("BUY", "STRONG BUY"):
            entry = row["open"]
            shares = int(cash * 0.95 / entry)
            if shares > 0:
                cash -= entry * shares
                pos = {
                    "entry": entry, "date": date, "shares": shares,
                    "stop": entry * (1 - stop_loss_pct / 100),
                    "target": entry * (1 + target_pct / 100),
                }

        port = cash + (row["close"] * pos["shares"] if pos else 0)
        equity.append({"date": date, "equity": port})

    # Close open position at end
    if pos:
        final = valid.iloc[-1]["close"]
        pnl = (final - pos["entry"]) * pos["shares"]
        cash += final * pos["shares"]
        trades.append({
            "entry_date": pos["date"], "exit_date": valid.index[-1],
            "entry_price": pos["entry"], "exit_price": final,
            "shares": pos["shares"],
            "pnl": round(pnl, 2),
            "pnl_pct": round((final / pos["entry"] - 1) * 100, 2),
            "exit_reason": "end-of-data",
        })

    eq = pd.DataFrame(equity).set_index("date")["equity"] if equity else pd.Series()
    return {"trades": trades, "summary": _summarize(trades, capital, cash, eq), "equity": eq}


# ─── DISPLAY ─────────────────────────────────────────────────────────────────

def display(results: dict):
    s = results["summary"]
    trades = results["trades"]

    print(f"  {C.BOLD}BACKTEST{C.RESET}")
    print(f"  {'─' * 46}")
    print(f"  Capital         ₹{s['start']:>12,.2f}")

    ret_c = C.GREEN if s["return_pct"] >= 0 else C.RED
    print(f"  Final           ₹{s['final']:>12,.2f}  {ret_c}({s['return_pct']:+.2f}%){C.RESET}")
    print(f"  Trades          {s['total']:>5d}   W: {C.GREEN}{s['wins']}{C.RESET}  L: {C.RED}{s['losses']}{C.RESET}  ({s['win_rate']:.0f}%)")
    print(f"  Avg Win/Loss    {C.GREEN}{s['avg_win']:+.2f}%{C.RESET} / {C.RED}{s['avg_loss']:+.2f}%{C.RESET}")
    print(f"  Max Drawdown    {C.RED}{s['max_dd']:.2f}%{C.RESET}")
    print()

    if trades:
        print(f"  {C.BOLD}TRADES{C.RESET}")
        print(f"  {'─' * 46}")
        print(f"  {C.DIM}{'Entry':<12s} {'Exit':<12s} {'P&L':>10s} {'%':>7s}  Why{C.RESET}")

        for t in trades:
            e = t["entry_date"].strftime("%Y-%m-%d") if hasattr(t["entry_date"], "strftime") else str(t["entry_date"])
            x = t["exit_date"].strftime("%Y-%m-%d") if hasattr(t["exit_date"], "strftime") else str(t["exit_date"])
            c = C.GREEN if t["pnl"] >= 0 else C.RED
            print(f"  {e}  {x}  {c}₹{t['pnl']:>+9,.2f}  {t['pnl_pct']:>+6.2f}%{C.RESET}  {t['exit_reason']}")
        print()


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _summarize(trades, start, final, equity):
    if not trades:
        return _empty(start)

    pcts = [t["pnl_pct"] for t in trades]
    wins = [p for p in pcts if p > 0]
    losses = [p for p in pcts if p <= 0]

    max_dd = 0.0
    if len(equity) > 0:
        peak = equity.expanding().max()
        dd = (equity - peak) / peak * 100
        max_dd = abs(dd.min())

    return {
        "start": start, "final": round(final, 2),
        "return_pct": round((final / start - 1) * 100, 2),
        "total": len(trades), "wins": len(wins), "losses": len(losses),
        "win_rate": len(wins) / len(trades) * 100 if trades else 0,
        "avg_win": round(np.mean(wins), 2) if wins else 0,
        "avg_loss": round(np.mean(losses), 2) if losses else 0,
        "max_dd": round(max_dd, 2),
    }


def _empty(capital):
    return {
        "start": capital, "final": capital, "return_pct": 0,
        "total": 0, "wins": 0, "losses": 0, "win_rate": 0,
        "avg_win": 0, "avg_loss": 0, "max_dd": 0,
    }