import sys
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yfinance', 'pandas', '-q'])

import yfinance as yf
from datetime import datetime, timedelta, timezone
import json
import os

INITIAL_INVESTMENT = 1000

# ── Dynamic date range: Feb 2 2026 → today ────────────────────────────
MONTH_START = datetime(2026, 2, 2)

# ── Use Central Time (Texas) for the date, not UTC ───────────────────
# GitHub Actions runs in UTC. At 9 PM CST, UTC is already next day.
# We must convert UTC → CT to get the correct "today" in Texas.
_utc_now    = datetime.utcnow()
_is_cdt     = (_utc_now.month > 3 or (_utc_now.month == 3 and _utc_now.day >= 8)) and \
              (_utc_now.month < 11 or (_utc_now.month == 11 and _utc_now.day < 1))
_ct_offset  = timedelta(hours=-5) if _is_cdt else timedelta(hours=-6)
_ct_now     = _utc_now + _ct_offset
MONTH_END   = _ct_now.replace(hour=0, minute=0, second=0, microsecond=0)

print(f'💰 Initial Investment: ${INITIAL_INVESTMENT}')
print(f'📅 Tracking: {MONTH_START.strftime("%b %d, %Y")} → {MONTH_END.strftime("%b %d, %Y")}')

# ── All weekly portfolio data ──────────────────────────────────────────
WEEKS_DATA = [
    {
        'week_num': 1,
        'start_date': datetime(2026, 2, 2),
        'end_date': datetime(2026, 2, 6),
        'portfolios': {
            'ChatGPT':  [{"stock": "NVDA", "weight": 30},{"stock": "TSLA", "weight": 25},{"stock": "META", "weight": 20},{"stock": "AMD",  "weight": 15},{"stock": "COIN", "weight": 10}],
            'Grok':     [{"stock": "NVDA",  "weight": 35},{"stock": "AMD",   "weight": 25},{"stock": "MU",    "weight": 20},{"stock": "PLTR",  "weight": 10},{"stock": "GOOGL", "weight": 10}],
            'DeepSeek': [{"stock": "TQQQ", "weight": 50},{"stock": "SPXL", "weight": 30},{"stock": "TSLA", "weight": 20}],
            'Claude AI':[{"stock": "NVDA",  "weight": 25},{"stock": "MSFT",  "weight": 20},{"stock": "AVGO",  "weight": 20},{"stock": "GOOGL", "weight": 15},{"stock": "META",  "weight": 10},{"stock": "AMD",   "weight": 10}]
        }
    },
    {
        'week_num': 2,
        'start_date': datetime(2026, 2, 9),
        'end_date': datetime(2026, 2, 13),
        'portfolios': {
            'ChatGPT':  [{"stock": "NVDA", "weight": 25},{"stock": "AAPL", "weight": 20},{"stock": "MSFT", "weight": 20},{"stock": "TSLA", "weight": 20},{"stock": "AMD",  "weight": 15}],
            'Grok':     [{"stock": "NVDA", "weight": 25},{"stock": "AMD",  "weight": 20},{"stock": "PLTR", "weight": 15},{"stock": "MU",   "weight": 15},{"stock": "HOOD", "weight": 10},{"stock": "BTDR", "weight": 10},{"stock": "AMZN", "weight": 5}],
            'DeepSeek': [{"stock": "SPXL", "weight": 40},{"stock": "NVDA", "weight": 35},{"stock": "IWM",  "weight": 25}],
            'Claude AI':[{"stock": "NVDA",  "weight": 25},{"stock": "TSM",   "weight": 20},{"stock": "GOOGL", "weight": 15},{"stock": "META",  "weight": 15},{"stock": "STX",   "weight": 10},{"stock": "ULTA",  "weight": 10},{"stock": "CDE",   "weight": 5}]
        }
    },
    {
        'week_num': 3,
        'start_date': datetime(2026, 2, 16),
        'end_date': datetime(2026, 2, 20),
        'portfolios': {
            'ChatGPT':  [{"stock": "NVDA",  "weight": 25},{"stock": "TSLA",  "weight": 20},{"stock": "AMD",   "weight": 15},{"stock": "PLTR",  "weight": 15},{"stock": "AMZN",  "weight": 15},{"stock": "COIN",  "weight": 10}],
            'Grok':     [{"stock": "CVNA", "weight": 30},{"stock": "PANW", "weight": 25},{"stock": "WMT",  "weight": 20},{"stock": "PLTR", "weight": 15},{"stock": "FSLY", "weight": 10}],
            'DeepSeek': [{"stock": "PANW", "weight": 50},{"stock": "CDNS", "weight": 30},{"stock": "WMT",  "weight": 20}],
            'Claude AI':[{"stock": "NVDA",  "weight": 25},{"stock": "TSM",   "weight": 20},{"stock": "META",  "weight": 15},{"stock": "GOOGL", "weight": 15},{"stock": "TTD",   "weight": 10},{"stock": "MELI",  "weight": 10},{"stock": "SPY",   "weight": 5}]
        }
    },
    {
        'week_num': 4,
        'start_date': datetime(2026, 2, 23),
        'end_date': datetime(2026, 2, 27),
        'portfolios': {
            'ChatGPT':  [{"stock": "FSLY", "weight": 20},{"stock": "VAL",   "weight": 20},{"stock": "DHX",  "weight": 20},{"stock": "MU",    "weight": 20},{"stock": "GOOGL", "weight": 20}],
            'Claude AI':[{"stock": "NVDA", "weight": 25},{"stock": "MSFT",  "weight": 20},{"stock": "AVGO", "weight": 20},{"stock": "GOOGL", "weight": 15},{"stock": "META",  "weight": 10},{"stock": "AMD",   "weight": 10}],
            'DeepSeek': [{"stock": "NVDA", "weight": 40},{"stock": "CRM",   "weight": 15},{"stock": "INTU", "weight": 15},{"stock": "CAVA",  "weight": 10},{"stock": "HIMS",  "weight": 10},{"stock": "RKLB", "weight": 10}],
            'Grok':     [{"stock": "NVDA", "weight": 40},{"stock": "HD",    "weight": 15},{"stock": "LOW",  "weight": 15},{"stock": "IONQ",  "weight": 10},{"stock": "CRM",   "weight": 10},{"stock": "WDAY", "weight": 10}]
        }
    },
    # ── Week 5: Mar 2–6, 2026 ─────────────────────────────────────────
    {
        'week_num': 5,
        'start_date': datetime(2026, 3, 2),
        'end_date': datetime(2026, 3, 6),
        'portfolios': {
            'ChatGPT':  [{"stock": "NVDA", "weight": 30},{"stock": "TSLA", "weight": 20},{"stock": "AMZN", "weight": 15},{"stock": "MSFT", "weight": 15},{"stock": "META", "weight": 10},{"stock": "AMD",  "weight": 10}],
            'Claude AI':[{"stock": "NVDA", "weight": 20},{"stock": "MSFT", "weight": 20},{"stock": "AAPL", "weight": 15},{"stock": "GOOGL","weight": 15},{"stock": "AMZN", "weight": 15},{"stock": "ISRG", "weight": 10},{"stock": "NEE",  "weight": 5}],
            'DeepSeek': [{"stock": "XLE",  "weight": 40},{"stock": "STRL", "weight": 30},{"stock": "TEJASNET.NS", "weight": 30}],
            'Grok':     [{"stock": "AVGO", "weight": 30},{"stock": "CRWD", "weight": 25},{"stock": "NVDA", "weight": 20},{"stock": "MDB",  "weight": 15},{"stock": "CRDO", "weight": 10}]
        }
    },
    # ── Week 6: Mar 9–13, 2026 ────────────────────────────────────────
    {
        'week_num': 6,
        'start_date': datetime(2026, 3, 9),
        'end_date': datetime(2026, 3, 13),
        'portfolios': {
            'ChatGPT':  [{"stock": "NVDA", "weight": 22},{"stock": "TSLA", "weight": 18},{"stock": "AMD",  "weight": 16},{"stock": "COIN", "weight": 15},{"stock": "SMCI", "weight": 15},{"stock": "META", "weight": 14}],
            'Claude AI':[{"stock": "XOM",  "weight": 18},{"stock": "CVX",  "weight": 14},{"stock": "LMT",  "weight": 12},{"stock": "NOC",  "weight": 10},{"stock": "XOP",  "weight": 10},{"stock": "GLD",  "weight": 8},{"stock": "MSFT", "weight": 8},{"stock": "RTX",  "weight": 7},{"stock": "PG",   "weight": 7},{"stock": "PSA",  "weight": 6}],
            'DeepSeek': [{"stock": "EQNR", "weight": 25},{"stock": "PBR",  "weight": 15},{"stock": "XOM",  "weight": 10},{"stock": "RHM",  "weight": 15},{"stock": "CAT",  "weight": 10},{"stock": "CMA",  "weight": 10},{"stock": "CMSC", "weight": 10},{"stock": "MU",   "weight": 5}],
            'Grok':     [{"stock": "ORCL", "weight": 30},{"stock": "NIO",  "weight": 25},{"stock": "AVAV", "weight": 20},{"stock": "PATH", "weight": 15},{"stock": "HPE",  "weight": 10}]
        }
    },
  # Week 7: Mar 16-20, 2026 -----------------------------------------------
  {
    'week_num': 7,
    'start_date': datetime(2026, 3, 16),
    'end_date': datetime(2026, 3, 20),
    'portfolios': {
        'ChatGPT':  [{"stock": "NVDA", "weight": 22},{"stock": "TSLA", "weight": 18},{"stock": "AMD", "weight": 16},{"stock": "META", "weight": 15},{"stock": "SMCI", "weight": 15},{"stock": "COIN", "weight": 14}],
        'Claude AI':[{"stock": "NVDA", "weight": 25},{"stock": "MU", "weight": 15},{"stock": "META", "weight": 15},{"stock": "LMT", "weight": 10},{"stock": "RTX", "weight": 10},{"stock": "XOM", "weight": 10},{"stock": "MSFT", "weight": 10},{"stock": "GS", "weight": 5}],
        'DeepSeek': [{"stock": "XOM", "weight": 25},{"stock": "OKE", "weight": 20},{"stock": "MPC", "weight": 15},{"stock": "NUE", "weight": 15},{"stock": "LMT", "weight": 15},{"stock": "VIXM", "weight": 10}],
        'Grok':     [{"stock": "NVDA", "weight": 35},{"stock": "MU", "weight": 30},{"stock": "BABA", "weight": 15},{"stock": "LULU", "weight": 10},{"stock": "ACN", "weight": 10}]
      }
  },

   # Week 8: Mar 23-27, 2026 -----------------------------------------------
  {
    'week_num': 8,
    'start_date': datetime(2026, 3, 23),
    'end_date': datetime(2026, 3, 27),
    'portfolios': {
        'ChatGPT':  [{"stock": "NVDA", "weight": 25},{"stock": "TSLA", "weight": 20},{"stock": "AMD", "weight": 15},{"stock": "META", "weight": 15},{"stock": "AMZN", "weight": 10},{"stock": "COIN", "weight": 10},{"stock": "SPY", "weight": 5}],
        'Grok':     [{"stock": "GME", "weight": 30},{"stock": "PDD", "weight": 25},{"stock": "CHWY", "weight": 20},{"stock": "BLNK", "weight": 15},{"stock": "CCL", "weight": 10}],
        'DeepSeek': [{"stock": "SLB", "weight": 20},{"stock": "CNQ", "weight": 12},{"stock": "MUR", "weight": 8},{"stock": "GME", "weight": 10},{"stock": "PDD", "weight": 10},{"stock": "NVDA", "weight": 10},{"stock": "FIX", "weight": 8},{"stock": "ONTO", "weight": 7},{"stock": "DTE", "weight": 5},{"stock": "CCL", "weight": 10}],
        'Claude AI':[{"stock": "UAL", "weight": 15},{"stock": "CAT", "weight": 12},{"stock": "NVDA", "weight": 12},{"stock": "GLW", "weight": 10},{"stock": "AAPL", "weight": 10},{"stock": "AMZN", "weight": 10},{"stock": "PH", "weight": 8},{"stock": "MS", "weight": 8},{"stock": "XOM", "weight": 8},{"stock": "IWM", "weight": 7}]
       }
   },

  # Week 9: Mar 30 - Apr 3, 2026 -----------------------------------------------
{
    'week_num': 9,
    'start_date': datetime(2026, 3, 30),
    'end_date': datetime(2026, 4, 3),
    'portfolios': {
        'ChatGPT':  [{"stock": "NVDA", "weight": 25},{"stock": "TSLA", "weight": 20},{"stock": "AMD", "weight": 15},{"stock": "META", "weight": 15},{"stock": "COIN", "weight": 10},{"stock": "SMCI", "weight": 10},{"stock": "PLTR", "weight": 5}],
        'Grok':     [{"stock": "NVDA", "weight": 30},{"stock": "TSLA", "weight": 25},{"stock": "NKE", "weight": 20},{"stock": "SPCE", "weight": 15},{"stock": "BITF", "weight": 10}],
        'DeepSeek': [{"stock": "MSFT", "weight": 25},{"stock": "MU", "weight": 25},{"stock": "NVDA", "weight": 20},{"stock": "ONGC", "weight": 15},{"stock": "FDX", "weight": 15}],
        'Claude AI':[{"stock": "AA", "weight": 25},{"stock": "USO", "weight": 20},{"stock": "NKE", "weight": 15},{"stock": "NVDA", "weight": 15},{"stock": "TSLA", "weight": 10},{"stock": "GLD", "weight": 10},{"stock": "BFRG", "weight": 5}]
       }
  },

  # Week 10: Apr 6-10, 2026 -----------------------------------------------
{
    'week_num': 10,
    'start_date': datetime(2026, 4, 6),
    'end_date': datetime(2026, 4, 10),
    'portfolios': {
        'ChatGPT':  [{"stock": "NVDA", "weight": 20},{"stock": "COIN", "weight": 15},{"stock": "MARA", "weight": 15},{"stock": "WDC", "weight": 15},{"stock": "TER", "weight": 10},{"stock": "SNDK", "weight": 10},{"stock": "DOCN", "weight": 10},{"stock": "MOD", "weight": 5}],
        'Grok':     [{"stock": "NVDA", "weight": 35},{"stock": "AMD", "weight": 25},{"stock": "PLTR", "weight": 15},{"stock": "MU", "weight": 15},{"stock": "SMCI", "weight": 10}],
        'DeepSeek': [{"stock": "SLNO", "weight": 15},{"stock": "AIXI", "weight": 15},{"stock": "PFSA", "weight": 15},{"stock": "AAOI", "weight": 15},{"stock": "MNTN", "weight": 10},{"stock": "MU", "weight": 10},{"stock": "TWLO", "weight": 10},{"stock": "NFLX", "weight": 5},{"stock": "USAR", "weight": 5}],
        'Claude AI':[{"stock": "NVDA", "weight": 20},{"stock": "AVGO", "weight": 15},{"stock": "META", "weight": 12},{"stock": "PANW", "weight": 10},{"stock": "SPOT", "weight": 8},{"stock": "WDC", "weight": 8},{"stock": "LMB", "weight": 7},{"stock": "ALIT", "weight": 7},{"stock": "KHC", "weight": 7},{"stock": "VZ", "weight": 6}]
       }
   },
  # Week 11: Apr 13-17, 2026 -----------------------------------------------
{
    'week_num': 11,
    'start_date': datetime(2026, 4, 13),
    'end_date': datetime(2026, 4, 17),
    'portfolios': {
        'ChatGPT':  [{"stock": "NVDA", "weight": 20},{"stock": "TSLA", "weight": 15},{"stock": "AMD", "weight": 15},{"stock": "SMCI", "weight": 10},{"stock": "META", "weight": 10},{"stock": "AMZN", "weight": 10},{"stock": "COIN", "weight": 10},{"stock": "PLTR", "weight": 10}],
        'Grok':     [{"stock": "JPM", "weight": 25},{"stock": "GS", "weight": 20},{"stock": "BAC", "weight": 20},{"stock": "C", "weight": 15},{"stock": "MS", "weight": 10},{"stock": "BLK", "weight": 10}],
        'DeepSeek': [{"stock": "GS", "weight": 25},{"stock": "ALLO", "weight": 20},{"stock": "SKYQ", "weight": 20},{"stock": "NFLX", "weight": 20},{"stock": "XLE", "weight": 15}],
        'Claude AI':[{"stock": "JPM", "weight": 18},{"stock": "NFLX", "weight": 15},{"stock": "MSFT", "weight": 14},{"stock": "NVDA", "weight": 13},{"stock": "MS", "weight": 10},{"stock": "AVGO", "weight": 10},{"stock": "BLK", "weight": 8},{"stock": "PLTR", "weight": 7},{"stock": "XOM", "weight": 5},{"stock": "COP", "weight": 5}]
       }
   }
]
print(f' {len(WEEKS_DATA)} weeks defined')

