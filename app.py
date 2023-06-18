from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()

# Initializing api keys
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'cred.json'

# Initializing app
app = Flask(__name__)

past_msgs = []

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route( '/welcome/<name>' )
def welcome(name):
    return render_template('index.html',name=name)

@app.route('/init')
def initialization():
    return render_template('init.html')

@app.route('/picksubject/<lang>')
def picksubject_render(lang):
    return render_template('picksubject.html', lang=lang)

'''
Low priority
'''
@app.route('/picksubject/<lang>/modules')
def modules_render(lang):
    return render_template('modules.html', lang=lang)

'''
Converse Area
'''
@app.route('/picksubject/<lang>/converse', methods=['GET', 'POST'])
def converse(lang):
    print(lang)
    global past_msgs
     # Create an empty list for past_msgs in the session
    if request.method == 'POST':
        audio_data = request.files.get('audio')
        audio_data.save("voice/currInput.wav")
        text = listen_for_audio(lang, "voice/currInput.wav")
        response, messages = conversateGPT(lang, text)
        past_msgs.append(messages)
        print(past_msgs)
        save_entire_sentence(lang, response)
        return jsonify({'response': response, 'audio_url': "/get_audio/sentence.wav"})
    else:
        # Render the page on a GET request.
        return render_template('converse.html')


@app.route('/get_audio/<path:filename>', methods=['GET'])
def get_audio(filename):
    return send_from_directory('voice', filename)

'''
Practice Area
'''
@app.route( '/picksubject/<lang>/practice' )
def practice_page_render(lang):
    return render_template('practice.html', syllables_dict=(requestGPT(lang,3)))

# Finished
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
        case 2:
            messages = [{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": """Please return a translation to English of what I say, and nothing else.:
            """},
            {"role": "user", "content": sentence}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=250,
            )
            res = response['choices'][0]['message']['content']
            return res
        case 3:
            messages = [{"role": "system", "content": "Please create curriculum of 10 vocabulary words along with helpful tips of pronunciation as their values for the language that I specify that is easy-intermediate. Do not say anything else except for the dict. Please format in a Python dictinary format. This is made for those who just want to learn words. Should be in format {'word': 'helpful tip on how to pronounce'}"},
            {"role": "user", "content": sentence}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=250,
            )

            res=str(response["choices"][0]["message"])
            final = json.loads(res)
            return final
        
    return "GPT is not accessible at this time."

'''
TODO: Need to retain past messages
'''
def conversateGPT(lang: str, sentence: str, past_msgs=[]) -> str:
    stop_sentences: dict = {
        "korean": ["초기화", "하지마"],
        "english": "Reset",
        "japanese": "リセット",
        "mandarin": "重置",
        "spanish": "Reiniciar"
    }
    # Define the system message and initial user message
    system_message = {"role": "system", "content": "You are a helpful assistant."}
    user_message_init = {
        "role": "user",
        "content": f"""
        You are an avid individual who loves learning languages -- you have knowledge about every language in existence, except for the extinct ones of course. If I do not respond in a correct language, or if you just don't understand my response because it's too vague, respond with 'What did you say?' in the respective language. Your job is to practice with me to speak. Do not start until I say 'Hello' to you -- when I say hello, begin a beginner-level conversation from easy terms in a language that I prefer, then gradually (very slowly) increase in difficulty. You'll return only the sentence without translation and nothing else. Please act naturally, as if you're a friend. For this conversation, let's start with {lang}"""
    }
    user_message = {"role": "user", "content": sentence}

    # Edge case
    if sentence.lower() in stop_sentences.get(lang, []):
        if past_msgs is not None:
            past_msgs.clear()
        return "Conversation reset."
    
    # Prepare the messages
    if len(past_msgs) > 0:
        messages = [system_message, user_message_init, user_message] + past_msgs
    else:
        messages = [system_message, user_message_init, user_message]

    # Call the API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=250,
    )

    # Get the response
    res = response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": res})

    past_msgs.append(({"role": "assistant", "content": res}))
    # Update the messages in the database
    return res, past_msgs

# Finished
def listen_for_audio(lang: str, audio_file_path: str) -> str:
    '''
    Args:
        lang: language to listen for
        audio_file_path: path to the audio file to be processed
    Returns:
        recognized text from the audio file
    '''
    import speech_recognition as sr
    legend = {
        "english": "en-GB",
        "korean": "ko-KR", 
        "japanese": "ja-JP",
        "mandarin": "zh-CN",
        "spanish": "es-ES"
    }
    # Ensure that the provided language is supported, if not default to English
    if lang not in legend:
        print(f'Unsupported language "{lang}". Defaulting to English.')
        lang = "english"

    r = sr.Recognizer()

    with sr.AudioFile(audio_file_path) as source:
        print("Processing audio file...")
        audio = r.record(source)  # Read the entire audio file
        print("Finished processing.")

    try:
        text = r.recognize_google(audio, language=legend[lang])
        print(f"Transcribed Text: {text}")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        text = None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        text = None

    return text

# Finished
from google.cloud import texttospeech
def save_entire_sentence(lang: str, sentence: str) -> None:
    lang=lang.lower()
    legend= {
    "english": "en-GB",
    "korean": "ko-KR",
    "japanese": "ja-JP",
    "mandarin": "zh-CN",
    "spanish": "es-ES"
    }
    client = texttospeech.TextToSpeechClient()
    voice = texttospeech.VoiceSelectionParams(
    language_code=legend[lang], 
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16) 
    os.makedirs("voice", exist_ok=True)
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=sentence),
        voice=voice,
        audio_config=audio_config)
    
    filename = f"voice/sentence.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    
    # Translating to English
    sentence = requestGPT(sentence, 2)
    voice = texttospeech.VoiceSelectionParams(
    language_code=legend["english"], 
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=sentence),
        voice=voice,
        audio_config=audio_config)
    filename = f"voice/sentenceTranslation.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    
'''
Syllables
'''
def get_syllables(lang: str, sentence: str) -> list:
    requestGPT(sentence,0)

if __name__ == "__main__":
    app.run(debug=True)