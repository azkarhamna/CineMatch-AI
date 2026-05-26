import os
from typing import Optional

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
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Default to a Gemini model known to support generate_content
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def set_page_style() -> None:
    st.markdown(
        """
        <style>
            .stApp { background: linear-gradient(180deg, #09090c 0%, #08080a 100%); }
            .block-container { padding: 1.5rem 2rem 2rem; }
            .stButton>button { background-color: #e50914; color: white; }
            .stButton>button:hover { background-color: #c3070f; }
            .chat-box { background: rgba(255,255,255,0.04); border: 1px solid #2f2f2f; border-radius: 18px; padding: 18px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_gemini_client() -> Optional[genai.Client]:
    if not GEMINI_API_KEY:
        return None
    # Instantiate the genai Client using the installed google-genai SDK
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_response(prompt: str) -> str:
    client = create_gemini_client()
    if client is None:
        return "Gemini API key missing. Add `GEMINI_API_KEY` to `.env`."
    try:
        # Use the models.generate_content API to get text responses
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        # response may expose text property
        if hasattr(response, 'text') and response.text:
            return str(response.text).strip()
        # Fallback: try to stringify the whole response
        return str(response)
    except Exception as exc:
        # If model is not found, list available models and suggest a fix
        msg = str(exc)
        if 'NOT_FOUND' in msg or 'not found' in msg.lower() or 'generateContent' in msg:
            try:
                pager = client.models.list(config={'page_size': 12})
                models = []
                for m in pager.page:
                    name = getattr(m, 'display_name', None) or getattr(m, 'name', None)
                    if name:
                        # include both display name and resource name when available
                        if hasattr(m, 'display_name') and getattr(m, 'display_name'):
                            disp = getattr(m, 'display_name')
                        else:
                            disp = None
                        resname = getattr(m, 'name', None)
                        entry = disp if disp else resname if resname else str(m)
                        if resname and disp:
                            entry = f"{disp} — {resname}"
                        models.append(entry)
                        if models:
                            model_list = '\n'.join(f"- {x}" for x in models[:10])
                            return (
                                "Gemini model not supported for this API.\n"
                                "Available models (first results):\n"
                                f"{model_list}\n\n"
                                "Set `GEMINI_MODEL` in your .env to the model id (for example: gemini-2.5-flash) or the resource name shown above."
                            )
            except Exception:
                pass
        return f"Unable to connect to Gemini: {exc}"


set_page_style()
st.set_page_config(page_title="CineBot | CineMatch AI", page_icon="🤖", layout="wide")

st.title("CineBot")
st.write("Ask CineBot for movie recommendations, mood-based picks, or genre suggestions.")

if "conversation" not in st.session_state:
    st.session_state.conversation = []

with st.form("cinebot_form"):
    user_prompt = st.text_input("Ask CineBot", "Recommend me sad sci-fi movies")
    submitted = st.form_submit_button("Send")

    if submitted and user_prompt:
        st.session_state.conversation.append({"role": "user", "text": user_prompt})
        ai_answer = generate_response(user_prompt)
        st.session_state.conversation.append({"role": "assistant", "text": ai_answer})

if st.session_state.conversation:
    for message in st.session_state.conversation:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['text']}")
        else:
            st.markdown(f"**CineBot:** {message['text']}")
        st.divider()

st.markdown("---")
st.subheader("Example prompts")
st.write(
    "- Recommend me sad sci-fi movies\n"
    "- I want a mind-blowing thriller\n"
    "- Suggest a feel-good action film for tonight"
)
