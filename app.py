import pickle
import streamlit as st
import requests
import numpy as np
import base64
from auth import signup, login, save_preference, get_liked_movies, remove_preference

st.set_page_config(page_title="Movie Recommender", layout="wide")
# ================= LOGIN SYSTEM =================
if "user" not in st.session_state:
    st.session_state.user = None
if "show_recommend" not in st.session_state:
    st.session_state.show_recommend = False

if "last_movie" not in st.session_state:
    st.session_state.last_movie = None
menu = st.sidebar.selectbox("Account", ["Login", "Signup"])

if st.session_state.user is None:

    if menu == "Signup":
        username = st.sidebar.text_input("Create Username")
        password = st.sidebar.text_input("Create Password", type="password")

        if st.sidebar.button("Signup"):
            if signup(username, password):
                st.sidebar.success("Account created! Please login.")
            else:
                st.sidebar.error("User already exists")

    elif menu == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            if login(username, password):
                st.session_state.user = username
                st.sidebar.success(f"Welcome {username}")
            else:
                st.sidebar.error("Invalid credentials")

else:
    st.sidebar.success(f"Logged in as {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None

    # ================= ADD THIS PART HERE =================
    liked_movies = get_liked_movies(st.session_state.user)

    st.sidebar.markdown("### ❤️ Your Liked Movies")

    if liked_movies:
        for movie in set(liked_movies):
            st.sidebar.write(f"• {movie}")
    else:
        st.sidebar.write("No liked movies yet")

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
    if st.button(
    "Recommendation",
    key="recommend_btn",
    disabled=not st.session_state.user
):
     st.session_state.show_recommend = True
if selected_movie != st.session_state.last_movie:
    st.session_state.show_recommend = False
    st.session_state.last_movie = selected_movie
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

def recommend_from_likes(user):
    liked_movies = get_liked_movies(user)

    if not liked_movies:
        return [], [], []

    all_recommendations = []

    for movie in liked_movies:
        try:
            index = movies[movies['title'] == movie].index[0]
            distances = list(enumerate(similarity[index]))
            distances = sorted(distances, key=lambda x: x[1], reverse=True)

            for i in distances[1:4]:
                all_recommendations.append(i[0])
        except:
            continue

    # Remove duplicates
    unique_movies = list(set(all_recommendations))[:5]

    names, posters, ratings = [], [], []

    for i in unique_movies:
        movie_id = movies.iloc[i].id
        poster, rating = fetch_poster(movie_id)

        names.append(movies.iloc[i].title)
        posters.append(poster)
        ratings.append(rating)

    return names, posters, ratings
# ================= DISPLAY RESULTS =================

if st.session_state.show_recommend:
    st.session_state.show_recommend = True

    if not st.session_state.user:
        st.warning("⚠️ Please login to get recommendations")
        st.stop()

    if not st.session_state.user:
        st.warning("⚠️ Please login to get recommendations")
        st.stop()

    # ✅ Get liked movies
    liked_movies = get_liked_movies(st.session_state.user)

    # ✅ MIX BOTH LOGIC HERE
    with st.spinner("Analyzing movie similarity... 🍿"):

        # Step 1: normal recommendation
        names1, posters1, ratings1 = recommend(selected_movie)

        # Step 2: liked-based recommendation
        if liked_movies:
            names2, posters2, ratings2 = recommend_from_likes(st.session_state.user)

            # 🔥 COMBINE BOTH
            names = list(dict.fromkeys(names1 + names2))[:5]
            posters = posters1 + posters2
            ratings = ratings1 + ratings2

            posters = posters[:len(names)]
            ratings = ratings[:len(names)]

        else:
            names, posters, ratings = names1, posters1, ratings1
    cols = st.columns(5)

    for idx in range(len(names)):
        col = cols[idx]
        with col:
            st.markdown(f"""
                <div class="movie-card">
                    <div class="rating">⭐ {round(ratings[idx],1) if ratings[idx] else 'N/A'}</div>
                    <img src="{posters[idx]}"
                         style="width:100%;
                                height:350px;
                                object-fit:cover;
                                border-radius:15px;">
                    <p style=" 
                              margin-top:12px;
                              color:white;
                              height:60px;
                              overflow:hidden;
                              text-align:center;">
                        {names[idx]}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if st.session_state.user:
              safe_name = names[idx].replace(" ", "_")

              is_liked = names[idx] in liked_movies

            if is_liked:
               if st.button("❤️ Dislike", key=f"unlike_{safe_name}_{idx}"):
                 remove_preference(st.session_state.user, names[idx])
                 st.success(f"Removed from liked: {names[idx]}")
            else:
                if st.button("🤍 Like", key=f"like_{safe_name}_{idx}"):
                 save_preference(st.session_state.user, names[idx], 1)
                 st.success(f"Liked saved: {names[idx]}")
                
                

                