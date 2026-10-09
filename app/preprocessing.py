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


def normalize_direction(value):
    if pd.isna(value):
        return np.nan

    val = str(value).strip().lower()

    if val in {"->", ">", "outbound", "out", "egress"}:
        return "   ->"
    if val in {"<-", "<", "inbound", "in", "ingress"}:
        return "  <-"
    if val in {"<->", "<>", "bidirectional", "both"}:
        return "  <->"
    if val in {"?>", "  ?>", "   ?>"}:
        return "   ?>"
    if val in {"<?>", " <?>", "  <?>", "who"}:
        return "  <->"

    # If it's already a valid CTU-13 formatted string with leading spaces
    raw_str = str(value)
    if raw_str in {"   ->", "  <-", "  <->", "   ?>", "  <?>", "  who"}:
        return raw_str

    return "   ->"


def normalize_connection_state(value):
    if pd.isna(value):
        return "CON"

    val = str(value).strip().upper()

    # Map standard TCP/Zeek/CICIDS flags to CTU-13 NetFlow state equivalents
    state_mapping = {
        "SF": "CON",
        "S0": "S_",
        "REJ": "R_",
        "RSTO": "R_",
        "RSTR": "R_",
        "SH": "S_",
        "OTH": "UNK",
    }

    return state_mapping.get(val, val)


def normalize_features_dataframe(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()

    if "source_port" in X.columns:
        X["source_port"] = X["source_port"].apply(normalize_port)

    if "destination_port" in X.columns:
        X["destination_port"] = X["destination_port"].apply(normalize_port)

    if "direction" in X.columns:
        X["direction"] = X["direction"].apply(normalize_direction)

    if "connection_state" in X.columns:
        X["connection_state"] = X["connection_state"].apply(normalize_connection_state)

    if "protocol" in X.columns:
        X["protocol"] = X["protocol"].astype(str).str.strip().str.lower()

    return X


def normalize_ports_dataframe(X):
    return normalize_features_dataframe(X)