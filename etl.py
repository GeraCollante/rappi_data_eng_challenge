import pandas as pd
import os


def save_csv(df: pd.DataFrame, output_dir: str, filename: str) -> str:
    """
    Save CSV

    Parameters
    ----------
    df : pd.DataFrame
        Original

    output_dir : str
        Folder for save df

    filename : str
        Name of file

    Returns
    ---------
    filepath : str
        Absolute
    """
    filepath: str = os.path.join(output_dir, filename)
    df.to_csv(filepath)
    return filepath


def get_revenue_per_store(df: pd.DataFrame) -> pd.DataFrame:
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
    revenue = (
        df.groupby(by="store")
        .sum()
        .total.to_frame()
        .rename(columns={"total": "revenue"})
    )
    return revenue


def get_pct_by_pay_method(df: pd.DataFrame, pay_method: str) -> pd.DataFrame:
    """
    Get percentage by payment method

    Parameters
    ----------
    df : pd.DataFrame
        Original
    pay_method : str
        Choose between cc or cash

    Returns
    ---------
    pd.DataFrame
        Computed
    """
    # Filter and group-by
    revenue_per_store = get_revenue_per_store(df)
    revenue_per_store_filtered = (
        df[df.pay == pay_method]
        .groupby(by="store")
        .sum()
        .total.to_frame()
        .rename(columns={"total": f"revenue_{pay_method}"})
    )

    # Match total and revenue per pay method
    temp_df = pd.concat([revenue_per_store, revenue_per_store_filtered], axis=1).fillna(0)

    # Get final df
    pct_by_pay_method = (
        (temp_df[f"revenue_{pay_method}"] / temp_df["revenue"])
        .to_frame()
        .rename(columns={0: f"pct_{pay_method}"})
    )
    return pct_by_pay_method


def get_orders_per_store(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get orders per store

    Parameters
    ----------
    df : pd.DataFrame
        Original
    Returns
    ---------
    pd.DataFrame
        Computed
    """
    # Return orders
    orders = df.groupby(by="store").count().order.rename("orders").to_frame()
    return orders


def get_aov_per_store(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute AOV per store

    Parameters
    df : pd.DataFrame
        Original
    ----------

    Returns
    ---------
    pd.DataFrame
        Computed
    """
    # Get orders and revenue
    orders = get_orders_per_store(df)
    rev = get_revenue_per_store(df)

    # Concat to create new DataFrame
    temp_df = pd.concat([orders, rev], axis=1)

    # Compute aov
    aov = (temp_df.revenue / temp_df.orders).to_frame().rename(columns={0: "aov"})
    return aov
