"""Phase 6 EDA / data validation checkpoint.

Reads data/processed/foods.csv and produces, under
notebooks/phase_06_eda/:
  - distributions_<column>.png  (histogram + boxplot) for each of
    fiber_g, fat_g, protein_g, carbs_g, sugar_g, GI
  - correlation_matrix.png      (heatmap across all numeric columns)
  - outlier_report.md           (IQR-based outlier flags + zero-variance check)

This is a human judgment gate, not a pass/fail test: it does not decide
whether the data is "clean," it only generates the evidence so a human
can decide. GI/GL are properties of the FOOD, not of a person eating it.

Run directly (`python notebooks/phase_06_eda.py`) or import and call main().
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
FOODS_JSON = REPO_ROOT / "data" / "processed" / "foods.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "phase_06_eda"

DISTRIBUTION_COLUMNS = ["fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g", "GI"]
NUMERIC_COLUMNS = ["fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g", "GI", "GL"]

# 6 South Asian mixed-meal dishes (documented in data/data_dictionary.md,
# "Documented GI/GL exceptions") have GI=0/GL=0 by first-principles reasoning
# rather than lab measurement -- they are not carbohydrate-containing foods
# in Atkinson's sense, so 0 is the correct value, not a data error. Flagged
# here so a reviewer doesn't mistake them for miscoded outliers.
GI_ZERO_EXCEPTION_DISHES = {
    "Butter chicken",
    "Tandoori chicken",
    "Chicken tikka masala",
    "Chicken curry (generic)",
    "Butter paneer (paneer makhani)",
    "Palak paneer",
}

# IQR (Tukey's fences), not z-score: with n=129 and several nutrient columns
# visibly right-skewed (e.g. sugar_g, fat_g -- a handful of honey/syrup and
# fried items pull the mean far above the median), z-score's implicit
# normality assumption would either over-flag the skewed tail or, if the SD
# is inflated by that same tail, under-flag genuine outliers. IQR fences are
# based on order statistics (quartiles), so they don't assume symmetry and
# stay robust with a data set this small.
IQR_MULTIPLIER = 1.5


def load_data():
    with open(FOODS_JSON, encoding="utf-8") as f:
        rows = json.load(f)
    return pd.DataFrame(rows)


def plot_distributions(df, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for col in DISTRIBUTION_COLUMNS:
        fig, (ax_hist, ax_box) = plt.subplots(1, 2, figsize=(9, 4))
        ax_hist.hist(df[col], bins=20, color="#4C72B0", edgecolor="white")
        ax_hist.set_title(f"{col} distribution")
        ax_hist.set_xlabel(col)
        ax_hist.set_ylabel("count")

        ax_box.boxplot(df[col], orientation="vertical")
        ax_box.set_title(f"{col} boxplot")
        ax_box.set_xticklabels([col])

        fig.suptitle(f"{col} (n={df[col].notna().sum()})")
        fig.tight_layout()
        path = output_dir / f"distributions_{col}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        paths.append(path)
    return paths


def plot_correlation_matrix(df, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    corr = df[NUMERIC_COLUMNS].corr()

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(NUMERIC_COLUMNS)))
    ax.set_yticks(range(len(NUMERIC_COLUMNS)))
    ax.set_xticklabels(NUMERIC_COLUMNS, rotation=45, ha="right")
    ax.set_yticklabels(NUMERIC_COLUMNS)
    for i in range(len(NUMERIC_COLUMNS)):
        for j in range(len(NUMERIC_COLUMNS)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Pearson r")
    ax.set_title("Correlation matrix (all numeric columns)")
    fig.tight_layout()
    path = output_dir / "correlation_matrix.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path, corr


def flag_iqr_outliers(df, columns, multiplier=IQR_MULTIPLIER):
    """Returns {column: [(food_name, cuisine, value, lower, upper), ...]}."""
    flags = {}
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        rows = df.loc[mask, ["food_name", "cuisine", col]].sort_values(col)
        flags[col] = {
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower": lower,
            "upper": upper,
            "rows": list(rows.itertuples(index=False, name=None)),
        }
    return flags


def check_zero_variance(df, columns):
    """Fatal-problem check: a feature with zero variance carries no signal
    for modeling, regardless of outliers."""
    return {col: df[col].std() for col in columns if df[col].std() == 0}


def write_outlier_report(df, flags, zero_variance, report_path):
    lines = []
    lines.append("# Phase 6 EDA: outlier-flagging report\n")
    lines.append(f"Source: `data/processed/foods.csv` ({len(df)} rows).\n")
    lines.append(
        "Method: IQR (Tukey's fences), flagged as < Q1 - 1.5*IQR or > Q3 + "
        "1.5*IQR per column. Chosen over z-score because several nutrient "
        "columns are visibly right-skewed at this sample size (n="
        f"{len(df)}), where z-score's normality assumption is a poor fit; "
        "IQR is based on order statistics and stays robust to skew.\n"
    )

    lines.append("## Zero-variance check\n")
    if zero_variance:
        lines.append("**FATAL: the following columns have zero variance:**\n")
        for col, std in zero_variance.items():
            lines.append(f"- `{col}` (std={std})")
    else:
        lines.append("None flagged -- every numeric column has nonzero variance.\n")
    lines.append("")

    lines.append("## Documented GI/GL=0 dishes (not outliers)\n")
    lines.append(
        "The following dishes carry `GI=0`/`GL=0` by documented first-"
        "principles reasoning (near-zero carbohydrate mixed meals excluded "
        "from Atkinson et al.'s lab testing), not measurement or coding "
        "error -- see `data/data_dictionary.md`, \"Documented GI/GL "
        "exceptions\". They will appear as low-end outliers on `GI` below; "
        "that is expected.\n"
    )
    for name in sorted(GI_ZERO_EXCEPTION_DISHES):
        lines.append(f"- {name}")
    lines.append("")

    lines.append("## Per-column IQR outlier flags\n")
    total_flagged = 0
    for col, info in flags.items():
        lines.append(f"### `{col}`\n")
        lines.append(
            f"Q1={info['q1']:.2f}, Q3={info['q3']:.2f}, IQR={info['iqr']:.2f}, "
            f"fence=[{info['lower']:.2f}, {info['upper']:.2f}]\n"
        )
        if not info["rows"]:
            lines.append("No outliers flagged.\n")
        else:
            total_flagged += len(info["rows"])
            lines.append("| food_name | cuisine | value |")
            lines.append("|---|---|---|")
            for food_name, cuisine, value in info["rows"]:
                marker = " (documented GI=0 exception)" if food_name in GI_ZERO_EXCEPTION_DISHES else ""
                lines.append(f"| {food_name}{marker} | {cuisine} | {value:.2f} |")
            lines.append("")

    lines.append("## Summary\n")
    lines.append(f"- Rows: {len(df)}")
    lines.append(f"- Zero-variance columns: {len(zero_variance)}")
    lines.append(f"- Total outlier flags across all columns: {total_flagged}")
    lines.append(
        "- Reminder: this report does not assert the data is clean. It "
        "surfaces candidates for human review per Phase 6's definition of done."
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main():
    df = load_data()
    plot_distributions(df, OUTPUT_DIR)
    _, corr = plot_correlation_matrix(df, OUTPUT_DIR)
    flags = flag_iqr_outliers(df, NUMERIC_COLUMNS)
    zero_variance = check_zero_variance(df, NUMERIC_COLUMNS)
    report_path = write_outlier_report(df, flags, zero_variance, OUTPUT_DIR / "outlier_report.md")
    return report_path


if __name__ == "__main__":
    out = main()
    print(f"Wrote report to {out}")
