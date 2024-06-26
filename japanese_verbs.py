import streamlit as st
import pandas as pd
import random
import time
import edge_tts
import asyncio
import tempfile
from pydub import AudioSegment
from pydub.playback import play

# Load CSV file (assuming 'verbs.csv' contains Romaji, Kana, and Meaning columns)
df = pd.read_csv('verbs.csv')

# Set up the page with custom CSS for colorful styling and scroll button
st.markdown("""
<style>
    .custom-text {
        font-size: 24px;
        color: #333;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .divider {
        border-top: 2px solid #ccc;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Function to speak and display the word
async def speak_and_display_word(word, option):
    if option == "Romaji":
        display_word = word['Romaji']
        speak_word = word['Romaji']
        meaning = word['Meaning']
    elif option == "English":
        display_word = word['Meaning']
        speak_word = word['Romaji']
        meaning = word['Romaji']
    else:  # Both Random
        if random.choice([True, False]):
            display_word = word['Romaji']
            speak_word = word['Romaji']
            meaning = word['Meaning']
        else:
            display_word = word['Meaning']
            speak_word = word['Meaning']
            meaning = word['Romaji']

    # Speak and display the Romaji or Meaning based on the option selected
    st.markdown(f'<div class="custom-text">{display_word}</div>', unsafe_allow_html=True)
    
    # Using edge-tts for text-to-speech
    communicate = edge_tts.Communicate()
    tts_stream = await communicate.tts(speak_word)
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    
    with open(temp_audio_file.name, "wb") as f:
        async for chunk in tts_stream:
            if chunk:
                f.write(chunk)
    
    audio = AudioSegment.from_file(temp_audio_file.name)
    play(audio)
    temp_audio_file.close()

    time.sleep(2)  # Keep the word displayed for 2 seconds

    # Clear previous text after 2 seconds
    st.empty()

    # Display the word meanings
    st.subheader(f"Romaji: {word['Romaji']}")
    st.subheader(f"Kana: {word['Kana']}")
    st.subheader(f"Meaning: {word['Meaning']}")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)  # Add divider after each word

# Set up the page
st.title("Learn Japanese Verbs")
st.write("Click on 'Guess Meaning' to start.")

# Select which words to show
option = st.selectbox(
    "Which words do you want to show?",
    ("Romaji", "English", "Both Random")
)

# Create a button to scroll automatically
scroll_button = st.empty()

# Button to start guessing
if st.button("Guess Meaning"):
    words = df.to_dict('records')
    random.shuffle(words)

    for word in words:
        # Speak and display the word
        asyncio.run(speak_and_display_word(word, option))

        # Execute JavaScript to scroll to the bottom of the page after 3 seconds
        scroll_button.markdown("""
        <script>
            setTimeout(function() {
                var element = document.getElementById("scrollButton");
                element.click();
            }, 3000);
        </script>
        """, unsafe_allow_html=True)

        # Pause briefly before showing the next word
        time.sleep(1)

    st.success("Congratulations, you've completed all verbs!")
