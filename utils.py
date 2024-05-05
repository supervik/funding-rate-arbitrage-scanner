import sys
import os
import pandas as pd
from config import CONFIG


def display_progress(index, total, info=""):
    """
   Displays progress of a process.

   Args:
       index (int): Current index.
       total (int): Total number of items.
       info (str, optional): Additional information to display. Defaults to "".
   """
    msg = f"{info}" if info else "Current progress"
    sys.stdout.write(f"\r {msg}: {round((index / total) * 100, 2)}% completed.")
    sys.stdout.flush()


def df_to_file(df, directory, filename):
    """
    Saves DataFrame to Excel or CSV file.

    Args:
        df (pd.DataFrame): DataFrame to be saved.
        directory (str): Directory to save the file.
        filename (str): Name of the file (without extension).
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        if CONFIG['file_format'] == 'xlsx':
            df.to_excel(f'{directory}/{filename}.xlsx', index=False)
        elif CONFIG['file_format'] == 'csv':
            df.to_csv(f'{directory}/{filename}.csv', index=False)
        else:
            print(f"File format {CONFIG['file_format']} is not supported. The data is saved to csv file: {filename}.csv")
            df.to_csv(f'{directory}/{filename}.csv', index=False)
    except Exception as e:
        print(f"Error: Error occurred while saving the file: {e}")


def file_to_df(directory, filename):
    """
    Loads DataFrame from Excel or CSV file.

    Args:
        directory (str): Directory containing the file.
        filename (str): Name of the file (without extension).

    Returns:
        pd.DataFrame: DataFrame loaded from the file.
    """
    df = pd.DataFrame()
    try:
        if CONFIG['file_format'] == 'xlsx':
            df = pd.read_excel(f"{directory}/{filename}.xlsx")
        elif CONFIG['file_format'] == 'csv':
            df = pd.read_csv(f"{directory}/{filename}.csv")
        else:
            print(f"File format {CONFIG['file_format']} is not supported. "
                  f"Please specify the correct file_format in the config")
    except FileNotFoundError as e:
        print(f"Error: No file found with name {filename} in directory {directory}: \n {str(e)}")
    return df