# ── Trading days from MONTH_START to MONTH_END ────────────────────────
def get_all_trading_days():
    dates, current = [], MONTH_START
    while current <= MONTH_END:
        if current.weekday() < 5:   # Mon–Fri only
            dates.append(current)
        current += timedelta(days=1)
    return dates

all_trading_days = get_all_trading_days()
print(f'📅 {len(all_trading_days)} trading days: {all_trading_days[0].strftime("%b %d")} → {all_trading_days[-1].strftime("%b %d")}')

# ── Fetch Stock Data ──────────────────────────────────────────────────
def fetch_stock_data():
    all_stocks = set()
    for w in WEEKS_DATA:
        # Only include weeks that have started
        if w['start_date'] <= MONTH_END:
            for p in w['portfolios'].values():
                for h in p:
                    sym = h['stock'].strip()
                    if sym:
                        all_stocks.add(sym)
    all_stocks.add('^GSPC')
    stock_data = {}
    print(f'\n📊 Fetching {len(all_stocks)} symbols...')
    print('=' * 75)
    for symbol in sorted(all_stocks):
        try:
            hist = yf.Ticker(symbol).history(
                start=MONTH_START.strftime('%Y-%m-%d'),
                end=(MONTH_END + timedelta(days=1)).strftime('%Y-%m-%d')
            )
            prices, last_known = [], None
            for td in all_trading_days:
                ds = td.strftime('%Y-%m-%d')
                m  = [i for i, d in enumerate(hist.index.strftime('%Y-%m-%d')) if d == ds]
                if m:
                    p = round(hist['Close'].iloc[m[0]], 2)
                    last_known = p
                elif last_known is not None:
                    p = last_known
                elif not hist.empty:
                    p = round(hist['Close'].iloc[0], 2)
                else:
                    p = 100.0
                prices.append(p)
            chg = round(((prices[-1]-prices[0])/prices[0])*100, 2) if prices[0] > 0 else 0
            stock_data[symbol] = {'prices': prices, 'start_price': prices[0], 'end_price': prices[-1], 'change_pct': chg}
            icon  = '✅' if chg >= 0 else '❌'
            label = 'S&P 500' if symbol == '^GSPC' else symbol
            print(f'{icon} {label:15s} | ${prices[0]:8.2f} → ${prices[-1]:8.2f} | {chg:+7.2f}%')
        except Exception as e:
            print(f'❌ {symbol:15s} | Error: {str(e)[:50]}')
            stock_data[symbol] = {'prices': [100.0]*len(all_trading_days), 'start_price': 100.0, 'end_price': 100.0, 'change_pct': 0.0}
    print('=' * 75)
    return stock_data

