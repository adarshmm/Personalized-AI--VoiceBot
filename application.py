import os
import base64
from dotenv import load_dotenv
import openai
import streamlit as st
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript_response = openai.Audio.transcribe("whisper-1", audio_file)
    if isinstance(transcript_response, dict) and "text" in transcript_response:
        transcript = transcript_response["text"]
    else:
        transcript = str(transcript_response)
    return transcript

def text_to_speech(input_text):
    tts = gTTS(text=input_text, lang='en')
    audio_file_path = "temp_audio_play.mp3"
    tts.save(audio_file_path)
    return audio_file_path

def get_answer(messages):
    content = """You are a person whose personality details are mentioned below that answers questions asked by an interviewer as this person.
                 Personality Details: \n\n
                 Life: Passionate to become software engineer, Likes coding in free time,
                 like to research and keeps updated on tech related contents, Improvising and aquiring knowledge continuously.
                 Super power : Adaptability. \n
                 Like to grow in these areas: Presentations, Leadership, Strategic Thinking. \n
                 Coworker's Misconception about the person: Introverted. \n
                 How the person pushes his boundaries: By taking every problem as a challenge. \n
                 Other: Person is having a moderate amount of humor(without hurting anyone) in all of his responses. So make all of the response funny. \n
                 If any questions are asked by the user which is not in personality context, then you can generate something out of context.
                 """
    system_message = [{"role": "system", "content": content}]
    messages = system_message + messages
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-1106", messages=messages)
    return response.choices[0].message.content

def autoplay_audio(file_path, placeholder):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""<audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
    placeholder.markdown(audio_html, unsafe_allow_html=True)

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! How may I assist you today?"}]

initialize_session_state()

st.title("PersonaliZed Voice Bot 🚀")
st.subheader("Please click on the record button to ask your question")

audio_placeholder = st.empty()
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

if audio_bytes:
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)
        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            final_response = get_answer(st.session_state.messages)
        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file, audio_placeholder)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)
