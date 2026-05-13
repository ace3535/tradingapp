"""Profit harvester / stop-loss watchdog.

Closes any position whose unrealized P/L percent crosses TAKE_PROFIT_PCT
or STOP_LOSS_PCT. Works for longs and shorts. Equities only — paper only.

Run continuously:  python harvester.py
Run a single pass: python harvester.py --once
"""
import sys
import time
from datetime import datetime, timezone

from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import config


def close_position(trading, p, reason: str) -> None:
    qty = abs(float(p.qty))
    side = OrderSide.BUY if float(p.qty) < 0 else OrderSide.SELL
    try:
        trading.submit_order(MarketOrderRequest(
            symbol=p.symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
        ))
        print(f"        {reason}: {side.value.upper()} {qty} {p.symbol} (P/L ${p.unrealized_pl} / {float(p.unrealized_plpc)*100:+.2f}%)")
    except Exception as e:
        print(f"        FAILED to close {p.symbol}: {e}")


def harvest_pass(trading) -> int:
    """Return number of positions closed this pass."""
    closed = 0
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    positions = trading.get_all_positions()
    if not positions:
        print(f"[{ts}] no positions")
        return 0

    print(f"[{ts}] reviewing {len(positions)} positions")
    for p in positions:
        plpc = float(p.unrealized_plpc)
        side = "SHORT" if float(p.qty) < 0 else "LONG "
        flag = ""
        if plpc >= config.TAKE_PROFIT_PCT:
            flag = "TAKE-PROFIT"
        elif plpc <= config.STOP_LOSS_PCT:
            flag = "STOP-LOSS"

        print(f"  {side} {p.symbol:5} qty={p.qty:<18} P/L=${p.unrealized_pl:<10} ({plpc*100:+.2f}%) {flag}")

        if flag:
            close_position(trading, p, flag)
            closed += 1
    return closed


def main() -> None:
    trading = config.trading_client()
    once = "--once" in sys.argv
    print(f"Harvester  take_profit=+{config.TAKE_PROFIT_PCT*100:.1f}%  stop_loss={config.STOP_LOSS_PCT*100:.1f}%  poll={config.HARVEST_POLL_SECONDS}s")
    if once:
        harvest_pass(trading)
        return
    print("Ctrl+C to stop.\n")
    while True:
        try:
            harvest_pass(trading)
        except Exception as e:
            print(f"pass error: {e}")
        time.sleep(config.HARVEST_POLL_SECONDS)


if __name__ == "__main__":
    main()
