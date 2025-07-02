from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

# Load API keys from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# WOLFRAM_APPID = os.getenv("WOLFRAM_APPID")

# Set up OpenAI/OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.base_url = "https://openrouter.ai/api/v1"


def load_local_reactions():
    # Use absolute path for reactions.json
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "reactions.json")) as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_reaction', methods=['POST'])
def get_reaction():
    data = request.json
    reactants = data.get("reactants", "")
    local_data = load_local_reactions()

    # Check local reactions
    for reaction in local_data["reactions"]:
        if set(reactants.replace(' ', '').split("+")) == set(reaction["reactants"]):
            return jsonify({
                "source": "local",
                "product": reaction["product"],
                "equation": reaction["equation"],
                "explanation": reaction["explanation"]
            })


    # If not found locally, use OpenRouter (GPT-4o)
    prompt = (
        f"If I mix {reactants.replace('+', ' and ')}, what is the result? "
        "Give the chemical equation, the product, and a short explanation (3-4 lines) about why it happens and its use. "
        "If there is no reaction, say 'No significant reaction.'"
    )

    try:
        completion = openai.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # Fix: handle string or object response
        if hasattr(completion, 'choices'):
            text = completion.choices[0].message.content
        else:
            text = str(completion)
        return jsonify({
            "source": "openrouter-gpt-4o",
            "explanation": text
        })
    except Exception as e:
        return jsonify({"error": f"OpenRouter API error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
