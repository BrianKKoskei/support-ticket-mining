from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def build_statistical_summary(df: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Exploratory Data Analysis Summary")
    lines.append(f"- **Total cleaned rows:** {len(df)}")
    lines.append(f"- **Overall escalation rate (`is_escalated`):** {df['is_escalated'].mean():.2%}")
    lines.append(f"- **Missing first-response rate (`is_missing_response`):** {df['is_missing_response'].mean():.2%}")

    # 1. Missing values & data types
    lines.append("\n## 1. Missing Values & Data Types")
    null_counts = df.isna().sum()
    for col in df.columns:
        lines.append(f"- `{col}` ({df[col].dtype}): {int(null_counts[col])} nulls")

    # 2. Numeric & engineered feature diagnostics (mean vs. median/IQR/skew)
    lines.append("\n## 2. Numeric & Engineered Feature Diagnostics")
    for col in ["response_time_mins", "hour_created", "is_missing_response", "is_escalated"]:
        s = df[col]
        q25, q50, q75 = s.quantile([0.25, 0.50, 0.75])
        lines.append(
            f"- `{col}`: mean={s.mean():.2f}, median={q50:.2f}, IQR={q75 - q25:.2f} "
            f"[{q25:.2f}, {q75:.2f}], skew={s.skew():.2f}, min={s.min():.2f}, max={s.max():.2f}"
        )

    # 3. Escalation rates across single dimensions
    lines.append("\n## 3. Escalation Rate by Dimension")
    dims = ["priority", "category", "product_module", "platform", "channel", "day_of_week", "is_missing_response"]
    for col in dims:
        rates = df.groupby(col)["is_escalated"].agg(["count", "mean"]).sort_values("mean", ascending=False)
        formatted = ", ".join([f"{idx}: {row['mean']:.1%} (n={int(row['count'])})" for idx, row in rates.iterrows()])
        lines.append(f"- **{col}:** {formatted}")

    # 4. Top Platform x Product Module escalation slices
    lines.append("\n## 4. Highest-Escalation Slices (Platform x Product Module)")
    pm_rates = (
        df.groupby(["platform", "product_module"])["is_escalated"]
        .agg(["count", "mean"])
        .sort_values("mean", ascending=False)
        .head(6)
    )
    for (plat, mod), row in pm_rates.iterrows():
        lines.append(f"- `{plat}` + `{mod}`: **{row['mean']:.1%}** escalated (n={int(row['count'])})")

    # 5. Slow response (>120 min) vs. faster response
    df_tmp = df.copy()
    df_tmp["slow_response_120m"] = (df_tmp["response_time_mins"] > 120).astype(int)
    slow_rates = df_tmp.groupby("slow_response_120m")["is_escalated"].agg(["count", "mean"])
    lines.append("\n## 5. Response Speed vs. Escalation")
    for flag, row in slow_rates.iterrows():
        label = "> 120 mins" if flag == 1 else "<= 120 mins"
        lines.append(f"- Response `{label}`: **{row['mean']:.1%}** escalated (n={int(row['count'])})")

    # 6. Pearson and Spearman correlations with target
    num_cols = ["response_time_mins", "hour_created", "is_missing_response", "is_escalated"]
    pearson_corr = df[num_cols].corr(method="pearson")["is_escalated"].drop("is_escalated")
    spearman_corr = df[num_cols].corr(method="spearman")["is_escalated"].drop("is_escalated")
    lines.append("\n## 6. Correlation with `is_escalated`")
    for col in num_cols:
        if col == "is_escalated":
            continue
        lines.append(f"- `{col}`: Pearson r={pearson_corr[col]:+.3f}, Spearman rho={spearman_corr[col]:+.3f}")

    return "\n".join(lines) + "\n"


def generate_plots(df: pd.DataFrame, out_dir: Path) -> None:
    sns.set_theme(style="whitegrid")

    # Plot 1: Ticket counts by Category and Priority
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    cat_order = df["category"].value_counts().index
    sns.countplot(data=df, y="category", order=cat_order, ax=axes[0], palette="viridis")
    axes[0].set_title("Tickets by Category")
    axes[0].set_xlabel("Count")
    axes[0].set_ylabel("Category")

    prio_order = ["Low", "Medium", "High", "Critical"]
    sns.countplot(data=df, x="priority", order=prio_order, ax=axes[1], palette="magma")
    axes[1].set_title("Tickets by Priority")
    axes[1].set_xlabel("Priority")
    axes[1].set_ylabel("Count")

    plt.tight_layout()
    fig.savefig(out_dir / "eda_counts_category_priority.png", dpi=300)
    plt.close(fig)

    # Plot 2: First response time distribution (log scale)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(data=df, x="response_time_mins", bins=40, log_scale=True, ax=ax, color="steelblue")
    ax.axvline(120, color="crimson", linestyle="--", label="120-min slow-response threshold")
    ax.set_title("First Response Time Distribution (Log Scale)")
    ax.set_xlabel("Response Time (Minutes, Log Scale)")
    ax.set_ylabel("Ticket Count")
    ax.legend()
    plt.tight_layout()
    fig.savefig(out_dir / "eda_response_time_dist.png", dpi=300)
    plt.close(fig)

    # Plot 3: Escalation rate heatmap by Product Module and Platform
    esc_pivot = (
        df.groupby(["product_module", "platform"])["is_escalated"]
        .mean()
        .unstack()
        .reindex(["Checkout", "Auth", "API", "Dashboard", "Notifications"])
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(esc_pivot, annot=True, fmt=".1%", cmap="YlOrRd", ax=ax)
    ax.set_title("Escalation Rate by Product Module and Platform")
    ax.set_xlabel("Platform")
    ax.set_ylabel("Product Module")
    plt.tight_layout()
    fig.savefig(out_dir / "eda_escalation_heatmap.png", dpi=300)
    plt.close(fig)


def run_eda(data_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path)

    summary_text = build_statistical_summary(df)
    (out_dir / "eda_summary.md").write_text(summary_text, encoding="utf-8")
    generate_plots(df, out_dir)

    print(summary_text)
    print(f"Saved summary and plots to {out_dir}/")


if __name__ == "__main__":
    run_eda(
        data_path=Path("data/processed/support_tickets_clean.csv"),
        out_dir=Path("reports"),
    )