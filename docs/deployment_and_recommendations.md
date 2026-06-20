# Deployment & Recommendations

## Recommended rollout (simplest first)

### Phase 1 — Batch scoring (start here)
Before each campaign, run the saved pipeline over the current customer list and export a ranked table (`customer_id`, `response_probability`, decile). Marketing filters to the top N% the budget allows. This needs no infrastructure — a scheduled Python job writing a CSV or a Power BI dataset.

```python
import joblib, pandas as pd
pipe = joblib.load("models/response_model.joblib")
customers = pd.read_csv("data/upcoming_campaign_list.csv")
customers["response_probability"] = pipe.predict_proba(customers)[:, 1]
customers["decile"] = pd.qcut(customers["response_probability"], 10, labels=False) + 1
customers.sort_values("response_probability", ascending=False)\
         .to_csv("data/scored_list.csv", index=False)
```

*(To enable this, add `joblib.dump(best_pipe, "models/response_model.joblib")` to `train_models.py`.)*

### Phase 2 — On-demand API
Wrap the pipeline in a small FastAPI service so other systems (CRM, campaign tool) can request a score for one customer in real time. Containerise with Docker; deploy to any cloud run/app service.

### Phase 3 — Monitoring & retraining
- **Input drift:** compare live feature distributions to training.
- **Prediction drift:** watch the score distribution over time.
- **Outcome tracking:** once responses land, compute realised precision/recall and **lift vs a contact-everyone baseline**.
- **Retrain** on a schedule (e.g. quarterly) or when lift degrades.

## Proving value with an A/B test
Split the eligible list: a **treatment** group targeted by model score and a **control** contacted as usual. Compare response rate, revenue, and cost per response. The model is validated if it holds revenue while cutting contact volume and cost.

## Business recommendations (from the analysis)
1. **Target the top 2–3 deciles by score** instead of the whole list.
2. **Prioritise recent engagers** — email click/open and recency are the dominant signals.
3. **Always contact on the customer's preferred channel** (`channel_match` lifts response and costs nothing).
4. **Reserve deeper discounts** for high-value, on-the-fence customers rather than discounting everyone.
5. **Stand up an A/B test** to quantify savings before a full rollout.
