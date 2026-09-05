
import re

KEYWORDS = {
    "smc": ["smc", "smart money", "liquidity", "order block", "ob", "fvg"],
    "ict": ["ict", "fair value gap", "fvg", "displacement", "market structure shift", "mss"],
    "crt": ["crt", "candle range theory", "premium", "discount", "equilibrium"],
    "news_filter": ["news", "cpi", "nfp", "fomc", "fed", "interest rate", "avoid news"],
    "session": ["london", "new york", "asia", "session"],
    "rr": ["risk reward", "rr", "1:2", "1:3", "two to one", "three to one"],
}

def parse_strategy(text):
    t = text.lower()
    found = {k: any(x in t for x in words) for k, words in KEYWORDS.items()}
    rr = 2.0
    m = re.search(r"(?:1\s*:\s*)(\d+(?:\.\d+)?)", t)
    if m:
        rr = max(1.0, float(m.group(1)))
    return {"text": text, "features": found, "target_rr": rr}

def strategy_summary(strategy):
    active = [k.upper() for k,v in strategy["features"].items() if v]
    return ", ".join(active) if active else "CUSTOM RULES"
