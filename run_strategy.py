import time
from datetime import datetime, timedelta

from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import config
from strategy import sma_crossover


POLL_SECONDS = 60


def get_position_qty(trading, symbol: str) -> float:
    try:
        return float(trading.get_open_position(symbol).qty)
    except Exception:
        return 0.0


def fetch_recent_closes(data, symbol: str):
    req = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start=datetime.utcnow() - timedelta(minutes=config.LONG_WINDOW * 3),
    )
    df = data.get_stock_bars(req).df
    if df.empty:
        return None
    return df.xs(symbol, level=0)["close"]


def step(trading, data) -> None:
    ts = datetime.utcnow().strftime("%H:%M:%S")
    for symbol in config.WATCHLIST:
        closes = fetch_recent_closes(data, symbol)
        if closes is None:
            print(f"[{ts}] {symbol}: no data")
            continue

        result = sma_crossover(closes, config.SHORT_WINDOW, config.LONG_WINDOW)
        if result is None:
            print(f"[{ts}] {symbol}: warming up")
            continue

        qty = get_position_qty(trading, symbol)
        action = "none"

        if result.signal == "BUY" and qty == 0:
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, qty=config.ORDER_QTY,
                side=OrderSide.BUY, time_in_force=TimeInForce.DAY,
            ))
            action = f"BUY {config.ORDER_QTY}"
        elif result.signal == "SELL" and qty > 0:
            trading.submit_order(MarketOrderRequest(
                symbol=symbol, qty=qty,
                side=OrderSide.SELL, time_in_force=TimeInForce.DAY,
            ))
            action = f"SELL {qty}"

        print(
            f"[{ts}] {symbol:5} price={result.price:<8.2f} "
            f"signal={result.signal:<4} pos={qty} action={action}"
        )


def main() -> None:
    trading = config.trading_client()
    data = config.data_client()
    print(f"Running SMA({config.SHORT_WINDOW}/{config.LONG_WINDOW}) on {config.WATCHLIST} every {POLL_SECONDS}s")
    print("Ctrl+C to stop.\n")
    while True:
        try:
            step(trading, data)
        except Exception as e:
            print(f"step error: {e}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
