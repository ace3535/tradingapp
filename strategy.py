from dataclasses import dataclass
from typing import Literal, Optional

import pandas as pd


Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass
class StrategyResult:
    signal: Signal
    short_sma: float
    long_sma: float
    price: float


def sma_crossover(closes: pd.Series, short: int, long: int) -> Optional[StrategyResult]:
    """Return a signal based on the most recent SMA crossover.

    BUY when short SMA crosses above long SMA on the latest bar.
    SELL when short SMA crosses below long SMA on the latest bar.
    HOLD otherwise. Returns None if not enough data.
    """
    if len(closes) < long + 1:
        return None

    short_sma = closes.rolling(short).mean()
    long_sma = closes.rolling(long).mean()

    prev_diff = short_sma.iloc[-2] - long_sma.iloc[-2]
    curr_diff = short_sma.iloc[-1] - long_sma.iloc[-1]

    if prev_diff <= 0 < curr_diff:
        signal: Signal = "BUY"
    elif prev_diff >= 0 > curr_diff:
        signal = "SELL"
    else:
        signal = "HOLD"

    return StrategyResult(
        signal=signal,
        short_sma=float(short_sma.iloc[-1]),
        long_sma=float(long_sma.iloc[-1]),
        price=float(closes.iloc[-1]),
    )