stock_data = fetch_stock_data()

# ── Calculate Performance ─────────────────────────────────────────────
def calculate_performance():
    llm_results = {n: {'weeks': [], 'cumulative_values': [], 'current_capital': INITIAL_INVESTMENT, 'week_end_points': []}
                   for n in ['ChatGPT', 'Grok', 'DeepSeek', 'Claude AI']}

    active_weeks = [w for w in WEEKS_DATA if w['start_date'] <= MONTH_END]

    for wd in active_weeks:
        wn, ws, we = wd['week_num'], wd['start_date'], wd['end_date']
        # Clamp week end to today if week hasn't finished
        effective_end = min(we, MONTH_END)
        print(f'\n{"="*75}\n📅 WEEK {wn}: {ws.strftime("%b %d")} – {effective_end.strftime("%b %d, %Y")}\n{"="*75}')
        week_days = [d for d in all_trading_days if ws <= d <= effective_end]
        week_idx  = [all_trading_days.index(d) for d in week_days]
        if not week_idx:
            continue

        for llm_name, portfolio in wd['portfolios'].items():
            cap, stocks_detail = llm_results[llm_name]['current_capital'], []
            for h in portfolio:
                sym  = h['stock'].strip()
                wt   = h['weight']
                alloc = (wt/100)*cap
                # Weeks 1-4 (Feb) use Monday's price to preserve original published results.
                # Weeks 5+ (Mar onwards) use Friday's close for daily chart accuracy.
                if wn <= 4:
                    buy_idx = week_idx[0]
                else:
                    buy_idx = week_idx[0] - 1 if week_idx[0] > 0 else week_idx[0]
                sp   = stock_data.get(sym, {}).get('prices', [100.0]*len(all_trading_days))[buy_idx]
                shares = alloc/sp if sp > 0 else 0  # full precision, no rounding
                ep   = stock_data.get(sym, {}).get('prices', [100.0]*len(all_trading_days))[week_idx[-1]]
                ev   = shares*ep
                stocks_detail.append({
                    'stock': sym, 'weight': wt, 'allocation': round(alloc,2),
                    'shares': shares, 'start_price': round(sp,2), 'end_price': round(ep,2),
                    'end_value': round(ev,2), 'return': round(ev-alloc,2),
                    'return_pct': round((ev-alloc)/alloc*100,2) if alloc > 0 else 0
                })

            ending  = sum(s['end_value'] for s in stocks_detail)
            ret     = ending - cap
            ret_pct = (ret/cap*100) if cap > 0 else 0
            llm_results[llm_name]['weeks'].append({
                'week_num': wn, 'start_date': ws, 'end_date': effective_end,
                'week_end_orig': we,
                'starting_capital': round(cap,2), 'ending_value': round(ending,2),
                'return': round(ret,2), 'return_pct': round(ret_pct,2), 'stocks': stocks_detail
            })
            end_idx = all_trading_days.index(min(effective_end, all_trading_days[-1]))
            llm_results[llm_name]['week_end_points'].append({
                'day_index': end_idx, 'value': round(ending,2),
                'date': effective_end.strftime('%b %d')
            })
            llm_results[llm_name]['current_capital'] = ending
            print(f'  {llm_name:12s} | ${cap:8.2f} → ${ending:8.2f} | {ret_pct:+6.2f}% | {"✅" if ret>=0 else "❌"}')

    for llm_name in llm_results:
        cum = []
        for day_idx, day in enumerate(all_trading_days):
            wfd = next((w for w in llm_results[llm_name]['weeks']
                        if w['start_date'] <= day <= w['end_date']), None)
            if wfd:
                #is_week_start = (day == wfd['start_date'])
                #if is_week_start and cum:
                    # On Monday (week start), carry forward Friday's closing value
                    # so the chart doesn't show a flat Mon==Fri line
                    #cum.append(cum[-1])
                #else:
                    val = sum(
                        s['shares'] * stock_data.get(s['stock'], {}).get('prices', [100.0]*len(all_trading_days))[day_idx]
                        for s in wfd['stocks']
                    )
                    cum.append(round(val,2))
            elif cum:
                cum.append(cum[-1])
            else:
                cum.append(INITIAL_INVESTMENT)
        if cum:
            cum[0] = float(INITIAL_INVESTMENT)
        llm_results[llm_name]['cumulative_values'] = cum
        llm_results[llm_name]['final_value']       = cum[-1]
        llm_results[llm_name]['total_return']      = round(cum[-1]-INITIAL_INVESTMENT, 2)
        llm_results[llm_name]['total_return_pct']  = round((cum[-1]-INITIAL_INVESTMENT)/INITIAL_INVESTMENT*100, 2)
    return llm_results

