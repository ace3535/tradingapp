from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import config


app = FastAPI(title="Alpaca Paper Dashboard")


@app.get("/api/account")
def account():
    a = config.trading_client().get_account()
    return {
        "status": str(a.status),
        "cash": a.cash,
        "equity": a.equity,
        "buying_power": a.buying_power,
        "portfolio_value": a.portfolio_value,
    }


@app.get("/api/positions")
def positions():
    return [
        {
            "symbol": p.symbol,
            "qty": p.qty,
            "avg_entry_price": p.avg_entry_price,
            "market_value": p.market_value,
            "unrealized_pl": p.unrealized_pl,
            "unrealized_plpc": p.unrealized_plpc,
        }
        for p in config.trading_client().get_all_positions()
    ]


@app.get("/api/orders")
def orders():
    return [
        {
            "symbol": o.symbol,
            "side": o.side.value,
            "qty": o.qty,
            "status": o.status.value,
            "submitted_at": str(o.submitted_at),
            "filled_avg_price": o.filled_avg_price,
        }
        for o in config.trading_client().get_orders()[:25]
    ]


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!doctype html>
<html><head><title>Alpaca Paper Dashboard</title>
<style>
body { font-family: -apple-system, sans-serif; margin: 2em; max-width: 900px; }
h1 { margin-bottom: 0; } h2 { margin-top: 2em; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; font-size: 14px; }
th { background: #f3f3f3; }
.kv { display: grid; grid-template-columns: 180px auto; gap: 4px 16px; }
.pos { color: green; } .neg { color: #c00; }
</style></head>
<body>
<h1>Alpaca Paper Dashboard</h1>
<p><small>auto-refreshes every 10s</small></p>

<h2>Account</h2>
<div class="kv" id="account">loading…</div>

<h2>Positions</h2>
<div id="positions">loading…</div>

<h2>Recent Orders</h2>
<div id="orders">loading…</div>

<script>
async function getJSON(url) { return (await fetch(url)).json(); }
function fmt(n) { return Number(n).toLocaleString(undefined, {maximumFractionDigits: 2}); }
function plClass(n) { return Number(n) >= 0 ? 'pos' : 'neg'; }

async function refresh() {
  const acct = await getJSON('/api/account');
  document.getElementById('account').innerHTML = Object.entries(acct)
    .map(([k,v]) => `<div><b>${k}</b></div><div>${v}</div>`).join('');

  const pos = await getJSON('/api/positions');
  document.getElementById('positions').innerHTML = pos.length === 0
    ? '<i>none</i>'
    : '<table><tr><th>symbol</th><th>qty</th><th>avg entry</th><th>market value</th><th>unrealized P/L</th><th>%</th></tr>'
      + pos.map(p => `<tr><td>${p.symbol}</td><td>${p.qty}</td><td>$${fmt(p.avg_entry_price)}</td>`
        + `<td>$${fmt(p.market_value)}</td>`
        + `<td class="${plClass(p.unrealized_pl)}">$${fmt(p.unrealized_pl)}</td>`
        + `<td class="${plClass(p.unrealized_plpc)}">${(p.unrealized_plpc*100).toFixed(2)}%</td></tr>`).join('')
      + '</table>';

  const ord = await getJSON('/api/orders');
  document.getElementById('orders').innerHTML = ord.length === 0
    ? '<i>none</i>'
    : '<table><tr><th>submitted</th><th>symbol</th><th>side</th><th>qty</th><th>status</th><th>fill</th></tr>'
      + ord.map(o => `<tr><td>${o.submitted_at}</td><td>${o.symbol}</td><td>${o.side}</td>`
        + `<td>${o.qty ?? '-'}</td><td>${o.status}</td><td>${o.filled_avg_price ? '$'+fmt(o.filled_avg_price) : '-'}</td></tr>`).join('')
      + '</table>';
}
refresh();
setInterval(refresh, 10000);
</script>
</body></html>
"""
