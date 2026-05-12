import os
import sys
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


def main() -> None:
    load_dotenv()
    client = TradingClient(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_SECRET_KEY"),
        paper=True,
    )

    orders = [
        MarketOrderRequest(symbol="AAPL", qty=1, side=OrderSide.BUY, time_in_force=TimeInForce.DAY),
        MarketOrderRequest(symbol="MSFT", qty=2, side=OrderSide.BUY, time_in_force=TimeInForce.DAY),
        MarketOrderRequest(symbol="SPY",  qty=1, side=OrderSide.BUY, time_in_force=TimeInForce.DAY),
        LimitOrderRequest(symbol="TSLA", qty=1, side=OrderSide.BUY, time_in_force=TimeInForce.DAY, limit_price=100.00),
        MarketOrderRequest(symbol="NVDA", notional=500, side=OrderSide.BUY, time_in_force=TimeInForce.DAY),
    ]

    for req in orders:
        try:
            o = client.submit_order(order_data=req)
            qty_str = f"{o.qty} sh" if o.qty else f"${o.notional}"
            print(f"  OK  {o.symbol:5}  {o.side.value:4}  {qty_str:10}  status={o.status.value}  id={o.id}")
        except Exception as e:
            print(f"  ERR {getattr(req, 'symbol', '?'):5}  {e}")

    print("\nOpen / recent orders:")
    for o in client.get_orders()[:10]:
        print(f"  {o.symbol:5}  {o.side.value:4}  qty={o.qty or '-':<5}  status={o.status.value:<12}  submitted={o.submitted_at}")

    print("\nPositions:")
    positions = client.get_all_positions()
    if not positions:
        print("  (none yet — market orders fill at next open if market is closed)")
    for p in positions:
        print(f"  {p.symbol:5}  qty={p.qty}  avg_entry=${p.avg_entry_price}  market=${p.market_value}  pl=${p.unrealized_pl}")


if __name__ == "__main__":
    main()
