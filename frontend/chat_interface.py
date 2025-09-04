import streamlit as st
from api_utils import get_api_response
from audiorecorder import audiorecorder
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import tempfile


load_dotenv()

# def speech_to_text():
#     """Capture voice from mic and convert to text"""
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         audio = recognizer.listen(source)
#         # try:
#         if audio is None:
#             st.error("Speak again")
#         else:
#             text = recognizer.recognize_google(audio)
#         # st.write(f"🗣️ You said: {text}")
#         return text
#         # except sr.UnknownValueError:
#         #     st.error("❌ Could not understand audio")
#         # except sr.RequestError:
#         #     st.error("⚠️ Speech recognition service error")
#     return None


def speech_to_text():

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        return text




def text_to_speech(text):
    """Convert text to speech and play audio in Streamlit"""
    if not text:
        return
    tts = gTTS(text=text, lang="en")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    st.audio(temp_file.name, format="audio/mp3", autoplay=True)



def display_voice_chat_interface():
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # if prompt := st.chat_input("Query:"):
    if st.button("🎙️ Speak"):
        with st.spinner("Recording voice..."):
            user_input = speech_to_text()
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                # with st.chat_message("user"):
                    # st.markdown(user_input)

        with st.spinner("Generating response..."):
            response = get_api_response(user_input, st.session_state.session_id, st.session_state.model)
            text_to_speech(response['answer'])
            
            if response:
                st.session_state.session_id = response.get('session_id')
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})
                
            else:
                st.error("Failed to get a response from the API. Please try again.")


# def display_voice_chat_interface():
#     # Chat interface
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     if st.button("🎙️ Speak"):
#         with st.spinner("Recording voice..."):
#             user_input = speech_to_text()

#         # Guard clause: if no valid speech, stop here
#         if not user_input:
#             st.warning("🎙️ No valid speech detected. Please try again.")
#             return

#         # If we got valid speech, add to chat
#         st.session_state.messages.append({"role": "user", "content": user_input})

#         with st.spinner("Generating response..."):
#             response = get_api_response(user_input, st.session_state.session_id, st.session_state.model)

#         # Guard clause: ensure response is valid
#         if not response or "answer" not in response:
#             st.error("⚠️ Failed to get a valid response from the API. Please try again.")
#             return

#         # If response is valid → speak + store in history
#         text_to_speech(response["answer"])
#         st.session_state.session_id = response.get("session_id", st.session_state.session_id)
#         st.session_state.messages.append({"role": "assistant", "content": response["answer"]})



def display_Text_chat_interface():
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Query:"):
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)
            
            if response:
                st.session_state.session_id = response.get('session_id')
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})
                
                with st.chat_message("assistant"):
                    st.markdown(response['answer'])
                    
                    with st.expander("Details"):
                        # st.subheader("Generated Answer")
                        # st.code(response['answer'])
                        st.subheader("Model Used")
                        st.code(response['model'])
                        st.subheader("Session ID")
                        st.code(response['session_id'])
            else:
                st.error("Failed to get a response from the API. Please try again.")
