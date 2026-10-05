import streamlit as st
from gtts import gTTS
import google.generativeai as genai
import os

st.set_page_config(page_title="Rythu Sahayakudu", page_icon="🌾")

# 1. UI Translations Dictionary
UI_TRANSLATIONS = {
    "Telugu (తెలుగు)": {
        "code": "te",
        "title": "🌾 రైతు సహాయకుడు (Rythu Sahayakudu)",
        "caption": "తయారు చేసినవారు: **యాస్వంత్ చౌదరి** | ఉచిత ఏఐ వ్యవసాయ సహాయకుడు",
        "select_lang": "భాషను ఎంచుకోండి:",
        "choose_mode": "ఇన్‌పుట్ మార్గాన్ని ఎంచుకోండి:",
        "mode_voice": "🎙️ వాయిస్ ద్వారా (మాట్లాడండి)",
        "mode_text": "✍️ టైప్ చేయడం ద్వారా",
        "voice_info": "మైక్ బటన్ నొక్కి మీ వ్యవసాయ ప్రశ్న లేదా తదుపరి ప్రశ్న (Follow-up) మాట్లాడండి:",
        "text_placeholder": "మీ వ్యవసాయ ప్రశ్న లేదా తదుపరి ప్రశ్నను ఇక్కడ టైప్ చేయండి...",
        "btn_submit": "🤖 ఏఐ సలహా పొందండి & వినండి",
        "btn_clear": "🔄 క్రొత్త సంభాషణ ప్రారంభించండి (Clear Chat)",
        "err_key": "దయచేసి Streamlit Secrets లో GEMINI_API_KEY నమోదు చేయండి!",
        "err_voice": "దయచేసి ముందుగా మీ ప్రశ్నను రికార్డ్ చేయండి!",
        "err_text": "దయచేసి ముందుగా మీ ప్రశ్నను టైప్ చేయండి!",
        "spinner": "ఏఐ మీ ప్రశ్నను విశ్లేషిస్తోంది...",
        "chat_history_header": "💬 సంభాషణ చరిత్ర (Conversation History):",
        "footer": "© 2026 **యాస్వంత్ చౌదరి** | భారతీయ రైతులకు అంకితం"
    },
    "Hindi (हिन्दी)": {
        "code": "hi",
        "title": "🌾 किसान सहायक (Rythu Sahayakudu)",
        "caption": "विकासकर्ता: **यसवंत चौधरी** | मुफ़्त एआई कृषि सहायक",
        "select_lang": "भाषा चुनें:",
        "choose_mode": "इनपुट का तरीका चुनें:",
        "mode_voice": "🎙️ आवाज़ द्वारा (बोलें)",
        "mode_text": "✍️ लिखकर (टाइप करें)",
        "voice_info": "माइक बटन दबाएं और अपना प्रश्न या अगला सवाल (Follow-up) बोलें:",
        "text_placeholder": "अपना प्रश्न या अगला सवाल यहाँ लिखें...",
        "btn_submit": "🤖 एआई सलाह प्राप्त करें और सुनें",
        "btn_clear": "🔄 नई बातचीत शुरू करें (Clear Chat)",
        "err_key": "कृपया Streamlit Secrets में GEMINI_API_KEY जोड़ें!",
        "err_voice": "कृपया पहले अपनी आवाज़ रिकॉर्ड करें!",
        "err_text": "कृपया पहले अपना प्रश्न लिखें!",
        "spinner": "एआई आपके प्रश्न का विश्लेषण कर रहा है...",
        "chat_history_header": "💬 बातचीत का इतिहास (Conversation History):",
        "footer": "© 2026 **यसवंत चौधरी** | भारतीय किसानों को समर्पित"
    },
    "English": {
        "code": "en",
        "title": "🌾 Rythu Sahayakudu (Farmer Assistant)",
        "caption": "Developed by **Yaswanth Chowdary** | Free Open-Source AI Farming Assistant",
        "select_lang": "Select Language:",
        "choose_mode": "Choose Input Method:",
        "mode_voice": "🎙️ Voice Input (Record Audio)",
        "mode_text": "✍️ Text Input (Type)",
        "voice_info": "Tap the mic button and speak your question or follow-up:",
        "text_placeholder": "Type your question or follow-up here...",
        "btn_submit": "🤖 Get AI Advice & Listen",
        "btn_clear": "🔄 Start New Conversation",
        "err_key": "Please add your GEMINI_API_KEY to Streamlit Secrets!",
        "err_voice": "Please record a voice message first!",
        "err_text": "Please type a question first!",
        "spinner": "AI is analyzing your query...",
        "chat_history_header": "💬 Conversation History:",
        "footer": "© 2026 **Yaswanth Chowdary** | Dedicated to Indian Farmers"
    }
}

