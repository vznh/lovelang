from gtts import gTTS
from google.cloud import texttospeech

# Set up the Google Cloud Text-to-Speech client
client = texttospeech.TextToSpeechClient()

# Define the text you want to synthesize
text = "Hello, world!"

# Specify the desired voice parameters
voice = texttospeech.VoiceSelectionParams(
    language_code="ko-KR",  # Language code (e.g., "en-US" for English)
    ssml_gender=texttospeech.SsmlVoiceGender.MALE  # Gender of the voice
)

# Set the audio output format
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3  # Specify MP3 as the audio format
)

# Generate the speech using the Google Cloud Text-to-Speech API
synthesis_input = texttospeech.SynthesisInput(text=text)
response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

# Save the synthesized speech as an MP3 file
with open('output.mp3', 'wb') as f:
    f.write(response.audio_content)


def listen_for_audio( lang: str, matching: str ):
    import speech_recognition as sr
    legend= {
    "English": "en_GB",
    "Korean": "ko_KR",
    "Japanese": "ja_JP",
    "Mandarin": "zh_CN",
    "Spanish": "es_ES"
    }
    lang=lang.capitalize()
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=7.5)  # Set a time limit for each phrase
        print("Stopped listening.")

    try:
        text = r.recognize_google(audio, language=legend[lang])  # Use 'zh-CN' for Mandarin
        print("You said : {}".format(text))
    except:
        print("Sorry, I didn't get that.")
    else:
        if text==matching:
            print("Correct!")
        else:
            print("Incorrect!")

def speak_syllable_by_syllable( lang: str, sentence: str) -> None:
    legend= {
    "English": "en_GB",
    "Korean": "ko_KR",
    "Japanese": "ja_JP",
    "Mandarin": "zh_CN",
    "Spanish": "es_ES"
    }
    client = texttospeech.TextToSpeechClient()
    lang=lang.capitalize()
    voice = texttospeech.VoiceSelectionParams(
    language_code="ko-KR", 
    ssml_gender=texttospeech.SsmlVoiceGender.MALE)  # gender of the voice

    audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3)  # specify MP3 as the audio format)
    for syllable in sentence:

if __name__ == "__main__":
    listen_for_audio("Korean", "안녕")