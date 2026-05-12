import os
import sys
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


def get_client() -> TradingClient:
    load_dotenv()
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    paper = os.getenv("ALPACA_PAPER", "true").lower() == "true"

    if not api_key or not secret_key:
        sys.exit("Missing ALPACA_API_KEY / ALPACA_SECRET_KEY. Copy .env.example to .env and fill in your paper keys.")

    return TradingClient(api_key, secret_key, paper=paper)


def show_account(client: TradingClient) -> None:
    account = client.get_account()
    print(f"Account status: {account.status}")
    print(f"Cash:           ${account.cash}")
    print(f"Equity:         ${account.equity}")
    print(f"Buying power:   ${account.buying_power}")
    print(f"Pattern day trader: {account.pattern_day_trader}")


def place_sample_order(client: TradingClient, symbol: str = "AAPL", qty: float = 1) -> None:
    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
    )
    submitted = client.submit_order(order_data=order)
    print(f"Submitted order {submitted.id}: {submitted.side} {submitted.qty} {submitted.symbol} ({submitted.status})")


def main() -> None:
    client = get_client()
    show_account(client)

    if "--order" in sys.argv:
        place_sample_order(client)


if __name__ == "__main__":
    main()
