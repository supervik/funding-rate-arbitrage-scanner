# Funding Rate Arbitrage scanner

This project is designed for analyzing funding rates and identifying potential Perpetual-Perpetual and Perpetual-Spot arbitrage opportunities.


## Introduction

This project fetches funding rate data from configured cryptocurrency exchanges and analyzes it to identify potential trading opportunities. You can use any exchange from the CCXT library. For a list of supported exchange IDs, refer to:
https://docs.ccxt.com/#/?id=exchanges

It provides functionality to fetch and save:
- Current funding rate data
- Historical funding rate data
- Daily volatility data


## Installation

Clone the repository:
```bash
git clone https://github.com/supervik/funding-rate-arbitrage-scanner.git
```
Navigate to the project directory:
 ```bash
 cd funding-rate-arbitrage-scanner
 ```
Install dependencies:
 ```bash
pip install -r requirements.txt
 ```
Run the main script:
```bash
python funding_rate_arbitrage_scanner.py
```

## Configuration

Configure the project according to your requirements by editing the `config.py` file. The configuration options include specifying the list of exchanges, file format, historical data parameters, and more.

To efficiently utilize the project, follow these steps:

1. **Fetch and Save Data:** To initiate the fetching and saving of funding rate data from exchanges, set the `fetch_and_save_data` parameter in the `config.py` file to `True`. This action will prompt the script to retrieve the data and store it in files within the `directory/subdirectory/data` folder. For each new analysis, consider adjusting the `subdirectory` parameter to maintain organized data storage. You can choose any format for the `subdirectory`, such as a date format or any other format that suits your needs.
2. **Analysis:** After fetching and saving the data, set the `fetch_and_save_data` parameter to `False`. Now, you can run analysis multiple times on the saved data by setting the `analyze_data_from_files` parameter to `True`. This enables the script to analyze the previously saved data from files without the need to fetch it again.


## Analysis

The analysis results are stored in the `directory/subdirectory/result` folder.

For Perpetual-Perpetual opportunities, the analysis generates a file named `result_perp_perp_*` with the following columns:

- **pair**: The trading pair involved in the opportunity
- **rate_diff**: The current difference in funding rates between the short and long exchanges
- **APY_historical_average**: The average APY calculated from historical rates over the past N days. The number of days configured by the `funding_historical_days` parameter
- **short_exchange**: The exchange with the higher funding rate where you are supposed to open a Short order
- **long_exchange**: The exchange with the lower funding rate where you are supposed to open a Long order
- **mean_daily_amplitude**: The average daily amplitude of the trading pair. Amplitude is the percentage difference between the daily high and low prices. Higher amplitudes indicate greater asset volatility. The number of days for calculation is configured by the `amplitude_days` parameter
- **max_daily_amplitude**: The maximum daily amplitude of the trading pair
- **short_rate**: The current funding rate of the short exchange
- **long_rate**: The current funding rate of the long exchange
- **short_cumulative_rate**: The cumulative funding rate of the short exchange
- **long_cumulative_rate**: The cumulative funding rate of the long exchange
- **short_historical_rates**: List of historical funding rates of the short exchange. The number of days configured by the `funding_historical_days` parameter
- **long_historical_rates**: List of historical funding rates of the long exchange. The number of days configured by the `funding_historical_days` parameter

For Perpetual-Spot arbitrage opportunities, the analysis generates two files named `result_spot_perp_positive_*` and `result_spot_perp_negative_*` for positive and negative funding rates, respectively, with the following columns:
- **pair**: The trading pair involved in the opportunity
- **rate**: The current funding rate on the perpetual exchange
- **APY_historical_average**: The average APY calculated from historical rates over the past N days. The number of days configured by the `funding_historical_days` parameter
- **perp_exchange**: The perpetual exchange where you are supposed to open a Short order if the rate is positive and Long order if the rate is negative
- **spot_exchange**: Spot exchanges where you can hedge the opportunity: open a Buy order if the rate is positive and Sell if the rate is negative
- **mean_daily_amplitude**: The average daily amplitude of the trading pair. Amplitude is the percentage difference between the daily high and low prices. Higher amplitudes indicate greater asset volatility. The number of days for calculation is configured by the `amplitude_days` parameter
- **max_daily_amplitude**: The maximum daily amplitude of the trading pair
- **historical_rates**: List of historical funding rates. The number of days configured by the `funding_historical_days` parameter