# Select Language
selected_lang_name = st.selectbox(
    "Select Language / భాషను ఎంచుకోండి / भाषा चुनें:", 
    list(UI_TRANSLATIONS.keys())
)

t = UI_TRANSLATIONS[selected_lang_name]
lang_code = t["code"]

# Render Header
st.title(t["title"])
st.caption(t["caption"])
st.markdown("---")

# Initialize Chat Memory in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Button to reset chat session
if st.button(t["btn_clear"]):
    st.session_state.messages = []
    st.rerun()

# Display Chat History
if st.session_state.messages:
    st.markdown(f"### {t['chat_history_header']}")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "audio" in msg and msg["audio"]:
                st.audio(msg["audio"], format="audio/mp3")

st.markdown("---")

# Input Mode Choice
input_mode_choice = st.radio(
    t["choose_mode"], 
    [t["mode_voice"], t["mode_text"]]
)

audio_file_input = None
text_file_input = ""

if input_mode_choice == t["mode_voice"]:
    st.info(t["voice_info"])
    audio_file_input = st.audio_input("Record Audio / వాయిస్ రికార్డ్ చేయండి")
else:
    text_file_input = st.text_area("Question / Follow-up:", placeholder=t["text_placeholder"])

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

if st.button(t["btn_submit"], type="primary"):
    if not GEMINI_API_KEY:
        st.error(t["err_key"])
    elif input_mode_choice == t["mode_voice"] and not audio_file_input:
        st.warning(t["err_voice"])
    elif input_mode_choice == t["mode_text"] and not text_file_input.strip():
        st.warning(t["err_text"])
    else:
        with st.spinner(t["spinner"]):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')

                # System context prompt
                system_instruction = (
                    f"You are an agricultural expert named Rythu Sahayakudu created by Yaswanth Chowdary. "
                    f"You are conversing with an Indian farmer in {selected_lang_name}. "
                    f"Keep your response concise, helpful, and directly in {selected_lang_name}."
                )

                # Format conversation history for Gemini context
                history_prompt = system_instruction + "\n\nConversation so far:\n"
                for m in st.session_state.messages:
                    history_prompt += f"{m['role'].capitalize()}: {m['content']}\n"

                if input_mode_choice == t["mode_voice"]:
                    audio_bytes = audio_file_input.read()
                    audio_data = {
                        "mime_type": audio_file_input.type,
                        "data": audio_bytes
                    }
                    prompt_parts = [history_prompt, "Farmer's new audio question:", audio_data]
                    response = model.generate_content(prompt_parts)
                    user_msg_text = "🎙️ [Voice Question Received]"
                else:
                    prompt_parts = f"{history_prompt}\nFarmer's new question: {text_file_input}"
                    response = model.generate_content(prompt_parts)
                    user_msg_text = text_file_input

                advice_text = response.text

                # Generate TTS for AI response
                audio_filename = f"response_{len(st.session_state.messages)}.mp3"
                try:
                    tts = gTTS(text=advice_text, lang=lang_code, slow=False)
                    tts.save(audio_filename)
                except Exception:
                    tts = gTTS(text=advice_text, lang="en", slow=False)
                    tts.save(audio_filename)

                # Store user message and AI response in session history
                st.session_state.messages.append({"role": "user", "content": user_msg_text})
                st.session_state.messages.append({"role": "assistant", "content": advice_text, "audio": audio_filename})

                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown(t["footer"])
