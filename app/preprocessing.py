import numpy as np
import pandas as pd


def normalize_port(value):
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    value = str(value).strip()

    try:
        if value.lower().startswith("0x"):
            return int(value, 16)

        return int(value)

    except (ValueError, TypeError):
        return np.nan


def normalize_ports_dataframe(X):
    X = X.copy()

    X["source_port"] = X["source_port"].apply(normalize_port)
    X["destination_port"] = X["destination_port"].apply(normalize_port)

    return X