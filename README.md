# Logistics Data Analytics - Week 2: Data Cleaning & Preprocessing

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License-MIT](https://img.shields.io/badge/License-Academic%20Internship-green.svg)
![Status-Complete](https://img.shields.io/badge/Status-Complete-success.svg)

An automated data cleaning, validation, and preprocessing pipeline for regional e-commerce shipments. Designed and implemented for Week 2 of the logistics data analytics internship capstone.

---

## 1. Project Overview & Deliverables

Week 2 focuses on simulating, cleaning, and preprocessing messy logistics shipment data across 3 regional distribution centers in the Bengaluru metropolitan area (WH_BLR_01, WH_BLR_02, WH_MYS_01).

### Primary Deliverables:
- **Cleaned Dataset:** [clean_shipments.csv](clean_shipments.csv) (5,000 validated shipments, 18 attributes, 0 missing cells)
- **Pipeline Audit Log:** [pipeline_log.csv](pipeline_log.csv) (Step-by-step row and missing cell tracking)
- **Official Word Report:** [
eport/Week2_Data_Cleaning_Preprocessing_Report.docx](report/Week2_Data_Cleaning_Preprocessing_Report.docx)
- **Markdown Report:** [
eport/Week2_Data_Cleaning_Preprocessing_Report.md](report/Week2_Data_Cleaning_Preprocessing_Report.md)
- **Academic References:** [
eferences.md](references.md)

---

## 2. Directory Layout

`
Logistics-data-analysis-week2/
├── raw_shipments.csv                 # Raw shipment transactions (5,060 rows, 1,013 missing cells)
├── clean_shipments.csv               # Cleaned & normalized dataset (5,000 rows, 0 missing cells)
├── pipeline_log.csv                  # Step-by-step audit trail log
├── fig_outliers_weight.png           # Log-scale boxplot comparison of parcel weight
├── fig_normalisation.png             # Before/after histogram of freight cost log transform
├── generate_data.py                  # Synthetic data generator injecting realistic errors
├── clean_pipeline.py                 # Core 8-stage cleaning, imputation, and scaling pipeline
├── validate_and_figures.py           # Verification script, sensitivity checks, and figure generator
├── requirements.txt                  # Python dependencies
├── references.md                     # Academic citations (Tukey, Little & Rubin, Van den Broeck)
├── Week2_Project_Brief.md            # Original internship specification brief
├── README.md                         # Project documentation and execution instructions
└── report/
    ├── Week2_Data_Cleaning_Preprocessing_Report.docx  # Final formatted Word document report
    └── Week2_Data_Cleaning_Preprocessing_Report.md    # Markdown technical report
`

---

## 3. Pipeline Run Order

Execute the pipeline in the following sequence:

`ash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate raw shipment data with injected quality problems
python generate_data.py          # creates raw_shipments.csv (5,060 rows)

# 3. Execute the data cleaning and preprocessing pipeline
python clean_pipeline.py         # creates clean_shipments.csv and pipeline_log.csv

# 4. Run validation checks, threshold sensitivity, and generate figures
python validate_and_figures.py   # creates fig_outliers_weight.png and fig_normalisation.png
`

---

## 4. Key Results & Verification

### Pipeline Audit Log

| Step | Rows | Missing Cells | Action Taken |
|---|---|---|---|
| **0. Raw load** | 5,060 | 1,013 | Baseline raw extract |
| **1. Remove exact duplicates** | 5,004 | 999 | 56 exact duplicate rows removed |
| **2. Standardise text labels** | 5,004 | 999 | Normalized case, stripped padding, unified _ separators |
| **3. Parse timestamps** | 5,004 | 999 | Handled mixed ISO and dd/mm/yyyy date formats |
| **3b. Deduplicate on shipment_id** | 5,000 | 999 | 4 formatted duplicates removed on business key |
| **4. Logical checks** | 5,000 | 1,019 | Corrected 20 inverted timestamps and 14 negative distances |
| **5. Outlier detection** | 5,000 | 1,242 | Log-scale IQR fences (=3$ weight, =2$ cost) set to NaN |
| **6. Impute missing values** | 5,000 | 169 | Applied mode-grouped medians; reconstructed delivery times |
| **7. Normalisation** | 5,000 | 0 | log1p + z-score transforms; min-max distance scaling |
| **Final validation** | 5,000 | 0 | All integrity assertions passed |

### Before vs. After Cleaning Statistics

| Field | Raw Median | Clean Median | Raw Mean | Clean Mean | Impact of Cleaning |
|---|---|---|---|---|---|
| **Weight (kg)** | 1.64 | **1.62** | 19.24 | **2.20** | Removed severe gram-entry errors that inflated mean by 870% |
| **Distance (km)** | 190.30 | **189.40** | 252.13 | **253.69** | Eliminated negative sign errors without shifting median |
| **Freight Cost (₹)** | 402.15 | **398.01** | 638.43 | **573.58** | Trimmed extreme data-entry extra zeros |

---

## 5. Threshold Sensitivity Analysis

- **Weight ( = 3.0$ chosen):** Using =1.5$ (95 flags) or =2.0$ (59 flags) cuts into legitimate heavy consignments. =3.0$ specifically isolates data-entry errors (38 values > 100 kg, max 10,600 kg).
- **Freight Cost ( = 2.0$ chosen):** Using =3.0$ (5 flags) leaves obvious extra-zero errors above ₹5,000. =2.0$ (16 flags) cleanly flags erroneous recording spikes while preserving legitimate airfreight deliveries.

---

## 6. Next Steps for Week 3

The verified output [clean_shipments.csv](clean_shipments.csv) is the official input for **Week 3: Exploratory Data Analysis (EDA)**.
