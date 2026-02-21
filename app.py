import os
import requests
from flask import Flask, request, jsonify, render_template, abort, send_from_directory
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from datetime import datetime
from functools import wraps

load_dotenv()

app = Flask(__name__)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins = [o.strip() for o in allowed_origins if o.strip()]
CORS(app, origins=allowed_origins if allowed_origins else ["*"])

limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
CHATDIS_SECRET_KEY = os.getenv("CHATDIS_SECRET_KEY")

OLLAMA_API_URL = "https://ollama.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OLLAMA_API_KEY}",
    "Content-Type": "application/json"
}

KB_PATH = "knowledge_base.md"
try:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = f.read()
except Exception:
    KNOWLEDGE_BASE = "Dunes International School info: Timings 7:30 AM - 2:50 PM."


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client_key = request.headers.get("x-api-key")
        if not CHATDIS_SECRET_KEY or client_key != CHATDIS_SECRET_KEY:
            abort(401)
        return f(*args, **kwargs)
    return decorated


def ai_generate_answer(question, context):
    if not OLLAMA_API_KEY:
        return "System Error: Ollama API Key is missing."

    system_instruction = f"""You are ChatDIS, the official and friendly AI assistant for Dunes International School (DIS), Abu Dhabi.

GUIDELINES:
1. Use the PROVIDED CONTEXT below to answer the user's question accurately.
2. If the answer is in the context, be specific (mention timings, dates, and contact info).
3. If the answer is NOT in the context, politely state that you don't have that specific information and suggest contacting the school office at +971 2 552 7527.
4. Keep the tone professional, welcoming, and helpful.
5. Use bullet points for lists and bold text for important details.

SCHOOL CONTEXT:
{context}"""

    payload = {
        "model": "gemini-3-flash-preview",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": question}
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            return f"API Error {response.status_code}: {response.text}"

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]

        return "Unexpected API response."

    except Exception as e:
        return f"Connection Error: {str(e)}"


def log_prompt(user_question, client_ip):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {client_ip} | {user_question}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/widget")
def widget():
    return send_from_directory("static", "widget.html")


@app.route("/ask", methods=["POST"])
@limiter.limit("5 per minute")
@require_api_key
def ask():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    user_question = data.get("question", "").strip()
    client_ip = request.remote_addr

    if not user_question or len(user_question) > 1000:
        return jsonify({"error": "Invalid question"}), 400

    log_prompt(user_question, client_ip)

    answer = ai_generate_answer(user_question, KNOWLEDGE_BASE)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=False)
