import streamlit as st
from gtts import gTTS
import google.generativeai as genai
import os

# Page title & config
st.set_page_config(page_title="Rythu Sahayakudu", page_icon="🌾")

# 1. Indian Languages
LANGUAGES = {
    "Telugu (తెలుగు)": "te",
    "Hindi (हिन्दी)": "hi",
    "Bengali (বাংলা)": "bn",
    "Tamil (தமிழ்)": "ta",
    "Kannada (కನ್ನಡ)": "kn",
    "Marathi (मరాఠీ)": "mr",
    "Gujarati (ગુજરાતી)": "gu",
    "Malayalam (മലയാളം)": "ml",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Urdu (اردو)": "ur"
}

# Header & Credits
st.title("🌾 Rythu Sahayakudu (రైతు సహాయకుడు)")
st.caption("Developed by **Yaswanth Chowdary** | Free Open-Source AI Farming Assistant")

# Select Language
selected_lang_name = st.selectbox("Select Language / భాషను ఎంచుకోండి:", list(LANGUAGES.keys()))
lang_code = LANGUAGES[selected_lang_name]

st.markdown("---")

# Input Method Selection
input_mode = st.radio("Choose Input Method / ఇన్‌పుట్ మార్గాన్ని ఎంచుకోండి:", ["🎙️ Voice Input (Record Audio)", "✍️ Text Input (Type)"])

audio_file_input = None
text_file_input = ""

if input_mode == "🎙️ Voice Input (Record Audio)":
    st.info("Tap the microphone below and speak your farming question clearly:")
    audio_file_input = st.audio_input("Record your question")
else:
    text_file_input = st.text_area("Type your question here:", placeholder="e.g., How to treat leaf yellowing in paddy?")

# Fetch API Key securely
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

if st.button("🤖 Process Question & Listen Advice", type="primary"):
    if not GEMINI_API_KEY:
        st.error("Please add your GEMINI_API_KEY to Streamlit Secrets!")
    elif input_mode == "🎙️ Voice Input (Record Audio)" and not audio_file_input:
        st.warning("Please record a voice message first!")
    elif input_mode == "✍️ Text Input (Type)" and not text_file_input.strip():
        st.warning("Please type a question first!")
    else:
        with st.spinner("Gemini AI is analyzing your farming query..."):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')

                # System instruction for farming domain
                system_prompt = f"You are an agricultural expert helping an Indian farmer. Answer clearly, simply, and directly in {selected_lang_name}."

                if input_mode == "🎙️ Voice Input (Record Audio)":
                    # Pass the audio bytes directly to Gemini
                    audio_bytes = audio_file_input.read()
                    audio_data = {
                        "mime_type": audio_file_input.type,
                        "data": audio_bytes
                    }
                    response = model.generate_content([system_prompt, audio_data])
                else:
                    response = model.generate_content(f"{system_prompt}\nFarmer Question: {text_file_input}")

                advice_text = response.text

                # Display Text Advice
                st.markdown("### 💡 Farming Advice:")
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
                st.error(f"Error processing with Gemini API: {str(e)}")

# Footer Credit
st.divider()
st.markdown("© 2026 **Yaswanth Chowdary** | Dedicated to Indian Farmers")
