# Week 2 Report: Data Collection, Cleaning, and Preprocessing for Logistics Analysis

**Internship Program Submission**  
**Student:** [Your Name] (B.E. AI & ML, Acharya Institute of Technology)  
**Organization:** [Internship Organization]  
**Mentor:** [Mentor Name]  
**Date:** October 2026  

---

## Executive Summary

Data quality is the foundational prerequisite for predictive analytics, inventory planning, and route dispatching in modern logistics. Raw transactional data collected from ERPs, warehouse management systems (WMS), and carrier telematics frequently suffer from transmission duplicates, format mismatches, non-physical values, and extreme recording anomalies.

This report presents the implementation and verification of an automated, audit-logged data cleaning and preprocessing pipeline applied to a regional shipment dataset of 5,060 raw records across 3 metropolitan distribution centers. Through an 8-stage pipeline, the system removed 60 duplicate records, standardized fragmented labels, parsed mixed timestamp formats, corrected 34 physically impossible values, detected and imputed 54 extreme outliers using log-scale IQR fences (=3$ for weight/distance, =2$ for freight cost), and applied feature normalization (log1p + z-score + min-max). All Section 6 benchmark statistics were 100% verified and reproduced.

---

## 1. Introduction and Objectives

### 1.1 Objective
The primary objective of Week 2 is to design, implement, and verify a robust Python data preprocessing pipeline that resolves messy data quality issues, handles missing values, and normalizes variables to prepare clean, high-quality transactional data for subsequent exploratory analysis, forecasting, and route optimization.

### 1.2 Key Deliverables
1. An automated Python pipeline (generate_data.py, clean_pipeline.py, alidate_and_figures.py).
2. Verification log (pipeline_log.csv) and cleaned dataset (clean_shipments.csv).
3. Comprehensive technical report detailing data issues, methodologies, threshold sensitivity, and reflection on business decision-making.

---

## 2. Data Collection Simulation

### 2.1 Choice of Reference Data
The dataset represents one full year (2024) of regional shipment dispatches across three distribution centers serving the Bengaluru metropolitan region (WH_BLR_01, WH_BLR_02, and WH_MYS_01). It is synthetically generated with a fixed seed (
ng = np.random.default_rng(42)) to ensure exact reproducibility while injecting controlled, realistic errors.

### 2.2 Dataset Schema
The raw dataset comprises 5,060 rows and 11 attributes:

| Field Name | Data Type | Constraint / Description |
|---|---|---|
| shipment_id | String | Unique consignment identifier (SH100000 to SH104999) |
| carrier | String | Logistics transport partner (5 commercial simulated carriers) |
| warehouse | String | Regional origin fulfillment hub |
| mode | String | Transport mode (Road, Rail, Air) |
| dispatch_time | Timestamp | Timestamp when vehicle departs fulfillment hub |
| delivery_time | Timestamp | Timestamp when delivery is completed at destination |
| distance_km | Float | Transit route distance in kilometres |
| weight_kg | Float | Consignment parcel weight in kilograms |
| reight_cost_inr| Float | Shipping cost in Indian Rupees (₹) |
| status | String | Consignment delivery outcome (Delivered, Delayed, In Transit, Returned) |
| destination_pin | Float | Destination postal PIN code |

---

## 3. Data Quality Issues Identified

A rigorous exploratory scan of the raw data identified 10 distinct quality defects:

| Issue Type | Affected Field(s) | Measured Raw Count | Operational Risk & Analytical Impact |
|---|---|---|---|
| **Missing Values** | carrier, delivery_time, distance_km, weight_kg, reight_cost_inr | 102, 152, 203, 301, 255 cells | Most ML models drop incomplete rows, creating severe sample selection bias |
| **Exact Duplicates** | All fields | 56 rows | Artificially inflates freight expenditure and parcel counts by ~1.1% |
| **ID-level Duplicates** | shipment_id | 4 additional rows | Re-transmitted entries with minor string variations |
| **Inconsistent Case** | carrier | 297 rows in uppercase | Splits carrier volume metrics across artificial categorical buckets |
| **Padding & Separators**| warehouse | 150 rows | Causes group-by aggregations to treat identical facilities as distinct |
| **Mixed Date Formats** | dispatch_time | 200 rows in dd/mm/yyyy | Causes naive parsers to swap day and month, invalidating timeline analysis |
| **Chronological Inversion**| delivery_time < dispatch_time | 20 rows | Results in negative transit duration, breaking SLA calculations |
| **Negative Distances** | distance_km | 14 rows | Physically impossible entry error corrupting vehicle mileage averages |
| **Extreme Weight Outliers**| weight_kg | 37 rows > 100 kg (max 10,600 kg) | Grams keyed in as kilograms; skews raw mean from 2.2 kg to 19.2 kg |
| **Extreme Cost Outliers** | reight_cost_inr | 21 rows > ₹5,000 (max ₹49,144) | Data entry extra zeros; distorts transportation budget projections |

---

## 4. Methodology: Cleaning and Preprocessing Pipeline

The preprocessing pipeline executes in a strictly audited sequence:

