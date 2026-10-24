"""
Simulate a raw shipment-records dataset for a regional logistics operator.
All records are SYNTHETIC. Quality problems are injected deliberately so the
cleaning pipeline has realistic issues to detect and fix.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 5000
carriers = ["BlueDart_Sim", "Delhivery_Sim", "EcomExpress_Sim", "Ekart_Sim", "XpressLite_Sim"]
warehouses = ["WH_BLR_01", "WH_BLR_02", "WH_MYS_01"]
modes = ["Road", "Rail", "Air"]
statuses = ["Delivered", "In Transit", "Delayed", "Returned"]

start = pd.Timestamp("2024-01-01")
dispatch_days = rng.integers(0, 365, N)
dispatch = start + pd.to_timedelta(dispatch_days, unit="D") + pd.to_timedelta(rng.integers(0, 86400, N), unit="s")

mode = rng.choice(modes, N, p=[0.6, 0.25, 0.15])
distance_km = np.where(mode == "Air", rng.uniform(150, 900, N),
              np.where(mode == "Rail", rng.uniform(100, 700, N),
                       rng.uniform(5, 250, N)))
speed = np.where(mode == "Air", 500, np.where(mode == "Rail", 60, 40))
transit_hours = distance_km / speed + rng.gamma(2.0, 2.0, N)
delivery = dispatch + pd.to_timedelta(transit_hours, unit="h")

weight_kg = np.round(rng.lognormal(0.5, 0.8, N), 2)
freight_cost = np.round(40 + 1.8 * distance_km * (1 + 0.4 * (mode == "Air")) + 6 * weight_kg + rng.normal(0, 25, N), 2)
# shipping cost is the same for every mode bucket here; keep positive
freight_cost = np.clip(freight_cost, 30, None)

df = pd.DataFrame({
    "shipment_id": [f"SH{100000 + i}" for i in range(N)],
    "carrier": rng.choice(carriers, N),
    "warehouse": rng.choice(warehouses, N, p=[0.45, 0.35, 0.20]),
    "mode": mode,
    "dispatch_time": dispatch,
    "delivery_time": delivery,
    "distance_km": np.round(distance_km, 1),
    "weight_kg": weight_kg,
    "freight_cost_inr": freight_cost,
    "status": rng.choice(statuses, N, p=[0.82, 0.05, 0.10, 0.03]),
    "destination_pin": rng.integers(560001, 560100, N).astype(float),
})

# ---- inject realistic data-quality problems ----
def inject_missing(col, frac):
    idx = rng.choice(N, int(N * frac), replace=False)
    df.loc[idx, col] = np.nan

inject_missing("weight_kg", 0.06)
inject_missing("distance_km", 0.04)
inject_missing("freight_cost_inr", 0.05)
inject_missing("delivery_time", 0.03)
inject_missing("carrier", 0.02)

# Outliers: extreme weights (data entry errors), huge costs
o = rng.choice(N, 40, replace=False)
df.loc[o, "weight_kg"] = df.loc[o, "weight_kg"] * 1000   # grams entered as kg
o2 = rng.choice(N, 25, replace=False)
df.loc[o2, "freight_cost_inr"] = df.loc[o2, "freight_cost_inr"] * 25  # extra zero

# Negative / impossible values
neg = rng.choice(N, 15, replace=False)
df.loc[neg, "distance_km"] = -df.loc[neg, "distance_km"].abs()

# Inconsistent categorical labels
case_idx = rng.choice(N, 300, replace=False)
df.loc[case_idx, "carrier"] = df.loc[case_idx, "carrier"].str.upper()
ws_idx = rng.choice(N, 150, replace=False)
df.loc[ws_idx, "warehouse"] = df.loc[ws_idx, "warehouse"].str.replace("_", " ")
df.loc[ws_idx[:50], "warehouse"] = "  " + df.loc[ws_idx[:50], "warehouse"] + " "

# Delivery before dispatch (timestamp error)
bad_ts = rng.choice(N, 20, replace=False)
df.loc[bad_ts, "delivery_time"] = df.loc[bad_ts, "dispatch_time"] - pd.Timedelta(hours=3)

# Exact duplicate rows (double-posted records)
dups = df.sample(60, random_state=1)
df = pd.concat([df, dups], ignore_index=True)

# Mixed date formats in a text column stored as string
df["dispatch_time"] = df["dispatch_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
fmt_idx = rng.choice(len(df), 200, replace=False)
df.loc[fmt_idx, "dispatch_time"] = pd.to_datetime(df.loc[fmt_idx, "dispatch_time"]).dt.strftime("%d/%m/%Y %H:%M")
df["delivery_time"] = pd.to_datetime(df["delivery_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

df.to_csv("raw_shipments.csv", index=False)
print("raw rows:", len(df))
print(df.isna().sum())
