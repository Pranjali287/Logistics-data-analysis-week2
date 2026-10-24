import json
import numpy as np
import pandas as pd

log = []  # record what each step did, for the report
def record(step, df, note=""):
    log.append({"step": step, "rows": len(df), "missing_cells": int(df.isna().sum().sum()), "note": note})

raw = pd.read_csv("raw_shipments.csv")
record("0. Raw load", raw)
df = raw.copy()

# 1. Remove exact duplicates
n_before = len(df)
df = df.drop_duplicates()
record("1. Remove exact duplicates", df, f"removed {n_before - len(df)} rows")

# 2. Standardise text fields: trim whitespace, unify case and separators
for col in ["carrier", "warehouse", "mode", "status"]:
    df[col] = df[col].astype("string").str.strip()
df["carrier"] = df["carrier"].str.title()
df["warehouse"] = df["warehouse"].str.replace(" ", "_").str.upper()
record("2. Standardise text labels", df, "trim, case, separator unification")

# 3. Parse timestamps with mixed formats
def parse_ts(s):
    s = str(s)
    try:
        return pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return pd.to_datetime(s, format="%d/%m/%Y %H:%M", errors="coerce")
df["dispatch_time"] = df["dispatch_time"].map(parse_ts)
df["delivery_time"] = df["delivery_time"].map(parse_ts)
record("3. Parse mixed timestamp formats", df, f"unparseable dispatch: {df['dispatch_time'].isna().sum()}")

# 3b. Duplicates that differ only in formatting: dedupe on business key
n_before = len(df)
df = df.drop_duplicates(subset=["shipment_id"], keep="first")
record("3b. Deduplicate on shipment_id", df, f"removed {n_before - len(df)} ID-level duplicates")

# 4. Logical validity rules
invalid_ts = df["delivery_time"] < df["dispatch_time"]
neg_dist = df["distance_km"] < 0
print("invalid timestamp order:", int(invalid_ts.sum()), "| negative distance:", int(neg_dist.sum()))
df.loc[invalid_ts, "delivery_time"] = pd.NaT   # cannot be trusted, treat as missing
df.loc[neg_dist, "distance_km"] = df.loc[neg_dist, "distance_km"].abs()  # sign error
record("4. Logical checks", df, f"timestamp order fixed/NaN: {int(invalid_ts.sum())}, negative distance sign-fixed: {int(neg_dist.sum())}")

# 5. Derive transit time (hours) before imputation, from valid timestamps
df["transit_hours"] = (df["delivery_time"] - df["dispatch_time"]).dt.total_seconds() / 3600

# 6. Outlier detection with IQR on log scale (costs and weights are right-skewed)
def iqr_bounds(s, k=3.0):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

outlier_report = {}
K_BY_COL = {"weight_kg": 3.0, "freight_cost_inr": 2.0, "distance_km": 3.0}  # k tuned by sensitivity check
for col in ["weight_kg", "freight_cost_inr", "distance_km"]:
    s = df[col].dropna()
    s_log = np.log1p(s.clip(lower=0))
    lo, hi = iqr_bounds(s_log, k=K_BY_COL[col])
    mask = (np.log1p(df[col].clip(lower=0)) > hi) | (np.log1p(df[col].clip(lower=0)) < lo)
    outlier_report[col] = {"flagged": int(mask.sum()),
                           "median": float(s.median()),
                           "max_before": float(s.max())}
    df.loc[mask, col] = np.nan   # set aside; imputed in step 7
print(json.dumps(outlier_report, indent=2))
record("5. Outlier detection (IQR, log scale, k=3 weight/distance, k=2 cost)", df, "outliers set to NaN for imputation")

# 7. Missing value handling
miss_before = df.isna().sum().to_dict()
# Numeric: median imputation within the mode group (air costs differ from road)
num_cols = ["weight_kg", "distance_km", "freight_cost_inr", "transit_hours"]
for col in num_cols:
    df[col] = df.groupby("mode")[col].transform(lambda s: s.fillna(s.median()))
# Categorical: explicit 'Unknown' category keeps the row, avoids inventing a carrier
df["carrier"] = df["carrier"].fillna("Unknown")
df["status"] = df["status"].fillna("Unknown")
record("6. Impute missing values", df, "numeric: group median by mode; categorical: 'Unknown'")

# 8. Re-derive transit after imputation so it is consistent with timestamps
df["delivery_time"] = df["delivery_time"].fillna(df["dispatch_time"] + pd.to_timedelta(df["transit_hours"], unit="h"))

# 9. Normalisation
# Log transform for skewed cost, then z-score for model input; min-max for distance
df["log_freight_cost"] = np.log1p(df["freight_cost_inr"])
df["log_weight"] = np.log1p(df["weight_kg"])
for col in ["log_freight_cost", "log_weight", "transit_hours"]:
    df[col + "_z"] = (df[col] - df[col].mean()) / df[col].std()
df["distance_minmax"] = (df["distance_km"] - df["distance_km"].min()) / (df["distance_km"].max() - df["distance_km"].min())
record("7. Normalisation", df, "log1p + z-score; min-max for distance")

# 10. Final validation checks
assert df["shipment_id"].is_unique, "duplicate IDs remain"
assert df.isna().sum()[["weight_kg", "distance_km", "freight_cost_inr", "transit_hours"]].sum() == 0
assert (df["distance_km"] >= 0).all()
assert (df["transit_hours"] >= 0).all()

df.to_csv("clean_shipments.csv", index=False)
pd.DataFrame(log).to_csv("pipeline_log.csv", index=False)
print(pd.DataFrame(log).to_string(index=False))
print("missing before imputation:", miss_before)
print("final shape:", df.shape)
print("final missing:", int(df.isna().sum().sum()))
