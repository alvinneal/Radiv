import pandas as pd


def load(period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch Nifty 50 data from Yahoo Finance.

    Parameters
    ----------
    period   : How far back — "1y", "6mo", "2y", etc.
    interval : Candle size — "1d", "1h", "15m", "5m".
               Intraday intervals only go back ~60 days.

    Returns
    -------
    DataFrame with columns: open, high, low, close, volume
    """
    try:
        import yfinance as yf
    except ImportError:
        raise ImportError("yfinance not installed. Run: pip install yfinance")

    ticker = yf.Ticker("^NSEI")
    df = ticker.history(period=period, interval=interval)

    if df.empty:
        raise RuntimeError(
            "No data returned from Yahoo Finance. "
            "Check your internet connection and try again."
        )

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.columns = ["open", "high", "low", "close", "volume"]
    df.dropna(inplace=True)
    return df