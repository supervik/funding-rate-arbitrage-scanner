import ccxt
import datetime


def init_exchange(exchange_name):
    """
    Initialize an exchange object using its name.

    Args:
        exchange_name (str): Name of the exchange.

    Returns:
        ccxt.Exchange: Initialized exchange object.
    """
    return getattr(ccxt, exchange_name)()


def get_all_trading_pairs(exchange, perpetual=False):
    """
    Fetch all trading pairs for the given exchange.

    Args:
        exchange (ccxt.Exchange): Exchange object.
        perpetual (bool): Whether to fetch perpetual trading pairs.

    Returns:
        list: List of trading pairs.
    """
    markets = exchange.fetch_markets()
    if not perpetual:
        trading_pairs = [market['symbol'] for market in markets if 'spot' in market['type'] and market['active']]
    else:
        trading_pairs = [market['symbol'] for market in markets if 'swap' in market['type'] and market['active']]
    return trading_pairs


def get_funding_rate(exchange, pair):
    """
    Fetch the current funding rate for a trading pair.

    Args:
        exchange (ccxt.Exchange): Exchange object.
        pair (str): Trading pair symbol.

    Returns:
        float: Current funding rate.
    """
    market_data = exchange.fetch_funding_rate(pair)
    current_rate = round(market_data['fundingRate'] * 100, 3)
    return current_rate


def get_historical_funding_rates(exchange, pair, hours=24):
    """
    Fetch historical funding rates for a trading pair.

    Args:
        exchange (ccxt.Exchange): Exchange object.
        pair (str): Trading pair symbol.
        hours (int): Number of hours of historical data to fetch. Default is 24 hours.

    Returns:
        list: List of historical funding rates.
    """
    current_time_ms = int(datetime.datetime.now().timestamp() * 1000)
    hours_in_ms = hours * 60 * 60 * 1000
    since = current_time_ms - hours_in_ms
    market_data = exchange.fetch_funding_rate_history(pair, since=since, limit=100)
    historical_rates = [round(100 * rate['fundingRate'], 3) for rate in market_data]
    return historical_rates


def get_ohlc(exchange, trading_pair, start_date_ms, end_date_ms, timeframe='1m', limit=1000):
    """Fetch OHLC data for a specific symbol and timeframe."""

    all_candles = []
    since = start_date_ms
    while True:
        ohlc = exchange.fetch_ohlcv(trading_pair, timeframe, since, limit)
        if not ohlc:
            break
        # Check if the last candle's timestamp exceeds end_date_ms
        if ohlc[-1][0] > end_date_ms:
            # Filter candles to include only those within the range
            candles_within_range = [candle for candle in ohlc if start_date_ms <= candle[0] < end_date_ms]
            all_candles.extend(candles_within_range)
            break  # Exit the loop since we have included the candles within the range
        all_candles.extend(ohlc)
        since = ohlc[-1][0] + 1  # Start from the next millisecond after the last fetched candle
    return all_candles
