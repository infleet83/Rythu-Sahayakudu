import streamlit as st
from gtts import gTTS
import google.generativeai as genai
import os

# Page title & config
st.set_page_config(page_title="Rythu Sahayakudu", page_icon="🌾")

# 1. UI Translations Dictionary for Supported Languages
UI_TRANSLATIONS = {
    "Telugu (తెలుగు)": {
        "code": "te",
        "title": "🌾 రైతు సహాయకుడు (Rythu Sahayakudu)",
        "caption": "తయారు చేసినవారు: **యాస్వంత్ చౌదరి** | ఉచిత ఏఐ వ్యవసాయ సహాయకుడు",
        "select_lang": "భాషను ఎంచుకోండి:",
        "choose_mode": "ఇన్‌పుట్ మార్గాన్ని ఎంచుకోండి:",
        "mode_voice": "🎙️️ వాయిస్ ద్వారా (మాట్లాడండి)",
        "mode_text": "✍️ టైప్ చేయడం ద్వారా",
        "voice_info": "కింది మైక్రోఫోన్ బటన్ నొక్కి మీ వ్యవసాయ ప్రశ్నను స్పష్టంగా చెప్పండి:",
        "text_placeholder": "ఉదాహరణ: వరి చేనులో ఆకులు పసుపు రంగులోకి మారుతున్నాయి, ఏమి చేయాలి?",
        "btn_submit": "🤖 ఉచిత ఏఐ సలహా పొందండి & వినండి",
        "err_key": "దయచేసి Streamlit Secrets లో GEMINI_API_KEY నమోదు చేయండి!",
        "err_voice": "దయచేసి ముందుగా మీ ప్రశ్నను రికార్డ్ చేయండి!",
        "err_text": "దయచేసి ముందుగా మీ ప్రశ్నను టైప్ చేయండి!",
        "spinner": "ఏఐ మీ వ్యవసాయ ప్రశ్నను విశ్లేషిస్తోంది...",
        "advice_header": "💡 వ్యవసాయ సలహా:",
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
        "voice_info": "नीचे दिए गए माइक बटन को दबाएं और अपना कृषि प्रश्न स्पष्ट रूप से बोलें:",
        "text_placeholder": "उदाहरण: धान के पत्तों में पीलापन आ रहा है, क्या करें?",
        "btn_submit": "🤖 एआई सलाह प्राप्त करें और सुनें",
        "err_key": "कृपया Streamlit Secrets में GEMINI_API_KEY जोड़ें!",
        "err_voice": "कृपया पहले अपनी आवाज़ रिकॉर्ड करें!",
        "err_text": "कृपया पहले अपना प्रश्न लिखें!",
        "spinner": "एआई आपके कृषि प्रश्न का विश्लेषण कर रहा है...",
        "advice_header": "💡 कृषि सलाह:",
        "footer": "© 2026 **यसवंत चौधरी** | भारतीय किसानों को समर्पित"
    },
    "Tamil (தமிழ்)": {
        "code": "ta",
        "title": "🌾 உழவன் உதவியாளர் (Rythu Sahayakudu)",
        "caption": "உருவாக்கியவர்: **யஷ்வந்த் சவுத்ரி** | இலவச AI விவசாய உதவியாளர்",
        "select_lang": "மொழியைத் தேர்ந்தெடுக்கவும்:",
        "choose_mode": "உள்ளீட்டு முறையைத் தேர்ந்தெடுக்கவும்:",
        "mode_voice": "🎙️ குரல் மூலம் (பேசவும்)",
        "mode_text": "✍️ தட்டச்சு மூலம்",
        "voice_info": "மைக்கை அழுத்தி உங்கள் விவசாயக் கேள்வியைப் பேசுங்கள்:",
        "text_placeholder": "எடுத்துக்காட்டு: நெல் பயிரில் இலைகள் மஞ்சளாக மாறினால் என்ன செய்வது?",
        "btn_submit": "🤖 AI ஆலோசனையைப் பெற்று கேட்கவும்",
        "err_key": "Streamlit Secrets இல் GEMINI_API_KEY ஐச் சேர்க்கவும்!",
        "err_voice": "தயவுசெய்து முதலில் உங்கள் குரலைப் பதிவு செய்யவும்!",
        "err_text": "தயவுசெய்து முதலில் உங்கள் கேள்வியைத் தட்டச்சு செய்யவும்!",
        "spinner": "AI உங்கள் கேள்வியை பகுப்பாய்வு செய்கிறது...",
        "advice_header": "💡 விவசாய ஆலோசனை:",
        "footer": "© 2026 **யஷ்வந்த் சவுத்ரி** | இந்திய விவசாயிகளுக்கு அர்ப்பணிக்கப்பட்டது"
    },
    "Kannada (ಕನ್ನಡ)": {
        "code": "kn",
        "title": "🌾 ರೈತ ಸಹಾಯಕ (Rythu Sahayakudu)",
        "caption": "ರೂಪಿಸಿದವರು: **ಯಶವಂತ್ ಚೌಧರಿ** | ಉಚಿತ AI ಕೃಷಿ ಸಹಾಯಕ",
        "select_lang": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "choose_mode": "ಇನ್‌ಪುಟ್ ವಿಧಾನವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "mode_voice": "🎙️ ಧ್ವನಿ ಮೂಲಕ (ಮಾತನಾಡಿ)",
        "mode_text": "✍️ ಟೈಪ್ ಮಾಡುವ ಮೂಲಕ",
        "voice_info": "ಮೈಕ್ ಬಟನ್ ಒತ್ತಿ ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ:",
        "text_placeholder": "ಉದಾಹರಣೆಗೆ: ಭತ್ತದ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ, ಏನು ಮಾಡಬೇಕು?",
        "btn_submit": "🤖 AI ಸಲಹೆ ಪಡೆಯಿರಿ ಮತ್ತು ಆಲಿಸಿ",
        "err_key": "Streamlit Secrets ನಲ್ಲಿ GEMINI_API_KEY ಸೇರಿಸಿ!",
        "err_voice": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಧ್ವನಿಯನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ!",
        "err_text": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ!",
        "spinner": "AI ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...",
        "advice_header": "💡 ಕೃಷಿ ಸಲಹೆ:",
        "footer": "© 2026 **ಯಶವಂತ್ ಚೌಧರಿ** | ಭಾರತೀಯ ರೈತರಿಗೆ ಅರ್ಪಿತ"
    },
    "English": {
        "code": "en",
        "title": "🌾 Rythu Sahayakudu (Farmer Assistant)",
        "caption": "Developed by **Yaswanth Chowdary** | Free Open-Source AI Farming Assistant",
        "select_lang": "Select Language:",
        "choose_mode": "Choose Input Method:",
        "mode_voice": "🎙️ Voice Input (Record Audio)",
        "mode_text": "✍️ Text Input (Type)",
        "voice_info": "Tap the microphone below and speak your farming question clearly:",
        "text_placeholder": "e.g., How to treat leaf yellowing in paddy crop?",
        "btn_submit": "🤖 Get AI Advice & Listen",
        "err_key": "Please add your GEMINI_API_KEY to Streamlit Secrets!",
        "err_voice": "Please record a voice message first!",
        "err_text": "Please type a question first!",
        "spinner": "AI is analyzing your farming query...",
        "advice_header": "💡 Farming Advice:",
        "footer": "© 2026 **Yaswanth Chowdary** | Dedicated to Indian Farmers"
    }
}

