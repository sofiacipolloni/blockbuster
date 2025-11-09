#Class for plots 
import matplotlib.pyplot as plt
import seaborn as sns

class MoviePlotter:
    def __init__(self, df):
        self.df = df
        sns.set_theme(style="whitegrid")

    # Distribution of a single variable
    def dist(self, column, bins=40):
        plt.figure(figsize=(7,5))
        sns.histplot(self.df[column], bins=bins, kde=True)
        plt.title(f"Distribution of {column}")
        plt.show()

    # Scatter plot between two variables
    def scatter(self, x, y):
        plt.figure(figsize=(7,5))
        sns.scatterplot(data=self.df, x=x, y=y)
        plt.title(f"{x} vs {y}")
        plt.show()

    # Boxplot by genre
    def box_by_genre(self, y):
        genre_col = "genre_main" if "genre_main" in self.df.columns else "genre"
        plt.figure(figsize=(10,5))
        sns.boxplot(data=self.df, x=genre_col, y=y)
        plt.xticks(rotation=45)
        plt.title(f"{y} by genre")
        plt.show()

    # Correlation heatmap
    def corr_heatmap(self):
        cols = ["budget_num", "income_num", "profit", "roi", "rating", "runtime_min"]
        cols = [c for c in cols if c in self.df.columns]
        plt.figure(figsize=(8,6))
        sns.heatmap(self.df[cols].corr(), annot=True, cmap="coolwarm", center=0)
        plt.title("Correlation Heatmap")
        plt.show()

    # Line plot over the years
    def line_by_year(self, y):
        data = self.df.groupby("year")[y].mean().reset_index()
        plt.figure(figsize=(9,5))
        sns.lineplot(data=data, x="year", y=y)
        plt.title(f"Average {y} by Year")
        plt.show()

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
        
    @staticmethod
    def from_row(row):
        """
        Create a Movie object directly from a row of the dataframe.
        Looks for column names commonly used in df_metrics.
        """
        return Movie(
            title=row.get("title"),
            budget=row.get("budget_num"),
            income=row.get("income_num"),
            rating=row.get("rating")
        )