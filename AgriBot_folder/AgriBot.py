
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from deep_translator import GoogleTranslator

# --- Configure Gemini API ---
genai.configure(api_key="your api key")  # Replace with your Gemini API key
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Streamlit Page Config ---
st.set_page_config(page_title="🌾 AgriBot", page_icon="🌱", layout="centered")
st.markdown("<h1 style='text-align: center;'>🌾 AgriBot – AI Agriculture Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ask me about crops, soil, fertilizers, diseases & more!</p>", unsafe_allow_html=True)

# --- Custom CSS for Chat Bubbles ---
st.markdown("""
    <style>
    .chat-bubble {
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 10px;
        font-size: 16px;
        line-height: 1.5;
    }
    .user-bubble {
        background-color: #e6f7ff;
        text-align: left;
        border-left: 5px solid #1890ff;
    }
    .bot-bubble {
        background-color: #fffbe6;
        text-align: left;
        border-left: 5px solid #faad14;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Language Selection ---
language_map = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Punjabi (ਪੰਜਾਬੀ)": "pa"
}
selected_language = st.selectbox("🌐 Choose Reply Language", list(language_map.keys()), index=0)
target_lang = language_map[selected_language]

# --- Translate Output ---
def translate_text(text, lang_code):
    if lang_code == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=lang_code).translate(text)
    except Exception as e:
        return f"Translation error: {e}"

# --- Gemini Response ---
def generate_response(user_query):
    prompt = f"""
You are AgriBot, an expert AI assistant in agriculture.
Answer the following question clearly and simply.

Question: {user_query}

Respond with helpful advice for Indian farmers. Mention crops, weather, soil, fertilizers, diseases, and best practices as needed.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# --- Voice Input ---
def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎤 Listening... Speak now")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError:
        return "Speech recognition is unavailable."

# --- Chat Input Section ---
with st.container():
    cols = st.columns([4, 1])
    user_input = cols[0].text_input("💬 Type your question:", key="text_input")
    if cols[1].button("🎤", use_container_width=True):
        user_input = recognize_speech()
        st.success(f"You said: {user_input}")

# --- Process and Show Reply ---
if user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.spinner("AgriBot is thinking..."):
        reply = generate_response(user_input)
        translated_reply = translate_text(reply, target_lang)
        st.session_state.chat_history.append(("bot", translated_reply))

# --- Display Chat History with Chat Bubbles ---
st.divider()
for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-bubble user-bubble'>🧑‍🌾 <strong>You:</strong><br>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble bot-bubble'>🤖 <strong>AgriBot:</strong><br>{message}</div>", unsafe_allow_html=True)