print('\n📈 CALCULATING PERFORMANCE...')
llm_results = calculate_performance()

ranked = sorted(llm_results.items(), key=lambda x: x[1]['total_return_pct'], reverse=True)
print(f'\n{"="*75}\n🏆 FINAL RANKINGS\n{"="*75}')
for i, (n, d) in enumerate(ranked):
    print(f'{["🥇","🥈","🥉","📊"][i]} #{i+1} {n:12s} | ${d["final_value"]:8.2f} | {d["total_return_pct"]:+6.2f}%')
print(f'\n📊 S&P 500: {stock_data["^GSPC"]["change_pct"]:+.2f}%')

# ── Generate HTML Dashboard ───────────────────────────────────────────
def generate_html(llm_results, stock_data, all_trading_days):
    import json as _json

    date_labels = [d.strftime('%b %d') for d in all_trading_days]

    # ── Central Time clock (12-hour format) ───────────────────────────
    utc_now   = datetime.utcnow()
    # CDT = UTC-5 (Mar–Nov), CST = UTC-6 (Nov–Mar)
    is_cdt    = (utc_now.month > 3 or (utc_now.month == 3 and utc_now.day >= 8)) and \
                (utc_now.month < 11 or (utc_now.month == 11 and utc_now.day < 1))
    ct_offset = timedelta(hours=-5) if is_cdt else timedelta(hours=-6)
    ct_now    = utc_now + ct_offset
    tz_label  = 'CDT' if is_cdt else 'CST'
    # 12-hour clock: %-I on Linux, %#I on Windows; use strftime then fix
    hour12    = ct_now.strftime('%I').lstrip('0') or '12'
    mins      = ct_now.strftime('%M')
    ampm      = ct_now.strftime('%p')
    fetch_time = f'{ct_now.strftime("%b %d, %Y")} at {hour12}:{mins} {ampm} {tz_label}'

    # ── Dynamic date range label ───────────────────────────────────────
    range_label = f'{all_trading_days[0].strftime("%b %-d")} – {all_trading_days[-1].strftime("%b %-d, %Y")}'

    ranked     = sorted(llm_results.items(), key=lambda x: x[1]['total_return_pct'], reverse=True)
    colors     = ['#6366f1', '#10b981', '#f59e0b', '#ef4444']
    bar_colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444']
    card_names = {r[0]: bar_colors[i] for i, r in enumerate(ranked)}

    sp500_prices     = stock_data['^GSPC']['prices']
    sp500_normalized = [round((p/sp500_prices[0])*INITIAL_INVESTMENT, 2) for p in sp500_prices]
    sp500_ret_pct    = stock_data['^GSPC']['change_pct']

    # ── Logo definitions (unchanged) ──────────────────────────────────
    DS_B64 = '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'
    CL_B64 = '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'

    logos = {
        'ChatGPT':  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="32" height="32" fill="white"><path d="M474.123 209.816a134.974 134.974 0 0 0-11.613-110.558 136.546 136.546 0 0 0-147.025-65.425A134.98 134.98 0 0 0 213.863 3.37a136.547 136.547 0 0 0-130.19 94.506 134.98 134.98 0 0 0-90.054 65.424 136.549 136.549 0 0 0 16.774 160.06 134.977 134.977 0 0 0 11.614 110.558 136.546 136.546 0 0 0 147.024 65.426 134.98 134.98 0 0 0 101.622 50.464 136.549 136.549 0 0 0 130.191-94.508 134.978 134.978 0 0 0 90.054-65.424 136.546 136.546 0 0 0-16.775-160.06zM298.136 470.458a101.21 101.21 0 0 1-64.974-23.505c.822-.45 2.264-1.244 3.198-1.813l107.895-62.302a17.508 17.508 0 0 0 8.855-15.332V236.11l45.6 26.328a1.619 1.619 0 0 1 .886 1.25v125.97a101.44 101.44 0 0 1-101.46 80.8zM77.076 385.538a101.19 101.19 0 0 1-12.09-68.11c.806.483 2.215 1.336 3.198 1.813l107.895 62.302a17.511 17.511 0 0 0 17.708 0l131.735-76.07v52.657a1.618 1.618 0 0 1-.647 1.393L218.084 421.84a101.441 101.441 0 0 1-141.008-36.302zm-13.203-235.08a101.197 101.197 0 0 1 52.88-44.54c0 .924-.048 2.551-.048 3.699v124.604a17.506 17.506 0 0 0 8.854 15.332l131.735 76.07-45.601 26.329a1.618 1.618 0 0 1-1.534.145L100.271 289.7a101.441 101.441 0 0 1-36.398-139.242zm374.547 87.081-131.735-76.07 45.6-26.328a1.619 1.619 0 0 1 1.535-.145l111.888 64.598a101.43 101.43 0 0 1-15.715 182.955V256.977a17.506 17.506 0 0 0-11.573-15.438zm45.4-68.396c-.806-.484-2.215-1.337-3.198-1.813l-107.895-62.302a17.512 17.512 0 0 0-17.708 0l-131.735 76.069v-52.657a1.619 1.619 0 0 1 .647-1.393l111.839-64.568a101.44 101.44 0 0 1 148.05 66.664zm-284.974 93.7-45.601-26.328a1.619 1.619 0 0 1-.886-1.25V110.296a101.44 101.44 0 0 1 166.35-77.908c-.822.45-2.263 1.245-3.198 1.814L208.616 196.502a17.51 17.51 0 0 0-8.855 15.332zm24.76-53.387 58.704-33.894 58.705 33.894v67.703l-58.705 33.894-58.704-33.894z"/></svg>',
        'Grok':     '<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="white"><path d="M178.57 127.15 290 0h-26.46l-97.03 110.38L89.34 0H0l117.13 166.93L0 300h26.46l102.4-116.59L208.66 300H298L178.57 127.15Zm-36.18 41.05-11.84-16.47-94.13-131.04h40.57l76.01 105.82 11.84 16.47 98.95 137.38h-40.55l-80.85-111.16Z"/></svg>',
        'DeepSeek': f'<img src="data:image/png;base64,{CL_B64}" style="width:32px;height:32px;object-fit:contain;display:block;border-radius:50%;" alt="DeepSeek">',
        'Claude AI': f'<img src="data:image/png;base64,{DS_B64}" style="width:32px;height:32px;object-fit:contain;display:block;border-radius:50%;" alt="Claude AI">',
    }

    html_open = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>LLM Portfolio Battle</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  *{margin:0;padding:0;box-sizing:border-box;}
  body{font-family:'Inter','Segoe UI',sans-serif;background:linear-gradient(135deg,#6366f1 0%,#818cf8 30%,#a78bfa 60%,#7c3aed 100%);min-height:100vh;padding:30px 80px;}
  .container{max-width:100%;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 40px rgba(99,102,241,.3);}
  .header{background:radial-gradient(ellipse at center,#1a2f72 0%,#1e3a8a 50%,#4c1d95 100%);color:#fff;padding:40px 32px 32px;text-align:center;position:relative;overflow:hidden;border-bottom:3px solid rgba(99,102,241,.4);}
  .header::before{content:'';position:absolute;top:-80px;right:-80px;width:320px;height:320px;background:rgba(99,102,241,.18);border-radius:50%;}
  .header::after{content:'';position:absolute;bottom:-60px;left:-60px;width:240px;height:240px;background:rgba(139,92,246,.15);border-radius:50%;}
  .header h1{font-size:clamp(1.4em,4vw,2.8em);font-weight:900;letter-spacing:-0.5px;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.3);}
  .header .subtitle{font-size:clamp(.8em,2.5vw,1.1em);color:#fbbf24;margin-top:12px;font-weight:700;}
  .header .meta{font-size:.8em;margin-top:8px;color:rgba(255,255,255,.55);}
  .section{padding:24px 24px 18px;background:#fff;width:100%;}
  .section.alt{background:#f5f6ff;}
  .section-title{display:flex;align-items:center;gap:10px;font-size:clamp(1em,2.5vw,1.3em);font-weight:800;color:#1e3a8a;margin-bottom:18px;padding-bottom:12px;border-bottom:2.5px solid #e0e7ff;letter-spacing:-0.2px;}
  .chart-box{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:8px 8px 16px;box-shadow:0 2px 12px rgba(0,0,0,.05);width:100%;overflow:hidden;}
  #line-chart{width:100%!important;}
  .bar-stage{display:flex;align-items:flex-end;justify-content:center;gap:24px;padding:16px 20px 0;min-height:260px;flex-wrap:wrap;}
  .bar-col{display:flex;flex-direction:column;align-items:center;flex:1;min-width:80px;max-width:180px;}
  .bar-amount{font-size:clamp(.9em,2vw,1.25em);font-weight:900;color:#1e3a8a;margin-bottom:10px;text-align:center;}
  .bar-body{width:100%;border-radius:14px 14px 0 0;display:flex;align-items:center;justify-content:center;padding:15px 0 14px;transition:filter .2s;cursor:default;min-height:24px;}
  .bar-body:hover{filter:brightness(1.08);}
  .bar-footer{margin-top:14px;text-align:center;width:100%;}
  .bar-footer .bname{font-size:clamp(.72em,1.8vw,.9em);font-weight:700;color:#1e3a8a;text-transform:uppercase;letter-spacing:.8px;}
  .bar-footer .bret{font-size:clamp(.7em,1.6vw,.85em);font-weight:600;margin-top:3px;}
  .bret.pos{color:#059669;} .bret.neg{color:#dc2626;}

  .llm-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:20px 24px;background:#f5f6ff;}
  .llm-card{background:#fff;border-radius:18px;overflow:hidden;border:1px solid #e2e8f0;box-shadow:0 4px 18px rgba(0,0,0,.09);}
  .llm-card-header{padding:16px 20px;font-size:clamp(.9em,2.5vw,1.15em);font-weight:900;color:#fff;display:flex;justify-content:space-between;align-items:center;letter-spacing:-0.3px;gap:8px;flex-wrap:wrap;}
  .llm-card-header .ret-badge{background:rgba(255,255,255,.18);border-radius:999px;padding:5px 14px;font-size:.88em;font-weight:700;white-space:nowrap;}
  /* ── Frozen first column in LLM tables ── */
  .card-table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;width:100%;position:relative;}
  .card-table-scroll table{border-collapse:separate;border-spacing:0;width:max-content;min-width:100%;}
  .card-table-scroll table thead th:first-child,
  .card-table-scroll table tbody td:first-child{
    position:sticky;left:0;z-index:2;background:#fff;border-right:2px solid #6366f1;
  }
  .card-table-scroll table thead th:first-child{background:linear-gradient(135deg,#3b3f9e,#6c40c9)!important;z-index:3;}
  table{width:100%;border-collapse:collapse;}
  .tbl-head-row th{background:linear-gradient(135deg,#3b3f9e,#6c40c9);color:#fff;padding:8px 6px;font-size:.70em;font-weight:800;text-transform:uppercase;letter-spacing:.7px;text-align:center;border-right:1px solid rgba(255,255,255,0.15);white-space:nowrap;}
  .tbl-sub-row th{background:linear-gradient(90deg,#4f52b8,#7c4dcf);color:#fff;padding:6px 5px;font-size:.66em;font-weight:700;text-transform:uppercase;letter-spacing:.5px;text-align:center;border-bottom:3px solid rgba(255,255,255,0.3);border-right:1px solid rgba(255,255,255,0.15);}
  tbody tr:nth-child(even){background:#f5f6ff;}
  tbody tr:hover{background:#eef0ff;}
  tbody tr{border-bottom:1px solid #e8eaf6;}
  td{padding:5px 5px;font-size:0.76em;text-align:center;color:#374151;border-right:1px solid #ececf8;}
  .stock-col{text-align:left!important;font-weight:800;color:#1e3a8a;padding-left:8px!important;padding-right:8px!important;font-size:0.78em;white-space:nowrap;}
  .pos{color:#059669!important;font-weight:700;} .neg{color:#dc2626!important;font-weight:700;}
  .price-section{padding:24px;background:#fff;border-top:1px solid #e2e8f0;}
  .price-table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:12px;border:1px solid #e2e8f0;margin-top:12px;}
  .price-table-wrap table{border-collapse:separate;border-spacing:0;width:max-content;min-width:100%;}
  .price-table-wrap table thead th:first-child,
  .price-table-wrap table tbody td:first-child{position:sticky;left:0;z-index:2;background:#1e3a8a;white-space:nowrap;}
  .price-table-wrap table tbody td:first-child{background:#eef2ff!important;}
  .price-table-wrap table thead th{background:#1e3a8a;color:#fff;padding:6px 4px;font-size:.60em;font-weight:700;text-transform:uppercase;letter-spacing:.4px;text-align:center;white-space:nowrap;border-right:1px solid rgba(255,255,255,0.15);}
  .price-table-wrap table tbody td{font-size:.67em;padding:4px 4px;border-right:1px solid #e8eaf6;}
  @media(max-width:900px){
    body{padding:14px 12px;}
    .llm-grid{grid-template-columns:1fr;gap:16px;padding:16px;}
    .bar-stage{gap:12px;padding:12px 10px 0;}
    .section{padding:18px 16px 14px;}
    .llm-card-header{padding:14px 16px;}
  }
  @media(max-width:600px){
    body{padding:10px 8px;}
    .header{padding:24px 16px 20px;}
    .header h1{font-size:1.3em;}
    .header .subtitle{font-size:.82em;}
    .section{padding:14px 12px 12px;}
    .section-title{font-size:.98em;margin-bottom:12px;}
    .chart-box{padding:4px 4px 10px;border-radius:10px;}
    .bar-stage{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px 8px 0;min-height:unset;align-items:end;}
    .bar-col{max-width:100%;}
    .bar-amount{font-size:.85em;}
    .bar-footer .bname{font-size:.68em;letter-spacing:.4px;}
    .bar-footer .bret{font-size:.68em;}

    .llm-grid{grid-template-columns:1fr;padding:12px;}
    .llm-card-header{font-size:.9em;padding:12px 14px;flex-direction:row;flex-wrap:wrap;gap:6px;}
    .llm-card-header .ret-badge{font-size:.8em;padding:4px 10px;}
    td{padding:4px 3px;font-size:.70em;}
    .stock-col{font-size:.72em;padding-left:6px!important;}
    .tbl-head-row th{font-size:.60em;padding:7px 3px;}
    .tbl-sub-row th{font-size:.58em;padding:5px 3px;}
    .price-section{padding:14px 10px;}
    .price-table-wrap table tbody td{font-size:.60em;padding:3px 3px;}
    .price-table-wrap table thead th{font-size:.55em;padding:5px 3px;}
  }
</style>
</head>
<body>
<div class="container">
'''

    html = html_open
    html += f'''  <div class="header">
    <h1> LLM Portfolio Battle</h1>
    <p class="subtitle">{range_label} | $1,000 Initial Investment | Rolling Weekly Strategy</p>
    <p class="authors" style="font-size:clamp(.8em,2vw,.95em);color:rgba(255,255,255,0.85);margin-top:10px;font-weight:500;letter-spacing:0.3px;">✍️&nbsp Manasa Dontireddy ,&nbsp;&nbsp; Orhan Erdem</p>
    <p class="meta">🕐 Last Updated: {fetch_time}</p>
  </div>
  <div class="section">
    <div class="section-title">📈 Cumulative Portfolio Value vs S&amp;P 500 ({range_label})</div>
    <div class="chart-box"><div id="line-chart"></div></div>
  </div>
  <div class="section alt">
    <div class="section-title">📊 Top Performing Portfolio — Ranked Highest to Lowest</div>
    <div class="bar-stage">
'''

    sp_fv      = sp500_normalized[-1]
    sp_sign    = '+' if sp500_ret_pct >= 0 else ''
    sp_clr     = '#1e293b'
    all_bars   = list(ranked) + [('S&P 500', {'final_value': sp_fv, 'total_return_pct': sp500_ret_pct})]
    max_val    = max(item[1]['final_value'] for item in all_bars)
    max_bar_px = 240
    for i, (name, data) in enumerate(ranked):
        fv     = data['final_value']
        trp    = data['total_return_pct']
        clr    = bar_colors[i]
        height = max(int((fv / max_val) * max_bar_px), 30)
        ssym   = '+' if trp >= 0 else ''
        rcls   = 'pos' if trp >= 0 else 'neg'
        html += f'''
      <div class="bar-col">
        <div class="bar-amount">${fv:,.2f}</div>
        <div class="bar-body" style="height:{height}px;background:linear-gradient(180deg,{clr}f0,{clr}99);">
        </div>
        <div class="bar-footer">
          <div class="bname">{name}</div>
          <div class="bret {rcls}">{ssym}{trp:.2f}%</div>
        </div>
      </div>
'''

    sp_height = max(int((sp_fv / max_val) * max_bar_px), 30)
    sp_rcls   = 'pos' if sp500_ret_pct >= 0 else 'neg'
    html += f'''
      <div class="bar-col">
        <div class="bar-amount">${sp_fv:,.2f}</div>
        <div class="bar-body" style="height:{sp_height}px;background:linear-gradient(180deg,{sp_clr}e0,{sp_clr}88);border:2px dashed {sp_clr}88;">
        </div>
        <div class="bar-footer">
          <div class="bname">S&amp;P 500</div>
          <div class="bret {sp_rcls}">{sp_sign}{sp500_ret_pct:.2f}%</div>
        </div>
      </div>
    </div>
  </div>
'''

    # ── 4 LLM Cards with FROZEN first column + REVERSED week order ────
    html += '  <div class="llm-grid">\n'
    for rank_i, (llm_name, data) in enumerate(ranked, 1):
        fv      = data['final_value']
        trp     = data['total_return_pct']
        ssym    = '+' if trp >= 0 else ''
        hdr_clr = card_names[llm_name]

        # Reverse weeks so latest week is on the LEFT
        weeks_reversed = list(reversed(data['weeks']))

        html += f'''
    <div class="llm-card">
      <div class="llm-card-header" style="background:linear-gradient(135deg,{hdr_clr},{hdr_clr}cc);">
        <span>#{rank_i} {llm_name}</span>
        <span class="ret-badge">${fv:.2f} ({ssym}{trp:.2f}%)</span>
      </div>
      <div class="card-table-scroll"><table>
          <thead><tr class="tbl-head-row">
              <th rowspan="2" style="vertical-align:middle;text-align:left;padding-left:8px;white-space:nowrap;">Stock</th>
'''
        for w in weeks_reversed:
            start_s  = w['start_date'].strftime('%b %-d') if hasattr(w['start_date'], 'strftime') else str(w['start_date'])
            orig_end = w.get('week_end_orig', w['end_date'])
            end_s    = orig_end.strftime('%b %-d') if hasattr(orig_end, 'strftime') else str(orig_end)
            html += f'<th colspan="2" style="white-space:nowrap;font-size:0.70em;">{start_s} (${w["starting_capital"]:.0f}) &ndash; {end_s} (${w["ending_value"]:.0f})</th>\n'

        html += '          </tr><tr class="tbl-sub-row">\n'
        for _ in weeks_reversed:
            html += '<th style="padding:3px 4px;">Wt</th><th style="padding:3px 4px;">Shares</th>\n'
        html += '          </tr></thead><tbody>\n'

        all_stocks_llm = sorted({s['stock'].strip() for w in data['weeks'] for s in w['stocks']})
        for sym in all_stocks_llm:
            html += f'            <tr><td class="stock-col">{sym.strip()}</td>\n'
            for w in weeks_reversed:
                s = next((x for x in w['stocks'] if x['stock'].strip() == sym), None)
                if s:
                    html += f'              <td style="font-weight:600;padding:3px 4px;">{s["weight"]}%</td><td style="color:#4b5563;padding:3px 4px;">{s["shares"]:.4f}</td>\n'
                else:
                    html += '              <td style="color:#9ca3af;padding:3px 4px;">-</td><td style="color:#9ca3af;padding:3px 4px;">-</td>\n'
            html += '            </tr>\n'
        html += '          </tbody></table></div>\n    </div>\n'
    html += '  </div>\n'

    # ── Yahoo Finance price table — oldest date first (left to right) ──
    prices_fwd_idx = list(range(len(all_trading_days)))

    html += '''
  <div class="price-section">
    <div class="section-title">📋 Yahoo Finance US Stock Close Prices </div>
    <div class="price-table-wrap"><table>
      <thead><tr><th style="text-align:left;padding-left:8px;">Stock</th>
'''
    for dl in date_labels:
        html += f'      <th>{dl}</th>\n'
    html += '      <th>Chg%</th></tr></thead><tbody>\n'

    for sym in sorted(stock_data.keys()):
        if sym == '^GSPC': continue
        prices = stock_data[sym]['prices']
        chg    = stock_data[sym]['change_pct']
        cc     = 'pos' if chg >= 0 else 'neg'
        html += f'      <tr><td class="stock-col">{sym}</td>'
        for idx in prices_fwd_idx:
            html += f'<td>${prices[idx]:.2f}</td>'
        html += f'<td class="{cc}">{chg:+.2f}%</td></tr>\n'
    html += '    </tbody></table></div>\n'

    # ── S&P 500 table — oldest date first (left to right) ─────────────
    html += f'''
    <div class="section-title" style="margin-top:36px;">📊 Normalized S&amp;P 500 Points </div>
    <div class="price-table-wrap"><table>
      <thead><tr><th style="text-align:left;padding-left:8px;">Metric</th>
'''
    for dl in date_labels:
        html += f'      <th>{dl}</th>\n'
    html += '      <th>Chg%</th></tr></thead><tbody>\n'

    sp_chg = stock_data['^GSPC']['change_pct']
    cc = 'pos' if sp_chg >= 0 else 'neg'
    html += '      <tr><td class="stock-col">Actual Points</td>'
    for idx in prices_fwd_idx:
        html += f'<td>{sp500_prices[idx]:.2f}</td>'
    html += f'<td class="{cc}">{sp_chg:+.2f}%</td></tr>\n'

    html += '      <tr><td class="stock-col">Normalized ($1,000)</td>'
    for idx in prices_fwd_idx:
        html += f'<td>${sp500_normalized[idx]:.2f}</td>'
    html += f'<td class="{cc}">{sp_chg:+.2f}%</td></tr>\n'
    html += '    </tbody></table></div>\n  </div>\n'

    # ── Plotly line chart ──────────────────────────────────────────────
    html += f'''
</div>
<script>
var dates  = {_json.dumps(date_labels)};
var colors = {_json.dumps(colors)};
var lineTraces = [];
'''
    for i, (llm_name, data) in enumerate(ranked):
        cv = data['cumulative_values']
        html += f'''
lineTraces.push({{
  x: dates, y: {_json.dumps(cv)},
  type: 'scatter', mode: 'lines',
  name: '{llm_name}',
  line: {{ color: colors[{i}], width: 3, shape: 'spline', smoothing: 0.7 }},
  hovertemplate: '{llm_name}: $%{{y:.2f}}<extra></extra>'
}});
'''
    html += f'''
lineTraces.push({{
  x: dates, y: {_json.dumps(sp500_normalized)},
  type: 'scatter', mode: 'lines',
  name: 'S&P 500',
  line: {{ color: '#1e293b', width: 2.5, dash: 'dashdot', shape: 'spline', smoothing: 0.7 }},
  hovertemplate: 'S&P 500: $%{{y:.2f}}<extra></extra>'
}});
var annotations = [];
var lastDate = dates[dates.length-1];
'''
    all_series = []
    for i, (llm_name, data) in enumerate(ranked):
        cv       = data['cumulative_values']
        last_val = cv[-1]
        trp      = data['total_return_pct']
        ssym     = '+' if trp >= 0 else ''
        label    = f'{llm_name}: ${last_val:.0f} ({ssym}{trp:.1f}%)'
        all_series.append((last_val, label, colors[i]))
    sp_last  = sp500_normalized[-1]
    sp_ssym  = '+' if sp500_ret_pct >= 0 else ''
    sp_label = f'S&P 500: ${sp_last:.0f} ({sp_ssym}{sp500_ret_pct:.1f}%)'
    all_series.append((sp_last, sp_label, '#1e293b'))
    all_series_sorted = sorted(all_series, key=lambda x: x[0], reverse=True)
    label_arr_js = _json.dumps([[s[0], s[1], s[2]] for s in all_series_sorted])

    html += f'''
var labelArr = {label_arr_js};
labelArr.sort(function(a,b){{ return b[0]-a[0]; }});
var adjY = [];
for (var li=0; li<labelArr.length; li++) {{
  var y = labelArr[li][0];
  for (var lj=0; lj<adjY.length; lj++) {{ if (Math.abs(adjY[lj]-y) < 18) y = adjY[lj]-18; }}
  adjY.push(y);
  annotations.push({{
    x: lastDate, y: adjY[li],
    xanchor: 'left', yanchor: 'middle', xshift: 10,
    text: '<b>'+labelArr[li][1]+'</b>',
    showarrow: false,
    font: {{ size: 13.5, color: labelArr[li][2], family: 'Inter,sans-serif' }},
    bgcolor: 'rgba(255,255,255,0.93)', borderpad: 4
  }});
}}
Plotly.newPlot('line-chart', lineTraces, {{
  paper_bgcolor: '#ffffff', plot_bgcolor: '#fafbff',
  xaxis: {{
    title: {{ text: '' }},
    showgrid: true, gridcolor: '#e8ecf4', gridwidth: 1,
    color: '#374151',
    tickfont: {{ size: 13, color: '#374151', family: 'Inter,sans-serif' }},
    zeroline: false, showline: true, linecolor: '#cbd5e1', tickcolor: '#94a3b8',
    automargin: true, tickangle: -45,
    range: [-0.8, dates.length - 0.8]
  }},
  yaxis: {{
    title: {{ text: 'Portfolio Value ($)', font: {{ size: 14, color: '#1e3a8a', family: 'Inter,sans-serif' }}, standoff: 25 }},
    showgrid: true, gridcolor: '#e8ecf4', gridwidth: 1,
    color: '#374151',
    tickfont: {{ size: 13, color: '#374151', family: 'Inter,sans-serif' }},
    tickprefix: '$', showline: true, linecolor: '#cbd5e1',
    tickcolor: '#94a3b8', automargin: true
  }},
  height: 680,
  autosize: true,
  hovermode: 'x unified',
  hoverlabel: {{
    bgcolor: 'rgba(255,255,255,0.97)', bordercolor: '#e2e8f0',
    font: {{ size: 12, family: 'Inter,sans-serif', color: '#1e3a8a' }},
    namelength: 0
  }},
  annotations: annotations,
  margin: {{ t: 60, b: 80, l: 155, r: 210 }},
  legend: {{
    orientation: 'h', yanchor: 'bottom', y: 1.02,
    xanchor: 'center', x: 0.5,
    font: {{ color: '#374151', size: 15, family: 'Inter,sans-serif' }},
    bgcolor: 'rgba(255,255,255,0)'
  }},
  font: {{ color: '#374151', family: 'Inter,sans-serif' }}
}}, {{ responsive: true, displayModeBar: false }});

function adjustForMobile() {{
  var isMobile = window.innerWidth < 600;
  Plotly.relayout('line-chart', {{
    'margin': isMobile
      ? {{ t: 40, b: 60, l: 55, r: 10 }}
      : {{ t: 60, b: 80, l: 155, r: 210 }},
    'height': isMobile ? 320 : 680,
    'annotations': isMobile ? [] : annotations,
    'xaxis.tickangle': isMobile ? -55 : -45,
    'xaxis.tickfont.size': isMobile ? 9 : 13,
    'yaxis.tickfont.size': isMobile ? 9 : 13,
    'legend.font.size': isMobile ? 10 : 15
  }});
}}
adjustForMobile();
window.addEventListener('resize', adjustForMobile);

// ── Auto-refresh every 30 minutes ─────────────────────────────────
setTimeout(function() {{ location.reload(); }}, 30 * 60 * 1000);
</script>
</body>
</html>'''
    return html

print('✅ generate_html() ready')

# ── Save Dashboard ────────────────────────────────────────────────────
print('Generating dashboard...')
html_content = generate_html(llm_results, stock_data, all_trading_days)
os.makedirs('docs', exist_ok=True)
with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f'SUCCESS: docs/index.html saved ({len(html_content)//1024} KB)')
