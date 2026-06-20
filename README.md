# Marketing Campaign Response Prediction — BrightCart

A clean, interview-ready predictive analytics project: given a customer about to be contacted in a promotional campaign, **predict whether they will respond** so marketing can target the right people and stop wasting budget on the rest. Three models are trained and compared end to end.

> **Stack:** Python · scikit-learn · XGBoost · pandas · Matplotlib
> **Role:** Business/Data Analyst
> **Data:** 2,500 customers · 19 raw features · binary target (17.4% response rate)
> **Best model:** Logistic Regression — **ROC-AUC 0.785**, recall 0.70

---

## 1. Business context

BrightCart (fictional online retailer) blasts promotional offers to large customer lists. Most recipients ignore them, so the campaigns are expensive and annoy customers. Marketing wants to **score each customer's likelihood to respond** and contact only the high-probability segment — cutting cost and contact fatigue while protecting revenue.

## 2. Problem statement

> *Predict, before a campaign is sent, which customers will respond (click and convert), using only information known at contact time. Use the model to rank customers so marketing can target the top deciles instead of the whole list.*

## 3. Target variable

`responded` — binary:
- **1** = customer clicked and converted on the campaign offer (positive class, 17.4%)
- **0** = no response

This is an **imbalanced binary classification** problem, so we evaluate beyond accuracy (precision, recall, F1, ROC-AUC) and use class weighting.

## 4. Features

19 raw inputs spanning demographics, relationship, behaviour, engagement, and campaign design — plus 3 engineered features. See [`docs/data_dictionary.md`](docs/data_dictionary.md). Highlights:

- **Engagement:** `email_open_rate`, `email_click_rate`, `web_visits_last_month`
- **Behaviour / value:** `recency_days`, `num_purchases_last_year`, `avg_order_value`, `tenure_months`
- **History:** `prev_campaigns_contacted`, `prev_campaign_response`
- **Campaign design:** `discount_offered_pct`, `contact_channel`
- **Segments:** `customer_segment`, `has_loyalty_card`, `region`, `device`

**Engineered features** (`src/train_models.py`):
- `channel_match` — was the customer contacted on their preferred channel?
- `engagement_score` — weighted blend of open and click rates.
- `purchases_per_year_tenure` — purchase intensity normalised by tenure.

## 5. Preprocessing

- Median imputation for missing `income` / `avg_order_value`; most-frequent for categoricals.
- One-hot encoding for categorical fields.
- Standard scaling for the linear model (tree models use raw numerics).
- Stratified 75/25 train-test split; **5-fold stratified cross-validation** for AUC.
- Class imbalance handled with `class_weight="balanced"` (LR, RF) and `scale_pos_weight` (XGBoost).

All preprocessing lives in scikit-learn `Pipeline` + `ColumnTransformer` objects, so there is **no train/test leakage** and the whole flow is reproducible.

## 6. Models & results

Three algorithms, evaluated on the held-out test set:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | CV ROC-AUC |
|---|---|---|---|---|---|---|
| **Logistic Regression** | 0.733 | 0.362 | **0.697** | **0.476** | **0.785** | 0.762 |
| Random Forest | **0.814** | **0.451** | 0.294 | 0.356 | 0.770 | 0.757 |
| XGBoost | 0.797 | 0.417 | 0.413 | 0.415 | 0.750 | 0.729 |


**Why Logistic Regression wins here:** ROC-AUC measures ranking quality — exactly what we need to target the top deciles — and the linear model ranks best while also recovering 70% of true responders (recall). The tree models post higher *accuracy* simply by predicting "no" more often (the majority class), which is misleading on imbalanced data. This is the project's key lesson: **pick the metric that matches the business goal, and more complex isn't automatically better.**


**Confusion matrix (Logistic Regression):** of 109 real responders in the test set, the model catches **76 (70%)**, at the cost of 134 false positives — an acceptable trade when a contact is cheap and a missed responder is lost revenue.


## 7. Feature importance

The drivers are intuitive and consistent across models:

1. **`email_click_rate`** and the blended **`engagement_score`** — recent engagement is the strongest signal.
2. **`recency_days`** — recent buyers respond more.
3. **`email_open_rate`**, **`prev_campaign_response`**, purchase intensity, and `avg_order_value`.

Demographics (age, region, device) matter far less than behaviour — a useful message for the marketing team.

## 8. Business interpretation & recommendations

- **Target the top 2–3 deciles by predicted probability.** Ranking customers by score lets marketing reach most responders while contacting a fraction of the list — directly cutting send costs and fatigue.
- **Engagement beats demographics.** Prioritise customers who recently opened/clicked; deprioritise long-lapsed, low-engagement contacts.
- **Contact on the preferred channel** — `channel_match` is a real lift and is free to act on.
- **Don't over-discount everyone.** Discount level matters less than engagement; reserve deeper offers for high-value, on-the-fence customers.

## 9. Deployment ideas

A practical, junior-friendly path is described in [`docs/deployment_and_recommendations.md`](docs/deployment_and_recommendations.md): batch scoring of the customer list before each campaign, exported as a ranked CSV / Power BI table; later, a lightweight REST API (FastAPI) wrapping the saved pipeline; monitoring for score drift and periodic retraining.

## 10. Interview preparation

[`docs/interview_qa.md`](docs/interview_qa.md) contains 18 likely questions and strong answers covering the problem framing, why AUC over accuracy, handling imbalance, leakage prevention, model choice, and how you'd explain results to a non-technical stakeholder.

## 11. Repository structure

```
03_marketing_campaign_prediction/
├── data/
│   ├── marketing_campaign.csv      # dataset (2,500 rows)
│   ├── model_results.csv           # metrics table (generated)
│   └── feature_importance.csv      # generated
├── sql/
│   └── 01_schema_and_eda.sql       # schema + 8 driver-exploration queries
├── src/
│   ├── generate_dataset.py         # reproducible data generator
│   └── train_models.py             # preprocessing, 3 models, evaluation, charts
├── docs/
│   ├── data_dictionary.md
│   ├── interview_qa.md
│   ├── deployment_and_recommendations.md
└── README.md
```

## 12. How to run

### Option A: Run Interactively in Your Web Browser (Recommended)
You can run individual code sections and view the interactive charts instantly without installing anything locally:

[![Open In Colab](https://google.com)](https://github.com/heryttage/marketing_campaign_prediction/blob/main/src/train_models.ipynb)

---

### Option B: Run Locally on Your Machine
If you prefer to download and run the project locally, open your terminal and run the following commands:

```bash
# 1. Install necessary dependencies
pip install pandas numpy matplotlib notebook

# 2. Generate the underlying dataset 
python src/generate_dataset.py       # creates data/recruitment_applications.csv

# 3. Open and run the interactive notebook
jupyter notebook src/analysis.ipynb   # launches interface to execute cells and view charts

# SQL: load data/recruitment_clean.csv then run sql/02_analysis_queries.sql
```
---

*Synthetic data generated. BrightCart is fictional. Metrics above are from a fixed-seed run; your numbers may vary by a fraction.*
