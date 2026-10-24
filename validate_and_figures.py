import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

raw = pd.read_csv("raw_shipments.csv")
clean = pd.read_csv("clean_shipments.csv")

# Sensitivity of outlier rule to threshold k (log scale IQR)
def flags(series, k):
    s = np.log1p(series.dropna().clip(lower=0))
    q1, q3 = s.quantile([.25,.75]); i = q3-q1
    v = np.log1p(series.clip(lower=0))
    return int(((v > q3+k*i) | (v < q1-k*i)).sum())
for k in [1.5, 2.0, 3.0]:
    print(f"k={k}: weight flags={flags(raw['weight_kg'],k)}, cost flags={flags(raw['freight_cost_inr'],k)}")

# Ground-truth check: how many extreme weights (>100kg) and extreme costs remain after cleaning
print("weights >100 kg remaining after cleaning:", int((clean['weight_kg']>100).sum()))
print("costs >5000 INR remaining after cleaning:", int((clean['freight_cost_inr']>5000).sum()))
print("raw weights >100 kg:", int((raw['weight_kg']>100).sum()), "| raw costs >5000:", int((raw['freight_cost_inr']>5000).sum()))

# Effect of imputation on distributions (mean/median before vs after, on non-missing raw values)
for col in ["weight_kg","distance_km","freight_cost_inr"]:
    r = raw[col].dropna()
    print(f"{col}: raw median={r.median():.2f} mean={r.mean():.2f} | clean median={clean[col].median():.2f} mean={clean[col].mean():.2f}")

# Summary numbers for the report
print("\nclean carriers:", clean['carrier'].value_counts().to_dict())
print("clean warehouses:", clean['warehouse'].value_counts().to_dict())
print("clean status:", clean['status'].value_counts().to_dict())
print("mode:", clean['mode'].value_counts().to_dict())
print("transit hours by mode (mean):", clean.groupby('mode')['transit_hours'].mean().round(2).to_dict())
print("clean z-score checks mean/std:", round(clean['log_freight_cost_z'].mean(),6), round(clean['log_freight_cost_z'].std(),6))

# Figure: boxplots before vs after cleaning for weight and cost
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].boxplot([raw['weight_kg'].dropna()], vert=True)
ax[0].set_yscale('log'); ax[0].set_title('Weight (kg), raw, log scale'); ax[0].set_xticks([])
ax[1].boxplot([clean['weight_kg']], vert=True)
ax[1].set_yscale('log'); ax[1].set_title('Weight (kg), cleaned, log scale'); ax[1].set_xticks([])
plt.tight_layout(); plt.savefig("fig_outliers_weight.png", dpi=150)

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].hist(clean['freight_cost_inr'], bins=60, color='#888'); ax[0].set_title('Freight cost (INR), skewed')
ax[1].hist(clean['log_freight_cost'], bins=60, color='#4a7'); ax[1].set_title('log1p(freight cost), after transform')
plt.tight_layout(); plt.savefig("fig_normalisation.png", dpi=150)
print("figures saved")
