#FUNCTIONS
import pandas as pd
import re
from pathlib import Path



#Loading the raw dataset
def load_data(path: str = "data/movies.csv") -> pd.DataFrame:
    """Loads the raw movie dataset from a CSV file.
    Args:
        path (str): Path to the CSV file to be loaded.
    Returns:
        pd.DataFrame: The loaded dataset, or an empty DataFrame if an error occurs.
    """
    try:
        df = pd.read_csv(path)
        print(f"Dataset loaded successfully: {path}")
        print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
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
    """Maps a raw genre string to a canonical, cleaned genre list.
    The function:
        - normalizes separators (`,` `|` `/` `;`)
        - searches for known genre keywords
        - returns the matched canonical genres as a comma-separated string.
    Args:
        raw (str): Original genre string from the dataset.
    Returns:
        str | None: Canonical genre string or None if no match.
    """
    if pd.isna(raw):
        return None
    txt = str(raw).lower()
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

# Return the first canonical genre as main
def _pick_main(gen_agg: str | None) -> str | None:
    """Selects the main genre from an aggregated genre string.
    The function takes a string like "Action, Comedy" and returns only
    the first canonical genre (e.g., "Action").
    Args:
        gen_agg (str | None): Aggregated canonical genres.
    Returns:
        str | None: Main genre (first in the list) or None if missing.
    """
    if not gen_agg:
        return None
    return gen_agg.split(",")[0].strip()


# "clean" function
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and enriches the raw movie dataset.
    The function:
        - standardizes column names
        - parses runtime, votes, gross, rating as numeric
        - derives month_num and decade from date information
        - removes duplicated (title, year) pairs
        - converts budget and income to numeric versions
        - normalizes genres and extracts the main genre.
    Args:
        df (pd.DataFrame): Raw input dataframe.
    Returns:
        pd.DataFrame: Cleaned and transformed dataframe.
    """
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
        
    # Convert budget and income to numeric 
    for col in ["budget", "income"]:
        if col in d.columns:
            s = d[col].astype(str).str.strip().replace({"Unknown": pd.NA})
            s = s.str.replace(r"[^\d.]", "", regex=True) 
            d[f"{col}_num"] = pd.to_numeric(s, errors="coerce")


    # Genre aggregation 
    if "genre" in d.columns:
    # Apply both cleaning and main-genre extraction at once
        d["genre_main"] = d["genre"].apply(lambda x: _pick_main(_map_genres_string(x)))

        print("\nSample genres (raw → main):")
        print(d[["genre", "genre_main"]])

        # Number of movies per main genre
        print("\nMovies per main genre:")
        print(d["genre_main"].value_counts(dropna=True).head(20))
        
    return d


# New clean dataset
def save_clean(df, path="data/movies_clean.csv") -> None:
    """Saves a dataframe to disk as a CSV file.
    Args:
        df (pd.DataFrame): Dataframe to save.
        path (str): Output file path.
    """
    df.to_csv(path, index=False)
    print(f"Saved cleaned data to {path}")



#File paths 
raw_path  = Path("data/movies.csv")
clean_path = Path("data/movies_clean.csv")

# "run" function
def run(input_path: str = str(raw_path), output_path: str = str(clean_path)) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Full cleaning pipeline: load raw data, clean it and save the result.
    Args:
        input_path (str): Path to the raw CSV file.
        output_path (str): Path where the cleaned CSV will be saved.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple with (raw_df, cleaned_df).
    """
    print(f"Loading raw dataset: {input_path}")
    df_raw = load_data(input_path)

    print("Cleaning...")
    df = clean(df_raw)

    print(f"Saving cleaned dataset to: {output_path}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    save_clean(df, output_path)

    print("Done.")
    return df_raw, df

#"add_metrics" function to create new metrics
def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Adds financial metrics (profit, ROI, hit flag) to the dataset.
    The hit variable is defined using the 75th percentile of rating and ROI.
    Args:
        df (pd.DataFrame): Cleaned dataframe with numeric budget and income.
    Returns:
        pd.DataFrame: Dataframe with additional metric columns.
    """
    d = df.copy()
    d["profit"] = d["income_num"] - d["budget_num"]
    d["roi"] = (d["income_num"] - d["budget_num"]) / d["budget_num"]

    rating_cut = d["rating"].quantile(0.75)
    roi_cut = d["roi"].quantile(0.75)
    d["hit"] = (d["rating"] >= rating_cut) & (d["roi"] >= roi_cut)

    return d


# "find_movie" function to find a movie by title
def find_movie(title, data) -> pd.DataFrame | None:
    """Searches for a movie by exact title (case-insensitive).
    Args:
        title (str): Movie title to search for.
        data (pd.DataFrame): Dataframe containing a 'title' column.
    Returns:
        pd.DataFrame | None: Matching rows if found, otherwise None.
    """
    match = data[data["title"].str.lower() == title.lower()]
    return match if not match.empty else None


# "ask_float" function to recognize different numeric formats 
def ask_float(prompt) -> float:
    """Asks the user for a numeric input and parses common formats.
    The function:
        - strips spaces
        - removes currency symbols and thousand separators
        - keeps asking until a valid float is entered.
    Args:
        prompt (str): Text to display when asking for input.
    Returns:
        float: Parsed numeric value.
    """
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw.replace("$", "").replace(",", "")) #float conversion
            return val
        except ValueError:
            print("Please enter a valid number")
            

output_dir = Path("outputs/figures")
output_dir.mkdir(parents=True, exist_ok=True)

def save_fig(fig, name: str):
    """Saves a matplotlib figure into the output folder."""
    fig.savefig(output_dir / f"{name}.png", dpi=300, bbox_inches="tight")