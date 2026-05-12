from collections import defaultdict, deque
from datetime import datetime

import pandas as pd

import config
from strategy import sma_crossover


price_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=config.LONG_WINDOW + 5))


async def on_bar(bar) -> None:
    price_history[bar.symbol].append(bar.close)
    closes = pd.Series(list(price_history[bar.symbol]))
    result = sma_crossover(closes, config.SHORT_WINDOW, config.LONG_WINDOW)

    ts = datetime.utcnow().strftime("%H:%M:%S")
    if result is None:
        print(f"[{ts}] {bar.symbol:5} close={bar.close:<8.2f} warming up ({len(closes)}/{config.LONG_WINDOW + 1})")
        return

    marker = "<<<" if result.signal != "HOLD" else ""
    print(
        f"[{ts}] {bar.symbol:5} close={result.price:<8.2f} "
        f"sma{config.SHORT_WINDOW}={result.short_sma:<8.2f} "
        f"sma{config.LONG_WINDOW}={result.long_sma:<8.2f} "
        f"signal={result.signal} {marker}"
    )


def main() -> None:
    stream = config.stream_client()
    print(f"Subscribing to minute bars: {config.WATCHLIST}")
    print("(signals are logged only — no orders placed)")
    stream.subscribe_bars(on_bar, *config.WATCHLIST)
    stream.run()


if __name__ == "__main__":
    main()
