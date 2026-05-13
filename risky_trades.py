"""Deliberately risky paper trades (equities only — no options, ever).

Concentrated long exposure to leveraged / volatile ETFs and single names,
plus naked shorts. All routed through the paper endpoint.
"""
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import config


risky_longs = [
    ("TQQQ", 20000.0, "3x leveraged QQQ ETF"),
    ("SOXL", 15000.0, "3x semiconductor ETF"),
    ("MSTR", 10000.0, "MicroStrategy — crypto-proxy, high volatility"),
    ("GME",   5000.0, "Meme stock"),
]

risky_shorts = [
    ("TSLA",  25, "Short TSLA (single-name, unbounded upside loss)"),
    ("PLTR", 100, "Short PLTR (single-name)"),
]


def main() -> None:
    trading = config.trading_client()

    print("LONGS (notional):")
    for sym, notional, note in risky_longs:
        try:
            o = trading.submit_order(MarketOrderRequest(
                symbol=sym,
                notional=notional,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            ))
            print(f"  OK  LONG  {sym:5} ${notional:>7,.0f}  status={o.status.value:<14} -- {note}")
        except Exception as e:
            print(f"  ERR LONG  {sym:5} ${notional:>7,.0f}  {e}")

    print("\nSHORTS (qty):")
    for sym, qty, note in risky_shorts:
        try:
            o = trading.submit_order(MarketOrderRequest(
                symbol=sym,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            ))
            print(f"  OK  SHORT {sym:5} {qty:>5} sh   status={o.status.value:<14} -- {note}")
        except Exception as e:
            print(f"  ERR SHORT {sym:5} {qty:>5} sh   {e}")

    print("\nAccount after submission:")
    a = trading.get_account()
    print(f"  cash=${a.cash}  equity=${a.equity}  buying_power=${a.buying_power}")


if __name__ == "__main__":
    main()
