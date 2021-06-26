import requests
import numpy as np
import pandas as pd
import os

APP_ID = "d2847e56a8474a9fb4416b519b1447ce"
SYMBOL = "COP"
CURRENCY_DIR = "currency"


def get_usd_symbol(date: str) -> float:
    """
    Function to get USD/COP quote

    Parameters
    ----------
    date : str
        Date of the day for get quote

    Returns
    -------
    float
        Currency USD/[symbol].
    """
    url = f"https://openexchangerates.org/api/historical/{date}.json?app_id={APP_ID}&symbols={SYMBOL}&prettyprint=false"
    usd = np.nan

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        usd = response.json()["rates"][SYMBOL]
    except requests.exceptions.HTTPError as errh:
        print("Http Error: ", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: ", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: ", errt)
    except requests.exceptions.RequestException as err:
        print("Other Error: ", err)
    return float(usd)


def create_currency_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to get create Currency DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        Original

    Returns
    ---------
    pd.DataFrame
        Currency DataFrame
    """
    filename = f"USD_{SYMBOL}.csv"
    currency_path = os.path.join(CURRENCY_DIR, filename)

    # Create folders if doesn't exists
    os.makedirs(CURRENCY_DIR, exist_ok=True)

    df_name = "Currency DataFrame"
    usd_df = None

    # Get unique dates
    dates = df.created.apply(lambda item: item.strftime("%Y-%m-%d")).unique()

    # Create/load DataFrame
    try:
        # Load usd_df if exists
        usd_df = pd.read_csv(currency_path, index_col=0)
        print(f"{df_name} loaded from file.")
    except FileNotFoundError:
        print(f"{df_name} does not exist.")
        # Create DataFrames
        usd_df = pd.DataFrame(columns=["date", "usd"])
        usd_df.set_index("date", inplace=True)
        print(f"{df_name} created.")
    # noinspection PyBroadException
    except Exception as e:
        print(f"{e} creating {df_name}")

    # Fill DataFrame
    for index, date in enumerate(dates):
        try:
            usd_df.loc[date, "usd"]
        except Exception as e:
            usd_df.loc[date] = [get_usd_symbol(date)]
    print(f"{df_name} filled.")

    # Save DataFrame
    usd_df.to_csv(currency_path)
    print(f"{df_name} saved.")
    return usd_df


def usd_currency(currency_df: pd.DataFrame, value: int, date: str) -> float:
    """
    Compute VALUE/(USD/SYMBOL)

    Parameters
    ----------
    currency_df : pd.DataFrame
        USD/SYMBOL df
    value : int
        Value of product
    date : str
        Currency quote day

    Returns
    ---------
    float
        Computed value
    """
    return value / currency_df.loc[date].usd
