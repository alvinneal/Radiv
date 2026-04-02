import numpy as np
import pandas as pd

"""
    EMA
       multiplier = 2 / (period + 1)
       EMA_today  = (price × multiplier) + (EMA_yesterday × (1 - multiplier))
"""

def ema(close: pd.Series, period: int) -> pd.Series:
    return close.ewm(span=period, adjust=False).mean()

"""
    EMA Crossover
        Fast crosses ABOVE slow → bullish (uptrend starting)
        Fast crosses BELOW slow → bearish (downtrend starting)
"""

def ema_crossover(
    close: pd.Series,
    fast_period: int = 9,
    slow_period: int = 21,
) -> pd.DataFrame:
    fast = ema(close, fast_period)
    slow = ema(close, slow_period)

    bullish = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    bearish = (fast < slow) & (fast.shift(1) >= slow.shift(1))
    trend = np.where(fast > slow, "BULLISH", "BEARISH")

    return pd.DataFrame({
        "ema_fast": fast,
        "ema_slow": slow,
        "bullish_cross": bullish,
        "bearish_cross": bearish,
        "trend": trend,
    }, index=close.index)