
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Movie Recommendation System", page_icon="🎬")

# -------------------------------
# Load Data
# -------------------------------
movies_df = pd.read_csv("movies_df.csv")
st.write("Dataset loaded:", movies_df.shape)

# -------------------------------
# Fix vote column safely
# -------------------------------
if "vote_avg" in movies_df.columns:
    vote_col = "vote_avg"
elif "vote_average" in movies_df.columns:
    vote_col = "vote_average"
else:
    st.error("Vote column not found!")
    st.stop()

movies_df[vote_col] = pd.to_numeric(movies_df[vote_col], errors="coerce")

# -------------------------------
# Fix revenue safely
# -------------------------------
if "revenue" in movies_df.columns:
    movies_df["revenue"] = pd.to_numeric(movies_df["revenue"], errors="coerce")

# -------------------------------
# Adult Category FIX
# -------------------------------
def change_adult(x):
    return "adult movie" if str(x).lower() in ["true", "1"] else "not an adult"

movies_df["adult_cat"] = movies_df["adult"].apply(change_adult)

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.header("Movie Recommendation System")

vote_cat = [
    "all movies",
    "excellent (7-10)",
    "good (5-7)",
    "average (3-5)",
    "poor (0-3)"
]

adult_cat = ["all movies", "adult movie", "not an adult"]

revenue_cat = ["all movies"]
if "revenue_category" in movies_df.columns:
    revenue_cat += movies_df["revenue_category"].dropna().unique().tolist()

votes = st.sidebar.selectbox("Choose vote filter", vote_cat)
adult = st.sidebar.selectbox("Choose adult", adult_cat)
revenue = st.sidebar.selectbox("Choose revenue option", revenue_cat)

# -------------------------------
# Filtering
# -------------------------------
filtered_data = movies_df.copy()

# Vote filter
if votes == "excellent (7-10)":
    filtered_data = filtered_data[(filtered_data[vote_col] >= 7) & (filtered_data[vote_col] <= 10)]
elif votes == "good (5-7)":
    filtered_data = filtered_data[(filtered_data[vote_col] >= 5) & (filtered_data[vote_col] < 7)]
elif votes == "average (3-5)":
    filtered_data = filtered_data[(filtered_data[vote_col] >= 3) & (filtered_data[vote_col] < 5)]
elif votes == "poor (0-3)":
    filtered_data = filtered_data[(filtered_data[vote_col] < 3)]

# Adult filter
if adult != "all movies":
    filtered_data = filtered_data[filtered_data["adult_cat"] == adult]

# Revenue filter
if revenue != "all movies" and "revenue_category" in filtered_data.columns:
    filtered_data = filtered_data[filtered_data["revenue_category"] == revenue]

# -------------------------------
# Display
# -------------------------------
st.header(f"Total Movies ({filtered_data.shape[0]})")

if filtered_data.shape[0] == 0:
    st.warning("No movies match the selected filters")
    st.stop()

for i in range(0, filtered_data.shape[0], 3):
    rows = filtered_data.iloc[i:i+3]
    cols = st.columns(3)

    for col, (_, movie) in zip(cols, rows.iterrows()):
        with col:
            if pd.notna(movie.poster_path) and movie.poster_path != "":
                image_url = f"https://image.tmdb.org/t/p/w500/{movie.poster_path}"
                st.image(image_url)
            else:
                st.image("https://via.placeholder.com/300x450?text=No+Image")

            st.write(f"### {movie.title}")
            st.markdown(f"""
            - {movie.tagline if pd.notna(movie.tagline) else "No tagline"}
            - **Revenue:** {movie.revenue if pd.notna(movie.revenue) else "N/A"}
            - **Release Date:** {movie.release_date if pd.notna(movie.release_date) else "N/A"}
            - **Genre:** {movie.genres if pd.notna(movie.genres) else "N/A"}
            - **Average Vote:** {movie[vote_col] if pd.notna(movie[vote_col]) else "N/A"}
            """)