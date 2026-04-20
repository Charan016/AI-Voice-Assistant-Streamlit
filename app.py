import streamlit as st # used to built the frontend page


# Configure the frontend page 
st.set_page_config(
    page_title="Voice Assistant",
    layout = "wide"
)

# import all req lib

import os
import time 
import pyttsx3
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

# Load the API key from Local Envirnoment 
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# checking if API keys is uploaded or not 

if not GROQ_API_KEY:
    st.error("Missing API KEY")
    st.stop()

# intialization of LLM Model
client = Groq(api_key = GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# Intialization of Speech Recognizer and Text to Speech Engine
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()

recognizer = get_recognizer()

# Intialization of Text to Speech 
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        st.error(f"Error initializing TTS engine: {e}")
        return None
    
def speak(text, voice_gender = "Girl"):
    try:
        engine = get_tts_engine()
        if not engine:
            return

        voices = engine.getProperty("voices")

        if voices:
            if voice_gender == "Boy":
                for voice in voices:
                    if "male" in voice.name.lower():
                        engine.setProperty("voice", voice.id)
                        break
            else:
                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty("voice", voice.id)
                        break
            
        engine.setProperty("rate", 150) # set the speech rate
        engine.setProperty("volume", 0.8) # set the volume level
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"Error during TTS: {e}")

def listen_to_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, phrase_time_limit=10)

            text = recognizer.recognize_google(audio)
            return text.lower()

    except sr.UnknownValueError:
        return "Sorry, I didn't catch you"
    except sr.RequestError:
        return "Speech service is not available"
    except Exception as e:
        return f"Error: {e}"

def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model = MODEL, 
            messages = messages,
            temperature = 0.7 # how much crative the answer will be 
        )
        result = response.choices[0].message.content
        return result.strip() if result else "Sorry, I could not generate the response"
    except Exception as e:
        return f"Error: {e}"


def main():
    st.title("AI Voice Assistant")
    st.markdown("---")

    # Intilaizing chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
             {"role": "system", "content": "You are a helpful voice assistant. Reply just one line"}
        ]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("CONTROLS")

        tts_enabled = st.checkbox("Enable Text to Speech", value = True)

        # selecting Gender of Voice assiatnce
        voice_gender = st.selectbox(
            "voice_gender",
            options = ["Girl", "Boy"],
            index = 0,
            help = "Choose the Gender of Voice Assiatnt"
        )

        if st.button("Start Voice Input", use_container_width = True):
            with st.spinner("Listening..."):
                user_input = listen_to_speech()

                if user_input and user_input not in ["Sorry, I didn't catch you", "Speech service is not available"]:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "user", "content": user_input})

                with st.spinner("Thinking..."):
                    ai_response = get_ai_response(st.session_state.chat_history)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

                if tts_enabled:
                    speak(ai_response, voice_gender)

                st.rerun()

                st.markdown("----")

        if st.button("Clear Chat", use_container_width = True):
            st.session_state.messages = []
            st.session_state.chat_history = [
                {"role": "system", "content": "You are a helpful voice assistant. Reply just one line"}
                ]
            st.success("Chat history cleared!")
            st.rerun()

    st.subheader("CONVERSATION")

    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
    
    st.markdown("---")
    st.markdown(
        """<div style="text-align: center; color: #666; font-size: 14px;">
            <p> copyright @ Nerella Charan </p>
        </div>""",
        unsafe_allow_html=True
    )
                

if __name__ == "__main__":
    main()