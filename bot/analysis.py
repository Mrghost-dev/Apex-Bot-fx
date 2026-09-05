
import math
import pandas as pd
from .indicators import add_indicators, recent_swing
from .strategy import strategy_summary

def _clamp(v, a=5, b=95):
    return max(a, min(b, v))

def analyze_market(symbol, timeframe, df, strategy, news, risk_pct=1.0):
    x = add_indicators(df)
    last = x.iloc[-1]
    prev = x.iloc[-2]
    close = float(last.Close)
    atr = float(last.atr) if pd.notna(last.atr) else float((x.High-x.Low).tail(14).mean())
    atr = max(atr, close * 0.0005)

    score = 50.0
    reasons = {"structure":[], "smc":[], "crt":[], "strategy":[], "risk":[]}

    # Trend / structure
    bullish = last.ema20 > last.ema50
    bearish = last.ema20 < last.ema50
    if bullish:
        score += 12
        reasons["structure"].append("EMA20 is above EMA50, giving a short-term bullish structure bias.")
    elif bearish:
        score -= 12
        reasons["structure"].append("EMA20 is below EMA50, giving a short-term bearish structure bias.")

    if close > last.ema200:
        score += 7
        reasons["structure"].append("Price is above EMA200.")
    else:
        score -= 7
        reasons["structure"].append("Price is below EMA200.")

    if last.rsi > 55:
        score += 5
        reasons["structure"].append("RSI confirms positive momentum.")
    elif last.rsi < 45:
        score -= 5
        reasons["structure"].append("RSI confirms negative momentum.")

    highs, lows = recent_swing(x)
    swing_high = highs[-1][1] if highs else float(x.High.tail(20).max())
    swing_low = lows[-1][1] if lows else float(x.Low.tail(20).min())

    # Liquidity sweep heuristic
    prev20h = float(x.High.iloc[-21:-1].max()) if len(x) > 21 else float(x.High.max())
    prev20l = float(x.Low.iloc[-21:-1].min()) if len(x) > 21 else float(x.Low.min())
    sweep_high = float(last.High) > prev20h and close < prev20h
    sweep_low = float(last.Low) < prev20l and close > prev20l
    if sweep_low:
        score += 9
        reasons["smc"].append("Potential sell-side liquidity sweep followed by recovery.")
    if sweep_high:
        score -= 9
        reasons["smc"].append("Potential buy-side liquidity sweep followed by rejection.")

    # Displacement / candle body
    body = abs(float(last.Close-last.Open))
    if body > atr * 0.8:
        if last.Close > last.Open:
            score += 6
            reasons["smc"].append("Bullish displacement-style candle detected.")
        else:
            score -= 6
            reasons["smc"].append("Bearish displacement-style candle detected.")

    # CRT zones based on prior completed candle range
    prior = x.iloc[-2]
    crt_high = float(prior.High)
    crt_low = float(prior.Low)
    crt_eq = (crt_high + crt_low)/2
    if close < crt_eq:
        score += 4
        reasons["crt"].append("Price is in the lower half (discount) of the prior candle range.")
    else:
        score -= 4
        reasons["crt"].append("Price is in the upper half (premium) of the prior candle range.")

    # Strategy text adaptation
    active = strategy["features"]
    if active["smc"] or active["ict"]:
        score += 4 if (sweep_low or sweep_high or body > atr*0.8) else -2
        reasons["strategy"].append("Custom strategy contains SMC/ICT concepts; liquidity/displacement evidence was weighted.")
    if active["crt"]:
        reasons["strategy"].append("CRT was explicitly requested, so premium/equilibrium/discount context was included.")
    if active["news_filter"]:
        reasons["strategy"].append("News filtering was explicitly requested; headline context is shown separately.")
    reasons["strategy"].append("Strategy profile: " + strategy_summary(strategy))

    direction = "BUY" if score >= 50 else "SELL"
    confidence = _clamp(score if direction=="BUY" else 100-score)

    # Entry / invalidation model
    if direction == "BUY":
        entry = close
        stop = min(float(x.Low.tail(8).min()), close - atr*1.2)
        risk = max(entry-stop, atr*0.8)
        target = entry + risk * strategy["target_rr"]
        invalidation = f"Close below {stop:.5f} or bullish structure fails."
        mode = "Market / confirmation"
        if sweep_low:
            mode = "Liquidity sweep → MSS/displacement confirmation"
    else:
        entry = close
        stop = max(float(x.High.tail(8).max()), close + atr*1.2)
        risk = max(stop-entry, atr*0.8)
        target = entry - risk * strategy["target_rr"]
        invalidation = f"Close above {stop:.5f} or bearish structure fails."
        mode = "Market / confirmation"
        if sweep_high:
            mode = "Liquidity sweep → MSS/displacement confirmation"

    rr = abs(target-entry)/max(abs(entry-stop), 1e-12)
    expiry = {"5m":45, "15m":120, "30m":180, "1h":300, "4h":720, "1d":2880}.get(timeframe, 120)

    # News caution heuristic
    if news:
        reasons["risk"].append(f"{len(news)} recent market/news headlines were collected. Check high-impact calendar events before execution.")
        confidence = _clamp(confidence - 2)
    else:
        reasons["risk"].append("No external news items were available; treat the setup as lower-context.")

    reasons["risk"].append(f"Risk setting supplied by user: {risk_pct:.2f}% per trade.")
    reasons["risk"].append("Confidence is a model score, not a win-rate guarantee.")

    status = "ACTIONABLE IF CONFIRMED" if confidence >= 65 and rr >= 1.5 else "WAIT FOR CONFIRMATION"

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "signal": {
            "direction": direction,
            "status": status,
            "confidence": confidence,
            "entry": entry,
            "stop_loss": stop,
            "take_profit": target,
            "rr": rr,
            "strategy": strategy_summary(strategy),
            "entry_mode": mode,
            "expiry_minutes": expiry,
            "invalidation": invalidation,
        },
        "reasoning": reasons,
        "news": news,
        "chart": {
            "time": x["Time"].astype(str).tolist(),
            "open": x["Open"].tolist(),
            "high": x["High"].tolist(),
            "low": x["Low"].tolist(),
            "close": x["Close"].tolist(),
        }
    }
