# Exploratory Data Analysis Summary
- **Total cleaned rows:** 3000
- **Overall escalation rate (`is_escalated`):** 17.43%
- **Missing first-response rate (`is_missing_response`):** 6.03%

## 1. Missing Values & Data Types
- `ticket_id` (str): 0 nulls
- `created_at` (str): 0 nulls
- `first_response_at` (str): 181 nulls
- `category` (str): 0 nulls
- `product_module` (str): 0 nulls
- `platform` (str): 0 nulls
- `channel` (str): 0 nulls
- `priority` (str): 0 nulls
- `is_escalated` (int64): 0 nulls
- `is_missing_response` (int64): 0 nulls
- `response_time_mins` (float64): 0 nulls
- `hour_created` (int64): 0 nulls
- `day_of_week` (str): 0 nulls

## 2. Numeric & Engineered Feature Diagnostics
- `response_time_mins`: mean=62.79, median=30.27, IQR=47.84 [14.45, 62.29], skew=13.54, min=0.46, max=4146.51
- `hour_created`: mean=11.53, median=11.00, IQR=13.00 [5.00, 18.00], skew=-0.00, min=0.00, max=23.00
- `is_missing_response`: mean=0.06, median=0.00, IQR=0.00 [0.00, 0.00], skew=3.69, min=0.00, max=1.00
- `is_escalated`: mean=0.17, median=0.00, IQR=0.00 [0.00, 0.00], skew=1.72, min=0.00, max=1.00

## 3. Escalation Rate by Dimension
- **priority:** Critical: 41.5% (n=277), High: 26.1% (n=560), Medium: 13.4% (n=1105), Low: 10.8% (n=1058)
- **category:** Billing: 19.4% (n=836), Feature_Request: 17.0% (n=270), Shipping: 17.0% (n=405), Technical: 16.9% (n=1011), Account: 15.7% (n=478)
- **product_module:** Checkout: 20.5% (n=692), Dashboard: 16.7% (n=672), Auth: 16.6% (n=632), Notifications: 16.4% (n=421), API: 16.3% (n=583)
- **platform:** iOS: 19.4% (n=966), Android: 17.0% (n=817), Web: 16.2% (n=1217)
- **channel:** Chat: 18.9% (n=956), Web_Form: 17.3% (n=784), Phone: 16.9% (n=385), Email: 16.1% (n=875)
- **day_of_week:** Monday: 20.9% (n=431), Wednesday: 20.8% (n=403), Saturday: 19.0% (n=416), Friday: 17.6% (n=433), Sunday: 17.4% (n=455), Tuesday: 14.2% (n=430), Thursday: 12.5% (n=432)
- **is_missing_response:** 0: 17.6% (n=2819), 1: 15.5% (n=181)

## 4. Highest-Escalation Slices (Platform x Product Module)
- `iOS` + `Checkout`: **29.0%** escalated (n=214)
- `iOS` + `API`: **18.9%** escalated (n=185)
- `Android` + `Auth`: **18.1%** escalated (n=166)
- `Web` + `Dashboard`: **18.0%** escalated (n=266)
- `Android` + `Checkout`: **17.7%** escalated (n=198)
- `iOS` + `Auth`: **17.4%** escalated (n=218)

## 5. Response Speed vs. Escalation
- Response `<= 120 mins`: **15.8%** escalated (n=2645)
- Response `> 120 mins`: **29.3%** escalated (n=355)

## 6. Correlation with `is_escalated`
- `response_time_mins`: Pearson r=+0.091, Spearman rho=+0.067
- `hour_created`: Pearson r=+0.001, Spearman rho=+0.001
- `is_missing_response`: Pearson r=-0.013, Spearman rho=-0.013
