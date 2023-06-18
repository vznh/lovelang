import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Listening...")
    audio = r.listen(source, phrase_time_limit=10)  # Set a time limit for each phrase

    # Check if Enter key was pressed
    input("Press Enter to stop listening...")
    print("Stopped listening.")

try:
    text = r.recognize_google(audio, language='fr-BE')  # Use 'zh-CN' for Mandarin
    print("You said : {}".format(text))
except:
    print("Sorry, I didn't get that.")

def listen_for_audio( lang: str, matching: str ):
    import speech_recognition as sr
    from legend import lang
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=7.5)  # Set a time limit for each phrase
        print("Stopped listening.")

    pass