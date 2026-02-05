import os
import requests
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenRouter Setup
# Make sure to rename your variable in Vercel to OPENROUTER_API_KEY
api_key = os.getenv("OPENROUTER_API_KEY")

# Load Knowledge Base
kb_path = "knowledge_base.md"
try:
    with open(kb_path, "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = f.read()
except Exception as e:
    KNOWLEDGE_BASE = "Dunes International School information: Timings 7:30 AM - 2:50 PM."

def ai_generate_answer(question, context):
    if not api_key:
        return "System Error: OpenRouter API Key missing."

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:5000", # Can be your site URL
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemini-2.0-flash-001", # High limit, very fast
                "messages": [
                    {
                        "role": "system", 
                        "content": f"You are ChatDIS, the assistant for Dunes International School. Use this info: {context}. Be professional and polite."
                    },
                    {
                        "role": "user", 
                        "content": question
                    }
                ]
            })
        )
        
        result = response.json()
        
        # OpenRouter returns a specific JSON structure
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return f"API Error: {result.get('error', {}).get('message', 'Unknown Error')}"

    except Exception as e:
        return f"Connection Error: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "").strip()
    # We pass the full KNOWLEDGE_BASE as context
    answer = ai_generate_answer(user_question, KNOWLEDGE_BASE)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run()
