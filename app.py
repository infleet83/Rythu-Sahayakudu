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
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase Connection Error: {str(e)}")

# --- 2. USER AUTHENTICATION & IDENTITY ---
user_logged_in = False
user_email = ""
user_name = ""

try:
    if hasattr(st, "user") and getattr(st.user, "is_logged_in", False):
        user_logged_in = True
        user_email = st.user.email
        user_name = st.user.name
except Exception:
    user_logged_in = False

if not user_logged_in:
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
        st.session_state.user_name = ""

    if not st.session_state.user_email:
        st.title("🌾 Rythu Sahayakudu (రైతు సహాయకుడు)")
        st.caption("Developed by **Yaswanth Chowdary** | Free Open-Source AI Agricultural Assistant")
        st.markdown("---")
        st.info("👋 Welcome! Please enter your email or mobile number to save and load your conversation history.")
        
        input_email = st.text_input("Enter Email ID or Phone Number:", placeholder="farmer@gmail.com")
        if st.button("🚀 Continue to App", type="primary"):
            if input_email.strip():
                st.session_state.user_email = input_email.strip()
                st.session_state.user_name = input_email.split("@")[0].capitalize()
                st.rerun()
            else:
                st.warning("Please enter a valid identifier.")
        st.stop()
    else:
        user_email = st.session_state.user_email
        user_name = st.session_state.user_name

