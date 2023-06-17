from flask import Flask, render_template
import os
import openai


openai.organization = "berkeley-hackathon Team 79"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)