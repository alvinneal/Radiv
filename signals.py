import pandas as pd
import numpy as np
from Radiv.indicators import ema_crossover


DEFAULT_CONFIG = {
    "ema_fast": 9,
    "ema_slow": 21,
}

# Signal Generation
def generate(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    df     : OHLCV DataFrame (needs 'close' column).
    config : Optional overrides for DEFAULT_CONFIG.

    Returns : DataFrame with added indicator columns + signal + reason.
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    df = df.copy()

    # Compute EMA crossover
    cross = ema_crossover(df["close"], cfg["ema_fast"], cfg["ema_slow"])
    df["ema_fast"] = cross["ema_fast"]
    df["ema_slow"] = cross["ema_slow"]
    df["bullish_cross"] = cross["bullish_cross"]
    df["bearish_cross"] = cross["bearish_cross"]
    df["trend"] = cross["trend"]

    # Generate signals
    signals = []
    reasons = []

    for i in range(len(df)):
        row = df.iloc[i]

        if pd.isna(row["ema_fast"]) or pd.isna(row["ema_slow"]):
            signals.append("WAIT")
            reasons.append("Indicators warming up")
            continue

        if row["bullish_cross"]:
            signals.append("BUY")
            reasons.append(f"EMA {cfg['ema_fast']} crossed ABOVE {cfg['ema_slow']}")
        elif row["bearish_cross"]:
            signals.append("SELL")
            reasons.append(f"EMA {cfg['ema_fast']} crossed BELOW {cfg['ema_slow']}")
        elif row["trend"] == "BULLISH":
            signals.append("HOLD")
            reasons.append(f"EMA trend: BULLISH (no new crossover)")
        else:
            signals.append("HOLD")
            reasons.append(f"EMA trend: BEARISH (no new crossover)")

    df["signal"] = signals
    df["reason"] = reasons
    return df