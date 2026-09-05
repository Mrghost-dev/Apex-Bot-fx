
# Apex Market Signal Bot

A local Python/Streamlit trading-analysis application designed to combine:
- live/near-live market OHLCV data through Yahoo Finance
- current Kenya (EAT) session detection
- SMC / ICT / CRT-style heuristics
- user-defined strategy text
- liquidity sweep and displacement heuristics
- premium / equilibrium / discount context
- configurable risk percentage
- news aggregation through Google News RSS plus optional NewsAPI/Finnhub keys
- confidence scoring, entry, stop loss, take profit, RR, entry mode and estimated validity window
- automatic JSON storage under `data/analyses/`
- downloadable analysis reports from the UI

## Important
This is a decision-support system, not a guaranteed signal generator. A “perfect” or guaranteed entry does not exist in financial markets. The confidence number is a model score based on the evidence the program can access.

## Windows installation

### Easiest
Double-click:

`run_windows.bat`

It creates a virtual environment, installs dependencies and launches the app.

### Command Prompt
Open Command Prompt in this folder:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Then open the local Streamlit address shown in the terminal.

## Strategy input

You can write rules such as:

“Use H4 bias. On M15 wait for a London or New York liquidity sweep, displacement, MSS, then enter at an FVG or order block. Use CRT discount for buys and premium for sells. Avoid high-impact USD news. Minimum RR 1:2.”

The current version detects and weights these concepts. It does not pretend to understand arbitrary prose with human-level reasoning; its strategy parser is deliberately transparent and inspectable.

## Data providers

### Market data
Yahoo Finance is used by default because it requires no API key for the basic implementation. Examples:
- XAUUSD -> GC=F (gold futures proxy)
- EURUSD -> EURUSD=X
- GBPUSD -> GBPUSD=X
- USDJPY -> JPY=X
- BTCUSD -> BTC-USD

For execution-quality FX/CFD pricing, connect a broker API later (MetaTrader 5, OANDA, FXCM, Interactive Brokers, etc.) rather than treating Yahoo quotes as broker execution prices.

### News
The bot can collect headlines from Google News RSS automatically. You can add:
- NewsAPI key in `.env`
- Finnhub key in `.env`

The UI deliberately shows news as context rather than pretending that every headline is automatically “high impact”.

## Saved files

Every successful analysis is automatically stored in:

`data/analyses/`

Each JSON contains:
- instrument
- timeframe
- timestamp
- session
- direction
- confidence score
- entry
- stop loss
- take profit
- RR
- strategy profile
- entry mode
- estimated expiry
- invalidation
- reasoning
- news
- chart data

## Extending the bot

Recommended next integrations for a production-grade trading assistant:
1. Broker feed/execution API
2. Economic calendar with event impact and release time
3. Higher-timeframe multi-feed analysis
4. Backtesting engine
5. Walk-forward validation
6. WebSocket streaming prices
7. Alert engine (desktop/Telegram/email)
8. Optional AI vision model for chart screenshots
9. User strategy versioning and performance statistics
10. Strict paper-trading mode before any live execution
"# Apex-Bot-fx" 
