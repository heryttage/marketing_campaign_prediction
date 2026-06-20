# Data Dictionary — Marketing Campaign

One row = one customer who was (or will be) contacted in a promotional campaign.

| Field | Type | Description |
|---|---|---|
| `customer_id` | string | Unique customer key (not used as a feature) |
| `age` | int | Customer age (18–80) |
| `income` | numeric | Estimated annual income (USD) |
| `tenure_months` | int | Months as a customer |
| `recency_days` | int | Days since last purchase |
| `num_purchases_last_year` | int | Purchases in the last 12 months |
| `avg_order_value` | numeric | Average order value (USD) |
| `web_visits_last_month` | int | Site visits in the last month |
| `email_open_rate` | numeric | Share of marketing emails opened (0–1) |
| `email_click_rate` | numeric | Share of marketing emails clicked (0–1) |
| `prev_campaigns_contacted` | int | Number of prior campaigns the customer received |
| `prev_campaign_response` | int (0/1) | Did the customer respond to a prior campaign? |
| `discount_offered_pct` | int | Discount offered in this campaign (5–30) |
| `has_loyalty_card` | int (0/1) | Loyalty program member |
| `contact_channel` | string | Channel used for this campaign: Email / SMS / Push / Phone |
| `channel_preference` | string | Customer's preferred channel |
| `region` | string | North / South / East / West |
| `device` | string | Primary device: Mobile / Desktop / Tablet |
| `customer_segment` | string | New / Regular / VIP / Dormant |
| **`responded`** | int (0/1) | **TARGET** — clicked and converted on the campaign |

## Engineered features (created in `train_models.py`)

| Feature | Definition |
|---|---|
| `channel_match` | 1 if `contact_channel == channel_preference`, else 0 |
| `engagement_score` | 0.4 × open_rate + 0.6 × click_rate |
| `purchases_per_year_tenure` | num_purchases_last_year ÷ (tenure_months/12 + 1) |

## Notes

- Target prevalence ≈ 17.4% (imbalanced) → evaluate with precision/recall/F1/ROC-AUC, not accuracy alone.
- ~3% of `income` and ~2% of `avg_order_value` are missing by design (imputed in the pipeline).
- No field encodes the outcome, so there is no target leakage.
