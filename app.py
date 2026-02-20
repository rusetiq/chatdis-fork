import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Ollama Cloud setup
API_KEY = os.getenv("OLLAMA_API_KEY")  # Set in .env
OLLAMA_API_URL = "https://ollama.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Load knowledge base as fallback
KB_PATH = "knowledge_base.md"
try:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = f.read()
except Exception:
    KNOWLEDGE_BASE = "Dunes International School info: Timings 7:30 AM - 2:50 PM."

# --- Web scraping function ---
def get_live_school_info():
    url = "https://www.dubaischoolwebsite.com"  # Replace with actual DIS site URL
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Example: extract timings, contact info, announcements, etc.
        timings_tag = soup.find("p", id="timings")
        timings = timings_tag.text.strip() if timings_tag else None

        contact_tag = soup.find("p", id="contact")
        contact = contact_tag.text.strip() if contact_tag else None

        announcements_tag = soup.find("div", class_="announcements")
        announcements = announcements_tag.text.strip() if announcements_tag else None

        # Combine whatever was found
        context_parts = []
        if timings:
            context_parts.append(f"**School Timings:** {timings}")
        if contact:
            context_parts.append(f"**Contact Info:** {contact}")
        if announcements:
            context_parts.append(f"**Announcements:** {announcements}")

        if context_parts:
            return "\n".join(context_parts)
        else:
            # If scraping succeeded but found nothing, fall back
            return KNOWLEDGE_BASE

    except Exception as e:
        # On failure, return fallback KB
        print(f"Web scraping failed: {str(e)}")
        return KNOWLEDGE_BASE

# --- AI Answer Generation ---
def ai_generate_answer(question, context):
    if not API_KEY:
        return "System Error: Ollama API Key is missing."

    system_instruction = f"""
You are ChatDIS, the official and friendly AI assistant for Dunes International School (DIS), Abu Dhabi.

GUIDELINES:
1. Use the PROVIDED CONTEXT below to answer the user's question accurately.
2. If the answer is in the context, be specific (mention timings, dates, and contact info).
3. If the answer is NOT in the context, politely state that you don't have that specific information and suggest contacting the school office at +971 2 552 7527.
4. Keep the tone professional, welcoming, and helpful.
5. Use bullet points for lists and bold text for important details.

SCHOOL CONTEXT:
{context}
"""

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

        # Ollama Cloud returns choices -> message -> content
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0].get("message", {}).get("content", "No content returned")

        return f"Unexpected API response: {result}"

    except Exception as e:
        return f"Connection Error: {str(e)}"

# --- Flask Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "").strip()
    # Get live website info first
    context = get_live_school_info()
    answer = ai_generate_answer(user_question, context)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)

























"""
import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Ollama Cloud setup
API_KEY = os.getenv("OLLAMA_API_KEY")  # Set in .env
OLLAMA_API_URL = "https://ollama.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Load knowledge base
KB_PATH = "knowledge_base.md"
try:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE_BASE = f.read()
except Exception:
    KNOWLEDGE_BASE = "Dunes International School info: Timings 7:30 AM - 2:50 PM."

def ai_generate_answer(question, context):
    if not API_KEY:
        return "System Error: Ollama API Key is missing."

    system_instruction = f""
You are ChatDIS, the official and friendly AI assistant for Dunes International School (DIS), Abu Dhabi.

GUIDELINES:
1. Use the PROVIDED CONTEXT below to answer the user's question accurately.
2. If the answer is in the context, be specific (mention timings, dates, and contact info).
3. If the answer is NOT in the context, politely state that you don't have that specific information and suggest contacting the school office at +971 2 552 7527.
4. Keep the tone professional, welcoming, and helpful.
5. Use bullet points for lists and bold text for important details.

SCHOOL CONTEXT:
{context}
""

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

        # Ollama Cloud returns choices -> message -> content
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0].get("message", {}).get("content", "No content returned")

        return f"Unexpected API response: {result}"

    except Exception as e:
        return f"Connection Error: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "").strip()
    answer = ai_generate_answer(user_question, KNOWLEDGE_BASE)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
"""


