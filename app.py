import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import tempfile
import pygame


# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("google_api_key"))

def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0]])
    return response.text

def get_input_text(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                'mime_type': uploaded_file.type,
                'data': bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No File Is Uploaded")

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Please speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        st.sidebar.write(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Sorry, I couldn't understand what you said.")
        return None
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Streamlit app
st.header("Health Advisor 😊")
uploaded_file = st.sidebar.file_uploader('Upload your file..', type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Your uploaded image')



general_prompt = "You are an AI assistant. Analyze the image and answer any questions about it. "


speak_button = st.button('Speak to Ask')


if speak_button:
    if uploaded_file is not None:
        image_data = get_input_text(uploaded_file)
        spoken_text = get_audio_input()
        if spoken_text:
            response = get_gemini_response(f"{general_prompt} The user asked: {spoken_text}", image_data)
            st.subheader("Response:")
            st.write(response)
            audio_file = text_to_speech(response)
            st.audio(audio_file)
            play_audio(audio_file)
    else:
        st.warning("Please upload an image first.")

if __name__ == "__main__":
    st.sidebar.markdown("### Instructions:")
    st.sidebar.markdown("1. Upload an image of food")
    st.sidebar.markdown("2. Or click 'Speak to Ask' to ask a question about the image")