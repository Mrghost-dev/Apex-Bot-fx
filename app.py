
import os
import json
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from bot.config import load_config
from bot.market import fetch_ohlcv, normalize_symbol
from bot.session import current_session
from bot.news import collect_news
from bot.strategy import parse_strategy, strategy_summary
from bot.analysis import analyze_market
from bot.storage import save_analysis, load_history

st.set_page_config(page_title="Apex Market Signal Bot", page_icon="📈", layout="wide")

cfg = load_config()

st.markdown("""
<style>
.main {background: #0b1020;}
.block-container {padding-top: 1.2rem;}
h1, h2, h3 {letter-spacing: .2px;}
.signal-card {
    padding: 18px; border-radius: 16px; background: #111a2e;
    border: 1px solid #263454; margin-bottom: 12px;
}
.metric-card {
    padding: 12px; border-radius: 12px; background: #0f172a;
    border: 1px solid #25324d;
}
.small {color:#9ca8bf;font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

st.title("📈 Apex Market Signal Bot")
st.caption("Market-session intelligence • SMC / ICT / CRT analysis • news context • custom strategy engine")

with st.sidebar:
    st.header("Market Setup")
    symbol = st.text_input("Instrument", value="XAUUSD")
    timeframe = st.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h", "1d"], index=1)
    period = st.selectbox("History", ["2d", "5d", "1mo", "3mo", "6mo", "1y"], index=1)
    risk_pct = st.number_input("Risk per trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

    st.divider()
    st.header("Your Strategy")
    default_strategy = """Use higher-timeframe bias, CRT premium/discount, liquidity sweeps,
displacement, MSS/BOS, order blocks and FVG retests. Prefer London/New York sessions.
Avoid entries immediately before high-impact USD news. Only take trades with at least 1:2 RR."""
    strategy_text = st.text_area("Describe your strategy in plain English", value=default_strategy, height=210)

    st.divider()
    analyze_btn = st.button("🔎 ANALYZE MARKET", use_container_width=True, type="primary")

st.session_state.setdefault("analysis", None)

session = current_session()
st.info(f"**Current session:** {session['name']}  •  **Kenya time:** {session['kenya_time']}  •  {session['description']}")

if analyze_btn:
    with st.spinner("Collecting market data, news and running the strategy engine..."):
        try:
            data = fetch_ohlcv(symbol, timeframe, period)
            parsed = parse_strategy(strategy_text)
            news = collect_news(symbol)
            result = analyze_market(
                symbol=symbol,
                timeframe=timeframe,
                df=data,
                strategy=parsed,
                news=news,
                risk_pct=risk_pct,
            )
            result["session"] = session
            result["generated_at"] = datetime.now(timezone.utc).isoformat()
            save_analysis(result)
            st.session_state.analysis = result
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

result = st.session_state.analysis

if result:
    signal = result["signal"]
    st.subheader(f"{result['symbol']} — {result['timeframe']} analysis")
    cols = st.columns(5)
    cols[0].metric("Signal", signal["direction"])
    cols[1].metric("Confidence", f"{signal['confidence']:.0f}%")
    cols[2].metric("Entry", f"{signal['entry']:.5f}")
    cols[3].metric("Stop Loss", f"{signal['stop_loss']:.5f}")
    cols[4].metric("Take Profit", f"{signal['take_profit']:.5f}")

    st.markdown(
        f"""<div class="signal-card">
        <b>Signal status:</b> {signal['status']}<br>
        <b>Entry mode:</b> {signal['entry_mode']}<br>
        <b>Strategy:</b> {signal['strategy']}<br>
        <b>Expected RR:</b> {signal['rr']:.2f}<br>
        <b>Estimated validity window:</b> {signal['expiry_minutes']} minutes<br>
        <b>Invalidation:</b> {signal['invalidation']}<br>
        <span class="small">This is a probabilistic market-analysis output, not a guarantee of profit.</span>
        </div>""", unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "🧠 Reasoning", "📰 News", "💾 Saved Data"])

    with tab1:
        fig = go.Figure(data=[go.Candlestick(
            x=result["chart"]["time"],
            open=result["chart"]["open"],
            high=result["chart"]["high"],
            low=result["chart"]["low"],
            close=result["chart"]["close"],
            name=result["symbol"]
        )])
        fig.update_layout(height=620, template="plotly_dark", xaxis_rangeslider_visible=False,
                          margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### Market structure")
        for item in result["reasoning"]["structure"]:
            st.write("•", item)
        st.markdown("### Liquidity / SMC / ICT")
        for item in result["reasoning"]["smc"]:
            st.write("•", item)
        st.markdown("### CRT")
        for item in result["reasoning"]["crt"]:
            st.write("•", item)
        st.markdown("### Strategy adaptation")
        for item in result["reasoning"]["strategy"]:
            st.write("•", item)
        st.markdown("### Risk and invalidation")
        for item in result["reasoning"]["risk"]:
            st.write("•", item)

    with tab3:
        if result["news"]:
            for n in result["news"]:
                st.markdown(f"**{n['title']}**")
                st.caption(f"{n['source']} • {n['published']}")
                if n.get("url"):
                    st.markdown(n["url"])
                st.write(n["impact"])
                st.divider()
        else:
            st.warning("No news items were retrieved. Configure optional news API keys in .env for broader coverage.")

    with tab4:
        st.json(result)
        st.download_button(
            "⬇️ Download this analysis as JSON",
            data=json.dumps(result, indent=2, default=str),
            file_name=f"{result['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

else:
    st.markdown("""
    ### How to use
    1. Enter an instrument such as **XAUUSD**, **EURUSD**, **GBPUSD**, or **BTCUSD**.
    2. Choose the timeframe.
    3. Describe your own strategy. The bot converts your rules into weighted analysis features.
    4. Click **ANALYZE MARKET**.
    5. Review the chart, current session, news context, structure, liquidity, CRT zones, entry mode, SL/TP and confidence.
    6. Save/download the result. Every completed analysis is also written automatically to `data/analyses/`.

    **Important:** no algorithm can honestly promise a “perfect” or guaranteed signal. The bot therefore reports a confidence score based on the evidence available and shows the conditions that would invalidate the setup.
    """)

st.divider()
st.subheader("Recent saved analyses")
history = load_history(limit=10)
if history:
    st.dataframe(pd.DataFrame(history), use_container_width=True)
else:
    st.caption("No saved analyses yet.")
