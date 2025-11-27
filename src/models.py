#CLASS OBJECTS
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

#Class for plots 
class MoviePlotter:
    def __init__(self, df):
        self.df = df

        # Theme
        sns.set_theme(style="whitegrid", context="talk")

        # Palette (green)
        self.palette = {
            "main": "#2E8B57",   
            "light": "#6FBF73",  
            "dark": "#1B5E20",   
            "aqua": "#80CBC4",   
            "neutral": "#E6EAE9" 
        }

        plt.rcParams.update({
            "axes.edgecolor": "#444444",
            "axes.labelcolor": "#333333",
            "xtick.color": "#444444",
            "ytick.color": "#444444",
            "axes.facecolor": "#fafafa",
            "figure.facecolor": "#ffffff",
            "grid.alpha": 0.3,
            "grid.color": "#cccccc",
            "font.size": 12,
            "axes.titlesize": 14,
        })
    
    #Palette for categorical series
    def _cat_palette(self, series, cmap="crest"):
        levels = list(pd.Series(series).dropna().unique())
        colors = sns.color_palette(cmap, n_colors=len(levels))
        pal = dict(zip(levels, colors))
        return pal, levels
 
    # Trimming data to remove extreme outliers (not in 0–99th percentile)
    def trimmed(self, column):
        data = self.df[column].dropna()
        lower = data.quantile(0.01)
        upper = data.quantile(0.99)
        return data[(data >= lower) & (data <= upper)]

    # 1. Distribution of a single variable
    def dist(self, column, show=True):
        filtered = self.trimmed(column)
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.histplot(filtered, kde=True, bins=40, color=self.palette["light"], ax=ax)
        ax.set_title(f"Distribution of {column} (trimmed 1–99%)")
        ax.set_xlabel(column)
        ax.set_ylabel("Count")
        if show:
            plt.show()
        return fig, ax

    # Scatter plot between 2 variables
    def scatter(self, x, y, show=True):
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.scatterplot(data=self.df, x=x, y=y, color=self.palette["main"], ax=ax)
        ax.set_title(f"{x} vs {y}")
        if show:
            plt.show()
        return fig, ax

    # Boxplot by genre 
    def box_by_genre(self, column, genre_col="genre_main", show=True):
        if genre_col not in self.df.columns:
            print("Column 'genre_main' not found.")
            return

        # Drop missing values + trimming 
        trimmed_df = self.df[[genre_col, column]].dropna().copy() 
        filtered_values = self.trimmed(column)
        trimmed_df = trimmed_df[trimmed_df[column].isin(filtered_values)]

        #colors
        levels = list(trimmed_df[genre_col].value_counts().index)  
        pal, _ = self._cat_palette(levels, cmap="crest")           
        colors = [pal[g] for g in levels] 
          
        #Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(data=trimmed_df, x=genre_col, y=column,
                    order=levels, palette=colors, showfliers=False, ax=ax)

        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_title(f"{column} by Genre (trimmed 1–99%)")
        if show:
            plt.show()
        return fig, ax
    
    # ROI vs Rating map (by genre)
    def roi_vs_rating(self, genre_col="genre_main", show=True):

        # Check required columns
        for c in ["roi", "rating", genre_col]:
            if c not in self.df.columns:
                print(f"Column '{c}' not found.")
                return

        # Drop missing values + trim ROI and Rating
        trimmed_df = self.df[[genre_col, "roi", "rating"]].dropna().copy()
        trimmed_df = trimmed_df[trimmed_df["roi"].isin(self.trimmed("roi"))]
        trimmed_df = trimmed_df[trimmed_df["rating"].isin(self.trimmed("rating"))]

        # Plot
        pal, _ = self._cat_palette(trimmed_df[genre_col], cmap="crest")

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(data=trimmed_df, x="rating", y="roi",
                        hue=genre_col, palette=pal,
                        alpha=0.7, s=55, edgecolor="white", linewidth=0.4, ax=ax)

        roi_low = trimmed_df["roi"].quantile(0.01)
        roi_high = trimmed_df["roi"].quantile(0.99)
        ax.set_ylim(roi_low, roi_high)
        ax.set_title("ROI vs Rating (trimmed 1–99%)")
        ax.set_xlabel("Rating")
        ax.set_ylabel("ROI")
        ax.legend(title="Genre", bbox_to_anchor=(1.02, 1), loc="upper left")

        if show:
            plt.show()
        return fig, ax



    # Correlation heatmap
    def corr_heatmap(self, show=True):
        cols = ["budget_num", "income_num", "profit", "roi", "rating", "runtime_min"]
        cols = [c for c in cols if c in self.df.columns]
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(self.df[cols].corr(), annot=True, cmap="YlGnBu", center=0, ax=ax)
        ax.set_title("Correlation Heatmap")
        if show:
            plt.show()
        return fig, ax

    # Line plot over the years 
    def line_by_year(self, y):
        data = self.df.groupby("year")[y].mean().reset_index()
        plt.figure(figsize=(9,5))
        sns.lineplot(data=data, x="year", y=y, color=self.palette["dark"])
        plt.title(f"Average {y} by Year")
        plt.show()
    
    # Share of hits per year
    def hit_trend_over_time(self, year_col="year", hit_col="hit", show=True):
    
        if year_col not in self.df.columns or hit_col not in self.df.columns:
            print("Columns not found.")
            return

        d = self.df[[year_col, hit_col]].dropna()
        
        # Compute yearly share of hits
        yearly = d.groupby(year_col)[hit_col].mean().reset_index()
        yearly[hit_col] = yearly[hit_col] * 100  # convert to %

        #Plot
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.lineplot(data=yearly, x=year_col, y=hit_col,
                     marker="o", linewidth=2.5,
                     color=self.palette["main"],
                     markerfacecolor=self.palette["light"],
                     markeredgecolor=self.palette["dark"],
                     alpha=0.9, ax=ax)

        ax.set_title("Share of Hits Over Time")
        ax.set_xlabel("Year")
        ax.set_ylabel("Share of Hits (%)")
        ax.grid(True, alpha=0.3)
        
        #years as integers 
        years = yearly[year_col].astype(int).unique()
        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation=45)
    
        if show:
            plt.show()
        return fig, ax
    
    # Share of hits per runtime
    def hit_by_runtime_bucket(self, runtime_col: str = "runtime_min", hit_col: str = "hit", show=True):

        if runtime_col not in self.df.columns or hit_col not in self.df.columns:
            print("Columns not found.")
            return

        d = self.df[[runtime_col, hit_col]].dropna().copy()
        # Fasce standard cinema; puoi modificare i cut come vuoi
        bins = [0, 90, 110, 130, 150, 1_000]
        labels = ["<90", "90–110", "110–130", "130–150", "≥150"]
        d["runtime_bucket"] = pd.cut(d[runtime_col], bins=bins, labels=labels, right=False)

        share = (
            d.groupby("runtime_bucket")[hit_col]
            .mean().mul(100).reset_index(name="hit_share")
        )

        #Plot
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.barplot(data=share, x="runtime_bucket", y="hit_share",
                    color=self.palette["main"], ax=ax)

        ax.set_title("Share of Hits by Runtime Bucket")
        ax.set_xlabel("Runtime")
        ax.set_ylabel("Share of Hits (%)")
        ax.set_ylim(0, 100)
        ax.grid(True, axis="y", alpha=0.25)
        if show:
            plt.show()
        return fig, ax
   
    # Graphic summary for a single movie
    def plot_movie_summary(self, movie, show: bool = True, block: bool = False):

        rating = float(movie.rating) if movie.rating is not None else 0.0
        roi    = float(movie.roi) if (movie.roi is not None and np.isfinite(movie.roi)) else 0.0
        is_hit = bool(movie.is_hit())

        # Cap ROI
        try:
            roi_cap = float(self.df["roi"].dropna().quantile(0.99))
        except Exception:
            roi_cap = max(1.0, roi)
        xmax_roi = max(roi_cap, roi, 1.0)

        # Palette
        main  = getattr(self, "palette", {}).get("main",  "#2E8B57")
        light = getattr(self, "palette", {}).get("light", "#6FBF73")
        dark  = getattr(self, "palette", {}).get("dark",  "#1B5E20")

        fig, ax = plt.subplots(figsize=(7, 3.8))

        # Bars
        y_pos   = [0, 1]
        labels  = ["Rating (0–10)", "ROI (×)"]
        ax.barh(y_pos[0], rating, color=light, edgecolor="white", height=0.35)
        ax.barh(y_pos[1], min(roi, xmax_roi), color=main, edgecolor="white", height=0.35)

        # Order: ROI below, rating above
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()

        ax2 = ax.twiny()
        ax2.set_xlim(0, 10)
        ax2.set_xlabel("Rating (0–10)")
        ax.set_xlim(0, xmax_roi)
        ax.set_xlabel("ROI (×, ≤99%)")

        ax.xaxis.set_label_position('bottom')
        ax.xaxis.tick_bottom()
        ax2.xaxis.set_label_position('top')
        ax2.xaxis.tick_top()

        # Title
        badge = "HIT!" if is_hit else "Not a HIT..."
        title_color = "#0F6C13" if is_hit else "#B31111"
        ax.set_title(f"{movie.title}: {badge}",
                    fontstyle="italic", fontweight="bold",
                    fontsize=20, color=title_color, pad=25)

        # Labels on bars
        ax.text(min(rating, 9.8) + 0.15, y_pos[0], f"{rating:.1f}",
                va="center", ha="left", fontsize=10, color="#333333")
        ax.text(min(roi, xmax_roi)*1.02 if roi <= xmax_roi*0.95 else xmax_roi*0.98,
                y_pos[1], f"{roi:.2f}×",
                va="center", ha="right", fontsize=10, color="#333333")

        # 
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
            ax2.spines[spine].set_visible(False)
        ax.grid(True, axis="x", alpha=0.25)
        plt.tight_layout()
        if show:
            plt.show(block=block)   #does not block the code when block=F

        return fig, (ax, ax2)




# Class for analysis of a single movie
class Movie:
    def __init__(self, title, budget, income, rating):
        self.title = title
        self.budget = budget
        self.income = income
        self.rating = rating
        self.profit = income - budget
        self.roi = income / budget if budget > 0 else None

    def is_hit(self):
        return self.roi and self.roi > 1 and self.rating > 7

    def describe(self):
        print(f"🎬 {self.title} → ROI: {self.roi:.2f}, Rating: {self.rating}")
        
    # Create a Movie object directly from a row of the dataframe
    @staticmethod #method belongs to the class, not to a particular object
    def from_row(row):
        return Movie(
            title=row.get("title"),
            budget=row.get("budget_num"),
            income=row.get("income_num"),
            rating=row.get("rating")
        )