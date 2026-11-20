from pathlib import Path
import numpy as np
import pandas as pd


def clean_tickets(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Remove exact duplicate rows
    df = df.drop_duplicates().reset_index(drop=True)

    # 2. Parse timestamps
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["first_response_at"] = pd.to_datetime(df["first_response_at"], errors="coerce")

    # 3. Standardize category strings (trim whitespace + title/clean formatting)
    df["category"] = (
        df["category"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({
            "billing": "Billing",
            "technical": "Technical",
            "account": "Account",
            "shipping": "Shipping",
            "feature_request": "Feature_Request",
        })
        .fillna("Other")
    )

    # 4. Track missing first response before any time calculations
    df["is_missing_response"] = df["first_response_at"].isna().astype(int)

    # 5. Compute first response time in minutes (clip negative/impossible values if any)
    resp_td = df["first_response_at"] - df["created_at"]
    df["response_time_mins"] = resp_td.dt.total_seconds() / 60.0
    df.loc[df["response_time_mins"] < 0, "response_time_mins"] = np.nan

    # Impute missing response_time_mins with median per priority (preserving is_missing_response)
    medians = df.groupby("priority")["response_time_mins"].transform("median")
    df["response_time_mins"] = df["response_time_mins"].fillna(medians).fillna(df["response_time_mins"].median())

    # 6. Extract helpful time features
    df["hour_created"] = df["created_at"].dt.hour
    df["day_of_week"] = df["created_at"].dt.day_name()

    return df


if __name__ == "__main__":
    in_path = Path("data/raw/support_tickets_raw.csv")
    out_path = Path("data/processed/support_tickets_clean.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    raw_df = pd.read_csv(in_path)
    clean_df = clean_tickets(raw_df)
    clean_df.to_csv(out_path, index=False)

    print(f"Raw rows: {len(raw_df)} -> Clean rows: {len(clean_df)}")
    print("Categories:", clean_df["category"].value_counts().to_dict())
    print(f"Saved clean dataset to {out_path}")