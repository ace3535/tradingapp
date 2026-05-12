from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

import config
from strategy import sma_crossover


def fetch_closes(symbol: str, days: int = 365) -> pd.Series:
    client = config.data_client()
    req = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=datetime.utcnow() - timedelta(days=days),
        end=datetime.utcnow() - timedelta(days=1),
    )
    bars = client.get_stock_bars(req).df
    if bars.empty:
        return pd.Series(dtype=float)
    return bars.xs(symbol, level=0)["close"]


def backtest(symbol: str, short: int, long: int, days: int = 365) -> dict:
    closes = fetch_closes(symbol, days=days)
    if closes.empty:
        return {"symbol": symbol, "error": "no data"}

    short_sma = closes.rolling(short).mean()
    long_sma = closes.rolling(long).mean()
    position = (short_sma > long_sma).astype(int).shift(1).fillna(0)

    returns = closes.pct_change().fillna(0)
    strategy_returns = returns * position
    buy_hold_eq = (1 + returns).cumprod().iloc[-1] - 1
    strat_eq = (1 + strategy_returns).cumprod().iloc[-1] - 1

    trades = position.diff().abs().sum() / 2

    return {
        "symbol": symbol,
        "bars": len(closes),
        "trades": int(trades),
        "buy_hold_return_pct": round(buy_hold_eq * 100, 2),
        "strategy_return_pct": round(strat_eq * 100, 2),
    }


def main() -> None:
    print(f"Backtesting SMA({config.SHORT_WINDOW}/{config.LONG_WINDOW}) on {config.WATCHLIST}\n")
    print(f"{'symbol':6} {'bars':>5} {'trades':>7} {'buy&hold %':>12} {'strategy %':>12}")
    for sym in config.WATCHLIST:
        r = backtest(sym, config.SHORT_WINDOW, config.LONG_WINDOW)
        if "error" in r:
            print(f"{sym:6} {'-':>5} {'-':>7} {'-':>12} {'(' + r['error'] + ')':>12}")
            continue
        print(f"{r['symbol']:6} {r['bars']:>5} {r['trades']:>7} {r['buy_hold_return_pct']:>12} {r['strategy_return_pct']:>12}")


if __name__ == "__main__":
    main()