`
[Raw Data: 5,060 rows, 1,013 missing]
       │
       ▼
1. Exact Deduplication (drop_duplicates) ────────► 5,004 rows (56 removed)
       │
       ▼
2. Label Standardization (strip, title, upper) ──► Unified carrier & warehouse names
       │
       ▼
3. Multi-Format Timestamp Parsing ───────────────► Resolved ISO & dd/mm formats
       │
       ▼
4. Business-Key Deduplication (shipment_id) ─────► 5,000 unique shipments (4 removed)
       │
       ▼
5. Logical Physical Checks ──────────────────────► Corrected 20 inversions, 14 negative signs
       │
       ▼
6. Log-Scale IQR Outlier Detection ──────────────► k=3 weight/dist, k=2 cost (set to NaN)
       │
       ▼
7. Group-Conditional Median Imputation ──────────► Mode-specific medians & 'Unknown' labels
       │
       ▼
8. Re-derivation & Normalization ────────────────► log1p, z-scores, min-max scaling
       │
       ▼
[Clean Data: 5,000 rows, 0 missing, 100% Validated]
`

---

## 5. Empirical Results and Verification

### 5.1 Pipeline Execution Log

All metrics exactly match the benchmark specifications in Section 6.1:

| Step | Output Rows | Missing Cells | Operational Action Taken |
|---|---|---|---|
| **0. Raw load** | 5,060 | 1,013 | Baseline raw ingestion |
| **1. Remove exact duplicates** | 5,004 | 999 | 56 exact duplicate rows dropped |
| **2. Standardise text labels** | 5,004 | 999 | Case normalized (Title case carriers, WH_... warehouses) |
| **3. Parse mixed timestamp formats** | 5,004 | 999 | 0 unparseable dispatch timestamps |
| **3b. Deduplicate on shipment_id** | 5,000 | 999 | 4 formatted duplicates removed on business key |
| **4. Logical checks** | 5,000 | 1,019 | 20 invalid delivery timestamps set to NaN; 14 negative distances sign-corrected |
| **5. Outlier detection** | 5,000 | 1,242 | 38 weights and 16 costs flagged via IQR and set to NaN |
| **6. Impute missing values** | 5,000 | 169 | Mode-grouped medians applied; remaining 169 delivery times reconstructed |
| **7. Normalisation** | 5,000 | 0 | log_freight_cost_z (mean 0.0, std 1.0), distance_minmax |
| **Final validation** | 5,000 | 0 | All assertions passed |

### 5.2 Before and After Cleaning Summary

| Metric Field | Raw Median | Clean Median | Raw Mean | Clean Mean | Operational Takeaway |
|---|---|---|---|---|---|
| **Weight (kg)** | 1.64 | **1.62** | 19.24 | **2.20** | Raw mean was 8.7x inflated by mis-keyed grams |
| **Distance (km)** | 190.30 | **189.40** | 252.13 | **253.69** | Preserved core distribution while removing negative errors |
| **Freight Cost (₹)**| 402.15 | **398.01** | 638.43 | **573.58** | Trimmed extreme recording errors without shifting median |

### 5.3 Outlier Sensitivity Analysis

| Threshold k | Weight Flags Flagged | Cost Flags Flagged | Diagnostic Decision |
|---|---|---|---|
| **k = 1.5** | 95 | 53 | Overly aggressive: falsely flags legitimate heavy/long-haul deliveries |
| **k = 2.0** | 59 | **16** | **Optimal for Cost:** cleanly isolates data-entry errors while retaining valid tail |
| **k = 3.0** | **38** | 5 | **Optimal for Weight:** safely isolates gram errors while preserving heavy items |

---

## 6. Generated Visualizations

The pipeline generates two diagnostic charts saved in the project directory:
1. ig_outliers_weight.png: Log-scale boxplots comparing raw weight (displaying extreme outliers up to 10,600 kg) against cleaned weight (all below 100 kg).
2. ig_normalisation.png: Histograms of freight cost before (severely right-skewed) and after log1p transformation (symmetrical distribution ready for regression models).

---

## 7. Limitations

1. **Synthetic Data Realism:** While the synthetic generator realistically injects known data errors, real-world telematics logs also feature missing GPS trails, corrupted character encodings, and complex multi-leg transshipments.
2. **Sign-Correction Assumption:** Converting negative distances to positive values assumes an inverted sign entry. On live enterprise datasets, this must be verified against carrier odometer logs.
3. **Median Imputation Variance Reduction:** Mode-conditional median imputation preserves the central tendency but slightly reduces natural variance. Retaining missingness indicator flags during modeling is recommended.

---

## 8. Reflection: Data Quality and Decision-Making in Logistics

1. **Averages Mislead Without Cleaning:** The raw mean weight (19.24 kg) was nearly 9 times the true typical weight (1.62 kg). A logistics capacity planner relying on raw averages would book 800% excess fleet tonnage.
2. **Categorical Duplication Distorts Vendor Management:** When BlueDart_Sim is recorded under multiple cases, carrier scorecards fragment, weakening volume discount negotiations.
3. **Validation Traceability:** Clean data pipelines must produce immutable audit logs (pipeline_log.csv) to enable managerial sign-off and algorithmic reproducibility.

---

## 9. Conclusion & Week 3 Preparation

Week 2 established an automated, validated preprocessing foundation resulting in 5,000 clean, normalized shipment records. This dataset serves as the verified input for **Week 3: Exploratory Data Analysis (EDA)**.
