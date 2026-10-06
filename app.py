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
        "mode_text": "✍ టైప్ చేయడం ద్వారా",
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
        "mode_voice": "🎙️️ आवाज़ द्वारा (बोलें)",
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
        "mode_text": "✍ தட்டச்சு மூலம்",
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
        "choose_mode": "ಇನ್‌‌ಪುಟ್ ವಿಧಾನವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "mode_voice": "🎙 ಧ್ವನಿ ಮೂಲಕ (ಮಾತನಾಡಿ)",
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
        "mode_voice": "🎙 आवाजाद्वारे (बोला)",
        "mode_text": "✍ टाइप करून",
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
        "mode_voice": "🎙️️ અવાજ દ્વારા (બોલો)",
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
        "err_text": "ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ ਆਪਣਾ ਸਵਾਲ ਟਾਈਪ ਕਰੋ!",
        "spinner": "AI ਤੁਹਾਡੇ ਸਵਾਲ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਿਹਾ ਹੈ...",
        "footer": "© 2026 **ਯਸ਼ਵੰਤ ਚੌਧਰੀ** | ਭਾਰਤੀ ਕਿਸਾਨਾਂ ਨੂੰ ਸਮਰਪਿਤ"
    },
    "Odia (ଓଡ଼ିଆ)": {
        "code": "or",
        "title": "🌾 କୃଷକ ସହାୟକ (Rythu Sahayakudu)",
        "caption": f"ସ୍ୱାଗତ, **{user_name}** | ପ୍ରସ୍ତୁତକର୍ତ୍ତା: **ୟଶବନ୍ତ ଚୌଧୁରୀ**",
        "choose_mode": "ଇନପୁଟ୍ ପଦ୍ଧତି ଚୟନ କରନ୍ତୁ:",
        "mode_voice": "🎙️ ସ୍ୱର ମାଧ୍ୟମରେ (କୁହନ୍ତୁ)",
        "mode_text": "✍️ ଟାଇପ୍ କରି",
        "voice_info": "ମାଇକ୍ ବଟନ୍ ଦବାନ୍ତୁ ଏବଂ ଆପଣଙ୍କ କୃଷି ପ୍ରଶ୍ନ କୁହନ୍ତୁ:",
        "text_placeholder": "ଆପଣଙ୍କ କୃଷି ପ୍ରଶ୍ନ ଏଠାରେ ଟାଇପ୍ କରନ୍ତୁ...",
        "btn_submit": "🤖 AI ପରାମର୍ଶ ପାଆନ୍ତୁ ଏବଂ ଶୁଣନ୍ତୁ",
        "btn_new_chat": "➕ ନୂତନ କଥୋପକଥନ ଆରମ୍ଭ କରନ୍ତୁ",
        "history_title": "📜 ପୂର୍ବ କଥୋପକଥନ",
        "err_key": "Streamlit Secrets ରେ GEMINI_API_KEY ଯୋଡନ୍ତୁ!",
        "err_voice": "ଦୟାକରି ପ୍ରଥମେ ଆପଣଙ୍କ ସ୍ୱର ରେକର୍ଡ କରନ୍ତୁ!",
        "err_text": "ଦୟାକରି ପ୍ରଥମେ ଆପଣଙ୍କ ପ୍ରଶ୍ନ ଟାଇପ୍ କରନ୍ତୁ!",
        "spinner": "AI ଆପଣଙ୍କ ପ୍ରଶ୍ନର ବିଶ୍ଳେଷଣ କରୁଛି...",
        "footer": "© 2026 **ୟଶବନ୍ତ ଚୌଧୁରୀ** | ଭାରତୀୟ କୃଷକମାନଙ୍କ ପାଇଁ ସମର୍ପିତ"
    },
    "Assamese (অসমীয়া)": {
        "code": "as",
        "title": "🌾 কৃষক সহায়ক (Rythu Sahayakudu)",
        "caption": f"স্বাগতম, **{user_name}** | প্ৰস্তুতকৰ্তা: **যশোৱন্ত চৌধুৰী**",
        "choose_mode": "ইনপুট পদ্ধতি বাছনি কৰক:",
        "mode_voice": "🎙️ ভইচৰ জৰিয়তে (কওক)",
        "mode_text": "✍️ টাইপ কৰি",
        "voice_info": "মাইক বুটাম টিপি আপোনাৰ কৃষি প্ৰশ্ন কওক:",
        "text_placeholder": "আপোনাৰ প্ৰশ্ন ইয়াত টাইপ কৰক...",
        "btn_submit": "🤖 AI পৰামৰ্শ লওক আৰু শুনক",
        "btn_new_chat": "➕ নতুন কথোপকথন আৰম্ভ কৰক",
        "history_title": "📜 পূৰ্বৰ কথোপকথন",
        "err_key": "Streamlit Secrets ত GEMINI_API_KEY যোগ কৰক!",
        "err_voice": "অনুগ্ৰহ কৰি প্ৰথমে আপোনাৰ মাত ৰেকৰ্ড কৰক!",
        "err_text": "অনুগ্ৰহ কৰি প্ৰথমে আপোনাৰ প্ৰশ্ন টাইপ কৰক!",
        "spinner": "AI এ আপোনাৰ প্ৰশ্ন বিশ্লেষণ কৰি আছে...",
        "footer": "© 2026 **যশোৱন্ত চৌধুৰী** | ভাৰতীয় কৃষকসকললৈ উৎসৰ্গিত"
    },
    "Urdu (اردو)": {
        "code": "ur",
        "title": "🌾 کسان معاون (Rythu Sahayakudu)",
        "caption": f"خوش آمدید، **{user_name}** | ڈویلپر: **یوشونت چودھری**",
        "choose_mode": "ان پٹ کا طریقہ منتخب کریں:",
        "mode_voice": "🎙️ آواز کے ذریعہ (بولیں)",
        "mode_text": "✍️ تحریر کے ذریعہ (ٹائپ کریں)",
        "voice_info": "مائیک بٹن دبائیں اور اپنا زرعی سوال بولیں:",
        "text_placeholder": "اپنا زرعی سوال یہاں ٹائپ کریں...",
        "btn_submit": "🤖 AI مشورہ حاصل کریں اور سنیں",
        "btn_new_chat": "➕ نئی گفتگو شروع کریں",
        "history_title": "📜 سابقہ گفتگو",
        "err_key": "براہ کرم Streamlit Secrets میں GEMINI_API_KEY شامل کریں!",
        "err_voice": "براہ کرم پہلے اپنی آواز ریکارڈ کریں!",
        "err_text": "براہ کرم پہلے اپنا سوال ٹائپ کریں!",
        "spinner": "AI آپ کے سوال کا تجزیہ کر رہا ہے...",
        "footer": "© 2026 **یوشونت چودھری** | بھارتی کسانوں کے نام"
    },
    "Sanskrit (संस्कृतम्)": {
        "code": "hi",
        "title": "🌾 कृषक सहायकः (Rythu Sahayakudu)",
        "caption": f"स्वागतम्, **{user_name}** | निर्माता: **यशवन्त चौधरी**",
        "choose_mode": "इनपुट-विधिं चिनोतु:",
        "mode_voice": "🎙️ वाण्या (वदतु)",
        "mode_text": "✍️ टङ्कनेन",
        "voice_info": "माइक-पिञ्जं पीडयित्वा स्वस्य कृषि-प्रश्नं वदतु:",
        "text_placeholder": "अत्र स्वस्य कृषि-प्रश्नं टङ्कयतु...",
        "btn_submit": "🤖 AI परामर्शं प्राप्नोतु शृणोतु च",
        "btn_new_chat": "🔄 नूतन-सम्भाषणं आरभताम्",
        "history_title": "📜 सम्भाषण-इतिहासः",
        "err_key": "कृपया Streamlit Secrets मध्ये GEMINI_API_KEY योजयतु!",
        "err_voice": "कृपया पूर्वं स्वस्य वाणीं ध्वन्यङ्कयतु!",
        "err_text": "कृपया पूर्वं स्वस्य प्रश्नं टङ्कयतु!",
        "spinner": "AI भवतः प्रश्नस्य विश्लेषणं करोति...",
        "footer": "© 2026 **यशवन्त चौधरी** | भारतीय-कृषकेभ्यः समर्पितम्"
    },
    "Maithili (मैथिली)": {
        "code": "hi",
        "title": "🌾 किसान सहायक (Rythu Sahayakudu)",
        "caption": f"स्वागत अछि, **{user_name}** | निर्माता: **यशवंत चौधरी**",
        "choose_mode": "इनपुट के तरीका चुनू:",
        "mode_voice": "🎙 आवाज द्वारा (बजू)",
        "mode_text": "✍️ टाइप कऽ कऽ",
        "voice_info": "माइक बटन दबा कऽ अपन कृषि प्रश्न बजू:",
        "text_placeholder": "अपन कृषि प्रश्न एतय टाइप करू...",
        "btn_submit": "🤖 AI सलाह प्राप्त करू आ सुनू",
        "btn_new_chat": "➕ नया बातचीत शुरू करू",
        "history_title": "📜 पुरान बातचीत",
        "err_key": "कृपया Streamlit Secrets मे GEMINI_API_KEY जोड़ू!",
        "err_voice": "कृपया पहिने अपन आवाज रिकॉर्ड करू!",
        "err_text": "कृपया पहिने अपन प्रश्न टाइप करू!",
        "spinner": "AI अहाँक प्रश्नक विश्लेषण कऽ रहल अछि...",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय किसान लोकनिक लेल समर्पित"
    },
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": {
        "code": "hi",
        "title": "🌾 ᱪᱟᱥᱤ ᱥᱚᱦᱚᱭᱚᱠ (Rythu Sahayakudu)",
        "caption": f"ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ, **{user_name}** | ᱛᱮᱭᱟᱨᱤᱡ: **ᱭᱚᱥᱣᱚᱱᱛᱷ ᱪᱚᱣᱫᱷᱚᱨᱤ**",
        "choose_mode": "ᱤᱱᱯᱩᱴ ᱰᱟᱦᱟᱨ ᱵᱟᱪᱷᱟᱣ ᱢᱮ:",
        "mode_voice": "🎙️ ᱟᱲᱟᱝ ᱛᱮ (ᱨᱚᱲ ᱢᱮ)",
        "mode_text": "✍️ ᱚᱞ ᱠᱟᱛᱮ",
        "voice_info": "ᱢᱟᱭᱤᱠ ᱵᱟᱴᱚᱱ ᱫᱟᱵᱟᱣ ᱠᱟᱛᱮ ᱪᱟᱥ ᱠᱩᱠᱞᱤ ᱨᱚᱲ ᱢᱮ:",
        "text_placeholder": "ᱟᱢᱟᱜ ᱪᱟᱥ ᱠᱩᱠᱞᱤ ᱱᱚᱸᱰᱮ ᱚᱞ ᱢᱮ...",
        "btn_submit": "🤖 AI ᱥᱚᱞᱦᱟ ᱧᱟᱢ ᱢᱮ ᱟᱨ ᱟᱸᱡᱚᱢ ᱢᱮ",
        "btn_new_chat": "➕ ᱱᱟᱶᱟ ᱜᱟᱞᱢᱟᱨᱟᱣ ᱮᱦᱚᱵ ᱢᱮ",
        "history_title": "📜 ᱜᱟᱞᱢᱟᱨᱟᱣ ᱤᱛᱤᱦᱟᱥ",
        "err_key": "Streamlit Secrets ᱨᱮ GEMINI_API_KEY ᱞᱟᱜᱟᱣ ᱢᱮ!",
        "err_voice": "ᱫᱟ stage ᱯᱷᱟᱥᱴ ᱟᱢᱟᱜ ᱟᱲᱟᱝ ᱨᱮᱠᱚᱨᱰ ᱢᱮ!",
        "err_text": "ᱫᱟ stage ᱯᱷᱟᱥᱴ ᱟᱢᱟᱜ ᱠᱩᱠᱞᱤ ᱚᱞ ᱢᱮ!",
        "spinner": "AI ᱟᱢᱟᱜ ᱠᱩᱠᱞᱤ ᱵᱤᱪᱟᱹᱨᱮᱫᱟ...",
        "footer": "© 2026 **ᱭᱚᱥᱣᱚᱱᱛᱷ ᱪᱚᱣᱫᱷᱚᱨᱤ** | ᱵᱷᱟᱨᱚᱛᱤᱭᱟᱹ ᱪᱟᱥᱤ ᱠᱚ ᱞᱟᱹᱜᱤᱫ"
    },
    "Kashmiri (کٲشُر)": {
        "code": "ur",
        "title": "🌾 کِسان مَدَدگار (Rythu Sahayakudu)",
        "caption": f"خوش آمَدید، **{user_name}** | بَناوَن وول: **یَشَوَنٹھ چودھری**",
        "choose_mode": "اِن پُٹ طَریقہِ زالِو:",
        "mode_voice": "🎙️ آوازِ ذَریعہِ (بَلیو)",
        "mode_text": "✍ ٹائپ کٔرِتھ",
        "voice_info": "مائک بَٹن دَباوِو تہِ پَنُن زِراعتِی سَوال بَلیو:",
        "text_placeholder": "پَنُن سَوال یِتین ٹائپ کٔرِو...",
        "btn_submit": "🤖 AI صَلاح حاصِل کٔرِو تہِ بوزِو",
        "btn_new_chat": "➕ نَو کَتھ باتھ شُرُوع کٔرِو",
        "history_title": "📜 پُرٲن کَتھ باتھ",
        "err_key": "Streamlit Secrets مَنز GEMINI_API_KEY دَرجم کٔرِو!",
        "err_voice": "مہِربانی کٔرِتھ گوڈہِ پَنِین آواز رِکارڈ کٔرِو!",
        "err_text": "مہِربانی کٔرِتھ گوڈہِ پَنُن سَوال ٹائپ کٔرِو!",
        "spinner": "AI چَھ پَنُن سَوال سَمجھان...",
        "footer": "© 2026 **یَشَوَنٹھ چودھری** | ہِندوستٲنی کِسانَن باپَتھ"
    },
    "Konkani (कोंकणी)": {
        "code": "mr",
        "title": "🌾 शेतकार आदारपी (Rythu Sahayakudu)",
        "caption": f"येवकार, **{user_name}** | निर्मोतो: **यशवंत चौधरी**",
        "choose_mode": "इनपुट मार्ग विंचात:",
        "mode_voice": "🎙️ आवाजा वरवीं (उलोवचें)",
        "mode_text": "✍️ टाईप करून",
        "voice_info": "मायक बटन दाबून तुमचो शेतकी प्रश्न उलोवचो:",
        "text_placeholder": "तुमचो प्रश्न हांगा टाईप करात...",
        "btn_submit": "🤖 AI सल्लो मेळयात आनी आयकात",
        "btn_new_chat": "➕ नवी उलोवप सुरवात करात",
        "history_title": "📜 आदली उलोवपां",
        "err_key": "Streamlit Secrets हांतूं GEMINI_API_KEY घालात!",
        "err_voice": "उपकार करून पयलीं तुमचो आवाज रेकॉर्ड करात!",
        "err_text": "उपकार करून पयलीं तुमचो प्रश्न टाईप करात!",
        "spinner": "AI तुमच्या प्रश्नाचें विश्लेषण करता...",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय शेतकाऱ्यांक अर्पण"
    },
    "Dogri (डोगरी)": {
        "code": "hi",
        "title": "🌾 किसान मददगार (Rythu Sahayakudu)",
        "caption": f"जी आयां गी, **{user_name}** | बनाने आला: **यशवंत चौधरी**",
        "choose_mode": "इनपुट दा तरीका चुनो:",
        "mode_voice": "🎙️ आवाज़ राहें (बोलो)",
        "mode_text": "✍️ टाइप करियै",
        "voice_info": "माइक बटन दबाओ ते अपना खेती दा सवाल बोलो:",
        "text_placeholder": "अपना सवाल इत्थै टाइप करो...",
        "btn_submit": "🤖 AI सलाह हासल करो ते सुनो",
        "btn_new_chat": "➕ नवीं गल्लबात शुरू करो",
        "history_title": "📜 पिछली गल्लबात",
        "err_key": "Streamlit Secrets च GEMINI_API_KEY पाओ!",
        "err_voice": "कृपा करियै पैहले अपनी आवाज़ रिकार्ड करो!",
        "err_text": "कृपा करियै पैहले अपना सवाल टाइप करो!",
        "spinner": "AI तुंदे सवाल दा विश्लेषण करा करदा ऐ...",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय किसानें गी समर्पित"
    },
    "Sindhi (سنڌي)": {
        "code": "ur",
        "title": "🌾 هاري مددگار (Rythu Sahayakudu)",
        "caption": f"ڀلي ڪري آيا، **{user_name}** | ٺاهيندڙ: **يشونت چوڌري**",
        "choose_mode": "انپٽ جو طريقو چونڊيو:",
        "mode_voice": "🎙️ آواز ذريعي (ڳالهايو)",
        "mode_text": "✍ ٽائپ ڪري",
        "voice_info": "مائيڪ بٽڻ ٻاري پنهنجو زرعي سوال ڳالهايو:",
        "text_placeholder": "پنهنجو سوال هتي ٽائپ ڪريو...",
        "btn_submit": "🤖 AI صلاح حاصل ڪريو ۽ ٻڌو",
        "btn_new_chat": "➕ نئين گفتگو شروع ڪريو",
        "history_title": "📜 پوئين گفتگو",
        "err_key": "Streamlit Secrets ۾ GEMINI_API_KEY داخل ڪريو!",
        "err_voice": "مهرباني ڪري پهريان پنهنجو آواز رڪارڊ ڪريو!",
        "err_text": "مهرباني ڪري پهريان پنهنجو سوال ٽائپ ڪريو!",
        "spinner": "AI توهان جي سوال جو تجزيو ڪري رهيو آهي...",
        "footer": "© 2026 **يشونت چوڌري** | بالڪل هندستاني هارين لاءِ"
    },
    "Bodo (बर')": {
        "code": "hi",
        "title": "🌾 आबादारी मदतगिरि (Rythu Sahayakudu)",
        "caption": f"बरायबाय, **{user_name}** | सोरजिनगिरि: **यसवंत चौधरी**",
        "choose_mode": "इनपुट लामा सायख':",
        "mode_voice": "🎙️ रावजों (रायाव)",
        "mode_text": "✍️ लिरनानै",
        "voice_info": "माइकु बटन थुनानै नोंथांनि आबादारी सोंथि रायाव:",
        "text_placeholder": "नोंथांनि सोंथि बेयाव लिर...",
        "btn_submit": "🤖 AI थिसाननाय लाआ आरो खोनासं",
        "btn_new_chat": "➕ गोदान रायज्लायनाय जागायनै",
        "history_title": "📜 सिगांनि रायज्लायनाय",
        "err_key": "Streamlit Secrets आव GEMINI_API_KEY सोना ला!",
        "err_voice": "अननानै सिगां नोंथांनि राव रेकर्ड खालाम!",
        "err_text": "अननानै सिगां नोंथांनि सोंथि लिर!",
        "spinner": "AI आ नोंथांनि सोंथिखौ बिजिरगासिनो दं...",
        "footer": "© 2026 **यसवंत चौधरी** | भारोतनि आबादारीफोरनि थाखाय"
    },
    "Manipuri (মৈতৈলোন্)": {
        "code": "bn",
        "title": "🌾 লৌমি মতেংপাংবা (Rythu Sahayakudu)",
        "caption": f"তরাম্না ওকচরি, **{user_name}** | শেম্বা: **যশবন্ত চৌধুরী**",
        "choose_mode": "ইনপুট লম্বী খনবীয়ু:",
        "mode_voice": "🎙️ খোঞ্জেলনা (ঙাংবীয়ু)",
        "mode_text": "✍️ ইদুনা",
        "voice_info": "মাইক নম্বর নম্বীয়ু অমসুং লৌউ-শিংউগী হংনিংবা ঙাংবীয়ু:",
        "text_placeholder": "অদোমগী হংনিংবা অসিদা ইবীয়ু...",
        "btn_submit": "🤖 AI পাউতাক লৌবীয়ু অমসুং তাবীয়ু",
        "btn_new_chat": "➕ অনৌবা ৱারী শাবা হৌবীয়ু",
        "history_title": "📜 মমাংগী ৱারীশিং",
        "err_key": "Streamlit Secrets দা GEMINI_API_KEY হাপচিনবীয়ু!",
        "err_voice": "チャンবীয়ু, হান্না অদোমগী খোঞ্জেল রেকোর্দ তৌবীয়ু!",
        "err_text": "チャンবীয়ু, হান্না অদোমগী হংনিংবা অদুবু ইবীয়ু!",
        "spinner": "AI না অদোমগী হংনিংবা নৈনরি...",
        "footer": "© 2026 **যশবন্ত চৌধুরী** | ইন্দিয়াগী লৌমিশিংগীদমক"
    },
    "Nepali (नेपाली)": {
        "code": "ne",
        "title": "🌾 किसान सहायक (Rythu Sahayakudu)",
        "caption": f"स्वागत छ, **{user_name}** | विकासकर्ता: **यशवन्त चौधरी**",
        "choose_mode": "इनपुट माध्यम छान्नुहोस्:",
        "mode_voice": "🎙 आवाजद्वारा (बोल्नुहोस्)",
        "mode_text": "✍️ टाइप गरेर",
        "voice_info": "माइक बटन थिचेर आफ्नो कृषि प्रश्न बोल्नुहोस्:",
        "text_placeholder": "आफ्नो कृषि प्रश्न यहाँ टाइप गर्नुहोस्...",
        "btn_submit": "🤖 AI सल्लाह प्राप्त गर्नुहोस् र सुन्नुहोस्",
        "btn_new_chat": "➕ नयाँ कुराकानी सुरु गर्नुहोस्",
        "history_title": "📜 पुराना कुराकानीहरू",
        "err_key": "Streamlit Secrets मा GEMINI_API_KEY थप्नुहोस्!",
        "err_voice": "कृपया पहिले आफ्नो आवाज रेकर्ड गर्नुहोस्!",
        "err_text": "कृपया पहिले आफ्नो प्रश्न टाइप गर्नुहोस्!",
        "spinner": "AI ले तपाईंको प्रश्नको विश्लेषण गर्दैछ...",
        "footer": "© 2026 **यशवन्त चौधरी** | भारतीय किसानहरूका लागि समर्पित"
    },
    "English": {
        "code": "en",
        "title": "🌾 Rythu Sahayakudu (Farmers' AI Assistant)",
        "caption": f"Welcome, **{user_name}** | Developed by **Yaswanth Chowdary**",
        "choose_mode": "Choose Input Mode:",
        "mode_voice": "🎙️ Voice Input (Speak)",
        "mode_text": "✍️ Text Input (Type)",
        "voice_info": "Click the microphone button and state your agricultural query:",
        "text_placeholder": "Type your farming question here...",
        "btn_submit": "🤖 Get AI Advice & Listen",
        "btn_new_chat": "➕ Start New Conversation",
        "history_title": "📜 My Past Conversations",
        "err_key": "Please configure GEMINI_API_KEY in Streamlit Secrets!",
        "err_voice": "Please record your audio query first!",
        "err_text": "Please type your question first!",
        "spinner": "AI is analyzing your farming query...",
        "footer": "© 2026 **Yaswanth Chowdary** | Dedicated to Empowering Indian Farmers"
    }
}

