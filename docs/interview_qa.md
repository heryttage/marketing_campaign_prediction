# Interview Questions & Answers — Campaign Response Prediction

Prepared to explain this project confidently in a Data Analyst / Junior Data Scientist interview.

### 1. What problem does this project solve?
Marketing was contacting entire customer lists, but only ~17% respond. I built a model that scores each customer's probability of responding so the team can target the high-probability segment, cutting send cost and contact fatigue while keeping most of the revenue.

### 2. What's the target variable and what type of problem is it?
`responded` (1 = clicked and converted, 0 = no response). It's a **binary classification** problem, and it's **imbalanced** (~17% positive), which shapes how I evaluate and train.

### 3. Why not just use accuracy?
On a 17% base rate, a model that predicts "no" for everyone scores 83% accuracy and is useless. That's the **accuracy paradox**. I focus on **ROC-AUC** (ranking quality), **recall** (how many responders we catch), and **precision/F1** for the trade-off.

### 4. Why is ROC-AUC the headline metric here?
Because the business use is **ranking** customers to pick the top deciles. AUC measures how well the model separates responders from non-responders across all thresholds, independent of where we set the cutoff.

### 5. How did you handle the class imbalance?
Three levers: `class_weight="balanced"` for Logistic Regression and Random Forest, `scale_pos_weight` for XGBoost, and stratified splitting/cross-validation so each fold preserves the 17% prevalence. I could also resample (SMOTE) but class weighting was sufficient.

### 6. Which models did you try and which won?
Logistic Regression, Random Forest, and XGBoost. **Logistic Regression won on ROC-AUC (0.785)** and recall (0.70). The tree models had higher raw accuracy but mostly by predicting the majority class.

### 7. Isn't it surprising that Logistic Regression beat XGBoost?
Not really, and it's a good lesson. The relationships between engagement and response are largely monotonic, which a linear model captures well. When the signal is simple, a well-specified simple model can match or beat complex ones — and it's more interpretable and cheaper to run. Complexity should earn its place.

### 8. How did you prevent data leakage?
All preprocessing (imputation, scaling, encoding) is inside a scikit-learn `Pipeline` fit only on the training fold, so test data never influences the transforms. I also excluded `customer_id` and made sure no feature encodes the outcome.

### 9. What were the most important features?
Engagement dominates: `email_click_rate`, the engineered `engagement_score`, `recency_days`, and `email_open_rate`, followed by purchase intensity and prior campaign response. Demographics (age, region, device) mattered far less.

### 10. What features did you engineer and why?
`channel_match` (contacted on preferred channel — actionable lift), `engagement_score` (combines open and click into one signal), and `purchases_per_year_tenure` (purchase intensity normalised by how long they've been a customer, so new and old customers compare fairly).

### 11. How would you choose the probability threshold in production?
It depends on economics. If a contact is cheap and a missed responder is costly, favour **recall** (lower threshold). I'd plot the precision-recall curve and pick the threshold that maximises expected profit given cost-per-contact and revenue-per-response — or simply target the top N% the budget allows.

### 12. How do you validate the model is stable, not just lucky on one split?
5-fold stratified cross-validation. The CV AUC (0.76 for LR) is close to the test AUC (0.785), which suggests the result is stable rather than an artefact of one split.

### 13. What are the model's limitations?
AUC ~0.78 means meaningful but imperfect separation; precision is modest, so we'll contact some non-responders. The data is synthetic, so real-world drift, seasonality, and richer text/behavioural signals aren't captured.

### 14. How would you explain this to a non-technical marketing manager?
"The model gives every customer a 0–100 score for how likely they are to respond. If you contact the top 30% by score, you'll reach most of the people who would have responded anyway, and skip the majority who wouldn't — so you spend less and annoy fewer people."

### 15. How would you deploy it?
Start with **batch scoring**: before each campaign, run the saved pipeline over the customer list and export a ranked CSV / Power BI table. Later, wrap the pipeline in a small FastAPI service for on-demand scoring. Save the fitted pipeline with `joblib`.

### 16. How would you monitor it after deployment?
Track input drift (feature distributions vs training), prediction drift (score distribution), and — once outcomes arrive — realised precision/recall and lift versus a random or "contact-everyone" baseline. Retrain on a schedule or when lift degrades.

### 17. How would you prove business value?
Run an **A/B test**: one group targeted by the model, a control contacted as usual. Compare response rate, revenue, and cost per response. The model wins if it delivers similar revenue at materially lower contact volume/cost.

### 18. What would you improve with more time/data?
Add behavioural sequences and time-of-day/send-time features, calibrate probabilities (Platt/iso), try a precision-recall-optimised threshold per segment, and test gradient boosting with proper hyperparameter tuning and SHAP for per-customer explanations.
