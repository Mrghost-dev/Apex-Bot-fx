
import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        "NEWSAPI_KEY": os.getenv("NEWSAPI_KEY", ""),
        "FINNHUB_API_KEY": os.getenv("FINNHUB_API_KEY", ""),
        "ALPHAVANTAGE_KEY": os.getenv("ALPHAVANTAGE_KEY", ""),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "DATA_PROVIDER": os.getenv("DATA_PROVIDER", "yfinance"),
    }
