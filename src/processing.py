
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


# CLEANING and DATA MANIPULATION

_months_map = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


# Genre mapping
canon_genres = [
    "Action","Adventure","Animation","Comedy","Crime","Drama",
    "Fantasy","Horror","Mystery","Romance","Sci-Fi","Thriller"
]

genre_keywords = {
    "Action":   ["action"],
    "Adventure":["adventure"],
    "Animation":["animation","animated"],
    "Comedy":   ["comedy"],
    "Crime":    ["crime"],
    "Drama":    ["drama"],
    "Fantasy":  ["fantasy"],
    "Horror":   ["horror"],
    "Mystery":  ["mystery"],
    "Romance":  ["romance"],
    "Sci-Fi":   ["sci fi","sci-fi","science fiction"],
    "Thriller": ["thriller"],
}

def _map_genres_string(raw: str) -> str | None:
    """Map 'Adventure, Comedy, Family' -> 'Adventure, Comedy' using CANON_GENRES."""
    import pandas as pd, re
    if pd.isna(raw):
        return None
    txt = str(raw).lower()
    # normalize separators: ',', '|', '/', ';' -> ','
    txt = re.sub(r"[|/;]", ",", txt)
    tokens = [t.strip() for t in txt.split(",") if t.strip()]
    hits = set()
    for tok in tokens:
        for canon, keys in genre_keywords.items():
            if any(k in tok for k in keys):
                hits.add(canon)
    if not hits:
        return None
    ordered = [g for g in canon_genres if g in hits]
    return ", ".join(ordered)

def _pick_main(gen_agg: str | None) -> str | None:
    """Return the first canonical genre as main."""
    if not gen_agg:
        return None
    return gen_agg.split(",")[0].strip()


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
        
    # --- Convert budget and income to numeric ---
    for col in ["budget", "income"]:
        if col in d.columns:
            s = d[col].astype(str).str.strip().replace({"Unknown": pd.NA})
            s = s.str.replace(r"[^\d.]", "", regex=True) 
            d[f"{col}_num"] = pd.to_numeric(s, errors="coerce")


    # --- Genre aggregation ---
    # show what the column is actually called
    print("Genre column present?:", any(c.lower() in ("genre","genres") for c in d.columns))
    genre_col = None
    for c in d.columns:
        if c.lower() in ("genre","genres"):
            genre_col = c
            break

    if "genre" in d.columns:
    # Apply both cleaning and main-genre extraction at once
        d["genre_main"] = d["genre"].apply(lambda x: _pick_main(_map_genres_string(x)))

        print("\nSample genres (raw → main):")
        print(d[["genre", "genre_main"]].head(10))

        # Number of movies per main genre
        print("\nMovies per main genre:")
        print(d["genre_main"].value_counts(dropna=True).head(20))
        
    return d

# Create a new clean dataset
def save_clean(df, path="data/movies_clean.csv"):
    df.to_csv(path, index=False)
    print(f"Saved cleaned data to {path}")

