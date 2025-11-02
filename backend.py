from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# === CONFIG ===
API_KEY = "AIzaSyDgQfWY2Q9av-fMoeg1UeKgpnqNgNZzDo4"  # Your Gemini API key
MODEL = "gemini-2.5-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}"

SYSTEM_INSTRUCTION = """
You are a professional AI tutor and teaching assistant.
When students ask a question, respond in clear, well-structured paragraphs.
Follow this format strictly:

1️⃣ **Brief Introduction** – One or two sentences introducing the concept.
2️⃣ **Detailed Explanation** – Step-by-step explanation, using bullet points if helpful.
3️⃣ **Example or Analogy** – Provide at least one simple example.
4️⃣ **Summary** – End with a short recap or key takeaway.

Rules:
- Use Markdown-style formatting (**bold**, lists, and line breaks).
- Keep explanations between 150–300 words.
- Avoid jargon unless the student asks for it.
"""

@app.route("/", methods=["GET"])
def home():
    return "<h2>✅ Gemini AI Backend is Running</h2><p>Use POST /chat to send questions.</p>"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data["message"]

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{SYSTEM_INSTRUCTION}\n\nStudent: {message}"}],
            }
        ],
        ""generationConfig": {
    "maxOutputTokens": 1500,   # increased from 700
    "temperature": 0.8,
    "topP": 0.95,
    "topK": 64
}

    }

    try:
        res = requests.post(
            ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )

        if res.status_code == 200:
            gemini_data = res.json()
            try:
                reply = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"reply": reply})
            except (KeyError, IndexError):
                return jsonify({"error": "⚠️ Could not parse Gemini response."}), 500
        else:
            return jsonify({"error": f"Gemini API error {res.status_code}: {res.text}"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

