#MAIN
import pandas as pd
import sys
from pathlib import Path
from matplotlib import pyplot as plt

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import functions and classes
from src.processing import run, find_movie, ask_float, add_metrics
from src.models import Movie, MoviePlotter


raw_path  = Path("data/movies.csv")
clean_path = Path("data/movies_clean.csv")

df_raw = None
df = None
if __name__ == "__main__":
    df_raw, df = run()


# Definition on financial metrics
df = add_metrics(df)

# Summary of main statistics after cleaning procedure
summary = {
    "Rows": df.shape[0],
    "Columns": df.shape[1],
    "Mean Rating": round(df["rating"].mean(skipna=True), 2),
    "Median ROI": round(df["roi"].median(skipna=True), 2),
    "Mean Profit ($M)": round(df["profit"].mean(skipna=True) / 1e6, 2),
    "Share of Hits (%)": round(100 * df["hit"].mean(), 1),
    "Hit threshold (Rating)": round(df["rating"].quantile(0.75), 2),
    "Hit threshold (ROI)": round(df["roi"].quantile(0.75), 2),
    "Hit threshold (Profit $M)": round(df["profit"].quantile(0.75) / 1e6, 2)
}

print("\n Cleaned dataset summary:")
for k, v in summary.items():
    print(f"{k}: {v}")

#Save new metrics in a new cleaned dataset 
df.to_csv("data/Movies_metrics.csv", index=False)

# Load the dataset
df_metrics = pd.read_csv("data/Movies_metrics.csv")

########
# Check if a movie in the dataset is a "hit"
print("\n🎬 Welcome! Check if a movie is a hit!")
print("Type a movie title to check it, or 'exit' to quit.\n")

plotter = MoviePlotter(df_metrics) # initialize the plotter

is_found = False # initialize control variable

# Loop until a valid movie title is found or ask whether to write another title or quit
while not is_found:
    
    user_input = input("Enter a movie title: ").strip() # ask the user for a movie title
    
    if user_input.lower() == "exit": # allow exit
        print("Goodbye!")
        break
    
    match = find_movie(user_input, df_metrics) # search for the movie in the dataset
    
    if match is None: # if not found
        print("❌ This movie is not in the dataset.")

        # Ask to insert data manually
        choice = input("Do you want to enter budget, income, and rating manually? (yes/no): ").strip().lower()
        if choice != "yes":
            print("Try another title.")
            continue

        budget = ask_float("Budget (USD): ")
        income = ask_float("Income (USD): ")
        
        while True: # rating 0–10
            try:
                rating = float(input("Rating (0-10): ").strip())
                if 0 <= rating <= 10:
                    break
                else:
                    print("Rating must be between 0 and 10")
            except ValueError:
                print("Please enter a valid number")

        movie = Movie(title=user_input, budget=budget, income=income, rating=rating) # create the movie
        print(f"\n✅ Movie: {movie.title}")
        movie.describe()
            
        if movie.is_hit(): # check if it’s a hit
            feedback = "Yes! This movie is a HIT!"
        else:
            feedback = "This movie is not quite a HIT..."
        
        print(feedback)

        # graphic summary
        plotter.plot_movie_summary(movie, show=True, block=False)
        plt.pause(0.1)
        
        is_found = True
        continue
    
    row = match.iloc[0] # if found
    movie = Movie.from_row(row) # Movie object 
    print(f"\n✅ Found: {movie.title}")
    movie.describe()
    
    if movie.is_hit(): # check if it’s a hit
        feedback = "Yes! This movie is a HIT!"
    else:
        feedback = "This movie is not quite a HIT..."
    
    print(feedback)
    
    # graphic summary
    plotter.plot_movie_summary(movie, show=True, block=False)
    plt.pause(0.1) 
    
    is_found = True # end loop

print("\n[info] Interactive loop finished. Starting plots...")


########## Plots
# 1. Distributions
plotter.dist("rating")
plotter.dist("roi")
plotter.dist("profit") #?

# 2. Economic relationship
plotter.scatter("budget_num", "income_num") #?

# 3. Genre analysis: single + comparison
plotter.box_by_genre("roi")
plotter.box_by_genre("rating")
plotter.box_by_genre("runtime_min") #?

plotter.roi_vs_rating()

# 4. Correlations
plotter.corr_heatmap()

# 5. Trends over time
plotter.hit_trend_over_time()

#6. Film duration
plotter.hit_by_runtime_bucket()
