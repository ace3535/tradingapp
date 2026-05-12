import os
import sys
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.news import NewsClient
from alpaca.data.live import StockDataStream


load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

WATCHLIST = ["AAPL", "MSFT", "SPY", "NVDA"]
SHORT_WINDOW = 10
LONG_WINDOW = 30
ORDER_QTY = 1

# News-sentiment bot universe: 10 most profitable / news-heavy S&P names.
NEWS_UNIVERSE = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "JPM", "V", "UNH", "XOM"]

# News bot tunables
NEWS_POLL_SECONDS = 10
NEWS_FRESHNESS_MINUTES = 5
SENTIMENT_BUY_THRESHOLD = 0.4
SENTIMENT_SELL_THRESHOLD = -0.4
NOTIONAL_PER_TRADE = 1000.0
MAX_OPEN_POSITIONS = 5
MIN_HOLD_SECONDS = 300
COOLDOWN_SECONDS = 600

if not API_KEY or not SECRET_KEY:
    sys.exit("Missing Alpaca keys. Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env.")


def trading_client() -> TradingClient:
    return TradingClient(API_KEY, SECRET_KEY, paper=PAPER)


def data_client() -> StockHistoricalDataClient:
    return StockHistoricalDataClient(API_KEY, SECRET_KEY)


def stream_client() -> StockDataStream:
    return StockDataStream(API_KEY, SECRET_KEY)


def news_client() -> NewsClient:
    return NewsClient(API_KEY, SECRET_KEY)
