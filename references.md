# Academic and Technical References - Week 2: Data Cleaning & Preprocessing

This document records the foundational research, methodologies, and technical documentation utilized in the Week 2 logistics data cleaning and preprocessing pipeline.

---

## 1. Outlier Detection and Exploratory Data Analysis
- **Tukey, J. W. (1977).**
  - *Title:* Exploratory Data Analysis.
  - *Publisher:* Addison-Wesley Publishing Company, Reading, MA.
  - *ISBN:* 978-0201076165.
  - *Relevance:* Theoretical formulation of the Interquartile Range (IQR) fence rule ( - k \times \text{IQR}, Q_3 + k \times \text{IQR}$) for robust non-parametric outlier detection without assuming Gaussian normality.

---

## 2. Data Cleaning and Imputation Methodologies
- **Little, R. J. A., & Rubin, D. B. (2019).**
  - *Title:* Statistical Analysis with Missing Data (3rd ed.).
  - *Publisher:* John Wiley & Sons, Hoboken, NJ.
  - *ISBN:* 978-0470526798.
  - *Relevance:* Principles of missing data mechanisms (MCAR, MAR, MNAR) and justification of grouped median conditional imputation over global mean substitution.

- **Van den Broeck, J., Cunningham, S. A., Eeckels, R., & Herbst, K. (2005).**
  - *Title:* Data cleaning: Detecting, diagnosing, and editing data abnormalities.
  - *Journal:* PLoS Medicine, 2(10), e267.
  - *DOI / URL:* [https://doi.org/10.1371/journal.pmed.0020267](https://doi.org/10.1371/journal.pmed.0020267)
  - *Relevance:* Systematic framework for data quality screening, diagnostic screening checks, and audit trail logging.

---

## 3. Technical Software Documentation
- **The pandas Development Team (2024).**
  - *Title:* pandas documentation: Working with missing data, time series / date functionality, and string manipulation.
  - *URL:* [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
  - *Relevance:* Implementation reference for deduplication, mixed date format parsing, and group-level conditional transformations.

- **Kaggle (2020).**
  - *Title:* DataCo Smart Supply Chain for Big Data Analysis.
  - *URL:* [https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
  - *Relevance:* Real-world benchmark logistics dataset recommended for extending this simulated preprocessing pipeline.
