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

# Load the dataset
df_metrics = pd.read_csv("data/Movies_metrics.csv")


########
from src.models import Movie


# Check if a movie in the dataset is a "hit"
# Function to find a movie by title
def find_movie(title, data):
    match = data[data["title"].str.lower() == title.lower()]
    return match if not match.empty else None

#
print("\n🎬 Welcome! Check if a movie is a hit!")
print("Type a movie title to check it, or 'exit' to quit.\n")

# Initialize control variable
is_found = False

# STEP 5: Loop until a valid movie title is found or user quits
while not is_found:
    
    # Ask the user for a movie title
    user_input = input("Enter a movie title: ").strip()
    
    # Allow exit
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    
    # STEP 6: Search for the movie in the dataset
    match = find_movie(user_input, df_metrics)
    
    # STEP 7: Provide feedback if not found
    if match is None:
        print("❌ This movie is not in the dataset.")

        # Chiedi se vuole inserire i dati a mano
        choice = input("Do you want to enter budget, income, and rating manually? (yes/no): ").strip().lower()
        if choice != "yes":
            print("Try another title.")
            continue

        # Helper per numeri (accetta 1,234,567 o $1,234 ecc.)
        def ask_float(prompt):
            while True:
                raw = input(prompt).strip()
                try:
                    val = float(raw.replace("$", "").replace(",", ""))
                    return val
                except ValueError:
                    print("Please enter a valid number (e.g., 100000000).")

        budget = ask_float("Budget (USD): ")
        income = ask_float("Income (USD): ")
        # rating vincolato a 0–10
        while True:
            try:
                rating = float(input("Rating (0-10): ").strip())
                if 0 <= rating <= 10:
                    break
                else:
                    print("Rating must be between 0 and 10.")
            except ValueError:
                print("Please enter a valid number.")

        # Crea il Movie “manuale” e mostra il risultato
        movie = Movie(title=user_input, budget=budget, income=income, rating=rating)
        print(f"\n✅ Custom movie: {movie.title}")
        movie.describe()
        print("🔥 Yes! This movie is a HIT!" if movie.is_hit() else "💤 Not quite a hit...")

        is_found = True
        continue
    
    # STEP 8: If found, create Movie object and show info
    row = match.iloc[0]
    movie = Movie.from_row(row)
    
    print(f"\n✅ Found: {movie.title}")
    movie.describe()
    
    # STEP 9: Check if it’s a hit
    if movie.is_hit():
        feedback = "🔥 Yes! This movie is a HIT!"
    else:
        feedback = "💤 Not quite a hit..."
    
    print(feedback)
    
    # End loop
    is_found = True

print("\n[info] Interactive loop finished. Starting plots...")

########## Plots
from src.models import MoviePlotter

# Initialize the plotter
plotter = MoviePlotter(df_metrics)

# 1. Distributions
plotter.dist("rating")
plotter.dist("roi")
plotter.dist("profit")

# 2. Economic relationship
plotter.scatter("budget_num", "income_num")

# 3. Genre analysis
plotter.box_by_genre("roi")
plotter.box_by_genre("rating")

# 4. Correlations
plotter.corr_heatmap()

# 5. Trends over time
plotter.line_by_year("roi")
plotter.line_by_year("rating")



