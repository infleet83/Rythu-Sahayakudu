import streamlit as st
from gtts import gTTS
import google.generativeai as genai
import os

# Page title & config
st.set_page_config(page_title="Rythu Sahayakudu", page_icon="🌾")

# 1. Indian Languages Supported
LANGUAGES = {
    "Telugu (తెలుగు)": "te",
    "Hindi (हिन्दी)": "hi",
    "Bengali (বাংলা)": "bn",
    "Tamil (தமிழ்)": "ta",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Marathi (मరాఠీ)": "mr",
    "Gujarati (ગુજરાતી)": "gu",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Urdu (اردو)": "ur"
}

# Header and Creator Credit
st.title("🌾 Rythu Sahayakudu (రైతు సహాయకుడు)")
st.caption("Developed by **Yaswanth Chowdary** | Free Open-Source AI Farming Assistant")

# Select Language
selected_lang_name = st.selectbox("Select Language / భాషను ఎంచుకోండి:", list(LANGUAGES.keys()))
lang_code = LANGUAGES[selected_lang_name]

# User Input
user_question = st.text_area("Ask Your Farming Question / మీ వ్యవసాయ ప్రశ్నను అడగండి:", placeholder="e.g., How to treat leaf yellowing in paddy?")

# API Key check
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

if st.button("🤖 Get AI Advice & Listen", type="primary"):
    if not user_question.strip():
        st.warning("Please enter a question first!")
    else:
        with st.spinner("Processing advice..."):
            # Get AI response
            if GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"You are an agricultural expert helping an Indian farmer. Answer simply and directly in {selected_lang_name}: {user_question}"
                try:
                    response = model.generate_content(prompt)
                    advice_text = response.text
                except Exception as e:
                    advice_text = f"Error generating advice: {str(e)}"
            else:
                advice_text = f"Advice in {selected_lang_name} for: '{user_question}'\n\n(Note: Add GEMINI_API_KEY in Secrets for live AI responses)."

            # Show Text Answer
            st.markdown("### 💡 Farming Advice:")
            st.write(advice_text)

            # Generate and Play Audio
            audio_path = "advice.mp3"
            try:
                tts = gTTS(text=advice_text, lang=lang_code, slow=False)
                tts.save(audio_path)
            except Exception:
                tts = gTTS(text=advice_text, lang="en", slow=False)
                tts.save(audio_path)

            st.audio(audio_path, format="audio/mp3")

# Footer Credit
st.divider()
st.markdown("© 2026 **Yaswanth Chowdary** | Dedicated to Indian Farmers")
