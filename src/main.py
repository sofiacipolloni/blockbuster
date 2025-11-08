import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.processing import load_data, clean, save_clean


raw_path  = Path("data/movies.csv")
clean_path = Path("data/movies_clean.csv")

def run(input_path: str = str(raw_path), output_path: str = str(clean_path)) -> pd.DataFrame:
    """Load -> clean -> save -> return cleaned DataFrame."""
    print(f"Loading raw dataset: {input_path}")
    df_raw = load_data(input_path)

    print("Cleaning...")
    df = clean(df_raw)

    print(f"Saving cleaned dataset to: {output_path}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    save_clean(df, output_path)

    print("Done.")
    return df_raw, df


if __name__ == "__main__":
    df_raw, df = run()
    

    
# BEFORE CLEANING 
print("Dataset shape:", df_raw.shape)
print("\nColumns:", list(df_raw.columns))
print("\nMissing values per column:\n", df_raw.isnull().sum())
print("\nDuplicate rows:", df_raw.duplicated().sum())
print("\nDataset information:", df_raw.info())


# DEFINITION OF METRICS 
# Financial metrics - PROFIT and ROI
df["profit"] = df["income_num"] - df["budget_num"]
df["roi"] = df["income_num"] / df["budget_num"]  # >1 --> profitable; can be NaN/inf if budget is 0/NaN

# 4) "Hit": top 25% by both rating and ROI
rating_cut = df["rating"].quantile(0.75)
roi_cut = df["roi"].quantile(0.75)
df["hit"] = (df["rating"] >= rating_cut) & (df["roi"] >= roi_cut)

# AFTER CLEANING
summary = {
    "Rows": df.shape[0],
    "Columns": df.shape[1],
    "Missing budgets": df["budget_num"].isna().sum(),
    "Missing incomes": df["income_num"].isna().sum(),
    "Mean Rating": round(df["rating"].mean(skipna=True), 2),
    "Median ROI": round(df["roi"].median(skipna=True), 2),
    "Mean Profit ($M)": round(df["profit"].mean(skipna=True) / 1e6, 2),
    "Correlation Budget - Income": round(df[["budget_num", "income_num"]].corr().iloc[0,1], 2),
    "Correlation Runtime - Rating": round(df[["runtime_min", "rating"]].corr().iloc[0,1], 2) if "runtime_min" in df else None,
    "Hit threshold (rating)": round(rating_cut, 2),
    "Hit threshold (ROI)": round(roi_cut, 2),
    "Share of Hits (%)": round(100 * df["hit"].mean(), 1),
}

print("\n Summary:")
for k, v in summary.items():
    print(f"{k}: {v}")

#Save the new metrics in a new cleaned dataset 
df.to_csv("data/Movies_metrics.csv", index=False)


