import streamlit as st
from groq_chatbot import generate_response, SUPPORTED_MODELS
import json
import os
import re
import glob
import time

# --- Dark Theme (default Streamlit) ---
st.set_page_config(
    page_title="Groq API Chatv1",
    page_icon="🤖",
    layout="centered"
)

# Remove custom CSS for white theme (use Streamlit's dark theme)

# --- Persistent Chat History ---
def safe_model_filename(model_name):
    # Replace slashes and spaces with underscores for safe filenames
    return re.sub(r'[^a-zA-Z0-9_-]', '_', model_name)

# --- Utility functions for per-model chat history ---
def get_history_file(model):
    return f"chat_history_{safe_model_filename(model)}.json"

def save_chat_history(messages, model):
    try:
        with open(get_history_file(model), "w", encoding="utf-8") as f:
            json.dump(messages, f)
    except Exception:
        pass

def load_chat_history(model):
    fname = get_history_file(model)
    if os.path.exists(fname):
        try:
            with open(fname, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def clear_all_histories():
    for model in SUPPORTED_MODELS:
        fname = get_history_file(model)
        if os.path.exists(fname):
            try:
                os.remove(fname)
            except Exception:
                pass

# --- Model icons, colors, and descriptions ---
MODEL_ICONS = {
    "meta-llama/llama-4-maverick-17b-128e-instruct": ("🦙", "#4f8cff"),
    "meta-llama/llama-4-scout-17b-16e-instruct": ("🦙", "#00b894"),
    "gemma2-9b-it": ("💎", "#a259ec"),
    "llama-3.1-8b-instant": ("⚡", "#fdcb6e")
}
MODEL_DESCRIPTIONS = {
    "meta-llama/llama-4-maverick-17b-128e-instruct": "meta-llama/llama-4-maverick-17b-128e-instruct – Developed by Meta, this Llama 4 variant balances instruction-following and reasoning with strong real-world task generalization.",
    "meta-llama/llama-4-scout-17b-16e-instruct": "meta-llama/llama-4-scout-17b-16e-instruct – By Meta, this is a lighter, faster Llama 4 model optimized for low-latency responses and efficient serving in chat applications.",
    "gemma2-9b-it": "gemma2-9b-it – Created by Google DeepMind, this is an instruction-tuned version of the lightweight Gemma 2 model, optimized for helpful, safe conversational output.",
    "llama-3.1-8b-instant": "llama-3.1-8b-instant – From Meta, this is a compact, high-speed version of Llama 3.1 designed for fast inference and responsive chat in resource-constrained environments."
}

if "selected_model" not in st.session_state:
    st.session_state.selected_model = SUPPORTED_MODELS[0]
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history(st.session_state.selected_model)
if "response_times" not in st.session_state:
    st.session_state.response_times = []
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# --- Sidebar with animated icon and model selector ---
with st.sidebar:
    st.markdown("<div style='text-align:center; margin-bottom: 1.5em;'>"
                "<span style='font-size:2.5em; display:inline-block; transition: transform 0.2s; cursor:pointer;' "
                "onmouseover=\"this.style.transform='scale(1.15)'\" onmouseout=\"this.style.transform='scale(1)'\">"
                f"{MODEL_ICONS[st.session_state.selected_model][0]}"
                "</span>"
                "<div style='font-size:1.1em; margin-top:0.5em; color: #888;'>Current Model</div>"
                f"<div style='font-weight:600; color:{MODEL_ICONS[st.session_state.selected_model][1]}; margin-bottom:0.5em;'>"
                f"{st.session_state.selected_model.split('/')[-1]}"
                "</div>"
                "</div>", unsafe_allow_html=True)
    model = st.selectbox(
        "Switch model:",
        SUPPORTED_MODELS,
        index=SUPPORTED_MODELS.index(st.session_state.selected_model),
        key="model_select_box"
    )
    if model != st.session_state.selected_model:
        st.session_state.selected_model = model
        st.session_state.messages = load_chat_history(model)
        st.rerun()
    # Temperature adjuster
    st.markdown("### Temperature")
    st.session_state.temperature = st.slider(
        "Model creativity (temperature)",
        min_value=0.0, max_value=1.5, value=st.session_state.temperature, step=0.1,
        help="Higher values = more creative, lower = more focused/repetitive"
    )
    # Clear all histories button
    if st.button("🗑️ Clear All Chat Histories", use_container_width=True):
        clear_all_histories()
        st.session_state.messages = []
        st.session_state.response_times = []
        st.rerun()
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:gray; font-size:0.95em;'>"
        "Groq API Chatv1 - Nauman"
        "</div>", unsafe_allow_html=True
    )

