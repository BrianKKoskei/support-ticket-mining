from pathlib import Path
import numpy as np
import pandas as pd


def generate_tickets(n_rows: int = 3000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    start = pd.Timestamp("2026-01-01 08:00:00")
    created_offsets = rng.exponential(scale=180.0, size=n_rows).cumsum()
    created_at = [start + pd.Timedelta(minutes=float(m)) for m in created_offsets]

    categories = ["Billing", "billing ", "BILLING", "Technical", "Account", "Shipping", "Feature_Request"]
    modules = ["Checkout", "Auth", "API", "Dashboard", "Notifications"]
    platforms = ["iOS", "Android", "Web"]
    channels = ["Email", "Chat", "Web_Form", "Phone"]
    priorities = ["Low", "Medium", "High", "Critical"]

    cat_raw = rng.choice(categories, size=n_rows, p=[0.14, 0.08, 0.05, 0.33, 0.16, 0.14, 0.10])
    mod = rng.choice(modules, size=n_rows, p=[0.24, 0.20, 0.20, 0.22, 0.14])
    plat = rng.choice(platforms, size=n_rows, p=[0.32, 0.28, 0.40])
    chan = rng.choice(channels, size=n_rows, p=[0.30, 0.32, 0.25, 0.13])
    prio = rng.choice(priorities, size=n_rows, p=[0.35, 0.38, 0.19, 0.08])

    # Skewed first response time (minutes), with occasional extreme delays
    resp_mins = rng.lognormal(mean=3.3, sigma=1.1, size=n_rows)
    outlier_mask = rng.random(n_rows) < 0.03
    resp_mins[outlier_mask] *= rng.uniform(5.0, 12.0, size=outlier_mask.sum())

    # Inject realistic missing first-response timestamps (~6%)
    missing_resp = rng.random(n_rows) < 0.06
    first_response_at = []
    for c_time, mins, is_miss in zip(created_at, resp_mins, missing_resp):
        if is_miss:
            first_response_at.append(pd.NaT)
        else:
            first_response_at.append(c_time + pd.Timedelta(minutes=float(mins)))

    # Plant defect/escalation patterns (e.g., iOS + Checkout + slow response)
    norm_cat = pd.Series(cat_raw).str.strip().str.lower()
    risk_score = (
        -2.2
        + 0.9 * (prio == "High").astype(float)
        + 1.6 * (prio == "Critical").astype(float)
        + 0.8 * ((plat == "iOS") & (mod == "Checkout")).astype(float)
        + 0.7 * (resp_mins > 120).astype(float)
        + 0.5 * ((norm_cat == "billing") & (chan == "Chat")).astype(float)
    )
    prob_escalated = 1.0 / (1.0 + np.exp(-risk_score))
    is_escalated = (rng.random(n_rows) < prob_escalated).astype(int)

    df = pd.DataFrame({
        "ticket_id": [f"TCK-{10000 + i}" for i in range(n_rows)],
        "created_at": created_at,
        "first_response_at": first_response_at,
        "category": cat_raw,
        "product_module": mod,
        "platform": plat,
        "channel": chan,
        "priority": prio,
        "is_escalated": is_escalated,
    })

    # Inject ~1% duplicate ticket rows to practice deduplication
    dup_rows = df.sample(n=max(1, n_rows // 100), random_state=seed)
    df = pd.concat([df, dup_rows], ignore_index=True).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    out_path = Path("data/raw/support_tickets_raw.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dataset = generate_tickets()
    dataset.to_csv(out_path, index=False)
    print(f"Saved {len(dataset)} rows to {out_path}")