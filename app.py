#WEB APPLICATION 
import streamlit as st
from pathlib import Path
import pandas as pd
import altair as alt

from src.models import Movie, MoviePlotter

data_path = Path("data/Movies_metrics.csv")

@st.cache_data #doesn't reload it at every interaction
def load_metrics():
    df = pd.read_csv(data_path)
    return df

df = load_metrics()
plotter = MoviePlotter(df)

###################### PAGE SETUP ######################
st.title("🎬 Blockbuster Movie Analyzer")
st.subheader("What makes a movie a hit?")

st.markdown(
    """
    This web app allows you to:
    - check whether a movie is classified as a **hit** (based on ROI and rating)
    - test custom movies
    - explore some global visualizations
    """
)

# sidebar to move between sections
st.sidebar.markdown("## 🧭 Navigation")
options = {
    "Dataset overview": "📊 Dataset overview",
    "Check a movie": "🎬 Check a movie",
    "Custom movie simulator": "✨ Custom movie simulator",
    "Global plots": "🌍 Global plots"
}

clicked = st.sidebar.radio("",list(options.values()))
page = [k for k, v in options.items() if v == clicked][0]


###################### Dataset overview ######################
if page == "Dataset overview":
    st.header("📊 Dataset overview")

    st.write("Shape (rows, columns):", df.shape)
    
    #1
    st.markdown("### 📂 Column list")
    with st.expander("Show variables in the dataset"):
        cols = df.columns.tolist()
        half = len(cols) // 2 + len(cols) % 2  # split in 2 cols

        left, right = st.columns(2)

        with left:
            for c in cols[:half]:
                st.markdown(f"- **{c}**")

        with right:
            for c in cols[half:]:
                st.markdown(f"- **{c}**")

    #2
    st.markdown("**First 20 rows:**")
    st.dataframe(df.head(20))

    #3
    st.markdown("**Basic stats (numeric columns):**")
    exclude_cols = ["year", "month_num", "decade"]
    numeric_cols = [c for c in df.select_dtypes(include="number").columns 
                if c not in exclude_cols]
    st.dataframe(df[numeric_cols].describe())


###################### Check a movie ######################
elif page == "Check a movie":
    st.header("🔎 Check if a movie in the dataset is a hit")

    title_input = st.text_input("Write a movie title from the dataset:")

    if title_input:
    
        match = df[df["title"].str.lower() == title_input.lower()]

        if match.empty:
            st.error("❌ This movie is not in the dataset.")
        else:
            row = match.iloc[0]
            movie = Movie.from_row(row)

            st.success(f"🎬 Found: **{movie.title}**")
            st.write(f"**Rating:** {movie.rating:.1f}")
            st.write(f"**ROI:** {movie.roi:.2f}×")
            st.write(f"**Profit ($):** {movie.profit:,.0f}")

            if movie.is_hit():
                st.success("🔥 This movie is classified as a **HIT**.")
            else:
                st.warning("❌ This movie is **not** classified as a hit.")

            # graph
            st.markdown("**Visual summary (rating & ROI):**")
            fig, _ = plotter.plot_movie_summary(movie, show=False)
            st.pyplot(fig)