# 2. Language Selection Dropdown
selected_lang_name = st.selectbox(
    "Select Language / భాషను ఎంచుకోండి / भाषा चुनें:", 
    list(UI_TRANSLATIONS.keys())
)

# Fetch translated UI strings for chosen language
t = UI_TRANSLATIONS[selected_lang_name]
lang_code = t["code"]

# Header & Creator Credit (Translated)
st.title(t["title"])
st.caption(t["caption"])

st.markdown("---")

# Input Method Selection (Translated)
input_mode_choice = st.radio(
    t["choose_mode"], 
    [t["mode_voice"], t["mode_text"]]
)

audio_file_input = None
text_file_input = ""

if input_mode_choice == t["mode_voice"]:
    st.info(t["voice_info"])
    audio_file_input = st.audio_input("Record Audio")
else:
    text_file_input = st.text_area("Type Question:", placeholder=t["text_placeholder"])

# Fetch API Key securely
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

                system_prompt = f"You are an agricultural expert helping an Indian farmer. Answer clearly, simply, and directly in {selected_lang_name} language."

                if input_mode_choice == t["mode_voice"]:
                    audio_bytes = audio_file_input.read()
                    audio_data = {
                        "mime_type": audio_file_input.type,
                        "data": audio_bytes
                    }
                    response = model.generate_content([system_prompt, audio_data])
                else:
                    response = model.generate_content(f"{system_prompt}\nFarmer Question: {text_file_input}")

                advice_text = response.text

                # Display Text Advice (Translated Header)
                st.markdown(f"### {t['advice_header']}")
                st.write(advice_text)

                # Convert text answer to spoken audio
                audio_output_path = "advice_output.mp3"
                try:
                    tts = gTTS(text=advice_text, lang=lang_code, slow=False)
                    tts.save(audio_output_path)
                except Exception:
                    tts = gTTS(text=advice_text, lang="en", slow=False)
                    tts.save(audio_output_path)

                st.audio(audio_output_path, format="audio/mp3")

            except Exception as e:
                st.error(f"Error processing query: {str(e)}")

# Footer Credit (Translated)
st.divider()
st.markdown(t["footer"])
