import streamlit as st
import os
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(path: str = '.env') -> bool:
        """Search upwards from cwd and the current file for a .env file and load it.

        This is a minimal parser and will not replace all features of
        python-dotenv. It will not overwrite existing environment variables.
        """
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

st.set_page_config(page_title="CineMatch AI", page_icon="🎬", layout="wide")


def set_page_style() -> None:
    st.markdown(
        """
        <style>
            :root { color-scheme: dark; }
            .stApp { background: #050607; }
            .block-container { padding: 2rem 2.5rem 2rem; background: rgba(10, 10, 10, 0.86); border-radius: 20px; }
            .stSidebar { background: #09090c; }
            .stButton>button { background-color: #e50914; color: #fff; border: 1px solid transparent; }
            .stButton>button:hover { background-color: #c3070f; }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #f2f2f3; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def home_page() -> None:
    st.title("🎬 Welcome to CineMatch AI")
    st.write("CineMatch AI is your movie recommendation companion for every mood and genre.")
    st.write("Explore trending films, ask CineBot for suggestions, or watch trailers in the Theater.")
    st.markdown(
        """
        **What CineMatch AI offers:**
        - Discover trending movies from TMDB
        - Ask an AI-powered chatbot for curated movie picks
        - Watch cinematic YouTube trailers
        """
    )
    st.markdown(
        """
        <div style='margin-top: 24px; padding: 18px; border-radius: 16px; background: rgba(255,255,255,0.04); border: 1px solid #29292d;'>
        CineMatch AI blends movie data with Gemini-powered recommendations in a dark, cinematic interface.
        Use the sidebar to navigate between Discover, CineBot, and Trailer Theater.
        </div>
        """,
        unsafe_allow_html=True,
    )


set_page_style()

st.sidebar.title("CineMatch AI")
st.sidebar.caption("Navigate to your next movie")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resolve_page_file(filename: str) -> str:
    paths = [
        os.path.join(BASE_DIR, "pages", filename),
        os.path.join(BASE_DIR, "Pages", filename),
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return paths[0]

pages = [
    st.Page(home_page, title="Home", default=True),
    st.Page(resolve_page_file("discover.py"), title="Discover"),
    st.Page(resolve_page_file("cinebot.py"), title="CineBot"),
    st.Page(resolve_page_file("theater.py"), title="Trailer Theater"),
]

page = st.navigation(pages)
page.run()
