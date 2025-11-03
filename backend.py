from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# === CONFIG ===
API_KEY = "AIzaSyDgQfWY2Q9av-fMoeg1UeKgpnqNgNZzDo4"
MODEL = "gemini-2.5-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}"

SYSTEM_INSTRUCTION = """
You are QUOKKA — a professional yet friendly AI tutor built by the team Señor Frogs.
You help students learn by explaining topics clearly, but you adapt your detail level based on the question type.

Behavior rules:
- If the student asks a **casual or factual question** (e.g., “What’s your name?”, “Who made you?”, “Tell me a joke”), reply **naturally and concisely (under 3 sentences)**.
- If the student asks an **academic or learning question**, use this structure:
  1️⃣ **Brief Introduction** – 1–2 lines introducing the topic.
  2️⃣ **Detailed Explanation** – A clear, step-by-step breakdown (with short bullet points if needed).
  3️⃣ **Example or Analogy** – One example to reinforce understanding.
  4️⃣ **Summary** – A short recap.
- Keep academic responses around 150–250 words, unless the question explicitly asks for more depth.
- Use Markdown formatting (**bold**, lists, breaks).
- Avoid unnecessary self-descriptions unless the user explicitly asks.
- If a question is inappropriate or vulgar, always respond with: “Quit that kid.”
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
        "generationConfig": {
            "maxOutputTokens": 1200,
            "temperature": 0.7,
            "topP": 0.9,
        },
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