# --- 3. UI TRANSLATIONS DICTIONARY (22 SCHEDULED INDIAN LANGUAGES + ENGLISH) ---
UI_TRANSLATIONS = {
    "Telugu (తెలుగు)": {
        "code": "te",
        "title": "🌾 రైతు సహాయకుడు (Rythu Sahayakudu)",
        "caption": f"స్వాగతం, **{user_name}** | తయారు చేసినవారు: **యాస్వంత్ చౌదరి**",
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
    "Bengali (বাংলা)": {
        "code": "bn",
        "title": "🌾 কৃষক সহায়ক (Rythu Sahayakudu)",
        "caption": f"স্বাগতম, **{user_name}** | প্রস্তুতকারক: **যশোবন্ত চৌধুরী**",
        "choose_mode": "ইনপুট পদ্ধতি নির্বাচন করুন:",
        "mode_voice": "🎙️ ভয়েস দ্বারা (বলুন)",
        "mode_text": "✍️ টাইপ করে",
        "voice_info": "মাইক বোতাম টিপে আপনার কৃষি প্রশ্ন বলুন:",
        "text_placeholder": "আপনার কৃষি প্রশ্ন এখানে লিখুন...",
        "btn_submit": "🤖 এআই পরামর্শ পান এবং শুনুন",
        "btn_new_chat": "➕ নতুন কথোপকথন শুরু করুন",
        "history_title": "📜 পূর্ববর্তী কথোপকথন",
        "err_key": "Streamlit Secrets-এ GEMINI_API_KEY যোগ করুন!",
        "err_voice": "দয়া করে প্রথমে আপনার প্রশ্ন রেকর্ড করুন!",
        "err_text": "দয়া করে প্রথমে আপনার প্রশ্ন টাইপ করুন!",
        "spinner": "এআই আপনার প্রশ্ন বিশ্লেষণ করছে...",
        "footer": "© 2026 **যশোবন্ত চৌধুরী** | ভারতীয় কৃষকদের উদ্দেশ্যে উৎসর্গীকৃত"
    },
    "Tamil (தமிழ்)": {
        "code": "ta",
        "title": "🌾 உழவன் உதவியாளர் (Rythu Sahayakudu)",
        "caption": f"வரவேற்கிறோம், **{user_name}** | உருவாக்கியவர்: **யஷ்வந்த் சவுத்ரி**",
        "choose_mode": "உள்ளீட்டு முறையைத் தேர்ந்தெடுக்கவும்:",
        "mode_voice": "🎙️ குரல் மூலம் (பேசவும்)",
        "mode_text": "✍️ தட்டச்சு மூலம்",
        "voice_info": "மைக்கை அழுத்தி உங்கள் விவசாயக் கேள்வியைப் பேசுங்கள்:",
        "text_placeholder": "உங்கள் கேள்வியை இங்கே தட்டச்சு செய்யவும்...",
        "btn_submit": "🤖 AI ஆலோசனையைப் பெற்று கேட்கவும்",
        "btn_new_chat": "➕ புதிய உரையாடலைத் தொடங்கவும்",
        "history_title": "📜 முந்தைய உரையாடல்கள்",
        "err_key": "Streamlit Secrets இல் GEMINI_API_KEY ஐச் சேர்க்கவும்!",
        "err_voice": "தயவுசெய்து முதலில் உங்கள் குரலைப் பதிவு செய்யவும்!",
        "err_text": "தயவுசெய்து முதலில் உங்கள் கேள்வியைத் தட்டச்சு செய்யவும்!",
        "spinner": "AI உங்கள் கேள்வியை பகுப்பாய்வு செய்கிறது...",
        "footer": "© 2026 **யஷ்வந்த் சவுத்ரி** | இந்திய விவசாயிகளுக்கு அர்ப்பணிக்கப்பட்டது"
    },
    "Kannada (ಕನ್ನಡ)": {
        "code": "kn",
        "title": "🌾 ರೈತ ಸಹಾಯಕ (Rythu Sahayakudu)",
        "caption": f"ಸ್ವಾಗತ, **{user_name}** | ರೂಪಿಸಿದವರು: **ಯಶವಂತ್ ಚೌಧರಿ**",
        "choose_mode": "ಇನ್‌ಪುಟ್ ವಿಧಾನವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "mode_voice": "🎙️️ ಧ್ವನಿ ಮೂಲಕ (ಮಾತನಾಡಿ)",
        "mode_text": "✍️ ಟೈಪ್ ಮಾಡುವ ಮೂಲಕ",
        "voice_info": "ಮೈಕ್ ಬಟನ್ ಒತ್ತಿ ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಮಾತನಾಡಿ:",
        "text_placeholder": "ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...",
        "btn_submit": "🤖 AI ಸಲಹೆ ಪಡೆಯಿರಿ ಮತ್ತು ಆಲಿಸಿ",
        "btn_new_chat": "➕ ಹೊಸ ಸಂಭಾಷಣೆ ಪ್ರಾರಂಭಿಸಿ",
        "history_title": "📜 ಹಿಂದಿನ ಸಂಭಾಷಣೆಗಳು",
        "err_key": "Streamlit Secrets ನಲ್ಲಿ GEMINI_API_KEY ಸೇರಿಸಿ!",
        "err_voice": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಧ್ವನಿಯನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ!",
        "err_text": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ!",
        "spinner": "AI ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...",
        "footer": "© 2026 **ಯಶವಂತ್ ಚೌಧರಿ** | ಭಾರತೀಯ ರೈತರಿಗೆ ಅರ್ಪಿತ"
    },
    "Marathi (मराठी)": {
        "code": "mr",
        "title": "🌾 शेतकरी सहाय्यक (Rythu Sahayakudu)",
        "caption": f"स्वागत आहे, **{user_name}** | डेव्हलपर: **यशवंत चौधरी**",
        "choose_mode": "इनपुटची पद्धत निवडा:",
        "mode_voice": "🎙️ आवाजाद्वारे (बोला)",
        "mode_text": "✍️️ टाइप करून",
        "voice_info": "माईक बटण दाबा आणि आपला शेतीविषयक प्रश्न बोला:",
        "text_placeholder": "आपला शेतीविषयक प्रश्न येथे टाइप करा...",
        "btn_submit": "🤖 एआय सल्ला मिळवा आणि ऐका",
        "btn_new_chat": "➕ नवीन संभाषण सुरू करा",
        "history_title": "📜 जुने संभाषण",
        "err_key": "कृपया Streamlit Secrets मध्ये GEMINI_API_KEY जोडा!",
        "err_voice": "कृपया आधी आपला आवाज रेकॉर्ड करा!",
        "err_text": "कृपया आधी आपला प्रश्न टाइप करा!",
        "spinner": "एआय आपल्या प्रश्नाचे विश्लेषण करत आहे...",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय शेतकऱ्यांना समर्पित"
    },
    "Gujarati (ગુજરાતી)": {
        "code": "gu",
        "title": "🌾 ખેડૂત સહાયક (Rythu Sahayakudu)",
        "caption": f"સ્વાગત છે, **{user_name}** | ડેવલપર: **યશવંત ચૌધરી**",
        "choose_mode": "ઇનપુટ પદ્ધતિ પસંદ કરો:",
        "mode_voice": "🎙️ અવાજ દ્વારા (બોલો)",
        "mode_text": "✍️ ટાઇપ કરીને",
        "voice_info": "માઇક બટન દબાવો અને તમારો કૃષિ પ્રશ્ન બોલો:",
        "text_placeholder": "તમારો પ્રશ્ન અહીં ટાઇપ કરો...",
        "btn_submit": "🤖 AI સલાહ મેળવો અને સાંભળો",
        "btn_new_chat": "➕ નવી વાતચીત શરૂ કરો",
        "history_title": "📜 અગાઉની વાતચીતો",
        "err_key": "Streamlit Secrets માં GEMINI_API_KEY ઉમેરો!",
        "err_voice": "કૃપા કરીને પહેલા તમારો અવાજ રેકોર્ડ કરો!",
        "err_text": "કૃપા કરીને પહેલા તમારો પ્રશ્ન ટાઇપ કરો!",
        "spinner": "AI તમારા પ્રશ્નનું વિશ્લેષણ કરી રહ્યું છે...",
        "footer": "© 2026 **યશવંત ચૌધરી** | ભારતીય ખેડૂતોને સમર્પિત"
    },
    "Malayalam (മലയാളം)": {
        "code": "ml",
        "title": "🌾 കർഷക സഹായി (Rythu Sahayakudu)",
        "caption": f"സ്വാഗതം, **{user_name}** | നിർമ്മാതാവ്: **യശവന്ത് ചൗധരി**",
        "choose_mode": "ഇൻപുട്ട് രീതി തിരഞ്ഞെടുക്കുക:",
        "mode_voice": "🎙️ ശബ്ദത്തിലൂടെ (സംസാരിക്കുക)",
        "mode_text": "✍️ ടൈപ്പ് ചെയ്തുകൊണ്ട്",
        "voice_info": "മൈക്ക് ബട്ടൺ അമർത്തി നിങ്ങളുടെ കാർഷിക ചോദ്യം ചോദിക്കുക:",
        "text_placeholder": "നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...",
        "btn_submit": "🤖 AI ഉപദേശം നേടുക & കേൾക്കുക",
        "btn_new_chat": "➕ പുതിയ സംഭാഷണം ആരംഭിക്കുക",
        "history_title": "📜 മുൻ സംഭാഷണങ്ങൾ",
        "err_key": "Streamlit Secrets-ൽ GEMINI_API_KEY ചേർക്കുക!",
        "err_voice": "ദയവായി ആദ്യം നിങ്ങളുടെ ശബ്ദം റെക്കോർഡ് ചെയ്യുക!",
        "err_text": "ദയവായി ആദ്യം നിങ്ങളുടെ ചോദ്യം ടൈപ്പ് ചെയ്യുക!",
        "spinner": "AI നിങ്ങളുടെ ചോദ്യം വിശകലനം ചെയ്യുന്നു...",
        "footer": "© 2026 **യശവന്ത് ചൗധരി** | ഇന്ത്യൻ കർഷകർക്കായി സമർപ്പിക്കുന്നു"
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "code": "pa",
        "title": "🌾 ਕਿਸਾਨ ਸਹਾਇਕ (Rythu Sahayakudu)",
        "caption": f"ਜੀ ਆਇਆਂ ਨੂੰ, **{user_name}** | ਡਿਵੈਲਪਰ: **ਯਸ਼ਵੰਤ ਚੌਧਰੀ**",
        "choose_mode": "ਇਨਪੁਟ ਦਾ ਤਰੀਕਾ ਚੁਣੋ:",
        "mode_voice": "🎙️ ਆਵਾਜ਼ ਰਾਹੀਂ (ਬੋਲੋ)",
        "mode_text": "✍️ ਟਾਈਪ ਕਰਕੇ",
        "voice_info": "ਮਾਈਕ ਬਟਨ ਦਬਾਓ ਅਤੇ ਆਪਣਾ ਖੇਤੀਬਾੜੀ ਸਵਾਲ ਬੋਲੋ:",
        "text_placeholder": "ਆਪਣਾ ਖੇਤੀਬਾੜੀ ਸਵਾਲ ਇੱਥੇ ਟਾਈਪ ਕਰੋ...",
        "btn_submit": "🤖 AI ਸਲਾਹ ਪ੍ਰਾਪਤ ਕਰੋ ਅਤੇ ਸੁਣੋ",
        "btn_new_chat": "➕ ਨਵੀਂ ਗੱਲਬਾਤ ਸ਼ੁਰੂ ਕਰੋ",
        "history_title": "📜 ਪਿਛਲੀ ਗੱਲਬਾਤ",
        "err_key": "ਕਿਰਪਾ ਕਰਕੇ Streamlit Secrets ਵਿੱਚ GEMINI_API_KEY ਜੋੜੋ!",
        "err_voice": "ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ ਆਪਣੀ ਆਵਾਜ਼ ਰਿਕਾਰਡ ਕਰੋ!",
        "
