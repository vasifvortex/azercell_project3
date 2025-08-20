import base64
import io
import json
import requests
import streamlit as st
from PIL import Image

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="One Piece Chatbot ▬▬ι═══════ﺤ",
    page_icon="🏴‍☠️",
    layout="centered",
)

# ---------------------------
# Background
# ---------------------------
image_path = "assets/one-piece-luffys-straw-hat-desktop-wallpaper-preview (1).jpg"
image = Image.open(image_path)
img_bytes = io.BytesIO()
image.save(img_bytes, format="JPEG")
encoded_bg = base64.b64encode(img_bytes.getvalue()).decode()
default_background = f"data:image/jpeg;base64,{encoded_bg}"

st.sidebar.title("Background Image")
uploaded_file = st.sidebar.file_uploader("Upload your background (jpg/png)", type=["jpg","jpeg","png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Uploaded Background", use_container_width=True)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    encoded_bg = base64.b64encode(img_bytes.getvalue()).decode()
    bg_url = f"data:image/png;base64,{encoded_bg}"
else:
    bg_url = default_background

st.markdown(f"""
<style>
.stApp {{
    background-image: url("{bg_url}");
    background-size: cover;
    background-attachment: fixed;
}}
.chat-user {{
    background-color: #ffcc00;
    color: #526bb5;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 5px 0px;
    font-weight: bold;
}}
.chat-bot {{
    background-color: white;
    color: #967bb6;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 5px 0px;
    font-weight: bold;
}}
.stTextInput label {{
    color: white;
    font-weight: bold;

}}
</style>
""", unsafe_allow_html=True)
# ---------------------------
# Header
# ---------------------------
st.markdown("<h1 style='text-align:center;color:#ffcc00;'>One Piece Chatbot ▬▬ι═══════ﺤ</h1>", unsafe_allow_html=True)
st.write("<p style='color:white;'>Ask questions and get answers from the AI powered by Amazon Bedrock.</p>", unsafe_allow_html=True)

# ---------------------------
# Session state initialization
# ---------------------------
if "all_chats" not in st.session_state:
    st.session_state.all_chats = [[]]
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = 0
if "music_playing" not in st.session_state:
    st.session_state.music_playing = False
if "user_input_cache" not in st.session_state:
    st.session_state.user_input_cache = ""
if "bot_streaming_text" not in st.session_state:
    st.session_state.bot_streaming_text = ""

system_prompt = "You are Monkey D. Luffy from One Piece. Respond in a pirate way, full of energy and adventure."

# ---------------------------
# Helper function
# ---------------------------
def add_message(role, message=""):
    msg = {"role": role, "message": message}
    st.session_state.all_chats[st.session_state.current_chat_index].append(msg)
    return msg

# ---------------------------
# Sidebar: Chat management & Music
# ---------------------------
st.sidebar.title("Chats")

# Chat management
if st.sidebar.button("New Chat"):
    st.session_state.all_chats.append([])
    st.session_state.current_chat_index = len(st.session_state.all_chats) - 1

if st.sidebar.button("Delete Current Chat") and st.session_state.all_chats:
    st.session_state.all_chats.pop(st.session_state.current_chat_index)
    st.session_state.current_chat_index = max(0, len(st.session_state.all_chats) - 1)
    if not st.session_state.all_chats:
            st.session_state.all_chats.append([])
       
if st.session_state.all_chats:
    chat_titles = [f"Chat {i+1}" for i in range(len(st.session_state.all_chats))]
    st.session_state.current_chat_index = st.sidebar.selectbox(
        "Select chat",
        range(len(st.session_state.all_chats)),
        index=st.session_state.current_chat_index,
        format_func=lambda x: chat_titles[x]
    )
# ---------------------------
# Layout: Chat
# ---------------------------

st.markdown("<h3 style='color:white;'>Chat History</h3>", unsafe_allow_html=True)
chat_container = st.container()
current_chat = st.session_state.all_chats[st.session_state.current_chat_index]

# Display full chat history
for chat in current_chat:
    style = "chat-user" if chat["role"] == "user" else "chat-bot"
    chat_name = "You" if chat["role"] == "user" else "Luffy"
    chat_container.markdown(f"<div class='{style}'>{chat_name}: {chat['message']}</div>", unsafe_allow_html=True)

# Chat input
user_input = st.text_input("Your question:", value=st.session_state.user_input_cache, key="user_input")
col1, col2 = st.columns([3, 1])
with col1:
    send_clicked = st.button("Send")

    if send_clicked and user_input.strip():
        # Clear the input box immediately
        st.session_state.user_input_cache = ""

        # Add user message
        add_message("user", user_input)
        chat_container.markdown(f"<div class='chat-user'>You: {user_input}</div>", unsafe_allow_html=True)

        # Placeholder for bot streaming response
        bot_placeholder = chat_container.empty()
        st.session_state.bot_streaming_text = ""

        try:
            with requests.post(
                "http://backend:8000/chat",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"query": user_input, "system": system_prompt}),
                stream=True
            ) as resp:
                if resp.status_code != 200:
                    bot_placeholder.markdown(f"❌ Error {resp.status_code}: {resp.text}")
                else:
                    for chunk in resp.iter_content(chunk_size=None):
                        if chunk:
                            st.session_state.bot_streaming_text += chunk.decode("utf-8")
                            # Always display Luffy as bot name
                            bot_placeholder.markdown(
                                f"<div class='chat-bot'>Luffy: {st.session_state.bot_streaming_text}</div>",
                                unsafe_allow_html=True
                            )

            # Save final bot message with role "luffy"
            add_message("luffy", st.session_state.bot_streaming_text)
            st.session_state.bot_streaming_text = ""

        except Exception as e:
            bot_placeholder.markdown(f"🚫 Failed: {e}")
# ---------------------------
# MP3 Player
# ---------------------------
with col2:
    if st.button("▶️Play Brook's Song"):
        st.session_state.music_playing = not st.session_state.music_playing
if st.session_state.music_playing:
    with open("assets/song.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read() 
        st.audio(audio_bytes, format="audio/mp3", start_time=0)