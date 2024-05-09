import re

import pandas as pd
from itertools import combinations
import ast
from config import CONFIG
from utils import df_to_file, file_to_df


def analyze_data():
    """
    Analyzes funding rates data from files and identifies trading opportunities.

    This function reads funding rates data from files, creates dataframes for each exchange,
    and identifies trading opportunities between perpetual contracts (Perpetual-Perpetual) and
    between perpetual contracts and spot markets (Spot-Perpetual).
    """
    directory_data = f"{CONFIG['directory']}/{CONFIG['subdirectory']}/data"
    directory_result = f"{CONFIG['directory']}/{CONFIG['subdirectory']}/result"
    perpetual_exchanges_str = '_'.join(CONFIG['perpetual_exchanges'])

    # Load perpetual data from files
    perpetual_data_df = create_perpetual_data_df_from_files(directory_data)
    if not perpetual_data_df:
        return

    print(f"- Analyzing Funding rates from files")

    # Analyze Perpetual-Perpetual opportunities
    if CONFIG['get_perp_perp_opportunities']:
        print(f"-- Analyzing Perpetual-Perpetual opportunities")
        if len(perpetual_data_df) < 2:
            print(f"Warning: Skip Perpetual-Perpetual opportunities analysis. More than 2 perpetual exchanges needed.")
        else:
            perp_exchange_combinations = list(combinations(perpetual_data_df.keys(), 2))
            final_df = pd.DataFrame()
            for combination in perp_exchange_combinations:
                exchange_1, exchange_2 = combination[0], combination[1]
                df_1, df_2 = perpetual_data_df[exchange_1], perpetual_data_df[exchange_2]

                df = create_perp_perp_opportunities_df(exchange_1, exchange_2, df_1, df_2)
                final_df = pd.concat([final_df, df], ignore_index=True)

            final_df = final_df[final_df['rate_diff'] > CONFIG['funding_rate_threshold']]
            final_df = final_df.sort_values(by='rate_diff', ascending=False, ignore_index=True)

            # print("Final Perpetual-Perpetual opportunities dataframe:")
            # print(final_df)
            df_to_file(final_df, directory_result, f"result_perp_perp_{perpetual_exchanges_str}")
            print(f"-- Analysis process finished. The data is saved in the directory: {directory_result}")

    # Analyze Spot-Perpetual opportunities
    if CONFIG['get_spot_perp_opportunities']:
        print(f"-- Analyzing Spot-Perpetual opportunities")

        spot_pairs_df = create_spot_data_df_from_files(directory_data)
        if spot_pairs_df.empty:
            return

        final_df = pd.DataFrame()
        for perpetual_exchange, perpetual_rates_df in perpetual_data_df.items():
            df = create_spot_perp_opportunites_df(perpetual_exchange, perpetual_rates_df, spot_pairs_df)
            final_df = pd.concat([final_df, df], ignore_index=True)
        positive_rates_df = filter_and_sort_rates(final_df, final_df['rate'] > 0, False, "positive")
        negative_rates_df = filter_and_sort_rates(final_df, final_df['rate'] < 0, True, "negative")

        df_to_file(positive_rates_df, directory_result, f"result_spot_perp_positive_{perpetual_exchanges_str}")
        df_to_file(negative_rates_df, directory_result, f"result_spot_perp_negative_{perpetual_exchanges_str}")
        print(f"-- Analysis process finished. The data is saved in the directory: {directory_result}")


def create_perpetual_data_df_from_files(directory_data):
    """
    Creates a dictionary of perpetual data dataframes from files.

    Args:
        directory_data (str): Directory containing files.

    Returns:
        dict: Dictionary with exchange names as keys and dataframes as values.
    """
    perpetual_data = {}
    for exchange in CONFIG['perpetual_exchanges']:
        df = file_to_df(f"{directory_data}", f"funding_rates_{exchange}")
        if not df.empty:
            df['pair'] = df['pair'].apply(remove_leading_numbers)
            perpetual_data[exchange] = df
    if len(perpetual_data) == 0:
        print(f"- Exiting: Perpetual exchange data not found.")
        return False
    print(f"Data for perpetual exchanges ({', '.join(perpetual_data.keys())}) loaded successfully")

    return perpetual_data


def create_spot_data_df_from_files(directory_data):
    """
    Creates a dataframe of spot trading pairs from files.

    Args:
        directory_data (str): Directory containing files.

    Returns:
        pd.DataFrame: DataFrame containing trading pairs and the exchanges where each pair is available.
    """
    spot_data = []
    for exchange in CONFIG['spot_exchanges']:
        df = file_to_df(f"{directory_data}", f"spot_pairs_{exchange}")
        if not df.empty:
            df['spot_exchange'] = exchange
            spot_data.append(df)
    if len(spot_data) == 0:
        print("- Exiting: No spot data found")
        return pd.DataFrame()
    combined_df = pd.concat(spot_data).groupby('pair')['spot_exchange'].apply('/'.join).reset_index()
    return combined_df


