import pandas as pd
from config import CONFIG
from fetch_data import fetch_and_save_data
from analyze_data import analyze_data

# Setting display options for pandas DataFrame
pd.set_option('display.max_columns', None)  # None means unlimited
pd.set_option('display.width', None)  # Ensure the display is not truncated horizontally
pd.set_option('display.max_colwidth', None)  # Ensure full width of each column is displayed


def main():
    """
    Main function to execute the script.

    This function checks the configuration parameters and executes the appropriate actions:
    - If fetch_and_save_data is True, it fetches and saves data to files.
    - If analyze_data_from_files is True, it analyzes data from previously saved files.

    Note: Data should be saved before analysis.
    """
    if CONFIG['fetch_and_save_data']:
        fetch_and_save_data()

    if CONFIG['analyze_data_from_files']:
        analyze_data()


if __name__ == '__main__':
    main()

