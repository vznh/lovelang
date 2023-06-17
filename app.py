# note: coded in Python 3.10.5 x64
from flask import Flask, render_template, request, jsonify, session
from flask_pymongo import PyMongo
import os
import openai
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()

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

def generate_text():
    """Generates text from the completion endpoint. Retains message history."""
    # Initialize the conversation history if it doesn't exist
    if 'history' not in session:
        session['history'] = ''

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

def setup_curriculum( language: str, curriculum: dict ) -> list:
    """Sets up the curriculum for the given language.

    Args:
        language (str): language of curriculum
        curriculum (dict): list of words

    Returns:
        list of words that will be depicted in the lesson
    """
    from random import choice



if __name__ == '__main__':
    app.run(port=5000, debug=True)