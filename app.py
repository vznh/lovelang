# note: coded in Python 3.10.5 x64
from flask import Flask, render_template, request, jsonify, session
from flask_pymongo import PyMongo
import os
import openai
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route( '/welcome/<name>' )
def welcome(name):
    return render_template('index.html',name=name)

@app.route( '/practice/<name>/<language>' )
def practice_page_render(name, language):
    return render_template('practice.html', name=name, language=language)

'''
TODO: high priority, base function for generating text using GPT-4 + GPT-3 API'''
def generate_text( prompt: str, option: int, language: str ) -> str:
    """Generates text from the completion endpoint. Retains message history."""
    # Initialize the conversation history if it doesn't exist
    if 'history' not in session:
        session['history'] = ''

    # Initializing whichever bot
    match option:
        case 0: # gaining syllables data
            session['history'] = ''
            session['history'].append("""
From now on, when I ask for a word in any language, return its syllables to help an English speaker understand the language better. Present it in such:
an array supporting Python that has the syllables such as:
bibimbap (비빔밥) be-bim-bap
-> { "be": "Pronounced such as the sentence 'to be'", "bim": "rhyme of dim", "bap": "bab"}
When returning a value, could you also give helpful guides on how to say the syllable in the value portion of the dict? 

I will request data like:
language word

So an example call  to you would be:
Korean 안녕

The ideal response is just a dictionary in this format. Don't say anything else.

{syllable: helpful tips to pronounce the word}
""")
        case 1: # conversational bot
            session['history'].append("""You are an avid individual who loves learning languages -- you have knowledge about every language in existence, except for the extinct ones of course. If I do not respond in a correct language, or if you just don't understand my response because it's too vague, respond with 'What did you say?' in the respective language. Your job is to practice with me to speak. Do not start until I say 'Hello' to you -- when I say hello, begin a beginner-level conversation from easy terms in a language that I prefer, then gradually (very slowly) increase in difficulty. For this conversation, let's start with {}.""").format(language)
            user_input = 
    # Append the user's input to the conversation history
    user_input = request.json['prompt']
    session['history'] += f"\nUser: {user_input}\n"

    functions = [
        {
            "name", ""
        }
    ]
    # Get a response from the API
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=session['history'],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Extract the generated text and add it to the conversation history
    generated_text = response.choices[0].text.strip()
    session['history'] += f"AI: {generated_text}"

    return jsonify({'text': generated_text})


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
    

if __name__ == '__main__':
    app.run(port=5000, debug=True)