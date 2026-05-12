import os
import sys
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream


load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

WATCHLIST = ["AAPL", "MSFT", "SPY", "NVDA"]
SHORT_WINDOW = 10
LONG_WINDOW = 30
ORDER_QTY = 1

if not API_KEY or not SECRET_KEY:
    sys.exit("Missing Alpaca keys. Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env.")


def trading_client() -> TradingClient:
    return TradingClient(API_KEY, SECRET_KEY, paper=PAPER)


def data_client() -> StockHistoricalDataClient:
    return StockHistoricalDataClient(API_KEY, SECRET_KEY)


def stream_client() -> StockDataStream:
    return StockDataStream(API_KEY, SECRET_KEY)
