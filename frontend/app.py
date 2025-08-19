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
    page_title="One Piece Chatbot ▬▬ι═══════ﺤ", page_icon="🏴‍☠️", layout="centered"
)

# ---------------------------
# Background image
# ---------------------------
image_path = "assets/one-piece-luffys-straw-hat-desktop-wallpaper-preview (1).jpg"
image = Image.open(image_path)
img_bytes = io.BytesIO()
image.save(img_bytes, format="JPEG")
encoded_bg = base64.b64encode(img_bytes.getvalue()).decode()
default_background = f"data:image/jpeg;base64,{encoded_bg}"

# Upload background
st.sidebar.title("Background Image")
uploaded_file = st.sidebar.file_uploader(
    "Upload your background (jpg/png)", type=["jpg", "jpeg", "png"]
)
if uploaded_file:
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption="Uploaded Background", use_container_width=True)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    encoded_bg = base64.b64encode(img_bytes.getvalue()).decode()
    bg_url = f"data:image/png;base64,{encoded_bg}"
else:
    bg_url = default_background

# ---------------------------
# Apply CSS
# ---------------------------
st.markdown(
    f"""
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
        max-width: 100%;
        margin: 5px 0px;
        font-weight: bold;
    }}
    .chat-bot {{
        background-color: white;
        color: #967bb6;
        padding: 8px 12px;
        border-radius: 15px;
        max-width: 100%;
        margin: 5px 0px;
        font-weight: bold;
    }}
    .stTextInput label {{
        color: white;
        font-weight: bold;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Header
# ---------------------------
st.markdown(
    "<h1 style='text-align: center; color: #ffcc00;'>One Piece Chatbot ▬▬ι═══════ﺤ</h1>",
    unsafe_allow_html=True,
)
st.write(
    "<p style='color: white;'>Ask questions and get answers from the AI powered by Amazon Bedrock.</p>",
    unsafe_allow_html=True,
)

# ---------------------------
# Initialize session state
# ---------------------------
if "all_chats" not in st.session_state:
    st.session_state.all_chats = [[]]
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = 0

# System message (Luffy personality)
system_prompt = "You are an anime character from One Piece, namely Monkey D. Luffy. Respond in a pirate way, full of energy, adventure, and mischief. Always stay in character as Luffy."


# ---------------------------
# Functions
# ---------------------------
def add_message(role, message):
    if not st.session_state.all_chats:
        st.session_state.all_chats.append([])
        st.session_state.current_chat_index = 0
    st.session_state.all_chats[st.session_state.current_chat_index].append(
        {"role": role, "message": message}
    )


def new_chat():
    st.session_state.all_chats.append([])
    st.session_state.current_chat_index = len(st.session_state.all_chats) - 1
    st.rerun()


def delete_current_chat():
    if st.session_state.all_chats:
        st.session_state.all_chats.pop(st.session_state.current_chat_index)
        st.current_chat_index = max(0, len(st.session_state.all_chats) - 1)
        if not st.session_state.all_chats:
            st.session_state.all_chats.append([])
        st.rerun()


# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.title("Chats")
if st.sidebar.button("New Chat"):
    new_chat()
if st.sidebar.button("Delete Current Chat"):
    delete_current_chat()

# Dropdown to select chat
if st.session_state.all_chats:
    chat_titles = [f"Chat {i+1}" for i in range(len(st.session_state.all_chats))]
    st.session_state.current_chat_index = st.sidebar.selectbox(
        "Select chat",
        range(len(st.session_state.all_chats)),
        index=st.session_state.current_chat_index,
        format_func=lambda x: chat_titles[x],
    )

# ---------------------------
# Display chat history
# ---------------------------
st.markdown("<h3 style=' color: white;'>Chat History</h3>", unsafe_allow_html=True)
current_chat = st.session_state.all_chats[st.session_state.current_chat_index]
if current_chat:
    for chat in current_chat:
        if chat["role"] == "user":
            st.markdown(
                f"<div class='chat-user'>You: {chat['message']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='chat-bot'>Luffy: {chat['message']}</div>",
                unsafe_allow_html=True,
            )
else:
    st.info("No messages in this chat. Start chatting!")

# ---------------------------
# Chat input
# ---------------------------
user_input = st.text_input("Your question:")

col1, col2 = st.columns([3, 1])

with col1:
    if st.button("Send") and user_input:
        add_message("user", user_input)
        try:
            response = requests.post(
                "http://backend:8000/chat",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"query": user_input, "system": system_prompt}),
            )

            bot_response = "⚠️ Bot gave an empty response."
            if response.status_code == 200:
                resp_json = response.json()
                if "response" in resp_json and resp_json["response"]:
                    try:
                        parsed = json.loads(resp_json["response"])
                        if "content" in parsed and parsed["content"]:
                            bot_response = parsed["content"][0].get(
                                "text", bot_response
                            )
                    except json.JSONDecodeError:
                        bot_response = (
                            f"⚠️ Response not valid JSON: {resp_json['response']}"
                        )
            else:
                bot_response = f"❌ Error {response.status_code}: {response.text}"

            add_message("bot", bot_response)

        except requests.exceptions.RequestException as e:
            add_message("bot", f"🚫 Failed to connect to backend: {e}")

        st.rerun()

# ---------------------------
# MP3 Player
# ---------------------------
with col2:
    play_song = st.button("▶️Play Brook's Song")
if play_song:
    audio_file = open("assets/song.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3")
