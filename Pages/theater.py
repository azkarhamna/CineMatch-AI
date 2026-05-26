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


def set_page_style() -> None:
    st.markdown(
        """
        <style>
            .stApp { background: linear-gradient(180deg, #070707 0%, #111111 100%); }
            .block-container { padding: 1.5rem 2rem 2rem; }
            .stButton>button { background-color: #e50914; color: white; }
            .stButton>button:hover { background-color: #c3070f; }
            .trailer-card { border: 1px solid #222; border-radius: 18px; padding: 16px; background: rgba(255,255,255,0.03); }
        </style>
        """,
        unsafe_allow_html=True,
    )


TRAILERS = [
    {
        "title": "Inception",
        "description": "A mind-bending thriller about dreams, reality, and a high-stakes heist.",
        "video_id": "YoHD9XEInc0",
    },
    {
        "title": "The Matrix",
        "description": "A hacker discovers the truth behind the world he thought was real.",
        "video_id": "m8e-FF8MsqU",
    },
    {
        "title": "Interstellar",
        "description": "A space adventure that explores love, time, and humanity's future.",
        "video_id": "zSWdZVtXT7E",
    },
    {
        "title": "Parasite",
        "description": "A dark drama that blends suspense and social satire.",
        "video_id": "SEUXfv87Wpk",
    },
]

set_page_style()
st.set_page_config(page_title="Trailer Theater | CineMatch AI", page_icon="🍿", layout="wide")

st.title("Trailer Theater")
st.write("Watch cinematic trailers and preview the next movie on your watchlist.")

selected_title = st.selectbox(
    "Choose a movie trailer",
    [trailer["title"] for trailer in TRAILERS],
)

selected_trailer = next(item for item in TRAILERS if item["title"] == selected_title)

with st.container():
    st.markdown(f"### {selected_trailer['title']}")
    st.write(selected_trailer["description"])
    st.video(f"https://www.youtube.com/watch?v={selected_trailer['video_id']}")
