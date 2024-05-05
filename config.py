CONFIG = {
    'perpetual_exchanges': ['binance', 'gate', 'kucoinfutures', 'okx'],
    # List of perpetual exchanges from which to obtain or analyze funding rates.
    # Specify exchange IDs according to the CCXT library format.
    # For a list of supported exchange IDs, refer to: https://docs.ccxt.com/#/?id=exchanges

    'spot_exchanges': ['binance', 'gate', 'kucoin', 'okx'],
    # List of spot exchanges for analyzing opportunities between Spot and Perpetual.
    # Specify exchange IDs according to the CCXT library format.
    # For a list of supported exchange IDs, refer to: https://docs.ccxt.com/#/?id=exchanges

    'fetch_and_save_data': False,
    # Whether the script should fetch funding rates from exchanges and save them to files
    # You can fetch the data first and then change this option to False and analyze the data

    'analyze_data_from_files': True,
    # Whether the script should analyze previously saved data from files.
    # Specify directory and subdirectory where files are located below.

    'directory': 'funding_data',
    # Directory where the current funding rates should be saved

    'subdirectory': '20240505_01',
    # Subdirectory within the main directory to save the current funding rates data.

    'file_format': 'xlsx',
    # The file format for saving and importing files. Define 'csv' or 'xlsx'

    'funding_historical_days': 3,
    # Number of days for historical funding rates that used for calculating average daily rate

    'volatility_days': 100,
    # Number of days for calculating average and maximum daily amplitude, representing asset volatility.
    # Amplitude is the percentage difference between the daily high and low, relative to the opening price.
    # Higher amplitudes indicate greater asset volatility.

    'funding_rate_threshold': 0.02,
    # Minimum funding rate (or rate difference). Data below this threshold will be filtered out

    'get_spot_perp_opportunities': True,
    # Whether to analyze opportunities between Spot and Perpetual markets

    'get_perp_perp_opportunities': True
    # Whether to analyze opportunities within Perpetual markets
}
