
import pandas as pd
import re
import numpy as np

#Loading the dataset
def load_data(path: str = "data/movies.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        print(f"Dataset loaded successfully: {path}")
        print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        print(df.shape)
        return df

    except FileNotFoundError:
        print("Error: File not found. Check the path and file name.")
    except pd.errors.ParserError:
        print("Error: There was a problem reading the CSV file.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return pd.DataFrame() 

if __name__ == "__main__":
    df = load_data("data/movies.csv")
    print("\n Preview")
    print(df.head())



# Cleaning the dataset
_months_map = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

#Clean function
def clean(df: pd.DataFrame) -> pd.DataFrame:

    d = df.copy()
    
    d.columns = (
        d.columns
         .str.strip()
         .str.lower()
         .str.replace(r"\s+", "_", regex=True)
         .str.replace(r"[^\w_]", "", regex=True)
    )
    
    if "runtime" in d:
        d["runtime_min"] = pd.to_numeric(
            d["runtime"].astype(str).str.extract(r"(\d+)")[0],
            errors="coerce"
        )

    if "votes" in d:
        d["votes_num"] = pd.to_numeric(
            d["votes"].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )
        
    if "gross" in d:
        d["gross_usd"] = pd.to_numeric(
            d["gross"].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce"
        )
    
    if "rating" in d:
        d["rating"] = pd.to_numeric(d["rating"], errors="coerce")

    if "month" in d:
        d["month_num"] = (
            d["month"].astype(str).str.lower().str[:3].map(_months_map)
        ).astype("Int64")
    
    if "year" in d:
        d["year"] = pd.to_numeric(d["year"], errors="coerce")
        d["decade"] = (d["year"] // 10 * 10).astype("Int64")
    
    if {"title", "year"}.issubset(d.columns):
        d = d.drop_duplicates(subset=["title", "year"])

    return d


def save_clean(df, path="data/movies_clean.csv"):
    df.to_csv(path, index=False)
    print(f"Saved cleaned data to {path}")



# Function which checks if values are numeric
def to_num(x):
    """
    Turn values like '120,000,000' or '$120M' into floats.
    - removes commas
    - supports 'K' (thousand) and 'M' (million) suffixes
    - keeps digits, dot, and minus only
    """
    if pd.isna(x):
        return np.nan
    s = str(x).replace(",", "").strip()
    mult = 1.0
    if s.lower().endswith("m"):
        mult, s = 1e6, s[:-1]
    elif s.lower().endswith("k"):
        mult, s = 1e3, s[:-1]
    # keep only digits, dot, minus
    s = "".join(ch for ch in s if ch.isdigit() or ch in ".-")
    if s in {"", ".", "-"}:
        return np.nan
    return float(s) * mult