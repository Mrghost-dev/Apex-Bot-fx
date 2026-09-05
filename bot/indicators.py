
import numpy as np
import pandas as pd

def add_indicators(df):
    x = df.copy()
    x["ema20"] = x["Close"].ewm(span=20, adjust=False).mean()
    x["ema50"] = x["Close"].ewm(span=50, adjust=False).mean()
    x["ema200"] = x["Close"].ewm(span=200, adjust=False).mean()
    delta = x["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    x["rsi"] = 100 - (100/(1+rs))
    x["atr"] = (x["High"]-x["Low"]).rolling(14).mean()
    x["range_high"] = x["High"].rolling(20).max()
    x["range_low"] = x["Low"].rolling(20).min()
    return x

def recent_swing(df, n=3):
    x = df.tail(max(30, n*8)).reset_index(drop=True)
    highs, lows = [], []
    for i in range(n, len(x)-n):
        if x.loc[i,"High"] == x.loc[i-n:i+n,"High"].max():
            highs.append((i, x.loc[i,"High"]))
        if x.loc[i,"Low"] == x.loc[i-n:i+n,"Low"].min():
            lows.append((i, x.loc[i,"Low"]))
    return highs, lows
