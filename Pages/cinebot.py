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
            :root { color-scheme: dark; }
            .stApp { background: #07070a; }
            .block-container { padding: 2rem; max-width: 1000px; margin: 0 auto; }
            .chat-header { font-size: 38px; font-weight: 700; color: #fff; margin-bottom: 8px; }
            .chat-sub { color: #cfcfcf; margin-bottom: 18px; }
            .messages { display: block; padding: 12px 6px 90px; }
            .msg-row { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 18px; }
            .msg-bot { background: rgba(255,160,0,0.12); color: #fff; padding: 14px 16px; border-radius: 12px; border: 1px solid rgba(255,160,0,0.14); max-width: 78%; }
            .msg-user { background: rgba(220,38,38,0.12); color: #fff; padding: 14px 16px; border-radius: 12px; border: 1px solid rgba(220,38,38,0.14); margin-left: auto; max-width: 78%; }
            .avatar { width: 36px; height: 36px; border-radius: 10px; display: inline-block; text-align:center; line-height:36px; font-weight:700 }
            .avatar-bot { background: #ffb84d; color: #1b1b1b }
            .avatar-user { background: #ef4444; color: #fff }
            .input-area { position: fixed; left: 0; right: 0; bottom: 18px; display: flex; justify-content: center; }
            .input-box { width: 100%; max-width: 980px; padding: 12px; background: rgba(0,0,0,0.35); border-radius: 12px; border: 1px solid rgba(255,255,255,0.04); display:flex; gap:10px; align-items:center }
            .text-input { flex:1; padding: 12px 14px; background: rgba(255,255,255,0.03); border-radius: 8px; color: #fff; border: none }
            .send-btn { background: #ef4444; color: #fff; padding: 10px 14px; border-radius: 8px; border: none }
            .example-prompts { margin-top: 28px; color: #ddd }
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
st.set_page_config(page_title="CineBot | CineMatch AI", page_icon="🤖", layout="wide")

st.markdown("<div class='chat-header'>CineBot</div>", unsafe_allow_html=True)
st.markdown("<div class='chat-sub'>Ask CineBot for movie recommendations, mood-based picks, or genre suggestions.</div>", unsafe_allow_html=True)

if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "assistant", "text": "Hi — I'm CineBot. Tell me your mood or a genre and I'll recommend movies."}
    ]

def render_message(msg: dict):
    role = msg.get('role')
    text = msg.get('text')
    if role == 'assistant':
        html = f"""
        <div class='msg-row'>
          <div class='avatar avatar-bot'>🤖</div>
          <div class='msg-bot'>{text}</div>
        </div>
        """
    else:
        html = f"""
        <div class='msg-row'>
          <div style='flex:1'></div>
          <div class='msg-user'>{text}</div>
          <div class='avatar avatar-user'>🙂</div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


container = st.container()
with container:
    st.markdown("<div class='messages'>", unsafe_allow_html=True)
    for m in st.session_state.conversation:
        render_message(m)
    st.markdown("</div>", unsafe_allow_html=True)

# Input area (not part of the main flow so visually at bottom)
user_input = st.text_input("", key="cinebot_input", placeholder="Type your question here...")
send = st.button("Send", key="cinebot_send")

if send and user_input:
    st.session_state.conversation.append({"role": "user", "text": user_input})
    # regenerate the container to show latest
    with container:
        render_message({"role": "user", "text": user_input})
    ai_answer = generate_response(user_input)
    st.session_state.conversation.append({"role": "assistant", "text": ai_answer})
    with container:
        render_message({"role": "assistant", "text": ai_answer})

st.markdown(
    "<div class='input-area'><div class='input-box'><input class='text-input' id='cinetext' placeholder='Type your question here...'>"
    "<button class='send-btn' onclick=\"document.querySelector('#root > div div textarea').value = document.getElementById('cinetext').value; document.querySelector('#root button[kind=primary]').click();\">Send</button></div></div>",
    unsafe_allow_html=True,
)

st.markdown("<div class='example-prompts'><b>Example prompts:</b> Recommend me sad sci-fi movies · I want a mind-blowing thriller · Suggest a feel-good action film for tonight</div>", unsafe_allow_html=True)
