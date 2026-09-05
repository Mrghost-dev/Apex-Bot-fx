
import os, json
from datetime import datetime

DIR = os.path.join("data", "analyses")
os.makedirs(DIR, exist_ok=True)

def save_analysis(result):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = result["symbol"].replace("/","_")
    path = os.path.join(DIR, f"{safe}_{stamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    return path

def load_history(limit=10):
    rows = []
    for fn in sorted(os.listdir(DIR), reverse=True):
        if not fn.endswith(".json"): continue
        try:
            with open(os.path.join(DIR, fn), encoding="utf-8") as f:
                r = json.load(f)
            s = r["signal"]
            rows.append({
                "file": fn,
                "time": r.get("generated_at",""),
                "symbol": r.get("symbol",""),
                "timeframe": r.get("timeframe",""),
                "signal": s.get("direction"),
                "confidence": s.get("confidence"),
                "entry": s.get("entry"),
                "SL": s.get("stop_loss"),
                "TP": s.get("take_profit"),
                "RR": s.get("rr"),
                "status": s.get("status")
            })
        except Exception:
            continue
        if len(rows) >= limit: break
    return rows
