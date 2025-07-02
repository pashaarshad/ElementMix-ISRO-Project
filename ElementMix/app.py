import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

WOLFRAM_URL = None  # Wolfram Alpha removed
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def load_local_reactions():
    try:
        with open('reactions.json') as f:
            return json.load(f)
    except Exception:
        return {"reactions": []}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_reaction', methods=['POST'])
def get_reaction():
    data = request.json
    reactants = data.get("reactants", "").replace(' ', '')
    local_data = load_local_reactions()
    reactant_list = reactants.split("+")

    # Check local reactions
    for reaction in local_data["reactions"]:
        if set(reactant_list) == set(reaction["reactants"]):
            return jsonify({
                "source": "local",
                "product": reaction["product"],
                "equation": reaction["equation"],
                "explanation": reaction["explanation"]
            })

    # If not found locally, use OpenRouter AI for explanation
    try:
        prompt = f"Explain the chemical reaction when {reactants.replace('+', ' and ')} react."
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://elementmix.onrender.com",  # Optional
                "X-Title": "ElementMix"
            },
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        explanation = completion.choices[0].message.content
        return jsonify({
            "source": "ai",
            "explanation": explanation
        })
    except Exception as e:
        return jsonify({"error": "Reaction not found and AI explanation failed."}), 404
        # Use OpenRouter AI for explanation
        try:
            prompt = f"Explain the chemical reaction when {reactants.replace('+', ' and ')} react."
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://elementmix.onrender.com",  # Optional
                    "X-Title": "ElementMix"
                },
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            explanation = completion.choices[0].message.content
            return jsonify({
                "source": "ai",
                "explanation": explanation
            })
        except Exception as e:
            return jsonify({"error": "Reaction not found and AI explanation failed."}), 404

if __name__ == '__main__':
    app.run(debug=True)
