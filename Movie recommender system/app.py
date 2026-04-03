import pickle
import streamlit as st
import requests
import numpy as np
import base64

st.set_page_config(page_title="Movie Recommender", layout="wide")

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = get_base64("background.jpg")
logo_img = get_base64("k_logo.png")

# ================= CSS =================
st.markdown(f"""
<style>

/* Remove default top spacing */
section.main > div:first-child {{
    padding-top: 0rem;
}}

.block-container {{
    padding-top: 0rem;
}}

/* Background */
[data-testid="stAppViewContainer"] {{
    background-image:
        linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)),
        url("data:image/jpg;base64,{bg_img}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

/* HERO */
.hero {{
    position: relative;
    padding: 10px;
}}

.hero img {{
    position: absolute;
    top: 0px;
    left: 0px;
    width: 200px;
    filter: drop-shadow(0 0 6px rgba(229,9,20,0.6))
            drop-shadow(0 0 12px rgba(229,9,20,0.4));
}}

.hero h1 {{
    text-align: center;
    margin-top: 90px;
    font-size: 50px;
    font-weight: 800;
    color: #B01515;
    text-shadow:
        0 0 6px rgba(229,9,20,0.45),
        0 0 12px rgba(229,9,20,0.35),
        0 0 20px rgba(0,0,0,0.8);
}}

.hero p {{
    text-align: center;
    font-size: 25px;
    color: #dddddd;
    margin-top: 5px;
}}

/* Dropdown Styling */
div[data-baseweb="select"] > div {{
    background-color: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 10px;
    height: 50px;
}}

div[data-baseweb="select"] span {{
    color: white !important;
    font-size: 16px;
}}

/* Button Styling */
.stButton > button {{
    width: 230px;
    height: 50px;
    font-size: 16px;
    font-weight: bold;
    border-radius: 10px;
    background: rgba(229,9,20,0.9);
    border: 1px solid rgba(255,255,255,0.3);
    color: white;
    transition: 0.3s ease;
}}

.stButton > button:hover {{
    background: rgba(229,9,20,1);
    box-shadow: 0 0 15px rgba(229,9,20,0.6);
}}

.movie-card {{
    position: relative;
    text-align: center;
}}

.rating {{
    position: absolute;
    top: 10px;
    left: 10px;
    background: #B01515;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
}}

</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown(f"""
<div class="hero">
    <img src="data:image/png;base64,{logo_img}">
    <h1>Endless Movie Recommendations</h1>
    <p>Discover your next favorite film instantly 🍿</p>
</div>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open('artifacts/movies_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
similarity = np.array(similarity)

movie_list = movies['title'].values

# ================= CENTERED DROPDOWN + BUTTON =================
col1, col2, col3 = st.columns([1,4,1])

with col2:
    selected_movie = st.selectbox("Select a movie", movie_list)
    recommend_clicked = st.button("Recommendation", key="recommend_btn")

# ================= FUNCTIONS =================
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3e807dd12d53c5b186867ae98b1b75ba&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        rating = data.get('vote_average')

        if poster_path:
            poster_url = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            poster_url = "https://via.placeholder.com/300x450?text=No+Image"

        return poster_url, rating
    except:
        return "https://via.placeholder.com/300x450?text=Error", None

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = list(enumerate(similarity[index]))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)

    names, posters, ratings = [], [], []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id
        poster, rating = fetch_poster(movie_id)
        names.append(movies.iloc[i[0]].title)
        posters.append(poster)
        ratings.append(rating)

    return names, posters, ratings

# ================= DISPLAY RESULTS =================
if recommend_clicked:

    with st.spinner("Analyzing movie similarity... 🍿"):
        names, posters, ratings = recommend(selected_movie)

    st.markdown("<br><br>", unsafe_allow_html=True)

    cols = st.columns(5)

    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"""
                <div class="movie-card">
                    <div class="rating">⭐ {round(ratings[idx],1) if ratings[idx] else 'N/A'}</div>
                    <img src="{posters[idx]}"
                         style="width:100%;
                                height:350px;
                                object-fit:cover;
                                border-radius:15px;">
                    <p style="margin-top:12px; color:white;">
                        {names[idx]}
                    </p>
                </div>
            """, unsafe_allow_html=True)