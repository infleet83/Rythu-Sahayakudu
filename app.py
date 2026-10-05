import streamlit as st
from gtts import gTTS
import google.generativeai as genai
import os

st.set_page_config(page_title="Rythu Sahayakudu", page_icon="🌾", layout="centered")

# 22 Official Scheduled Languages of India + English
# Map each language to gTTS language code, display name, and UI translations
UI_TRANSLATIONS = {
    "Telugu (తెలుగు)": {
        "code": "te",
        "title": "🌾 రైతు సహాయకుడు (Rythu Sahayakudu)",
        "caption": "తయారు చేసినవారు: **యాస్వంత్ చౌదరి** | ఉచిత ఏఐ వ్యవసాయ సహాయకుడు",
        "select_lang": "భాషను ఎంచుకోండి:",
        "choose_mode": "ఇన్‌పుట్ మార్గాన్ని ఎంచుకోండి:",
        "mode_voice": "🎙️ వాయిస్ ద్వారా (మాట్లాడండి)",
        "mode_text": "✍️ టైప్ చేయడం ద్వారా",
        "voice_info": "మైక్ బటన్ నొక్కి మీ వ్యవసాయ ప్రశ్న మాట్లాడండి:",
        "text_placeholder": "మీ వ్యవసాయ ప్రశ్నను ఇక్కడ టైప్ చేయండి...",
        "btn_submit": "🤖 ఏఐ సలహా పొందండి & వినండి",
        "btn_clear": "🔄 క్రొత్త సంభాషణ ప్రారంభించండి",
        "err_key": "దయచేసి Streamlit Secrets లో GEMINI_API_KEY నమోదు చేయండి!",
        "err_voice": "దయచేసి ముందుగా మీ ప్రశ్నను రికార్డ్ చేయండి!",
        "err_text": "దయచేసి ముందుగా మీ ప్రశ్నను టైప్ చేయండి!",
        "spinner": "ఏఐ మీ ప్రశ్నను విశ్లేషిస్తోంది...",
        "chat_history_header": "💬 సంభాషణ చరిత్ర:",
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
        "voice_info": "माइक बटन दबाएं और अपना कृषि प्रश्न बोलें:",
        "text_placeholder": "अपना कृषि प्रश्न यहाँ लिखें...",
        "btn_submit": "🤖 एआई सलाह प्राप्त करें और सुनें",
        "btn_clear": "🔄 नई बातचीत शुरू करें",
        "err_key": "कृपया Streamlit Secrets में GEMINI_API_KEY जोड़ें!",
        "err_voice": "कृपया पहले अपनी आवाज़ रिकॉर्ड करें!",
        "err_text": "कृपया पहले अपना प्रश्न लिखें!",
        "spinner": "एआई आपके प्रश्न का विश्लेषण कर रहा है...",
        "chat_history_header": "💬 बातचीत का इतिहास:",
        "footer": "© 2026 **यसवंत चौधरी** | भारतीय किसानों को समर्पित"
    },
    "Bengali (বাংলা)": {
        "code": "bn",
        "title": "🌾 কৃষক সহায়ক (Rythu Sahayakudu)",
        "caption": "প্রস্তুতকারক: **যশোবন্ত চৌধুরী** | বিনামূল্যে এআই কৃষি সহকারী",
        "select_lang": "ভাষা নির্বাচন করুন:",
        "choose_mode": "ইনপুট পদ্ধতি নির্বাচন করুন:",
        "mode_voice": "🎙️ ভয়েস দ্বারা (বলুন)",
        "mode_text": "✍️ টাইপ করে",
        "voice_info": "মাইক বোতাম টিপে আপনার কৃষি প্রশ্ন বলুন:",
        "text_placeholder": "আপনার কৃষি প্রশ্ন এখানে লিখুন...",
        "btn_submit": "🤖 এআই পরামর্শ পান এবং শুনুন",
        "btn_clear": "🔄 নতুন কথোপকথন শুরু করুন",
        "err_key": "Streamlit Secrets-এ GEMINI_API_KEY যোগ করুন!",
        "err_voice": "দয়া করে প্রথমে আপনার প্রশ্ন রেকর্ড করুন!",
        "err_text": "দয়া করে প্রথমে আপনার প্রশ্ন টাইপ করুন!",
        "spinner": "এআই আপনার প্রশ্ন বিশ্লেষণ করছে...",
        "chat_history_header": "💬 কথোপকথনের ইতিহাস:",
        "footer": "© 2026 **যশোবন্ত চৌধুরী** | ভারতীয় কৃষকদের উদ্দেশ্যে উৎসর্গীকৃত"
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
        "text_placeholder": "உங்கள் கேள்வியை இங்கே தட்டச்சு செய்யவும்...",
        "btn_submit": "🤖 AI ஆலோசனையைப் பெற்று கேட்கவும்",
        "btn_clear": "🔄 புதிய உரையாடலைத் தொடங்கவும்",
        "err_key": "Streamlit Secrets இல் GEMINI_API_KEY ஐச் சேர்க்கவும்!",
        "err_voice": "தயவுசெய்து முதலில் உங்கள் குரலைப் பதிவு செய்யவும்!",
        "err_text": "தயவுசெய்து முதலில் உங்கள் கேள்வியைத் தட்டச்சு செய்யவும்!",
        "spinner": "AI உங்கள் கேள்வியை பகுப்பாய்வு செய்கிறது...",
        "chat_history_header": "💬 உரையாடல் வரலாறு:",
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
        "voice_info": "ಮೈಕ್ ಬಟನ್ ಒತ್ತಿ ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಮಾತನಾಡಿ:",
        "text_placeholder": "ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...",
        "btn_submit": "🤖 AI ಸಲಹೆ ಪಡೆಯಿರಿ ಮತ್ತು ಆಲಿಸಿ",
        "btn_clear": "🔄 ಹೊಸ ಸಂಭಾಷಣೆ ಪ್ರಾರಂಭಿಸಿ",
        "err_key": "Streamlit Secrets ನಲ್ಲಿ GEMINI_API_KEY ಸೇರಿಸಿ!",
        "err_voice": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಧ್ವನಿಯನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ!",
        "err_text": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ!",
        "spinner": "AI ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...",
        "chat_history_header": "💬 ಸಂಭಾಷಣೆಯ ಇತಿಹಾಸ:",
        "footer": "© 2026 **ಯಶವಂತ್ ಚೌಧರಿ** | ಭಾರತೀಯ ರೈತರಿಗೆ ಅರ್ಪಿತ"
    },
    "Marathi (मराठी)": {
        "code": "mr",
        "title": "🌾 शेतकरी सहाय्यक (Rythu Sahayakudu)",
        "caption": "डेव्हलपर: **यशवंत चौधरी** | मोफत एआय कृषी सहाय्यक",
        "select_lang": "भाषा निवडा:",
        "choose_mode": "इनपुटची पद्धत निवडा:",
        "mode_voice": "🎙️ आवाजाद्वारे (बोला)",
        "mode_text": "✍️ टाइप करून",
        "voice_info": "माईक बटण दाबा आणि आपला शेतीविषयक प्रश्न बोला:",
        "text_placeholder": "आपला शेतीविषयक प्रश्न येथे टाइप करा...",
        "btn_submit": "🤖 एआय सल्ला मिळवा आणि ऐका",
        "btn_clear": "🔄 नवीन संभाषण सुरू करा",
        "err_key": "कृपया Streamlit Secrets मध्ये GEMINI_API_KEY जोडा!",
        "err_voice": "कृपया आधी आपला आवाज रेकॉर्ड करा!",
        "err_text": "कृपया आधी आपला प्रश्न टाइप करा!",
        "spinner": "एआय आपल्या प्रश्नाचे विश्लेषण करत आहे...",
        "chat_history_header": "💬 संभाषणाचा इतिहास:",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय शेतकऱ्यांना समर्पित"
    },
    "Gujarati (ગુજરાતી)": {
        "code": "gu",
        "title": "🌾 ખેડૂત સહાયક (Rythu Sahayakudu)",
        "caption": "ડેવલપર: **યશવંત ચૌધરી** | મફત AI કૃષિ સહાયક",
        "select_lang": "ભાષા પસંદ કરો:",
        "choose_mode": "ઇનપુટ પદ્ધતિ પસંદ કરો:",
        "mode_voice": "🎙️ અવાજ દ્વારા (બોલો)",
        "mode_text": "✍️ ટાઇપ કરીને",
        "voice_info": "માઇક બટન દબાવો અને તમારો કૃષિ પ્રશ્ન બોલો:",
        "text_placeholder": "તમારો પ્રશ્ન અહીં ટાઇપ કરો...",
        "btn_submit": "🤖 AI સલાહ મેળવો અને સાંભળો",
        "btn_clear": "🔄 નવી વાતચીત શરૂ કરો",
        "err_key": "Streamlit Secrets માં GEMINI_API_KEY ઉમેરો!",
        "err_voice": "કૃપા કરીને પહેલા તમારો અવાજ રેકોર્ડ કરો!",
        "err_text": "કૃપા કરીને પહેલા તમારો પ્રશ્ન ટાઇપ કરો!",
        "spinner": "AI તમારા પ્રશ્નનું વિશ્લેષણ કરી રહ્યું છે...",
        "chat_history_header": "💬 વાતચીતનો ઇતિહાસ:",
        "footer": "© 2026 **યશવંત ચૌધરી** | ભારતીય ખેડૂતોને સમર્પિત"
    },
    "Malayalam (മലയാളം)": {
        "code": "ml",
        "title": "🌾 കർഷക സഹായി (Rythu Sahayakudu)",
        "caption": "നിർമ്മാതാവ്: **യശവന്ത് ചൗധരി** | സൗജന്യ AI കാർഷിക സഹായി",
        "select_lang": "ഭാഷ തിരഞ്ഞെടുക്കുക:",
        "choose_mode": "ഇൻപുട്ട് രീതി തിരഞ്ഞെടുക്കുക:",
        "mode_voice": "🎙️ ശബ്ദത്തിലൂടെ (സംസാരിക്കുക)",
        "mode_text": "✍️ ടൈപ്പ് ചെയ്തുകൊണ്ട്",
        "voice_info": "മൈക്ക് ബട്ടൺ അമർത്തി നിങ്ങളുടെ കാർഷിക ചോദ്യം ചോദിക്കുക:",
        "text_placeholder": "നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...",
        "btn_submit": "🤖 AI ഉപദേശം നേടുക & കേൾക്കുക",
        "btn_clear": "🔄 പുതിയ സംഭാഷണം ആരംഭിക്കുക",
        "err_key": "Streamlit Secrets-ൽ GEMINI_API_KEY ചേർക്കുക!",
        "err_voice": "ദയവായി ആദ്യം നിങ്ങളുടെ ശബ്ദം റെക്കോർഡ് ചെയ്യുക!",
        "err_text": "ദയവായി ആദ്യം നിങ്ങളുടെ ചോദ്യം ടൈപ്പ് ചെയ്യുക!",
        "spinner": "AI നിങ്ങളുടെ ചോദ്യം വിശകലനം ചെയ്യുന്നു...",
        "chat_history_header": "💬 സംഭാഷണ ചരിത്രം:",
        "footer": "© 2026 **യശവന്ത് ചൗധരി** | ഇന്ത്യൻ കർഷകർക്കായി സമർപ്പിക്കുന്നു"
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "code": "pa",
        "title": "🌾 ਕਿਸਾਨ ਸਹਾਇਕ (Rythu Sahayakudu)",
        "caption": "ਡਿਵੈਲਪਰ: **ਯਸ਼ਵੰਤ ਚੌਧਰੀ** | ਮੁਫ਼ਤ AI ਖੇਤੀਬਾੜੀ ਸਹਾਇਕ",
        "select_lang": "ਭਾਸ਼ਾ ਚੁਣੋ:",
        "choose_mode": "ਇਨਪੁਟ ਦਾ ਤਰੀਕਾ ਚੁਣੋ:",
        "mode_voice": "🎙️ ਆਵਾਜ਼ ਰਾਹੀਂ (ਬੋਲੋ)",
        "mode_text": "✍️ ਟਾਈਪ ਕਰਕੇ",
        "voice_info": "ਮਾਈਕ ਬਟਨ ਦਬਾਓ ਅਤੇ ਆਪਣਾ ਖੇਤੀਬਾੜੀ ਸਵਾਲ ਬੋਲੋ:",
        "text_placeholder": "ਆਪਣਾ ਖੇਤੀਬਾੜੀ ਸਵਾਲ ਇੱਥੇ ਟਾਈਪ ਕਰੋ...",
        "btn_submit": "🤖 AI ਸਲਾਹ ਪ੍ਰਾਪਤ ਕਰੋ ਅਤੇ ਸੁਣੋ",
        "btn_clear": "🔄 ਨਵੀਂ ਗੱਲਬਾਤ ਸ਼ੁਰੂ ਕਰੋ",
        "err_key": "ਕਿਰਪਾ ਕਰਕੇ Streamlit Secrets ਵਿੱਚ GEMINI_API_KEY ਜੋੜੋ!",
        "err_voice": "ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ ਆਪਣੀ ਆਵਾਜ਼ ਰਿਕਾਰਡ ਕਰੋ!",
        "err_text": "ਕਿਰਪਾ ਕਰਕੇ ਪਹਿਲਾਂ ਆਪਣਾ ਸਵਾਲ ਟਾਈਪ ਕਰੋ!",
        "spinner": "AI ਤੁਹਾਡੇ ਸਵਾਲ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਿਹਾ ਹੈ...",
        "chat_history_header": "💬 ਗੱਲਬਾਤ ਦਾ ਇਤਿਹਾਸ:",
        "footer": "© 2026 **ਯਸ਼ਵੰਤ ਚੌਧਰੀ** | ਭਾਰਤੀ ਕਿਸਾਨਾਂ ਨੂੰ ਸਮਰਪਿਤ"
    },
    "Odia (ଓଡ଼ିଆ)": {
        "code": "or",
        "title": "🌾 କୃଷକ ସହାୟକ (Rythu Sahayakudu)",
        "caption": "ପ୍ରସ୍ତୁତକର୍ତ୍ତା: **ୟଶବନ୍ତ ଚୌଧୁରୀ** | ମାଗଣା AI କୃଷି ସହାୟକ",
        "select_lang": "ଭାଷା ଚୟନ କରନ୍ତୁ:",
        "choose_mode": "ଇନପୁଟ୍ ପଦ୍ଧତି ଚୟନ କରନ୍ତୁ:",
        "mode_voice": "🎙️ ସ୍ୱର ମାଧ୍ୟମରେ (କୁହନ୍ତୁ)",
        "mode_text": "✍️ ଟାଇପ୍ କରି",
        "voice_info": "ମାଇକ୍ ବଟନ୍ ଦବାନ୍ତୁ ଏବଂ ଆପଣଙ୍କ କୃଷି ପ୍ରଶ୍ନ କୁହନ୍ତୁ:",
        "text_placeholder": "ଆପଣଙ୍କ କୃଷି ପ୍ରଶ୍ନ ଏଠାରେ ଟାଇପ୍ କରନ୍ତୁ...",
        "btn_submit": "🤖 AI ପରାମର୍ଶ ପାଆନ୍ତୁ ଏବଂ ଶୁଣନ୍ତୁ",
        "btn_clear": "🔄 ନୂତନ କଥୋପକଥନ ଆରମ୍ଭ କରନ୍ତୁ",
        "err_key": "Streamlit Secrets ରେ GEMINI_API_KEY ଯୋଡନ୍ତୁ!",
        "err_voice": "ଦୟାକରି ପ୍ରଥମେ ଆପଣଙ୍କ ସ୍ୱର ରେକର୍ଡ କରନ୍ତୁ!",
        "err_text": "ଦୟାକରି ପ୍ରଥମେ ଆପଣଙ୍କ ପ୍ରଶ୍ନ ଟାଇପ୍ କରନ୍ତୁ!",
        "spinner": "AI ଆପଣଙ୍କ ପ୍ରଶ୍ନର ବିଶ୍ଳେଷଣ କରୁଛି...",
        "chat_history_header": "💬 କଥୋପକଥନ ଇତିହାସ:",
        "footer": "© 2026 **ୟଶବନ୍ତ ଚୌଧୁରୀ** | ଭାରତୀୟ କୃଷକମାନଙ୍କ ପାଇଁ ସମର୍ପିତ"
    },
    "Assamese (অসমীয়া)": {
        "code": "as",
        "title": "🌾 কৃষক সহায়ক (Rythu Sahayakudu)",
        "caption": "প্ৰস্তুতকৰ্তা: **যশোৱন্ত চৌধুৰী** | বিনামূলীয়া AI কৃষি সহায়ক",
        "select_lang": "ভাষা বাছনি কৰক:",
        "choose_mode": "ইনপুট পদ্ধতি বাছনি কৰক:",
        "mode_voice": "🎙️ ভইচৰ জৰিয়তে (কওক)",
        "mode_text": "✍️ টাইপ কৰি",
        "voice_info": "মাইক বুটাম টিপি আপোনাৰ কৃষি প্ৰশ্ন কওক:",
        "text_placeholder": "আপোনাৰ প্ৰশ্ন ইয়াত টাইপ কৰক...",
        "btn_submit": "🤖 AI পৰামৰ্শ লওক আৰু শুনক",
        "btn_clear": "🔄 নতুন কথোপকথন আৰম্ভ কৰক",
        "err_key": "Streamlit Secrets ত GEMINI_API_KEY যোগ কৰক!",
        "err_voice": "অনুগ্ৰহ কৰি প্ৰথমে আপোনাৰ মাত ৰেকৰ্ড কৰক!",
        "err_text": "অনুগ্ৰহ কৰি প্ৰথমে আপোনাৰ প্ৰশ্ন টাইপ কৰক!",
        "spinner": "AI এ আপোনাৰ প্ৰশ্ন বিশ্লেষণ কৰি আছে...",
        "chat_history_header": "💬 কথোপকথনৰ ইতিহাস:",
        "footer": "© 2026 **যশোৱন্ত চৌধুৰী** | ভাৰতীয় কৃষকসকললৈ উৎসৰ্গিত"
    },
    "Urdu (اردو)": {
        "code": "ur",
        "title": "🌾 کسان معاون (Rythu Sahayakudu)",
        "caption": "ڈویلپر: **یوشونت چودھری** | مفت AI زرعی معاون",
        "select_lang": "زبان منتخب کریں:",
        "choose_mode": "ان پٹ کا طریقہ منتخب کریں:",
        "mode_voice": "🎙️ آواز کے ذریعہ (بولیں)",
        "mode_text": "✍️ تحریر کے ذریعہ (ٹائپ کریں)",
        "voice_info": "مائیک بٹن دبائیں اور اپنا زرعی سوال بولیں:",
        "text_placeholder": "اپنا زرعی سوال یہاں ٹائپ کریں...",
        "btn_submit": "🤖 AI مشورہ حاصل کریں اور سنیں",
        "btn_clear": "🔄 نئی گفتگو شروع کریں",
        "err_key": "براہ کرم Streamlit Secrets میں GEMINI_API_KEY شامل کریں!",
        "err_voice": "براہ کرم پہلے اپنی آواز ریکارڈ کریں!",
        "err_text": "براہ کرم پہلے اپنا سوال ٹائپ کریں!",
        "spinner": "AI آپ کے سوال کا تجزیہ کر رہا ہے...",
        "chat_history_header": "💬 گفتگو کی ہسٹری:",
        "footer": "© 2026 **یوشونت چودھری** | بھارتی کسانوں کے نام"
    },
    "Sanskrit (संस्कृतम्)": {
        "code": "hi", # Sanskrit TTS uses Hindi voice phonetics
        "title": "🌾 कृषक सहायकः (Rythu Sahayakudu)",
        "caption": "निर्माता: **यशवन्त चौधरी** | निःशुल्क AI कृषि सहायकः",
        "select_lang": "भाषां चिनोतु:",
        "choose_mode": "इनपुट-विधिं चिनोतु:",
        "mode_voice": "🎙️ वाण्या (वदतु)",
        "mode_text": "✍️ टङ्कनेन",
        "voice_info": "माइक-पिञ्जं पीडयित्वा स्वस्य कृषि-प्रश्नं वदतु:",
        "text_placeholder": "अत्र स्वस्य कृषि-प्रश्नं टङ्कयतु...",
        "btn_submit": "🤖 AI परामर्शं प्राप्नोतु शृणोतु च",
        "btn_clear": "🔄 नूतन-सम्भाषणं आरभताम्",
        "err_key": "कृपया Streamlit Secrets मध्ये GEMINI_API_KEY योजयतु!",
        "err_voice": "कृपया पूर्वं स्वस्य वाणीं ध्वन्यङ्कयतु!",
        "err_text": "कृपया पूर्वं स्वस्य प्रश्नं टङ्कयतु!",
        "spinner": "AI भवतः प्रश्नस्य विश्लेषणं करोति...",
        "chat_history_header": "💬 सम्भाषण-इतिहासः:",
        "footer": "© 2026 **यशवन्त चौधरी** | भारतीय-कृषकेभ्यः समर्पितम्"
    },
    "Maithili (मैथिली)": {
        "code": "hi",
        "title": "🌾 किसान सहायक (Rythu Sahayakudu)",
        "caption": "निर्माता: **यशवंत चौधरी** | मुफ़्त AI कृषि सहायक",
        "select_lang": "भाषा चुनू:",
        "choose_mode": "इनपुट के तरीका चुनू:",
        "mode_voice": "🎙️ आवाज द्वारा (बजू)",
        "mode_text": "✍️ टाइप कऽ कऽ",
        "voice_info": "माइक बटन दबा कऽ अपन कृषि प्रश्न बजू:",
        "text_placeholder": "अपन कृषि प्रश्न एतय टाइप करू...",
        "btn_submit": "🤖 AI सलाह प्राप्त करू आ सुनू",
        "btn_clear": "🔄 नया बातचीत शुरू करू",
        "err_key": "कृपया Streamlit Secrets मे GEMINI_API_KEY जोड़ू!",
        "err_voice": "कृपया पहिने अपन आवाज रिकॉर्ड करू!",
        "err_text": "कृपया पहिने अपन प्रश्न टाइप करू!",
        "spinner": "AI अहाँक प्रश्नक विश्लेषण कऽ रहल अछि...",
        "chat_history_header": "💬 बातचीत के इतिहास:",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय किसान लोकनिक लेल समर्पित"
    },
    "Santali (ᱥᱟᱱᱛᱟᱲᱤ)": {
        "code": "hi",
        "title": "🌾 ᱪᱟᱥᱤ ᱥᱚᱦᱚᱭᱚᱠ (Rythu Sahayakudu)",
        "caption": "ᱛᱮᱭᱟᱨᱤᱡ: **ᱭᱚᱥᱣᱚᱱᱛᱷ ᱪᱚᱣᱫᱷᱚᱨᱤ** | ᱯᱷᱨᱤ AI ᱪᱟᱥ ᱥᱚᱦᱚᱭᱚᱠ",
        "select_lang": "ᱵᱷᱟᱥᱟ ᱵᱟᱪᱷᱟᱣ ᱢᱮ:",
        "choose_mode": "ᱤᱱᱯᱩᱴ ᱰᱟᱦᱟᱨ ᱵᱟᱪᱷᱟᱣ ᱢᱮ:",
        "mode_voice": "🎙️ ᱟᱲᱟᱝ ᱛᱮ (ᱨᱚᱲ ᱢᱮ)",
        "mode_text": "✍️ ᱚᱞ ᱠᱟᱛᱮ",
        "voice_info": "ᱢᱟᱭᱤᱠ ᱵᱟᱴᱚᱱ ᱫᱟᱵᱟᱣ ᱠᱟᱛᱮ ᱪᱟᱥ ᱠᱩᱠᱞᱤ ᱨᱚᱲ ᱢᱮ:",
        "text_placeholder": "ᱟᱢᱟᱜ ᱪᱟᱥ ᱠᱩᱠᱞᱤ ᱱᱚᱸᱰᱮ ᱚᱞ ᱢᱮ...",
        "btn_submit": "🤖 AI ᱥᱚᱞᱦᱟ ᱧᱟᱢ ᱢᱮ ᱟᱨ ᱟᱸᱡᱚᱢ ᱢᱮ",
        "btn_clear": "🔄 ᱱᱟᱶᱟ ᱜᱟᱞᱢᱟᱨᱟᱣ ᱮᱦᱚᱵ ᱢᱮ",
        "err_key": "Streamlit Secrets ᱨᱮ GEMINI_API_KEY ᱞᱟᱜᱟᱣ ᱢᱮ!",
        "err_voice": "ᱫᱟ stage ᱯᱷᱟᱥᱴ ᱟᱢᱟᱜ ᱟᱲᱟᱝ ᱨᱮᱠᱚᱨᱰ ᱢᱮ!",
        "err_text": "ᱫᱟ stage ᱯᱷᱟᱥᱴ ᱟᱢᱟᱜ ᱠᱩᱠᱞᱤ ᱚᱞ ᱢᱮ!",
        "spinner": "AI ᱟᱢᱟᱜ ᱠᱩᱠᱞᱤ ᱵᱤᱪᱟᱹᱨᱮᱫᱟ...",
        "chat_history_header": "💬 ᱜᱟᱞᱢᱟᱨᱟᱣ ᱤᱛᱤᱦᱟᱥ:",
        "footer": "© 2026 **ᱭᱚᱥᱣᱚᱱᱛᱷ ᱪᱚᱣᱫᱷᱚᱨᱤ** | ᱵᱷᱟᱨᱚᱛᱤᱭᱟᱹ ᱪᱟᱥᱤ ᱠᱚ ᱞᱟᱹᱜᱤᱫ"
    },
    "Kashmiri (کٲشُر)": {
        "code": "ur",
        "title": "🌾 کِسان مَدَدگار (Rythu Sahayakudu)",
        "caption": "بَناوَن وول: **یَشَوَنٹھ چودھری** | مَفَت AI زِراعتِی مَدَدگار",
        "select_lang": "زَبان زالِو:",
        "choose_mode": "اِن پُٹ طَریقہِ زالِو:",
        "mode_voice": "🎙️ آوازِ ذَریعہِ (بَلیو)",
        "mode_text": "✍️️ ٹائپ کٔرِتھ",
        "voice_info": "مائک بَٹن دَباوِو تہِ پَنُن زِراعتِی سَوال بَلیو:",
        "text_placeholder": "پَنُن سَوال یِتین ٹائپ کٔرِو...",
        "btn_submit": "🤖 AI صَلاح حاصِل کٔرِو تہِ بوزِو",
        "btn_clear": "🔄 نَو کَتھ باتھ شُرُوع کٔرِو",
        "err_key": "Streamlit Secrets مَنز GEMINI_API_KEY دَرجم کٔرِو!",
        "err_voice": "مہِربانی کٔرِتھ گوڈہِ پَنِین آواز رِکارڈ کٔرِو!",
        "err_text": "مہِربانی کٔرِتھ گوڈہِ پَنُن سَوال ٹائپ کٔرِو!",
        "spinner": "AI چَھ پَنُن سَوال سَمجھان...",
        "chat_history_header": "💬 کَتھ باتھ ہِسٹری:",
        "footer": "© 2026 **یَشَوَنٹھ چودھری** | ہِندوستٲنی کِسانَن باپَتھ"
    },
    "Konkani (कोंकणी)": {
        "code": "mr",
        "title": "🌾 शेतकार आदारपी (Rythu Sahayakudu)",
        "caption": "निर्मोतो: **यशवंत चौधरी** | फुकट AI शेतकी आदारपी",
        "select_lang": "भास विंचात:",
        "choose_mode": "इनपुट मार्ग विंचात:",
        "mode_voice": "🎙️ आवाजा वरवीं (उलोवचें)",
        "mode_text": "✍️ टाईप करून",
        "voice_info": "मायक बटन दाबून तुमचो शेतकी प्रश्न उलोवचो:",
        "text_placeholder": "तुमचो प्रश्न हांगा टाईप करात...",
        "btn_submit": "🤖 AI सल्लो मेळयात आनी आयकात",
        "btn_clear": "🔄 नवी उलोवप सुरवात करात",
        "err_key": "Streamlit Secrets हांतूं GEMINI_API_KEY घालात!",
        "err_voice": "उपकार करून पयलीं तुमचो आवाज रेकॉर्ड करात!",
        "err_text": "उपकार करून पयलीं तुमचो प्रश्न टाईप करात!",
        "spinner": "AI तुमच्या प्रश्नाचें विश्लेषण करता...",
        "chat_history_header": "💬 उलोवपाचो इतिहास:",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय शेतकाऱ्यांक अर्पण"
    },
    "Dogri (डोगरी)": {
        "code": "hi",
        "title": "🌾 किसान मददगार (Rythu Sahayakudu)",
        "caption": "बनाने आला: **यशवंत चौधरी** | मुफ़्त AI खेती मददगार",
        "select_lang": "भाषा चुनो:",
        "choose_mode": "इनपुट दा तरीका चुनो:",
        "mode_voice": "🎙️ आवाज़ राहें (बोलो)",
        "mode_text": "✍️ टाइप करियै",
        "voice_info": "माइक बटन दबाओ ते अपना खेती दा सवाल बोलो:",
        "text_placeholder": "अपना सवाल इत्थै टाइप करो...",
        "btn_submit": "🤖 AI सलाह हासल करो ते सुनो",
        "btn_clear": "🔄 नवीं गल्लबात शुरू करो",
        "err_key": "Streamlit Secrets च GEMINI_API_KEY पाओ!",
        "err_voice": "कृपा करियै पैहले अपनी आवाज़ रिकार्ड करो!",
        "err_text": "कृपा करियै पैहले अपना सवाल टाइप करो!",
        "spinner": "AI तुंदे सवाल दा विश्लेषण करा करदा ऐ...",
        "chat_history_header": "💬 गल्लबात दी हिस्ट्री:",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय किसानें गी समर्पित"
    },
    "Sindhi (سنڌي)": {
        "code": "ur",
        "title": "🌾 هاري مددگار (Rythu Sahayakudu)",
        "caption": "ٺاهيندڙ: **يشونت چوڌري** | مفت AI زرعي مددگار",
        "select_lang": "ٻولي چونڊيو:",
        "choose_mode": "انپٽ جو طريقو چونڊيو:",
        "mode_voice": "🎙️ آواز ذريعي (ڳالهايو)",
        "mode_text": "✍️️ ٽائپ ڪري",
        "voice_info": "مائيڪ بٽڻ ٻاري پنهنجو زرعي سوال ڳالهايو:",
        "text_placeholder": "پنهنجو سوال هتي ٽائپ ڪريو...",
        "btn_submit": "🤖 AI صلاح حاصل ڪريو ۽ ٻڌو",
        "btn_clear": "🔄 نئين گفتگو شروع ڪريو",
        "err_key": "Streamlit Secrets ۾ GEMINI_API_KEY داخل ڪريو!",
        "err_voice": "مهرباني ڪري پهريان پنهنجو آواز رڪارڊ ڪريو!",
        "err_text": "مهرباني ڪري پهريان پنهنجو سوال ٽائپ ڪريو!",
        "spinner": "AI توهان جي سوال جو تجزيو ڪري رهيو آهي...",
        "chat_history_header": "💬 گفتگو جي هسٽري:",
        "footer": "© 2026 **يشونت چوڌري** | بالڪل هندستاني هارين لاءِ"
    },
    "Bodo (बर')": {
        "code": "hi",
        "title": "🌾 आबादारी मदतगिरि (Rythu Sahayakudu)",
        "caption": "सोरजिनगिरि: **यसवंत चौधरी** | बिनामुलिया AI आबादारी मददगिरि",
        "select_lang": "राव सायख':",
        "choose_mode": "इनपुट लामा सायख':",
        "mode_voice": "🎙️ रावजों (रायाव)",
        "mode_text": "✍️ लिरनानै",
        "voice_info": "माइकु बटन थुनानै नोंथांनि आबादारी सोंथि रायाव:",
        "text_placeholder": "नोंथांनि सोंथि बेयाव लिर...",
        "btn_submit": "🤖 AI थिसाननाय लाआ आरो खोनासं",
        "btn_clear": "🔄 गोदान रायज्लायनाय जागायनै",
        "err_key": "Streamlit Secrets आव GEMINI_API_KEY सोना ला!",
        "err_voice": "अननानै सिगां नोंथांनि राव रेकर्ड खालाम!",
        "err_text": "अननानै सिगां नोंथांनि सोंथि लिर!",
        "spinner": "AI आ नोंथांनि सोंथिखौ बिजिरगासिनो दं...",
        "chat_history_header": "💬 रायज्लायनायनि जारौ:",
        "footer": "© 2026 **यसवंत चौधरी** | भारोतनि आबादारीफोरनि थाखाय"
    },
    "Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)": {
        "code": "bn",
        "title": "🌾 ꯂꯧꯃꯤ ꯃꯇꯦꯡꯄꯥꯡꯕ (Rythu Sahayakudu)",
        "caption": "ꯁꯦꯝꯈꯤꯕ: **ꯌꯁꯋꯟꯊ ꯆꯧꯙꯔꯤ** | ꯐ꯭ꯔꯤ AI ꯂꯧꯃꯤ ꯃꯇꯦꯡꯄꯥꯡꯕ",
        "select_lang": "ꯂꯣꯟ ꯈꯅꯕꯤꯌꯨ:",
        "choose_mode": "ꯏꯟꯄꯨꯠ ꯃꯑꯣꯡ ꯈꯅꯕꯤꯌꯨ:",
        "mode_voice": "🎙️ ꯈꯣꯜꯊꯦꯡꯅ (ꯉꯥꯡꯕꯤꯌꯨ)",
        "mode_text": "✍️ ꯏꯕꯅ",
        "voice_info": "ꯃꯥꯏꯛ ꯕꯇꯟ ꯅꯃꯗꯨꯅ ꯑꯗꯣꯃꯒꯤ ꯋꯥꯍꯪ ꯉꯥꯡꯕꯤꯌꯨ:",
        "text_placeholder": "ꯑꯗꯣꯃꯒꯤ ꯋꯥꯍꯪ ꯁꯋꯥꯏꯗ ꯏꯕꯤꯌꯨ...",
        "btn_submit": "🤖 AI ꯄꯥꯎꯇꯥꯛ ꯂꯧꯕꯤꯌꯨ ꯑꯃꯁꯨꯡ ꯇꯥꯕꯤꯌꯨ",
        "btn_clear": "🔄 ꯑꯅꯧꯕ ꯋꯥꯔꯤ ꯍꯧꯕꯤꯌꯨ",
        "err_key": "Streamlit Secrets ꯗ GEMINI_API_KEY ꯍꯥꯄꯆꯤꯟꯕꯤꯌꯨ!",
        "err_voice": "ꯑꯍꯥꯟꯕꯗ ꯑꯗꯣꯃꯒꯤ ꯈꯣꯜꯊꯦꯡ ꯔꯦꯀꯣꯔ꯭ꯗ ꯇꯧꯕꯤꯌꯨ!",
        "err_text": "ꯑꯍꯥꯟꯕꯗ ꯑꯗꯣꯃꯒꯤ ꯋꯥꯍꯪ ꯏꯕꯤꯌꯨ!",
        "spinner": "AI ꯅ ꯑꯗꯣꯃꯒꯤ ꯋꯥꯍꯪ ꯅꯩꯔꯤ...",
        "chat_history_header": "💬 ꯋꯥꯔꯤꯒꯤ ꯄꯨꯋꯥꯔꯤ:",
        "footer": "© 2026 **ꯌꯁꯋꯟꯊ ꯆꯧꯙꯔꯤ** | ꯏꯟꯗꯤꯌꯥꯒꯤ ꯂꯧꯃꯤꯁꯤꯡꯒꯤꯗꯃꯛ"
    },
    "Nepali (नेपाली)": {
        "code": "ne",
        "title": "🌾 किसान सहायक (Rythu Sahayakudu)",
        "caption": "विकासकर्ता: **यशवंत चौधरी** | नि:शुल्क AI कृषि सहायक",
        "select_lang": "भाषा छान्नुहोस्:",
        "choose_mode": "इनपुटको माध्यम छान्नुहोस्:",
        "mode_voice": "🎙️ आवाजद्वारा (बोल्नुहोस्)",
        "mode_text": "✍️ टाइप गरेर",
        "voice_info": "माइक बटन थिचेर आफ्नो कृषि प्रश्न बोल्नुहोस्:",
        "text_placeholder": "आफ्नो प्रश्न यहाँ टाइप गर्नुहोस्...",
        "btn_submit": "🤖 AI सल्लाह प्राप्त गर्नुहोस् र सुन्नुहोस्",
        "btn_clear": "🔄 नयाँ कुराकानी सुरु गर्नुहोस्",
        "err_key": "कृपया Streamlit Secrets मा GEMINI_API_KEY थप्नुहोस्!",
        "err_voice": "कृपया पहिले आफ्नो आवाज रेकर्ड गर्नुहोस्!",
        "err_text": "कृपया पहिले आफ्नो प्रश्न टाइप गर्नुहोस्!",
        "spinner": "AI ले तपाईंको प्रश्नको विश्लेषण गर्दैछ...",
        "chat_history_header": "💬 कुराकानीको इतिहास:",
        "footer": "© 2026 **यशवंत चौधरी** | भारतीय किसानहरूका लागि समर्पित"
    },
    "English": {
        "code": "en",
        "title": "🌾 Rythu Sahayakudu (Farmer Assistant)",
        "caption": "Developed by **Yaswanth Chowdary** | Free Open-Source AI Farming Assistant",
        "select_lang": "Select Language:",
        "choose_mode": "Choose Input Method:",
        "mode_voice": "🎙️ Voice Input (Record Audio)",
        "mode_text": "✍️ Text Input (Type)",
        "voice_info": "Tap the mic button and speak your farming question:",
        "text_placeholder": "Type your farming question or follow-up here...",
        "btn_submit": "🤖 Get AI Advice & Listen",
        "btn_clear": "🔄 Start New Conversation",
        "err_key": "Please add your GEMINI_API_KEY to Streamlit Secrets!",
        "err_voice": "Please record a voice message first!",
        "err_text": "Please type a question first!",
        "spinner": "AI is analyzing your farming query...",
        "chat_history_header": "💬 Conversation History:",
        "footer": "© 2026 **Yaswanth Chowdary** | Dedicated to Indian Farmers"
    }
}

