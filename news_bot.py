import time
from datetime import datetime, timedelta, timezone

from alpaca.data.requests import NewsRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import config
from sentiment import score


seen_article_ids: set[str] = set()
entry_time: dict[str, float] = {}      # symbol -> unix ts of last BUY fill
cooldown_until: dict[str, float] = {}  # symbol -> unix ts after which we may re-buy


def market_is_open(trading) -> bool:
    try:
        return trading.get_clock().is_open
    except Exception:
        return False


def open_positions(trading) -> dict[str, float]:
    return {p.symbol: float(p.qty) for p in trading.get_all_positions()}


def fetch_recent_articles(news, since: datetime):
    """Fetch articles for our universe published since `since` (UTC)."""
    req = NewsRequest(
        symbols=",".join(config.NEWS_UNIVERSE),
        start=since,
        limit=50,
        include_content=False,
    )
    resp = news.get_news(req)
    return getattr(resp, "news", None) or getattr(resp, "data", {}).get("news", []) or []


def article_text(a) -> str:
    headline = getattr(a, "headline", "") or ""
    summary = getattr(a, "summary", "") or ""
    return f"{headline}. {summary}".strip()


def relevant_symbols(a) -> list[str]:
    syms = getattr(a, "symbols", None) or []
    universe = set(config.NEWS_UNIVERSE)
    return [s for s in syms if s in universe]


def handle_article(trading, a, positions: dict[str, float]) -> None:
    text = article_text(a)
    s = score(text)
    syms = relevant_symbols(a)
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    headline = (getattr(a, "headline", "") or "")[:80]
    tag = "++" if s >= config.SENTIMENT_BUY_THRESHOLD else "--" if s <= config.SENTIMENT_SELL_THRESHOLD else "  "
    print(f"[{ts}] {tag} s={s:+.2f} {','.join(syms):<20} {headline}")

    now = time.time()
    for symbol in syms:
        held_qty = positions.get(symbol, 0.0)

        if s >= config.SENTIMENT_BUY_THRESHOLD:
            if held_qty > 0:
                continue
            if now < cooldown_until.get(symbol, 0):
                continue
            if len(positions) >= config.MAX_OPEN_POSITIONS:
                print(f"        skip BUY {symbol}: max positions reached")
                continue
            try:
                trading.submit_order(MarketOrderRequest(
                    symbol=symbol,
                    notional=config.NOTIONAL_PER_TRADE,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY,
                ))
                entry_time[symbol] = now
                positions[symbol] = 1.0  # placeholder so we don't double-buy in same poll
                print(f"        BUY  {symbol} ${config.NOTIONAL_PER_TRADE:.0f} notional")
            except Exception as e:
                print(f"        BUY {symbol} FAILED: {e}")

        elif s <= config.SENTIMENT_SELL_THRESHOLD:
            if held_qty <= 0:
                continue
            if now - entry_time.get(symbol, 0) < config.MIN_HOLD_SECONDS:
                continue
            try:
                trading.submit_order(MarketOrderRequest(
                    symbol=symbol,
                    qty=held_qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                ))
                cooldown_until[symbol] = now + config.COOLDOWN_SECONDS
                positions.pop(symbol, None)
                print(f"        SELL {symbol} qty={held_qty}")
            except Exception as e:
                print(f"        SELL {symbol} FAILED: {e}")


def poll_once(trading, news) -> None:
    if not market_is_open(trading):
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] market closed — sleeping")
        return

    since = datetime.now(timezone.utc) - timedelta(minutes=config.NEWS_FRESHNESS_MINUTES)
    articles = fetch_recent_articles(news, since)
    positions = open_positions(trading)

    new_articles = [a for a in articles if getattr(a, "id", None) and a.id not in seen_article_ids]
    for a in new_articles:
        seen_article_ids.add(a.id)
        if relevant_symbols(a):
            handle_article(trading, a, positions)


def main() -> None:
    trading = config.trading_client()
    news = config.news_client()
    print(f"News-sentiment bot on {config.NEWS_UNIVERSE}")
    print(f"poll={config.NEWS_POLL_SECONDS}s  freshness={config.NEWS_FRESHNESS_MINUTES}min  "
          f"buy>=+{config.SENTIMENT_BUY_THRESHOLD}  sell<={config.SENTIMENT_SELL_THRESHOLD}  "
          f"notional=${config.NOTIONAL_PER_TRADE:.0f}")
    print("Ctrl+C to stop.\n")
    while True:
        try:
            poll_once(trading, news)
        except Exception as e:
            print(f"poll error: {e}")
        time.sleep(config.NEWS_POLL_SECONDS)


if __name__ == "__main__":
    main()
