#!/usr/bin/env python
# coding: utf-8

# Rappi Challenge Data Engineer
# **Developer**: COLLANTE, Gerardo
from currency import *
from etl import *

# OS libraries
import os

# Constants
INPUT_DIR = "input"
OUTPUT_DIR = "output"
FILENAME = "challenge_orders.csv"

if __name__ == "__main__":
    # Data load
    PATH = os.path.join(INPUT_DIR, FILENAME)
    df = pd.read_csv(PATH, index_col=0, parse_dates=["CREATED_AT"])

    # Create output folder
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Columns rename
    df.rename(
        columns={
            "ORDER_ID": "order",
            "PRODUCT_ID": "producto",
            "PAYMENT_METHOD": "pay",
            "TOTAL_VALUE": "total",
            "CREATED_AT": "created",
            "STORE_TO_USER_DISTANCE": "dist",
            "OBSF_USER_ID": "user",
            "OBSF_STORE_TYPE": "store",
        },
        inplace=True,
    )

    # Change columns types
    df.total = df.total.astype(int)
    df.dist = df.dist.astype(int)
    df.user = df.user.astype(str)
    df.store = df.store.astype(str)
    df.pay = df.pay.astype(str)
    df.order = df.order.astype(str)
    df.producto = df.producto.astype(str)

    currency_df = create_currency_df(df)

    # Compute value for each row in df
    # COP to USD
    df["total"] = df.apply(
        lambda x: usd_currency(
            currency_df, x["total"], x["created"].strftime("%Y-%m-%d")
        ),
        axis=1,
    )
    print("Computed currency quotes for each order.")

    # Compute DataFrames
    revenue = get_revenue_per_store(df)
    print("Computed revenues per store.")
    pct_by_pay_cc = get_pct_by_pay_method(df, "cc")
    pct_by_pay_cash = get_pct_by_pay_method(df, "cash")
    print("Computed percentage of pay per store.")
    aov = get_aov_per_store(df)
    print("Computed AOV per store.")

    # Create ranking
    ranking_df = pd.concat(
        [revenue, pct_by_pay_cc, pct_by_pay_cash, aov], axis=1
    ).fillna(0)
    print("Ranking created.")

    # Sort
    ranking_df.sort_values(by="revenue", ascending=False, inplace=True)
    print("Ranking sorted by revenue.")

    # Store result
    output_path = save_csv(ranking_df, OUTPUT_DIR, "ranking.csv")
    print(f"Ranking saved at {output_path}.")

    # Product Analysis
    print("Product Data Analysis.")
    # Create DataFrames
    producto_total = df.groupby(by="producto").total.sum().to_frame()
    producto_dist = df.groupby(by="producto").dist.mean().to_frame()
    producto_orders = df.groupby(by="producto").order.count().to_frame()

    # Concat
    producto_df = pd.concat([producto_total, producto_dist, producto_orders], axis=1)
    print("Created Product DataFrame.")
    output_path = save_csv(producto_df, OUTPUT_DIR, "producto.csv")
    print(f"Product DataFrame saved at {output_path}.")

    # Time series
    print("Time Series.")
    ts = df.set_index(df.created)
    # Compute DataFrames
    t = "1H"
    ts_orders = ts.resample(t).order.count().to_frame()
    ts_total = ts.resample(t).total.sum().to_frame()
    ts_df = pd.concat([ts_total, ts_orders], axis=1)
    print("Created time series.")
    output_path = save_csv(ts_df, OUTPUT_DIR, "time_series.csv")
    print(f"Time Series DataFrame saved at {output_path}.")
