import streamlit as st
from gtts import gTTS
import google.generativeai as genai
import os
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Rythu Sahayakudu", page_icon="🌾", layout="wide")

# --- 1. SUPABASE DATABASE SETUP (FREE TIER) ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. USER AUTHENTICATION (Google Login) ---
# Streamlit Cloud supports user login via st.user
if not st.user.is_logged_in:
    st.title("🌾 Rythu Sahayakudu (రైతు సహాయకుడు)")
    st.caption("Developed by **Yaswanth Chowdary** | Free AI Agricultural Assistant")
    st.markdown("---")
    st.info("👋 Welcome! Please log in with your Google account to save your conversation history and access personalized farming advice.")
    
    if st.button("🔑 Log in with Google / Gmail", type="primary"):
        st.login()
    st.stop()

# Get logged-in user details
user_email = st.user.email
user_name = st.user.name

# --- 3. UI TRANSLATIONS DICTIONARY (22+ LANGUAGES) ---
UI_TRANSLATIONS = {
    "Telugu (తెలుగు)": {
        "code": "te",
        "title": "🌾 రైతు సహాయకుడు (Rythu Sahayakudu)",
        "caption": f"స్వాగతం, **{user_name}** | తయారు చేసినవారు: **యాస్వంత్ చౌదరి**",
        "select_lang": "భాషను ఎంచుకోండి:",
        "choose_mode": "ఇన్‌పుట్ మార్గాన్ని ఎంచుకోండి:",
        "mode_voice": "🎙️ వాయిస్ ద్వారా (మాట్లాడండి)",
        "mode_text": "✍️ టైప్ చేయడం ద్వారా",
        "voice_info": "మైక్ బటన్ నొక్కి మీ వ్యవసాయ ప్రశ్న మాట్లాడండి:",
        "text_placeholder": "మీ వ్యవసాయ ప్రశ్నను ఇక్కడ టైప్ చేయండి...",
        "btn_submit": "🤖 ఏఐ సలహా పొందండి & వినండి",
        "btn_new_chat": "➕ క్రొత్త సంభాషణ ప్రారంభించండి",
        "history_title": "📜 నా గత సంభాషణలు",
        "err_key": "Streamlit Secrets లో GEMINI_API_KEY నమోదు చేయండి!",
        "err_voice": "దయచేసి ముందుగా మీ ప్రశ్నను రికార్డ్ చేయండి!",
        "err_text": "దయచేసి ముందుగా మీ ప్రశ్నను టైప్ చేయండి!",
        "spinner": "ఏఐ మీ ప్రశ్నను విశ్లేషిస్తోంది...",
        "footer": "© 2026 **యాస్వంత్ చౌదరి** | భారతీయ రైతులకు అంకితం"
    },
    "Hindi (हिन्दी)": {
        "code": "hi",
        "title": "🌾 किसान सहायक (Rythu Sahayakudu)",
        "caption": f"स्वागत है, **{user_name}** | विकासकर्ता: **यसवंत चौधरी**",
        "select_lang": "भाषा चुनें:",
        "choose_mode": "इनपुट का तरीका चुनें:",
        "mode_voice": "🎙️ आवाज़ द्वारा (बोलें)",
        "mode_text": "✍️ लिखकर (टाइप करें)",
        "voice_info": "माइक बटन दबाएं और अपना कृषि प्रश्न बोलें:",
        "text_placeholder": "अपना कृषि प्रश्न यहाँ लिखें...",
        "btn_submit": "🤖 एआई सलाह प्राप्त करें और सुनें",
        "btn_new_chat": "➕ नई बातचीत शुरू करें",
        "history_title": "📜 मेरी पुरानी बातचीत",
        "err_key": "Streamlit Secrets में GEMINI_API_KEY जोड़ें!",
        "err_voice": "कृपया पहले अपनी आवाज़ रिकॉर्ड करें!",
        "err_text": "कृपया पहले अपना प्रश्न लिखें!",
        "spinner": "एआई आपके प्रश्न का विश्लेषण कर रहा है...",
        "footer": "© 2026 **यसवंत चौधरी** | भारतीय किसानों को समर्पित"
    },
    "English": {
        "code": "en",
        "title": "🌾 Rythu Sahayakudu (Farmer Assistant)",
        "caption": f"Welcome, **{user_name}** | Developed by **Yaswanth Chowdary**",
        "select_lang": "Select Language:",
        "choose_mode": "Choose Input Method:",
        "mode_voice": "🎙️ Voice Input (Record Audio)",
        "mode_text": "✍️️ Text Input (Type)",
        "voice_info": "Tap the mic button and speak your farming question:",
        "text_placeholder": "Type your farming question or follow-up here...",
        "btn_submit": "🤖 Get AI Advice & Listen",
        "btn_new_chat": "➕ Start New Chat",
        "history_title": "📜 Previous Conversations",
        "err_key": "Please add your GEMINI_API_KEY to Streamlit Secrets!",
        "err_voice": "Please record a voice message first!",
        "err_text": "Please type a question first!",
        "spinner": "AI is analyzing your query...",
        "footer": "© 2026 **Yaswanth Chowdary** | Dedicated to Indian Farmers"
    }
}

