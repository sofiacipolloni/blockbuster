# 🎬 Blockbuster Movie Analyzer
This project analyzes a large movie dataset to answer a key question:

## **🔥 What makes a movie a HIT — both financially and for audiences**

To explore this, the project includes:
- full data cleaning and metric creation (profit, ROI, hit),
- exploratory visualizations,
- an interactive **Streamlit web application**.

---

# 📁 Project Structure
blockbuster/
│
├── data/
│   ├── movies.csv               ← raw dataset
│   ├── movies_clean.csv         ← cleaned dataset
│   └── Movies_metrics.csv       ← cleaned & enriched dataset (financial metrics)
│
├── src/
│   ├── __init__.py
│   ├── processing.py            ← functions: loading, cleaning, metric creation
│   ├── models.py                ← class objects: Movie, MoviePlotter
│   └── main.py                  ← full analysis pipeline
│
├── app.py                       ← Streamlit web application
├── requirements.txt             ← libraries required to run the project
└── README.md

---

# Goals
The project investigates movie success from **two perspectives**:

### Audience Success  
measured by **rating** (0–10 scale).

### Financial Success  
measured by:
- **profit** = income − budget  
- **ROI - Return on Investments** = (income − budget) / budget

### Hit Definition  
A movie is considered a **HIT** if:
> **rating ≥ 75th percentile AND ROI ≥ 75th percentile**

This allows the anaysis to capture the **top 25%** movies in both quality and profitability.

---
**Project organization**
## 1. Data Source & Libraries
The dataset used in this project comes from **Kaggle**, downloaded as a CSV file and saved locally in the file:
**data/movies.csv**
This is a raw dataset of ~2000 movies, containing all original fields before any cleaning or processing.  

All libraries required to run the project — including `pandas`, `numpy`, `matplotlib`, `seaborn`, `altair`, and `streamlit` — are listed in the file **`requirements.txt`**

# 2. Data Cleaning and new financial metrics
Cleaning and enrichment steps are implemented in **`processing.py`**:

### Standardization of variables and creation of new ones
| Variable        | Description |
|-----------------|-------------|
| `profit`        | income − budget |
| `roi`           | Return on Investment |
| `hit`           | boolean value based on 75th percentiles |
| `runtime_min`   | runtime in minutes |
| `budget_num`    | numeric budget |
| `income_num`    | numeric income |
| `genre_main`    | standardized genre |

The cleaned and enriched dataset has been saved as **Movies_metrics.csv** and used everywhere else.

---

# 3. Exploratory Data Analysis (main.py)
_(it requires class objects from **`models.py`**)_

The analysis includes:
### Post-cleaning summary
- mean rating,
- median ROI,
- mean profit,
- share of hits in the dataset
- hit thresholds.

### Graphic visualizations 
- distributions (rating, profit, ROI with trimming),
- budget vs income scatter,
- boxplots by genre (rating, ROI, runtime),
- ROI vs Rating by genre,
- correlation heatmap,
- hit percentage by year,
- share of hits by runtime bucket.

### Possibility to chech whether if a film (in the dataset or not) is classified as a HIT.

---

# 4. Streamlit Web Application
The web app (**`app.py`**) is organized in 4 different pages:
### 1️⃣ Dataset Overview
- variables listed in 2 columns
- first rows of the dataset displayed
- descriptive statistics for variables of interest.

### 2️⃣ Check a Movie (from the dataset)
- user searches for a movie title
- app displays:
  - rating, budget, income, profit, ROI
  - whether it is a **HIT** or not
  - a graphic summary.

### 3️⃣ Custom Movie Simulator
- user inputs budget, income, and rating
- app computes ROI and hit status
- app displays a graphic summary.

### 4️⃣ Global Visualizations
- **scatter plots**  
  - Budget vs Income (with optional log scale)  
  - ROI (trimmed 1–99%) vs Rating
- **distributions**  
  - rating  
  - ROI (trimmed 1–99%)  
  - profit
- **trends over time**  
  mean rating, median ROI, median profit by year

***Sidebar filters:***
***- filter by genre,***
***- show only hits,***
***- choose sample size,***
***- log scale***

---

# 🔍 Key Findings
Below, the _main_ insights on trends behind cinematic triumphs obtained from both the analyzed dataset in **`app.py`** and **`app.py`**.

### ⭐ How many hits?
- **Number of hit movies:** ~10% of the dataset  
  (based on: ROI ≥ 75th percentile, rating ≥ 75th percentile)

- **Average performance of hit movies - HIT THRESHOLDS**
| Metric | Value |
|-------|-------|
| **Median ROI of (hits)** | ~3.83 |
| **Median rating (hits)** | ~7.3 / 10 |
| **Median profit (hits)** | ~ 170($M) |

Hits systematically outperform non-hits on both ROI and rating (and on profit too).

---

###  Genre patterns
Some genres show a higher probability of producing hits.
- **Action and Adventure** movies: big budgets, big incomes, stable ROI, ratings 6–7.5;
- 8% of **crime** films and 15% of **drama** ones have been evaluated as hits;
- **Horror** tends to have low budgets and high ROI variance, meaning that small investments can lead to profitable hits;
- **comedy** genre appears to be quite successful, and one film in particular has a huge ROI value of 115;
- _no hits_ among films belonging to **animation, fantasy, mistery, romance and thriller** genres (least represented ones in the dataset).

---

###  Financial patterns
- Bigger budgets bring higher revenues (correlation: 0.07 - weak), but do not guarantee higher profits (correlation: -0.85)
- Profit is driven almost entirely by revenue (corr: 0.47), not by budget size.
-	Rating is almost independent of monetary performance, while is positively linked to film's duratioon (corr: 0.37)
- ROI distribution is highly skewed (trimming and log-scaling are necessary)

---

###  Temporal trends
This section suggests how financial outcomes are more sensitive to industry dynamics than viewer reception.
- **Ratings** almost constant over the years, (average: 6.6–6.8);
- **ROI** and **profit** fluctuate much more, showing peaks (2014,2018) and a dramatic collapse (2020) maybe due to pandemic effects.
Overall:
**Share of hits** not steadily over time, strongly influenced by external industry factors and market conditions: 
  - noticeable peak around 2017–2018
  - very low levels in 2020–2021 (pandemic).

*These patterns refers to the whole dataset, they can differ according to the genre*

---

###  Runtime patterns
Correlation between duration of the film and financial returns is not significantly high (0.09 with budget, 0.3 with income, 0.08 with profit). 
However, there is a positive relationship between “standard-length” films balance the commercial appeal:
- movies of **90–130 minutes** tend to have the **highest share of hits**
- very short (<90 min) and very long (≥150 min) films are less likely to be hits

---

▶️ ***How to Run the project***

***1. Install all dependencies***
_`pip install -r requirements.txt`_

***2. Run data cleaning & metric creation***
_`python src/processing.py`_

***3. Run the full analysis***
_`python src/models.py`_
_`python src/main.py`_

***4. Launch the interactive web app***
_`streamlit run app.py`_