# 1. Language Dropdown Selection
selected_lang_name = st.selectbox(
    "Select Language / भाषा चुनिए / భాషను ఎంచుకోండి:", 
    list(UI_TRANSLATIONS.keys())
)

# Fetch current language's UI dictionary
t = UI_TRANSLATIONS[selected_lang_name]
lang_code = t["code"]

# Render Header & Developer Credit
st.title(t["title"])
st.caption(t["caption"])
st.markdown("---")

# Initialize Session State Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear Chat Session Button
if st.button(t["btn_clear"]):
    st.session_state.messages = []
    st.rerun()

# Display Ongoing Chat History
if st.session_state.messages:
    st.markdown(f"### {t['chat_history_header']}")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "audio" in msg and msg["audio"]:
                st.audio(msg["audio"], format="audio/mp3")

st.markdown("---")

# Choose Input Method (Voice or Text)
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
    text_file_input = st.text_area("Question / Follow-up:", placeholder=t["text_placeholder"])

# Securely retrieve API Key from Streamlit Secrets
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

                # System instruction directing Gemini to answer strictly in the selected language
                system_instruction = (
                    f"You are an agricultural expert named Rythu Sahayakudu built by Yaswanth Chowdary. "
                    f"You are advising an Indian farmer in the {selected_lang_name} language. "
                    f"Provide direct, simple, and practical agricultural advice strictly in {selected_lang_name}."
                )

                # Format past conversation history
                history_prompt = system_instruction + "\n\nConversation Context:\n"
                for m in st.session_state.messages:
                    history_prompt += f"{m['role'].capitalize()}: {m['content']}\n"

                if input_mode_choice == t["mode_voice"]:
                    audio_bytes = audio_file_input.read()
                    audio_data = {
                        "mime_type": audio_file_input.type,
                        "data": audio_bytes
                    }
                    prompt_parts = [history_prompt, "Farmer's audio query:", audio_data]
                    response = model.generate_content(prompt_parts)
                    user_msg_text = "🎙️ [Voice Question Received]"
                else:
                    prompt_parts = f"{history_prompt}\nFarmer's query: {text_file_input}"
                    response = model.generate_content(prompt_parts)
                    user_msg_text = text_file_input

                advice_text = response.text

                # Generate Spoken Audio Output (TTS)
                audio_filename = f"response_{len(st.session_state.messages)}.mp3"
                try:
                    tts = gTTS(text=advice_text, lang=lang_code, slow=False)
                    tts.save(audio_filename)
                except Exception:
                    tts = gTTS(text=advice_text, lang="en", slow=False)
                    tts.save(audio_filename)

                # Append user prompt and assistant response into conversation history
                st.session_state.messages.append({"role": "user", "content": user_msg_text})
                st.session_state.messages.append({"role": "assistant", "content": advice_text, "audio": audio_filename})

                st.rerun()

            except Exception as e:
                st.error(f"Error processing with AI: {str(e)}")

# Footer
st.divider()
st.markdown(t["footer"])
