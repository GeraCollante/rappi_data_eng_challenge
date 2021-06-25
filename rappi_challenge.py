#!/usr/bin/env python
# coding: utf-8

# Rappi Challenge Data Engineer
# **Developer**: COLLANTE, Gerardo

# Data processing libraries
import pandas as pd
import numpy as np
# OS libraries
import os
import requests

# Constants
APP_ID = 'd2847e56a8474a9fb4416b519b1447ce'
SYMBOL = 'COP'
symbol = SYMBOL.lower()
PRETTY = 'true'
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
FILENAME = 'challenge_orders.csv'
CURRENCY_DIR = 'currency'
USD_CURRENCY = f'usd_{symbol}.csv'  # For match with columns df later


def save_csv(df_to_save: pd.DataFrame, filename: str) -> str:
    """
    Save CSV
    
    Parameters
    ----------
    df_to_save : pd.DataFrame
        Original
        
    filename : str
        Name of file

    Returns
    ---------
    None
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    df_to_save.to_csv(filepath)
    return filepath


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
    url = f'https://openexchangerates.org/api/historical/{date}.json?app_id={APP_ID}&symbols={SYMBOL}&prettyprint=false'
    usd = np.nan

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        usd = response.json()['rates'][symbol]
    except requests.exceptions.HTTPError as errh:
        print("Http Error: ", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: ", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: ", errt)
    except requests.exceptions.RequestException as err:
        print("Other Error: ", err)
    return float(usd)


def create_currency_df(filepath: str):
    """
    Function to get create Currency DataFrame
    
    Parameters
    ----------
    filepath : str
        Path of the CSV that contains past values of currency quote (if exists)

    Returns
    ---------
    pd.DataFrame
        Currency DataFrame
    """
    global usd_df
    df_name = 'Currency DataFrame'

    # Get unique dates
    dates = df.created.apply(lambda item: item.strftime('%Y-%m-%d')).unique()

    # Create/load DataFrame
    try:
        # Load usd_df if exists
        usd_df = pd.read_csv(filepath, index_col=0)
        print(f"{df_name} loaded from file.")
    except FileNotFoundError:
        print(f"{df_name} does not exist.")
        # Create DataFrames
        usd_df = pd.DataFrame(columns=["date", "usd"])
        usd_df.set_index('date', inplace=True)
        print(f"{df_name} created.")
    # noinspection PyBroadException
    except Exception as e:
        print(f"{e} creating {df_name}")

    # Fill DataFrame
    for index, date in enumerate(dates):
        try:
            usd_df.loc[date, 'usd']
        except Exception as e:
            usd_df.loc[date] = [get_usd_symbol(date)]
    print(f"{df_name} filled.")

    # Save DataFrame
    usd_df.to_csv(filepath)
    print(f"{df_name} saved.")


def usd_currency(value, date):
    """
    Compute VALUE/(USD/SYMBOL)
    
    Parameters
    ----------
    value : int
        Value of product
    date : str
        Currency quote day

    Returns
    ---------
    float
        Computed value
    """
    return value / usd_df.loc[date].usd


def get_revenue_per_store() -> pd.DataFrame:
    """
    Get revenues
    
    Parameters
    ----------
    Returns
    ---------
    pd.DataFrame
        Computed
    """
    # Revenues
    return df.groupby(by='store').sum().total.sort_values(ascending=False).to_frame().rename(
        columns={'total': 'revenue'})


def get_pct_by_pay_method(pay_method: str) -> pd.DataFrame:
    """
    Get percentage by payment method
    
    Parameters
    ----------
    pay_method : str
        Choose between cc or cash

    Returns
    ---------
    pd.DataFrame
        Computed
    """
    # Filter and group-by
    revenue_per_store = get_revenue_per_store()
    revenue_per_store_filtered = df[df.pay == pay_method].groupby(by='store').sum().total.to_frame().rename(
        columns={'total': f'revenue_{pay_method}'})

    # Match total and revenue per pay method
    temp_df = pd.concat([revenue_per_store, revenue_per_store_filtered], axis=1).fillna(0)

    # Get final df
    pct_by_pay_method = (temp_df[f'revenue_{pay_method}'] / temp_df['revenue']).to_frame().rename(
        columns={0: f'pct_{pay_method}'})
    return pct_by_pay_method


def get_orders_per_store() -> pd.DataFrame:
    """
    Get orders per store
    
    Parameters
    ----------

    Returns
    ---------
    pd.DataFrame
        Computed
    """
    # Return orders
    return df.groupby(by='store').count().order.rename('orders').to_frame()


def get_aov_per_store() -> pd.DataFrame:
    """
    Compute AOV per store
    
    Parameters
    ----------

    Returns
    ---------
    pd.DataFrame
        Computed
    """
    # Get orders and revenue
    orders = get_orders_per_store()
    rev = get_revenue_per_store()

    # Concat to create new DataFrame
    temp_df = pd.concat([orders, rev], axis=1)

    # Compute aov
    return (temp_df.revenue / temp_df.orders).to_frame().rename(columns={0: 'aov'})


if __name__ == "__main__":
    # Data load
    PATH = os.path.join(INPUT_DIR, FILENAME)
    df = pd.read_csv(PATH, index_col=0, parse_dates=['CREATED_AT'])

    # Columns rename
    df.rename(columns={'ORDER_ID': 'order',
                       'PRODUCT_ID': 'producto',
                       'PAYMENT_METHOD': 'pay',
                       'TOTAL_VALUE': 'total',
                       'CREATED_AT': 'created',
                       'STORE_TO_USER_DISTANCE': 'dist',
                       'OBSF_USER_ID': 'user',
                       'OBSF_STORE_TYPE': 'store'}, inplace=True)

    # Change columns types
    df.total = df.total.astype(int)
    df.dist = df.dist.astype(int)
    df.user = df.user.astype(str)
    df.store = df.store.astype(str)
    df.pay = df.pay.astype(str)
    df.order = df.order.astype(str)
    df.producto = df.producto.astype(str)

    CURRENCY_PATH = os.path.join(CURRENCY_DIR, USD_CURRENCY)

    # Create folders if doesn't exists
    os.makedirs(CURRENCY_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    create_currency_df(CURRENCY_PATH)

    df['value'] = df.apply(lambda x: usd_currency(x['total'], x['created'].strftime('%Y-%m-%d')), axis=1)
    print("Computed currency quotes for each order.")

    # Compute DataFrames
    revenue = get_revenue_per_store()
    print("Computed revenues per store.")
    pct_by_pay_cc = get_pct_by_pay_method('cc')
    pct_by_pay_cash = get_pct_by_pay_method('cash')
    print("Computed percentage of pay per store")
    aov = get_aov_per_store()
    print("Computed AOV per store")

    # Create ranking
    ranking_df = pd.concat([revenue, pct_by_pay_cc, pct_by_pay_cash, aov], axis=1).fillna(0)
    print("Ranking created")

    # Sort
    ranking_df.sort_values(by='revenue', ascending=False)
    print("Ranking sorted by revenue.")

    # Store result
    output_path = save_csv(ranking_df, 'ranking.csv')
    print(f"Ranking saved at {output_path}")

    # Product Analysis
    print("Product Data Analysis")
    # Create DataFrames
    producto_total = df.groupby(by='producto').total.sum().to_frame()
    producto_dist = df.groupby(by='producto').dist.mean().to_frame()
    producto_orders = df.groupby(by='producto').order.count().to_frame()

    # Concat
    producto_df = pd.concat([producto_total, producto_dist, producto_orders], axis=1)
    print("Created Product DataFrame")
    output_path = save_csv(producto_df, 'producto_df.csv')
    print(f"Product DataFrame saved at {output_path}")

    # Time series
    print("")
    ts = df.set_index(df.created)
    # Compute DataFrames
    t = '1H'
    ts_orders = ts.resample(t).order.count().to_frame()
    ts_total = ts.resample(t).total.sum().to_frame()
