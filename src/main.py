import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.processing import load_data, clean, save_clean, to_num


def run(input_path: str = "data/movies.csv",
        output_path: str = "data/movies_clean.csv") -> None:
    print(f"Loading: {input_path}")
    df = load_data(input_path)

    print("Cleaning...")
    df = clean(df)

    print(f"Saving: {output_path}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    save_clean(df, output_path)

    print("Done.")

if __name__ == "__main__":
    run()
    
#LOAD DATA (auto) 
DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "movies.csv"
CLEAN_PATH = DATA_DIR / "movies_clean.csv"

if CLEAN_PATH.exists():
    print(f"Found cleaned dataset. Loading: {CLEAN_PATH}")
    df = pd.read_csv(CLEAN_PATH)
else:
    print("No cleaned dataset found. Loading raw dataset and cleaning")
    df = clean(load_data(str(RAW_PATH)))
    save_clean(df, str(CLEAN_PATH))
    print(f"Cleaned and saved to {CLEAN_PATH}")
    
    
# Display the dataset shape (rows, columns)
print("Dataset shape:", df.shape)
# Show the column names
print("\nColumns:")
print(df.columns)
# Display info about data types and missing values
print("\nDataset information:")
df.info()

print("\nFirst rows of the dataset:")
print(df.head())

print("\n Missing values per column:")
print(df.isnull().sum())

print("\n Duplicate rows:")
print(df.duplicated().sum())


# DEFINITION OF METRICS 
#1) Budget, income
# #Transforming objects into numeric values (create new columns)
if df["budget"].dtype == "object":
    df["budget_num"] = df["budget"].apply(to_num)
else:
    df["budget_num"] = df["budget"].astype(float)

if df["income"].dtype == "object":
    df["income_num"] = df["income"].apply(to_num)
else:
    df["income_num"] = df["income"].astype(float)
    
# 2) Financial metrics - PROFIT and ROI
df["profit"] = df["income_num"] - df["budget_num"]
df["roi"] = df["income_num"] / df["budget_num"]  # >1 --> profitable; can be NaN/inf if budget is 0/NaN

#3) Audience/Critic success --- 'rating' column from dataset
# could add normalized version (0-1 scale) if needed later

# 4) Define a "hit": top 25% by BOTH rating and ROI
rating_cut = df["rating"].quantile(0.75)
roi_cut = df["roi"].quantile(0.75)
df["hit"] = (df["rating"] >= rating_cut) & (df["roi"] >= roi_cut)

# 5) Quick sanity checks
print("Rows:", len(df))
print("Missing budgets:", df['budget_num'].isna().sum())
print("Missing incomes:", df['income_num'].isna().sum())
print("Median ROI:", round(df['roi'].median(skipna=True), 3))
print(f"Hit thresholds → rating ≥ {round(rating_cut,2)} and ROI ≥ {round(roi_cut,2)}")
print("Share of hits:", round(100*df['hit'].mean(), 1), "%")

summary = {
    "Rows": len(df),
    "Mean Rating": round(df["rating"].mean(skipna=True), 2),
    "Median ROI": round(df["roi"].median(skipna=True), 2),
    "Mean Profit ($M)": round(df["profit"].mean(skipna=True) / 1e6, 2),
    "Correlation Budget - Income": round(df[["budget_num","income_num"]].corr().iloc[0,1], 2),
    "Correlation Runtime - Rating": round(df[["runtime_min","rating"]].corr().iloc[0,1], 2) if "runtime_min" in df else None,
    "Hit threshold (rating)": round(rating_cut, 2),
    "Hit threshold (ROI)": round(roi_cut, 2),
    "Share of Hits (%)": round(100 * df["hit"].mean(), 1),
}

pd.Series(summary)

#Save the new metrics in a new cleaned dataset 
df.to_csv("data/Movies_metrics.csv", index=False)


