
from datetime import datetime
from zoneinfo import ZoneInfo

def current_session():
    now = datetime.now(ZoneInfo("Africa/Nairobi"))
    mins = now.hour * 60 + now.minute

    # Practical FX-session windows in Kenya time (EAT), with overlaps highlighted.
    if 3*60 <= mins < 12*60:
        name = "ASIA / LONDON BUILD-UP"
        desc = "Asian flow transitioning toward London; watch range formation and liquidity."
    elif 12*60 <= mins < 17*60:
        name = "LONDON"
        desc = "London session; often useful for liquidity sweeps, displacement and structure shifts."
    elif 17*60 <= mins < 22*60:
        name = "NEW YORK"
        desc = "New York session; watch USD news, NY reversals and continuation after London."
    elif 22*60 <= mins or mins < 3*60:
        name = "NEW YORK LATE / ASIA PREP"
        desc = "Liquidity usually decreases; avoid forcing trades when structure is unclear."
    else:
        name = "TRANSITION"
        desc = "Session transition."
    return {
        "name": name,
        "kenya_time": now.strftime("%Y-%m-%d %H:%M:%S EAT"),
        "description": desc
    }
