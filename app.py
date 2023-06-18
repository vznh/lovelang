# note: coded in Python 3.10.5 x64
from flask import Flask, render_template, request, jsonify, session
from flask_pymongo import PyMongo
import os
import openai
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'cred.json'

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init')
def initialization():
    return render_template('init.html')

@app.route('/picksubject/<lang>')
def picksubject_render(lang):
    return render_template('picksubject.html', lang=lang)

@app.route('/picksubject/<lang>/modules')
def modules_render(lang):
    return render_template('modules.html', lang=lang)

@app.route('/picksubject/<lang>/converse')
def converse_render(lang):
    return render_template('converse.html', lang=lang)

@app.route( '/welcome/<name>' )
def welcome(name):
    return render_template('index.html',name=name)

@app.route( '/picksubject/<lang>/practice' )
def practice_page_render(lang):
    return render_template('practice.html', lang=lang)


def requestGPT(sentence:str, method:int): 
    """
    Args:
        sentence: the sentence to be processed by GPT
        method: 0-syllable breakdown, 1-conversational side, 2-split sentence
    Returns:
        based on method, 0->dict, 1->string, 2->array
    """
    res: str = ''
    match method:
        case 0: # this is syllable split up by sentence
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": """
From now on, when I ask for a word in any language, return its syllables to help an English speaker understand the language better. Present it in such:
an array supporting Python that has the syllables such as:
bibimbap (비빔밥) be-bim-bap
-> { "be": "Pronounced such as the sentence 'to be'", "bim": "rhyme of dim", "bap": "bab"}
When returning a value, could you also give helpful guides on how to say the syllable in the value portion of the dict? 

I will request data like:
language word

So an example call  to you would be:
Korean 안녕

The ideal response is just a dictionary in this format. No other necessary notes are needed EXCEPT for the dictionary. Make sure to add detail in the values of the dict.
{syllable: helpful tips to pronounce the word}
                """},
                {"role": "user", "content": sentence}
            ]
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=250,
            )
            res = response['choices'][0]['message']['content']
            return res

        case 1: # split sentence
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": """
For a sentence, could you split a sentence of any language that I give you into syllable-by-syllable of the original pronunciation? For each word, please put into a separate lists to make a list of lists. Such as if:

아, 네!
[[아], [네]]

or
안녕하세요, 제 이름은 봅입니다.
[[안, 녕, 하, 세, 요], [제], [이, 름, 은], [봅, 입, 니, 디]]
and return a response with ONLY an array format with these responses in mind. Do not say anything more

Here's your first one (REMEMBER TO ONLY REPLY IN THE ARRAY):
                """},
                {"role": "user", "content": sentence}
            ]
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=250,
            )
            res = response['choices'][0]['message']['content']
            return res
    return "GPT is not accessible at this time."

def conversateGPT( lang: str, sentence: str ) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": """
You are an avid individual who loves learning languages -- you have knowledge about every language in existence, except for the extinct ones of course. If I do not respond in a correct language, or if you just don't understand my response because it's too vague, respond with 'What did you say?' in the respective language. Your job is to practice with me to speak. Do not start until I say 'Hello' to you -- when I say hello, begin a beginner-level conversation from easy terms in a language that I prefer, then gradually (very slowly) increase in difficulty. For this conversation, let's start with {}""".format(lang),
                },
                {"role": "user", "content": sentence}
            ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=250,
        )
        res = response['choices'][0]['message']['content']
        return res

def listen_for_audio( lang: str, matching: str ) -> bool:
    '''
    Args:
        lang: language to listen for
        matching: the matching string to compare to
    Returns:
        true if the matching string is said, false otherwise

    example call
    listen_for_audio("Korean", "안녕")
    '''
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
        print("{}".format(text))
    except:
        raise "Didn't understand this."
    else: return text
    
def setup_curriculum(language: str, curriculum: dict, level: int) -> set:
    from random import choice
    """Sets up the curriculum for the given language.
    
    Example usage:
    setup_curriculum("Korean", dataset, 2)
    -> set of 10 words that are at level 2 or below in the Korean curriculum

    Args:
        language (str): language of curriculum
        curriculum (dict): list of words

    Returns:
        set of words that will be depicted in the lesson, always will be 10 words
    """
    res = []
    for i in range(level + 1):
        for j in range(i + 1):
            curriculum_i = curriculum.get(j)
            if curriculum_i:
                res.extend(curriculum_i)
    return [choice(res) for _ in range(10)]

import pygame
import os
from google.cloud import texttospeech

def speak_syllable_by_syllable(lang: str, sentence: str) -> None:
    legend= {
    "English": "en_GB",
    "Korean": "ko_KR",
    "Japanese": "ja_JP",
    "Mandarin": "zh_CN",
    "Spanish": "es_ES"
    }
    
    arr: list = requestGPT(sentence, 1)
    print(arr)
    
    client = texttospeech.TextToSpeechClient()
    voice = texttospeech.VoiceSelectionParams(
    language_code=legend[lang.capitalize()], 
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3)

    os.makedirs("syllables", exist_ok=True)

    i = 0  # Initialize word counter
    for word in arr:  # Removed i from enumerate
        j = 0  # Initialize syllable counter for each word
        word_has_valid_syllable = False  # Keep track if word has at least one valid syllable
        for syllable in word:  # Removed j from enumerate
            syllable = syllable.strip()  # Remove leading and trailing whitespace
            # Skip if syllable is empty, whitespace or punctuation
            if not syllable or syllable in {',', '[', ']', ' '}:
                continue
            # Synthesize the speech
            response = client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=syllable),
                voice=voice,
                audio_config=audio_config)

            # Write the response to an MP3 file
            filename = f"syllables/word{i}_syllable{j}.mp3"
            with open(filename, "wb") as out:
                out.write(response.audio_content)

            j += 1  # Increment syllable counter only after a valid syllable is processed
            word_has_valid_syllable = True  # Set flag to True because a valid syllable was found

        if word_has_valid_syllable:  # Only increment word counter if word had at least one valid syllable
            i += 1

    # Initialize pygame
    pygame.mixer.init()

    # Get the list of all files in the directory
    files = os.listdir("syllables")

    # Play each file one by one
    for file in sorted(files):
        filename = f"syllables/{file}"
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue  
    
    # End, remove all syllables
    for file in files:
        os.remove(f"syllables/{file}")

if __name__ == '__main__':
    speak_syllable_by_syllable("Korean", "안녕하세요")
  #  app.run(port=5000, debug=True)