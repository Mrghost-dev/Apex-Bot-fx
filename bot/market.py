
import pandas as pd
import yfinance as yf

MAP = {
    "XAUUSD": "GC=F",
    "GOLD": "GC=F",
    "XAGUSD": "SI=F",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X",
    "USDCHF": "CHF=X",
    "USDCAD": "CAD=X",
    "AUDUSD": "AUDUSD=X",
    "NZDUSD": "NZDUSD=X",
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "SPX": "^GSPC",
    "NAS100": "^NDX",
}

def normalize_symbol(symbol):
    s = symbol.upper().replace("/", "").replace("-", "")
    return MAP.get(s, symbol)

def fetch_ohlcv(symbol, interval="15m", period="5d"):
    ticker = normalize_symbol(symbol)
    df = yf.download(ticker, interval=interval, period=period, auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise RuntimeError(f"No market data returned for {symbol} ({ticker}).")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={c: c.capitalize() for c in df.columns})
    required = ["Open","High","Low","Close"]
    for c in required:
        if c not in df.columns:
            raise RuntimeError(f"Market provider did not return {c} data.")
    df = df[required + ([ "Volume" ] if "Volume" in df.columns else [])].dropna()
    df.index = pd.to_datetime(df.index)
    df = df.reset_index().rename(columns={"Datetime":"Time","Date":"Time"})
    return df
