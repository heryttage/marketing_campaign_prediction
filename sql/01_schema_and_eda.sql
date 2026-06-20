-- =====================================================================
-- BrightCart | Marketing Campaign Response Prediction
-- Schema + exploratory queries used to understand drivers before modelling
-- Dialect: PostgreSQL
-- =====================================================================
DROP TABLE IF EXISTS marketing_campaign;

CREATE TABLE marketing_campaign (
    customer_id              VARCHAR(20) PRIMARY KEY,
    age                      INT,
    income                   NUMERIC(10,2),
    tenure_months            INT,
    recency_days             INT,
    num_purchases_last_year  INT,
    avg_order_value          NUMERIC(10,2),
    web_visits_last_month    INT,
    email_open_rate          NUMERIC(5,3),
    email_click_rate         NUMERIC(5,3),
    prev_campaigns_contacted INT,
    prev_campaign_response   INT,        -- 0/1
    discount_offered_pct     INT,
    has_loyalty_card         INT,        -- 0/1
    contact_channel          VARCHAR(10),
    channel_preference       VARCHAR(10),
    region                   VARCHAR(10),
    device                   VARCHAR(10),
    customer_segment         VARCHAR(10),
    responded                INT         -- target: 0/1
);
-- \copy marketing_campaign FROM 'data/marketing_campaign.csv' WITH (FORMAT csv, HEADER true);

-- E1. Overall response rate (class balance)
SELECT COUNT(*) AS customers,
       SUM(responded) AS responders,
       ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign;

-- E2. Response rate by segment (is VIP/Dormant predictive?)
SELECT customer_segment, COUNT(*) AS n,
       ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign GROUP BY customer_segment ORDER BY response_rate_pct DESC;

-- E3. Does contacting on the preferred channel help?
SELECT (contact_channel = channel_preference) AS channel_match,
       COUNT(*) AS n, ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign GROUP BY 1;

-- E4. Response rate by prior-campaign response (strong expected driver)
SELECT prev_campaign_response, COUNT(*) AS n,
       ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign GROUP BY prev_campaign_response;

-- E5. Response by email engagement bucket
SELECT CASE WHEN email_click_rate < 0.05 THEN '1 <5%'
            WHEN email_click_rate < 0.15 THEN '2 5-15%'
            WHEN email_click_rate < 0.30 THEN '3 15-30%'
            ELSE '4 30%+' END AS click_band,
       COUNT(*) AS n, ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign GROUP BY 1 ORDER BY 1;

-- E6. Response by discount offered (do bigger offers convert better?)
SELECT discount_offered_pct, COUNT(*) AS n,
       ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign GROUP BY discount_offered_pct ORDER BY discount_offered_pct;

-- E7. Recency effect (recent buyers vs lapsed)
SELECT CASE WHEN recency_days <= 30 THEN '0-30d'
            WHEN recency_days <= 90 THEN '31-90d'
            WHEN recency_days <= 180 THEN '91-180d'
            ELSE '180d+' END AS recency_band,
       COUNT(*) AS n, ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign GROUP BY 1 ORDER BY 1;

-- E8. Loyalty card holders vs not
SELECT has_loyalty_card, COUNT(*) AS n,
       ROUND(100.0*AVG(responded),1) AS response_rate_pct
FROM marketing_campaign GROUP BY has_loyalty_card;