###################### Custom movie ######################
elif page == "Custom movie simulator":
    st.header("📝 Test a custom movie (not necessarily in the dataset)")

    custom_title = st.text_input("Movie title (custom):", value="My Movie")

    col1, col2, col3 = st.columns(3)
    with col1:
        custom_budget = st.number_input("Budget ($)", min_value=0.0, step=1_000_000.0)
    with col2:
        custom_income = st.number_input("Income ($)", min_value=0.0, step=1_000_000.0)
    with col3:
        custom_rating = st.slider("Rating (0-10)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)

    if st.button("Check this custom movie"):
        movie = Movie(
            title=custom_title,
            budget=custom_budget,
            income=custom_income,
            rating=custom_rating,
        )

        st.write(f"**ROI:** {movie.roi:.2f}x")
        st.write(f"**Profit ($):** {movie.profit:,.0f}")

        if movie.is_hit():
            st.success("🔥 This movie is/would be considered a **HIT**")
        else:
            st.warning("❌ This movie is **not**/would **not** be considered a hit")

        # graph
        fig, _ = plotter.plot_movie_summary(movie, show=False)
        st.pyplot(fig)
     
        
###################### Global plots ######################
elif page == "Global plots":
    st.header("📈 Global visualizations")

    # Sidebar filters 
    st.sidebar.subheader("Filters for global plots")
    d = df.copy()

    # 1) Genre filter
    if "genre_main" in d.columns:
        all_genres = ["All genres"] + sorted(d["genre_main"].dropna().unique().tolist())
        selected_genre = st.sidebar.selectbox("Genre", all_genres)

        if selected_genre != "All genres":
            d = d[d["genre_main"] == selected_genre]

    # 2) Only hits
    only_hits = False
    if "hit" in d.columns:
        only_hits = st.sidebar.checkbox("Show only hits")
        if only_hits:
            d = d[d["hit"] == True]

    # 3) Slider: how many movies to use (for scatter / distributions)
    max_n = len(d)

    if max_n == 0:
        st.warning("No movies match the current filters.")
        st.stop()

    # if just 1 film
    if max_n == 1:
        n_movies = 1
        st.sidebar.info("Only 1 movie matches the current filters.")
    else:
        # min=1, max = all filtered films
        n_movies = st.sidebar.slider(
            "Number of movies to display (sampled)",
            min_value=1,
            max_value=max_n,
            value=min(500, max_n),
            step=max(1, max_n // 10),
        )

    # random sample (not necessarily first rows)
    if len(d) > n_movies:
        d_sample = d.sample(n=n_movies, random_state=0)
    else:
        d_sample = d

    # 4) Log scale option for money
    log_money = st.sidebar.checkbox("Use log scale for Budget/Income")

    st.divider()

    # TABS 
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Scatter", "📊 Distributions", "📆 Trends", "⏱️ Correlation & Runtime"])

    # TAB 1: Scatter 
    with tab1:
        left, right = st.columns(2)

        # Left: Budget vs Income
        with left:
            st.subheader("Budget vs Income")
            if {"budget_num", "income_num"}.issubset(d_sample.columns):
                d_money = d_sample.dropna(subset=["budget_num", "income_num"]).copy()

                chart = alt.Chart(d_money).mark_circle(size=45, opacity=0.6).encode(
                    x=alt.X(
                        "budget_num:Q",
                        title="Budget",
                        scale=alt.Scale(type="log") if log_money else alt.Undefined
                    ),
                    y=alt.Y(
                        "income_num:Q",
                        title="Income",
                        scale=alt.Scale(type="log") if log_money else alt.Undefined
                    ),
                    color=alt.Color("hit:N", legend=alt.Legend(title="Hit")) if "hit" in d_money.columns else alt.value("#2E8B57"),
                    tooltip=["title:N", "genre_main:N", "year:Q", "budget_num:Q", "income_num:Q", "roi:Q", "rating:Q"]
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Columns 'budget_num'/'income_num' not available.")

        # Right: ROI vs Rating
        with right:
            st.subheader("ROI vs Rating")
            if {"roi", "rating"}.issubset(d_sample.columns):
                d_roi_scatter = d_sample.dropna(subset=["roi", "rating"]).copy()

                if len(d_roi_scatter) > 0:
                    roi_low = float(d_roi_scatter["roi"].quantile(0.01))
                    roi_high = float(d_roi_scatter["roi"].quantile(0.99))

                    chart = alt.Chart(d_roi_scatter).mark_circle(size=45, opacity=0.6).encode(
                        x=alt.X(
                            "roi:Q",
                            title="ROI",
                            scale=alt.Scale(domain=[roi_low, roi_high])
                        ),
                        y=alt.Y("rating:Q", title="Rating"),
                        color=alt.Color(
                            "genre_main:N",
                            legend=alt.Legend(title="Genre")
                        ) if "genre_main" in d_roi_scatter.columns else alt.value("#2E8B57"),
                        tooltip=["title:N", "genre_main:N", "year:Q", "roi:Q", "rating:Q"]
                    ).interactive()

                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No data available for ROI vs Rating with current filters.")
            else:
                st.info("Columns 'roi'/'rating' not available.")

    # TAB 2: Distributions
    with tab2:
        left, right, extra = st.columns(3)
        
            # less than 5 films --> distribution plots not shown ()
        if len(d) < 5:
            st.info("Not enough data to display distribution plots. Please broaden the filters.")
        else:

            # ROI distribution 
            if "roi" in d.columns:
                d_roi = d.dropna(subset=["roi"]).copy()

                if len(d_roi) > 0:
                    roi_low = float(d_roi["roi"].quantile(0.01))
                    roi_high = float(d_roi["roi"].quantile(0.99))

                    d_roi = d_roi[(d_roi["roi"] >= roi_low) & (d_roi["roi"] <= roi_high)] # trimming  1–99% (no outliers)
                    n_roi = len(d_roi)
                    roi_bins = 10 if n_roi < 50 else 40
                    
                    roi_hist = alt.Chart(d_roi).mark_bar().properties(width=250, height=350).encode(
                        x=alt.X(
                            "roi:Q", bin=alt.Bin(maxbins=roi_bins), title="ROI (trimmed 1–99%)", scale=alt.Scale(domain=[roi_low, roi_high])
                        ),
                        y=alt.Y("count():Q", title="Count", axis=alt.Axis(tickMinStep=1)) #only integers
                    )
                    left.subheader("ROI")
                    left.altair_chart(roi_hist, use_container_width=False)
                else:
                    left.info("No ROI values available with the current filters.")

            # Rating distribution
            if "rating" in d.columns:
                d_rating = d.dropna(subset=["rating"])
                n_rating = len(d_rating)
                rating_bins = 10 if n_rating < 50 else 30
                
                rating_hist = alt.Chart(d_rating).mark_bar().properties(width=250, height=350).encode(
                    x=alt.X("rating:Q", bin=alt.Bin(maxbins=rating_bins), title="Rating"),
                    y=alt.Y("count():Q", title="Count", axis=alt.Axis(tickMinStep=1))
                    )
                right.subheader("Rating")
                right.altair_chart(rating_hist, use_container_width=False)

            # Profit distribution (in millions)
            if "profit" in d.columns:
                d_prof = d.dropna(subset=["profit"]).copy()
                d_prof["profit_million"] = d_prof["profit"] / 1e6
                n_prof = len(d_prof)
                prof_bins = 10 if n_prof < 50 else 40
                
                prof_hist = alt.Chart(d_prof).mark_bar().properties(width=250, height=350).encode(
                    x=alt.X("profit_million:Q", bin=alt.Bin(maxbins=prof_bins), title="Profit ($M)"),
                    y=alt.Y("count():Q", title="Count", axis=alt.Axis(tickMinStep=1))
                    )
                extra.subheader("Profit ($M)")
                extra.altair_chart(prof_hist, use_container_width=False)

    # TAB 3: Trends 
    with tab3:
        st.subheader("Metric by Year")

        if "year" in d.columns:
            # choose metric among available ones
            metric_options = [c for c in ["roi", "rating", "profit"] if c in d.columns]
            metric = st.selectbox("Metric", metric_options, index=0)

            if metric:
                # aggregation rule
                agg = "median" if metric in ["roi", "profit"] else "mean"

                ts = (
                    d.dropna(subset=["year", metric])
                     .groupby("year")[metric]
                     .agg(agg)
                     .reset_index()
                     .sort_values("year")
                )

                line = alt.Chart(ts).mark_line(point=True).encode(
                    x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
                    y=alt.Y(f"{metric}:Q", title=f"{agg.capitalize()} {metric}"),
                    tooltip=[
                        alt.Tooltip("year:Q", format="d"),
                        alt.Tooltip(f"{metric}:Q", format=".2f"),
                    ],
                ).interactive()

                st.altair_chart(line, use_container_width=True)
        else:
            st.info("Column 'year' not available.")
        
        # Share of hits over time
        if {"year", "hit"}.issubset(d.columns):
            st.subheader("Share of hits over time")
            d_year = d.dropna(subset=["year", "hit"]).copy()
            d_year = (
                d_year.groupby("year")["hit"]
                    .mean().mul(100)
                    .reset_index()
            )

            line = alt.Chart(d_year).mark_line(point=True).encode(
                x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
                y=alt.Y("hit:Q", title="Share of hits (%)"),
                tooltip=["year:Q", alt.Tooltip("hit:Q", format=".1f")]
            )
            
            st.altair_chart(line, use_container_width=True)

     # TAB 4: Correlation & Runtime Analysis 
    with tab4:
        st.subheader("🔄 Correlation heatmap")

        # Columns to include in the correlation matrix
        corr_cols = [c for c in ["budget_num", "income_num", "profit", "roi", "rating", "runtime_min"]
                     if c in d.columns]

        if len(corr_cols) < 2:
            st.info("Not enough numeric columns available to compute correlations.")
        else:
            corr_df = d[corr_cols].dropna().corr()

            # Convert correlation matrix to long format
            corr_long = (
                corr_df
                .reset_index()
                .melt(id_vars="index", var_name="variable2", value_name="corr")
                .rename(columns={"index": "variable1"})
            )

            heatmap = (
                alt.Chart(corr_long)
                .mark_rect()
                .encode(
                    x=alt.X("variable1:O", title=""),
                    y=alt.Y("variable2:O", title=""),
                    color=alt.Color("corr:Q",
                                    scale=alt.Scale(scheme="blueorange", domain=(-1, 1))),
                    tooltip=[
                        alt.Tooltip("variable1:N", title="Variable 1"),
                        alt.Tooltip("variable2:N", title="Variable 2"),
                        alt.Tooltip("corr:Q", format=".2f", title="Correlation"),
                    ],
                )
                .properties(width=450, height=450)
            )

            st.altair_chart(heatmap, use_container_width=True)



        st.markdown("---")
        st.subheader("⏱ Hit share by runtime bucket")
        if {"runtime_min", "hit"}.issubset(d.columns):

            # Create bucket
            bins = [0, 90, 110, 130, 150, 1_000]
            labels = ["<90", "90–110", "110–130", "130–150", "≥150"]
            d_rt = d.dropna(subset=["runtime_min", "hit"]).copy()
            d_rt["runtime_bucket"] = pd.cut(
                d_rt["runtime_min"], bins=bins, labels=labels, right=False, ordered=True
            )

            # Share of hit per bucket
            share = (
                d_rt.groupby("runtime_bucket")["hit"]
                .mean()
                .mul(100)
                .reset_index()
            )

            # Graph
            chart = (
                alt.Chart(share)
                .mark_bar()
                .encode(
                    x=alt.X("runtime_bucket:N", sort=labels, title="Runtime bucket"),
                    y=alt.Y("hit:Q", title="Hit share (%)"),
                    color=alt.Color("hit:Q", scale=alt.Scale(scheme="yellowgreenblue"), legend=None),
                    tooltip=["runtime_bucket:N", alt.Tooltip("hit:Q", format=".1f")]
                )
                .properties(height=300)
            )

            st.altair_chart(chart, use_container_width=True)

        else:
            st.info("Columns 'runtime_min' and 'hit' not available.")
                
    st.caption("Tip: use the filters in the sidebar and the log scale to explore money-related patterns.")