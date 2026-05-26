import os
from typing import List, Dict

import requests
import streamlit as st
import os
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(path: str = '.env') -> bool:
        try:
            candidates = [os.getcwd()]
            try:
                candidates.append(os.path.dirname(__file__))
            except Exception:
                pass
            seen = set()
            for start in candidates:
                current = os.path.abspath(start)
                while True:
                    if current in seen:
                        break
                    seen.add(current)
                    candidate = os.path.join(current, path)
                    if os.path.exists(candidate):
                        with open(candidate, 'r') as f:
                            for raw in f:
                                line = raw.strip()
                                if not line or line.startswith('#'):
                                    continue
                                if '=' not in line:
                                    continue
                                k, v = line.split('=', 1)
                                k = k.strip()
                                v = v.strip().strip('"').strip("'")
                                if k and k not in os.environ:
                                    os.environ[k] = v
                        return True
                    parent = os.path.dirname(current)
                    if parent == current:
                        break
                    current = parent
            return False
        except Exception:
            return False

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342"


def set_page_style() -> None:
    st.markdown(
        """
        <style>
            .stApp { background: linear-gradient(180deg, #0f141d 0%, #07080c 100%); }
            .block-container { padding: 1.5rem 2rem 2rem; }
            .stButton>button { background-color: #e50914; color: white; }
            .stButton>button:hover { background-color: #c3070f; }
            .stImage img { border-radius: 16px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fetch_trending_movies(api_key: str) -> List[Dict]:
    try:
        response = requests.get(
            f"{TMDB_API_URL}/trending/movie/week",
            params={"api_key": api_key, "language": "en-US"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("results", [])[:12]
    except Exception:
        return []


set_page_style()
st.set_page_config(page_title="Discover | CineMatch AI", page_icon="🎥", layout="wide")

st.title("Discover Trending Movies")
st.write("Browse top movies from TMDB with posters, ratings, and short descriptions.")

if not TMDB_API_KEY:
    st.warning("Add your `TMDB_API_KEY` to `.env` to fetch live trending movies.")
    movies = [
        {
            "title": "Inception",
            "overview": "A thief who steals corporate secrets through dream-sharing technology.",
            "vote_average": 8.3,
            "poster_path": "/qmDpIHrmpJINaRKAfWQfftjCdyi.jpg",
        },
        {
            "title": "Interstellar",
            "overview": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "vote_average": 8.6,
            "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        },
        {
            "title": "The Matrix",
            "overview": "A hacker discovers a shocking truth about the world and his role in the human rebellion.",
            "vote_average": 8.7,
            "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        },
    ]
else:
    movies = fetch_trending_movies(TMDB_API_KEY)

if not movies:
    st.error("No trending movies found. Check your TMDB key or try again later.")
else:
    for row in range(0, len(movies), 3):
        cols = st.columns(3, gap="large")
        for index, movie in enumerate(movies[row:row + 3]):
            with cols[index]:
                poster_path = movie.get("poster_path")
                if poster_path:
                    st.image(
                        f"{TMDB_IMAGE_BASE}{poster_path}",
                        use_container_width=True,
                        caption=f"{movie.get('title', 'Unknown')} — {movie.get('vote_average', 0):.1f}/10",
                    )
                else:
                    st.markdown("**No image available**")
                st.markdown(f"### {movie.get('title', 'Untitled')}")
                overview = movie.get("overview", "No description available.")
                st.write(overview[:180].strip() + ("..." if len(overview) > 180 else ""))
                st.caption(f"Rating: {movie.get('vote_average', 0):.1f}")