# --- Main Chat Area ---
st.markdown("""
    <style>
    .chat-avatar {
        display: inline-block;
        width: 2.2em;
        height: 2.2em;
        border-radius: 50%;
        background: #23272f;
        color: #fff;
        text-align: center;
        line-height: 2.2em;
        font-size: 1.3em;
        margin-right: 0.7em;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .chat-bubble {
        display: inline-block;
        padding: 0.7em 1.1em;
        border-radius: 1.2em;
        margin-bottom: 0.2em;
        background: #23272f;
        color: #fff;
        animation: fadeIn 0.5s;
    }
    .chat-bubble.assistant {
        background: #1e293b;
        color: #aee6ff;
    }
    .chat-bubble.user {
        background: #4f8cff;
        color: #fff;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatInput input {
        font-size: 1.1em !important;
        padding: 0.7em 1em !important;
        border-radius: 1em !important;
        border: 1.5px solid #4f8cff !important;
        background: #181c24 !important;
        color: #fff !important;
    }
    .model-desc-card {
        background: #181c24;
        border-radius: 1.2em;
        padding: 0.7em 1em;
        margin: 1.2em auto 1.5em auto;
        max-width: 600px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.12);
        color: #fff;
        font-size: 0.98em;
        border-left: 6px solid #4f8cff;
        animation: fadeIn 0.5s;
    }
    .avg-response-time {
        color: #aee6ff;
        font-size: 0.98em;
        margin-top: 0.5em;
        margin-bottom: 1.2em;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Groq API Chatv1")
st.markdown("---")

# Welcome message if chat is empty
if not st.session_state.messages:
    color = MODEL_ICONS[st.session_state.selected_model][1]
    desc = MODEL_DESCRIPTIONS[st.session_state.selected_model]
    st.markdown(
        f"""
        <div style='text-align:center; margin-top:2em; margin-bottom:2em;'>
            <span style='font-size:2.5em;'>🤖</span><br>
            <span style='font-size:1.2em; color:#aaa;'>Welcome to GroqChatv1!<br>Start chatting with a blazing-fast LLM assistant.</span>
            <div class='model-desc-card' style='margin-top:2em; border-left: 6px solid {color};'>
                <span>{desc}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat display with avatars and bubbles
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    bubble_class = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(msg["role"]):
        st.markdown(
            f"<span class='chat-avatar'>{avatar}</span>"
            f"<span class='chat-bubble {bubble_class}'>"
            f"{msg['content']}"
            f"</span>", unsafe_allow_html=True)

# Show average response time
if st.session_state.response_times:
    avg_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
    st.markdown(f"<div class='avg-response-time'>Avg response time: <b>{avg_time:.2f}</b> sec</div>", unsafe_allow_html=True)

# Download button for chat history
if st.session_state.messages:
    st.download_button(
        label="⬇️ Download Conversation (JSON)",
        data=json.dumps(st.session_state.messages, indent=2, ensure_ascii=False),
        file_name="groqchatv1_history.json",
        mime="application/json",
        use_container_width=True
    )

# User input
user_input = st.chat_input("Type your message and press Enter...")

if user_input is not None:
    user_input = user_input.strip()
    if not user_input:
        st.warning("Please enter a message.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        save_chat_history(st.session_state.messages, st.session_state.selected_model)
        start_time = time.time()
        with st.spinner("GroqChatv1 is typing..."):
            response_text = ""
            response_generator = generate_response(
                st.session_state.messages,
                st.session_state.selected_model,
                stream=True,
                temperature=st.session_state.temperature
            )
            with st.chat_message("assistant"):
                response_container = st.empty()
                for token in response_generator:
                    response_text += token
                    response_container.markdown(
                        f"<span class='chat-avatar'>🤖</span>"
                        f"<span class='chat-bubble assistant'>{response_text}</span>",
                        unsafe_allow_html=True)
        elapsed = time.time() - start_time
        st.session_state.response_times.append(elapsed)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        save_chat_history(st.session_state.messages, st.session_state.selected_model)
        st.rerun()

st.markdown("<hr style='border:0; border-top:1.5px solid #222; margin:2em 0 1em 0;'>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center; color:gray; font-size:0.95em;'>"
    "🛠️ Made at Musketeers Tech"
    "</div>", unsafe_allow_html=True
) 