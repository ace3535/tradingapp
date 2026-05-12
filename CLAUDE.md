# Project rules

## Trading constraints

- **No options, ever.** Equities only. Do not import any options-related classes
  from `alpaca.trading` (e.g. `OptionLegRequest`, option order types, option
  contract lookups). Do not add option symbols to any watchlist. Do not suggest
  options-based strategies, hedges, or examples.
- All orders go through the **paper** trading endpoint
  (`paper=True` in `TradingClient`). Do not flip to live without explicit
  confirmation from the user in the current session.

## Secrets

- Real Alpaca keys live in `.env` (gitignored). Never commit them. Never echo
  them back in chat. `.env.example` is the only env file that gets committed.