# --- 4. SIDEBAR SETTINGS ---
st.sidebar.title("⚙️ Settings / அமைப்புகள்")

lang_choice = st.sidebar.selectbox("🌐 Select Language / భాషను ఎంచుకోండి:", list(UI_TRANSLATIONS.keys()), index=0)
t = UI_TRANSLATIONS[lang_choice]

if user_logged_in:
    st.sidebar.write(f"👤 Logged in as: **{user_name}**")

if st.sidebar.button("🚪 Change Account / Logout"):
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.chat_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.chat_history = []
    st.rerun()

# --- 5. INITIALIZE GEMINI API ---
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
if not api_key:
    st.error(t["err_key"])
    st.stop()

genai.configure(api_key=api_key)

SYSTEM_INSTRUCTION = (
    f"You are Rythu Sahayakudu, an expert AI Agricultural Advisor created by Yaswanth Chowdary. "
    f"Always respond in {lang_choice}. Provide clear, practical, step-by-step agricultural solutions "
    f"regarding crop diseases, fertilizers, pest control, weather guidance, and government schemes. "
    f"Keep responses structured, encouraging, and easy to understand for farmers."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# --- 6. SESSION STATE INITIALIZATION ---
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 7. DATABASE HELPER FUNCTIONS ---
def save_chat_to_db(session_id, user_q, ai_ans):
    if supabase:
        try:
            supabase.table("farmer_chats").insert({
                "user_email": user_email,
                "session_id": session_id,
                "language": lang_choice,
                "user_query": user_q,
                "ai_response": ai_ans,
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            st.warning(f"Note: Could not save to cloud history: {e}")

def load_user_sessions():
    if supabase and user_email:
        try:
            res = supabase.table("farmer_chats").select("session_id, user_query, created_at").eq("user_email", user_email).order("created_at", desc=True).execute()
            return res.data
        except Exception:
            return []
    return []

def load_specific_session(session_id):
    if supabase:
        try:
            res = supabase.table("farmer_chats").select("*").eq("session_id", session_id).order("created_at", asc=True).execute()
            return res.data
        except Exception:
            return []
    return []

# --- 8. HISTORICAL CHATS IN SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.subheader(t["history_title"])

if st.sidebar.button(t["btn_new_chat"], use_container_width=True):
    st.session_state.chat_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.chat_history = []
    st.rerun()

past_data = load_user_sessions()
if past_data:
    unique_sessions = {}
    for row in past_data:
        sid = row["session_id"]
        if sid not in unique_sessions:
            unique_sessions[sid] = row["user_query"]
    
    for sid, q_preview in list(unique_sessions.items())[:10]:
        display_label = (q_preview[:25] + '...') if len(q_preview) > 25 else q_preview
        if st.sidebar.button(f"💬 {display_label}", key=sid, use_container_width=True):
            st.session_state.chat_session_id = sid
            history_rows = load_specific_session(sid)
            st.session_state.chat_history = []
            for h in history_rows:
                st.session_state.chat_history.append({"role": "user", "text": h["user_query"]})
                st.session_state.chat_history.append({"role": "ai", "text": h["ai_response"]})
            st.rerun()

# --- 9. MAIN APP UI ---
st.title(t["title"])
st.caption(t["caption"])
st.markdown("---")

input_mode = st.radio(t["choose_mode"], [t["mode_voice"], t["mode_text"]], horizontal=True)

query_text = ""

if input_mode == t["mode_voice"]:
    st.write(t["voice_info"])
    audio_val = st.audio_input("Record Audio Question")
    
    if audio_val is not None:
        if st.button(t["btn_submit"], type="primary"):
            with st.spinner(t["spinner"]):
                try:
                    audio_bytes = audio_val.read()
                    audio_part = {"mime_type": "audio/wav", "data": audio_bytes}
                    prompt = f"Listen to this audio query. Translate or process it and answer thoroughly in {lang_choice}."
                    
                    response = model.generate_content([prompt, audio_part])
                    ai_text = response.text
                    
                    query_text = "[Voice Input Audio Query]"
                    st.session_state.chat_history.append({"role": "user", "text": query_text})
                    st.session_state.chat_history.append({"role": "ai", "text": ai_text})
                    save_chat_to_db(st.session_state.chat_session_id, query_text, ai_text)
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")

else:
    user_input = st.text_area(t["text_placeholder"], height=100)
    if st.button(t["btn_submit"], type="primary"):
        if not user_input.strip():
            st.warning(t["err_text"])
        else:
            with st.spinner(t["spinner"]):
                try:
                    formatted_prompt = f"Language: {lang_choice}\nFarmer Question: {user_input}"
                    response = model.generate_content(formatted_prompt)
                    ai_text = response.text
                    
                    st.session_state.chat_history.append({"role": "user", "text": user_input})
                    st.session_state.chat_history.append({"role": "ai", "text": ai_text})
                    save_chat_to_db(st.session_state.chat_session_id, user_input, ai_text)
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

# --- 10. CHAT DISPLAY & SPEECH GENERATION ---
if st.session_state.chat_history:
    st.markdown("---")
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.chat_message("user").write(chat["text"])
        else:
            with st.chat_message("assistant"):
                st.write(chat["text"])
                try:
                    tts = gTTS(text=chat["text"], lang=t["code"], slow=False)
                    audio_file_path = "temp_response.mp3"
                    tts.save(audio_file_path)
                    st.audio(audio_file_path, format="audio/mp3")
                except Exception:
                    pass

# --- 11. FOOTER ---
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: gray;'>{t['footer']}</div>", unsafe_allow_html=True)