# --- 4. SIDEBAR: USER PROFILE & CHAT HISTORY ---
with st.sidebar:
    st.write(f"👤 **{user_name}**")
    st.caption(f"📧 {user_email}")
    if st.button("🚪 Log out"):
        st.logout()

    st.markdown("---")

    selected_lang_name = st.selectbox(
        "🌐 Select Language / భాషను ఎంచుకోండి:", 
        list(UI_TRANSLATIONS.keys())
    )
    t = UI_TRANSLATIONS.get(selected_lang_name, UI_TRANSLATIONS["English"])
    lang_code = t["code"]

    st.markdown("---")
    st.subheader(t["history_title"])

    # Load Saved Sessions from Database
    saved_chats = []
    if supabase:
        try:
            res = supabase.table("chat_history").select("session_id, title, created_at").eq("user_email", user_email).order("created_at", desc=True).execute()
            saved_chats = res.data
        except Exception:
            pass

    if st.button(t["btn_new_chat"], type="secondary", use_container_width=True):
        st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.rerun()

    # Display list of past conversations
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []

    for chat in saved_chats:
        chat_title = chat.get("title", f"Chat {chat['created_at'][:10]}")
        if st.button(f"💬 {chat_title}", key=chat["session_id"], use_container_width=True):
            st.session_state.current_session_id = chat["session_id"]
            # Fetch message history for selected session
            history_res = supabase.table("chat_messages").select("*").eq("session_id", chat["session_id"]).order("id", desc=False).execute()
            st.session_state.messages = [{"role": row["role"], "content": row["content"]} for row in history_res.data]
            st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
st.title(t["title"])
st.caption(t["caption"])
st.markdown("---")

# Render active session messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

st.markdown("---")

# Input Controls
input_mode_choice = st.radio(t["choose_mode"], [t["mode_voice"], t["mode_text"]])
audio_file_input = None
text_file_input = ""

if input_mode_choice == t["mode_voice"]:
    st.info(t["voice_info"])
    audio_file_input = st.audio_input("Record Audio")
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

                system_instruction = f"You are Rythu Sahayakudu, an AI agriculture helper created by Yaswanth Chowdary. Respond directly in {selected_lang_name}."
                
                # Format context
                history_prompt = system_instruction + "\n\nConversation Context:\n"
                for m in st.session_state.messages:
                    history_prompt += f"{m['role'].capitalize()}: {m['content']}\n"

                if input_mode_choice == t["mode_voice"]:
                    audio_bytes = audio_file_input.read()
                    audio_data = {"mime_type": audio_file_input.type, "data": audio_bytes}
                    response = model.generate_content([history_prompt, "Farmer's audio question:", audio_data])
                    user_msg_text = "🎙️ [Voice Question Received]"
                else:
                    response = model.generate_content(f"{history_prompt}\nFarmer's query: {text_file_input}")
                    user_msg_text = text_file_input

                advice_text = response.text

                # Save audio response
                audio_filename = f"response_{len(st.session_state.messages)}.mp3"
                try:
                    tts = gTTS(text=advice_text, lang=lang_code, slow=False)
                    tts.save(audio_filename)
                except Exception:
                    tts = gTTS(text=advice_text, lang="en", slow=False)
                    tts.save(audio_filename)

                # Save to Session State
                st.session_state.messages.append({"role": "user", "content": user_msg_text})
                st.session_state.messages.append({"role": "assistant", "content": advice_text})

                # Save session and messages to Supabase DB
                if supabase:
                    # Upsert chat session header
                    supabase.table("chat_history").upsert({
                        "session_id": st.session_state.current_session_id,
                        "user_email": user_email,
                        "title": user_msg_text[:30] + "...",
                        "created_at": datetime.now().isoformat()
                    }).execute()

                    # Save user & assistant messages
                    supabase.table("chat_messages").insert([
                        {"session_id": st.session_state.current_session_id, "role": "user", "content": user_msg_text},
                        {"session_id": st.session_state.current_session_id, "role": "assistant", "content": advice_text}
                    ]).execute()

                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown(t["footer"])