def create_perp_perp_opportunities_df(exchange_1, exchange_2, df_1, df_2):
    """
    Creates a dataframe of Perpetual-Perpetual trading opportunities.

    Args:
        exchange_1 (str): Name of the first exchange.
        exchange_2 (str): Name of the second exchange.
        df_1 (pd.DataFrame): Dataframe of funding rates for exchange_1.
        df_2 (pd.DataFrame): Dataframe of funding rates for exchange_2.

    Returns:
        pd.DataFrame: DataFrame containing Perpetual-Perpetual trading opportunities.
    """
    df = pd.merge(df_1, df_2, on='pair', how='inner')

    # Identify short and long exchanges
    df['short_exchange'] = exchange_1
    df['long_exchange'] = exchange_2
    df.loc[df['rate_x'] < df['rate_y'], ['short_exchange', 'long_exchange']] = exchange_2, exchange_1

    # Identify short and long rates
    df['short_rate'] = df.apply(lambda x: x['rate_x'] if x['short_exchange'] == exchange_1 else x['rate_y'],
                                axis=1)
    df['long_rate'] = df.apply(lambda x: x['rate_x'] if x['long_exchange'] == exchange_1 else x['rate_y'],
                               axis=1)
    df['rate_diff'] = df['short_rate'] - df['long_rate']

    # Identify historical rates for short and long exchanges
    df['historical_rates_x'] = df['historical_rates_x'].fillna('[]').apply(ast.literal_eval)
    df['historical_rates_y'] = df['historical_rates_y'].fillna('[]').apply(ast.literal_eval)

    df['short_historical_rates'] = df.apply(
        lambda x: x['historical_rates_x'] if x['short_exchange'] == exchange_1
        else x['historical_rates_y'], axis=1)
    df['long_historical_rates'] = df.apply(
        lambda x: x['historical_rates_x'] if x['long_exchange'] == exchange_1
        else x['historical_rates_y'], axis=1)

    # Calculate cumulative rates
    df['short_cumulative_rate'] = df['short_historical_rates'].apply(sum)
    df['long_cumulative_rate'] = df['long_historical_rates'].apply(sum)

    df['cumulative_rate_diff'] = df['short_cumulative_rate'] - df['long_cumulative_rate']
    days = CONFIG['funding_historical_days']
    df[f'{days}_days_average_daily_rate_diff'] = df['cumulative_rate_diff'] / days

    df['mean_daily_amplitude'] = df[['mean_daily_amplitude_x', 'mean_daily_amplitude_y']].max(axis=1)
    df['max_daily_amplitude'] = df[['max_daily_amplitude_x', 'max_daily_amplitude_y']].max(axis=1)

    return df[
        ['pair', 'rate_diff', f'{days}_days_average_daily_rate_diff', 'short_exchange', 'long_exchange',
         'mean_daily_amplitude', 'max_daily_amplitude', 'short_rate', 'long_rate',
         'short_cumulative_rate', 'long_cumulative_rate', 'short_historical_rates', 'long_historical_rates']]


def create_spot_perp_opportunites_df(perpetual_exchange, perpetual_rates_df, spot_pairs_df):
    """
   Creates a dataframe of Spot-Perpetual trading opportunities.

   Args:
       perpetual_exchange (str): Name of the perpetual exchange.
       perpetual_rates_df (pd.DataFrame): DataFrame of funding rates for perpetual_exchange.
       spot_pairs_df (pd.DataFrame): DataFrame of spot trading pairs.

   Returns:
       pd.DataFrame: DataFrame containing Spot-Perpetual trading opportunities.
   """
    spot_pairs_df.rename(columns={'pair': 'spot_pair'}, inplace=True)
    perpetual_rates_df['spot_pair'] = perpetual_rates_df['pair'].str.split(':').str.get(0)
    perpetual_rates_df['spot_pair'] = perpetual_rates_df['spot_pair'].apply(remove_leading_numbers)
    perpetual_rates_df = perpetual_rates_df[perpetual_rates_df['rate'].abs() > CONFIG['funding_rate_threshold']]
    spot_perp_df = pd.merge(perpetual_rates_df, spot_pairs_df, on='spot_pair', how='inner')
    spot_perp_df['perp_exchange'] = perpetual_exchange
    spot_perp_df['historical_rates'] = spot_perp_df['historical_rates'].fillna('[]').apply(ast.literal_eval)
    days = CONFIG['funding_historical_days']
    spot_perp_df[f'{days}_days_average_daily_rate'] = spot_perp_df['historical_rates'].apply(sum) / days

    return spot_perp_df[
        ['pair', 'rate', f'{days}_days_average_daily_rate', 'perp_exchange', 'spot_exchange',
         'mean_daily_amplitude', 'max_daily_amplitude', 'historical_rates']]


def filter_and_sort_rates(df, filter_condition, ascending_order, side):
    """
    Filters and sorts DataFrame with Spot-Perpetual trading opportunities based on specified conditions.

    Args:
        df (pd.DataFrame): DataFrame containing Spot-Perpetual trading opportunities
        filter_condition (bool): Condition to filter the DataFrame.
        ascending_order (bool): Specifies whether to sort the DataFrame in ascending order.
        side (str): Side of the trading rates to filter (e.g., "positive" or "negative").

    Returns:
        pd.DataFrame: Filtered and sorted DataFrame.
    """
    filtered_df = df[filter_condition]
    sorted_df = filtered_df.sort_values(by='rate', ascending=ascending_order, ignore_index=True)
    # print(f"\n Final Spot-Perpetual opportunities {side} rates dataframe:")
    # print(sorted_df)
    return sorted_df


def remove_leading_numbers(trading_pair):
    """
    Removes leading numbers starting with '10', '100', '1000', etc., from a trading pair string.

    Args:
    - trading_pair (str): The trading pair string containing currency names and possibly leading numbers.

    Returns:
    - str: The trading pair string with leading numbers removed.
    """
    return re.sub(r'^(10+)', '', trading_pair)

