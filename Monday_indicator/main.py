import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from datetime import datetime, timedelta
import sys
import nest_asyncio
nest_asyncio.apply()
from send_telegram_message import send_telegram_message
from dotenv import load_dotenv
import os

load_dotenv()


# CONFIG
TIMEFRAME = os.getenv("TIMEFRAM")
SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL"))
CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT"))

def format_signal_message(sig):
    """
    Build a readable message for a single signal.
    """
    return (
        f"[NEW SIGNAL]\n"
        f"Symbol: {sig['symbol']}\n"
        f"Type: {sig['type']}\n"
        f"Level: {sig['level']}\n"
        f"Tap Price: {sig['tap_price']}\n"
        f"Time (UTC): {sig['tap_time']}\n"
    )



async def fetch_binance_futures_markets():
    exchange = ccxt.binance({
        'options': {'defaultType': 'future'},
        'enableRateLimit': True,
    })
    try:
        markets = await exchange.load_markets()
        usdt_futures = [s for s in markets if s.endswith('/USDT:USDT')]
        return exchange, usdt_futures
    except Exception as e:
        print("Error loading markets:", e)
        await exchange.close()
        return None, []


async def fetch_ohlcv(exchange, symbol, timeframe=TIMEFRAME, limit=100):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        return df
    except:
        return None


async def analyze_symbol(exchange, symbol, semaphore, seen_signals, current_week_start):
    async with semaphore:
        df = await fetch_ohlcv(exchange, symbol)

    if df is None or df.empty:
        return []

    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['week_start'] = df['timestamp'].apply(lambda x: x - timedelta(days=x.dayofweek)).dt.date

    # filter only this week's data
    df = df[df['week_start'] == current_week_start]
    if df.empty:
        return []

    # Monday high & low
    monday = df[df['day_of_week'] == 0]
    if monday.empty:
        return []

    monday_high = monday['high'].max()
    monday_low = monday['low'].min()

    # Tue-Sun
    rest = df[df['day_of_week'] > 0]
    if rest.empty:
        return []

    new_signals = []

    # --- High Tap ---
    high_taps = rest[rest['high'] >= monday_high]
    if not high_taps.empty:
        first = high_taps.iloc[0]
        sig_id = (symbol, current_week_start, "HIGH")
        if sig_id not in seen_signals:
            seen_signals.add(sig_id)
            new_signals.append({
                'symbol': symbol,
                'type': 'Monday High Tap',
                'level': monday_high,
                'tap_time': first['timestamp'],
                'tap_price': first['high']
            })

    # --- Low Tap ---
    low_taps = rest[rest['low'] <= monday_low]
    if not low_taps.empty:
        first = low_taps.iloc[0]
        sig_id = (symbol, current_week_start, "LOW")
        if sig_id not in seen_signals:
            seen_signals.add(sig_id)
            new_signals.append({
                'symbol': symbol,
                'type': 'Monday Low Tap',
                'level': monday_low,
                'tap_time': first['timestamp'],
                'tap_price': first['low']
            })

    return new_signals


async def main_loop():
    print("Connecting to Binance Futures (async)...")
    exchange, symbols = await fetch_binance_futures_markets()
    if not exchange:
        return

    print(f"Found {len(symbols)} USDT-M futures pairs.")

    seen_signals = set()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    # Determine current week start
    def get_week_start(d=None):
        d = d or datetime.utcnow().date()
        return d - timedelta(days=d.weekday())

    current_week_start = get_week_start()
    print("Current trading week starts on:", current_week_start)

    try:
        while True:

            # Detect week rollover, reset memory
            new_week_start = get_week_start()
            if new_week_start != current_week_start:
                print("=== New week detected, clearing old signals ===")
                seen_signals.clear()
                current_week_start = new_week_start

            print(f"\n--- Scan started {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC ---")

            tasks = [
                analyze_symbol(exchange, symbol, semaphore, seen_signals, current_week_start)
                for symbol in symbols
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            message_signals = []

            new_count = 0
            for res in results:
                if isinstance(res, Exception):
                    continue
                for sig in res:
                    message_signals.append(sig)
                    new_count += 1
            
            if not message_signals:
                print("No new signals found.")
            else:
                full_message = "\n".join([format_signal_message(sig) for sig in message_signals])
                print(full_message)
                await send_telegram_message(full_message)

            print(f"Scan complete. New signals this run: {new_count}")
            print(f"Sleeping {SLEEP_INTERVAL} sec...\n")

            await asyncio.sleep(SLEEP_INTERVAL)

    except KeyboardInterrupt:
        print("Stopped manually.")
    finally:
        await exchange.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_loop())