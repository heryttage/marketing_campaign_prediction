"""
Marketing Campaign Response Prediction - synthetic dataset generator
Company (fictional): BrightCart - online retailer running promotional campaigns.
Target: will a contacted customer RESPOND (click + convert) to the campaign?

Run:  python src/generate_dataset.py
Output: data/marketing_campaign.csv  (~2,500 rows)
"""
import numpy as np, pandas as pd

RNG = np.random.default_rng(7)
N = 2500

age = np.clip(RNG.normal(40, 13, N), 18, 80).round().astype(int)
income = np.clip(RNG.normal(52000, 21000, N), 12000, 200000).round(-2)
tenure_months = np.clip(RNG.gamma(2.2, 14, N), 1, 160).round().astype(int)
recency_days = np.clip(RNG.exponential(70, N), 1, 540).round().astype(int)
num_purchases_last_year = np.clip(RNG.poisson(4.5, N), 0, 40).astype(int)
avg_order_value = np.clip(RNG.gamma(3, 28, N), 8, 600).round(2)
web_visits_last_month = np.clip(RNG.poisson(6, N), 0, 60).astype(int)
email_open_rate = np.clip(RNG.beta(2.2, 3.0, N), 0, 1).round(3)
email_click_rate = np.clip(email_open_rate * RNG.beta(1.6, 4.0, N), 0, 1).round(3)
prev_campaigns = np.clip(RNG.poisson(3, N), 0, 20).astype(int)
prev_response = (RNG.random(N) < (0.12 + 0.5*email_click_rate)).astype(int)
discount_offered = RNG.choice([5,10,15,20,25,30], N, p=[0.20,0.28,0.22,0.15,0.10,0.05])
has_loyalty = (RNG.random(N) < (0.3 + 0.0000035*income)).astype(int)

contact_channel = RNG.choice(["Email","SMS","Push","Phone"], N, p=[0.5,0.22,0.20,0.08])
channel_pref    = RNG.choice(["Email","SMS","Push","Phone"], N, p=[0.45,0.25,0.22,0.08])
region = RNG.choice(["North","South","East","West"], N, p=[0.3,0.25,0.25,0.2])
device = RNG.choice(["Mobile","Desktop","Tablet"], N, p=[0.62,0.30,0.08])
segment = RNG.choice(["New","Regular","VIP","Dormant"], N, p=[0.22,0.45,0.13,0.20])

# ---- Latent response propensity (the signal the models must recover) ----
z = (
    -4.75
    + 4.3*email_click_rate
    + 1.5*email_open_rate
    + 1.4*prev_response
    + 0.035*web_visits_last_month
    + 0.14*num_purchases_last_year
    - 0.007*recency_days
    + 0.030*discount_offered
    + 0.65*has_loyalty
    + 0.85*(contact_channel == channel_pref).astype(float)   # contacting on preferred channel helps
    + np.where(segment=="VIP", 0.95, np.where(segment=="Dormant", -1.05,
               np.where(segment=="New", -0.25, 0.0)))
    - 0.012*np.maximum(0, age-55)
    + RNG.normal(0, 0.38, N)                                  # irreducible noise
)
p = 1/(1+np.exp(-z))
responded = (RNG.random(N) < p).astype(int)

df = pd.DataFrame({
    "customer_id": [f"CUST-{90000+i}" for i in range(N)],
    "age": age, "income": income, "tenure_months": tenure_months,
    "recency_days": recency_days, "num_purchases_last_year": num_purchases_last_year,
    "avg_order_value": avg_order_value, "web_visits_last_month": web_visits_last_month,
    "email_open_rate": email_open_rate, "email_click_rate": email_click_rate,
    "prev_campaigns_contacted": prev_campaigns, "prev_campaign_response": prev_response,
    "discount_offered_pct": discount_offered, "has_loyalty_card": has_loyalty,
    "contact_channel": contact_channel, "channel_preference": channel_pref,
    "region": region, "device": device, "customer_segment": segment,
    "responded": responded,
})

# light, realistic missingness (no leakage on target)
df.loc[df.sample(frac=0.03, random_state=1).index, "income"] = np.nan
df.loc[df.sample(frac=0.02, random_state=2).index, "avg_order_value"] = np.nan

df.to_csv("data/marketing_campaign.csv", index=False)
rate = df["responded"].mean()
print(f"Wrote data/marketing_campaign.csv: {len(df)} rows, {df.shape[1]} cols")
print(f"Response rate: {rate*100:.1f}% (positives={df['responded'].sum()})")
