import pandas as pd
import numpy as np
import sys
from pathlib import Path
from matplotlib import pyplot as plt

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import functions and classes
from src.processing import run, find_movie, ask_float, add_metrics
from src.models import Movie, MoviePlotter


raw_path  = Path("data/movies.csv")
clean_path = Path("data/movies_clean.csv")


if __name__ == "__main__":
    df_raw, df = run()
    

    
# BEFORE CLEANING 
print("\n Analysis of raw dataset:")
print("Dataset shape:", df_raw.shape)
print("\nColumns:", list(df_raw.columns))
print("\nMissing values per column:\n", df_raw.isnull().sum())
print("\nDuplicate rows:", df_raw.duplicated().sum())
print("\nDataset information:", df_raw.info())


# DEFINITION OF METRICS 
df = add_metrics(df)

# AFTER CLEANING
summary = {
    "9 columns added: numeric runtime, budget and income; month's number and decade; main genre; ROI, profit and HIT (boolean)"
    "\nRows": df.shape[0],
    "Columns": df.shape[1],
    "Missing budgets": df["budget_num"].isna().sum(),
    "Missing incomes": df["income_num"].isna().sum(),
    "Mean Rating": round(df["rating"].mean(skipna=True), 2),
    "Median ROI": round(df["roi"].median(skipna=True), 2),
    "Mean Profit ($M)": round(df["profit"].mean(skipna=True) / 1e6, 2),
    "Correlation Budget - Income": round(df[["budget_num", "income_num"]].corr().iloc[0,1], 2),
    "Correlation Runtime - Rating": round(df[["runtime_min", "rating"]].corr().iloc[0,1], 2) if "runtime_min" in df else None,
    "Hit threshold (rating)": round(df["rating"].quantile(0.75), 2),
    "Hit threshold (ROI)": round(df["roi"].quantile(0.75), 2),
    "Share of Hits (%)": round(100 * df["hit"].mean(), 1),
}

print("\n Summary of cleaned dataset:")
for k, v in summary.items():
    print(f"{k}: {v}")


#Save the new metrics in a new cleaned dataset 
df.to_csv("data/Movies_metrics.csv", index=False)
# Load the dataset
df_metrics = pd.read_csv("data/Movies_metrics.csv")


########
# Check if a movie in the dataset is a "hit"
print("\n🎬 Welcome! Check if a movie is a hit!")
print("Type a movie title to check it, or 'exit' to quit.\n")

# Initialize the plotter
plotter = MoviePlotter(df_metrics)

# Initialize control variable
is_found = False

# Loop until a valid movie title is found or ask wether to write another title or quit
while not is_found:
    
    # Ask the user for a movie title
    user_input = input("Enter a movie title: ").strip()
    
    # Allow exit
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    
    # Search for the movie in the dataset
    match = find_movie(user_input, df_metrics)
    
    # Provide feedback if not found
    if match is None:
        print("❌ This movie is not in the dataset.")

        # Ask to insert data manually
        choice = input("Do you want to enter budget, income, and rating manually? (yes/no): ").strip().lower()
        if choice != "yes":
            print("Try another title.")
            continue

        budget = ask_float("Budget (USD): ")
        income = ask_float("Income (USD): ")
        # rating 0–10
        while True:
            try:
                rating = float(input("Rating (0-10): ").strip())
                if 0 <= rating <= 10:
                    break
                else:
                    print("Rating must be between 0 and 10")
            except ValueError:
                print("Please enter a valid number")

        # Create the movie
        movie = Movie(title=user_input, budget=budget, income=income, rating=rating)
        print(f"\n✅ Movie: {movie.title}")
        movie.describe()
            
        # Check if it’s a hit
        if movie.is_hit():
            feedback = "Yes! This movie is a HIT!"
        else:
            feedback = "This movie is not quite a HIT..."
        
        print(feedback)

        # graphic summary
        plotter.plot_movie_summary(movie, show=True, block=False)
        plt.pause(0.1)
        
        is_found = True
        continue
    
    # If found, create Movie object and show info
    row = match.iloc[0]
    movie = Movie.from_row(row)
    print(f"\n✅ Found: {movie.title}")
    movie.describe()
    
    # Check if it’s a hit
    if movie.is_hit():
        feedback = "Yes! This movie is a HIT!"
    else:
        feedback = "This movie is not quite a HIT..."
    
    print(feedback)
    
    # graphic summary
    plotter.plot_movie_summary(movie, show=True, block=False)
    plt.pause(0.1) 
    
    # End loop
    is_found = True

print("\n[info] Interactive loop finished. Starting plots...")



########## Plots

# 1. Distributions
plotter.dist("rating")
plotter.dist("roi")
plotter.dist("profit")

# 2. Economic relationship
plotter.scatter("budget_num", "income_num")

# 3. Genre analysis: single + comparison
plotter.box_by_genre("roi")
plotter.box_by_genre("rating")
plotter.box_by_genre("runtime_min")

plotter.roi_vs_rating()

# 4. Correlations
plotter.corr_heatmap()

# 5. Trends over time
#line by year for ROI and rating excluded from the main (HIT covers both)
plotter.hit_trend_over_time()

#6. Film duration
plotter.hit_by_runtime_bucket()
