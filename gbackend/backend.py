from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import re

# === CONFIG ===
API_KEY = "AIzaSyDgQfWY2Q9av-fMoeg1UeKgpnqNgNZzDo4"  # your Gemini API key
MODEL = "gemini-2.5-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}"

# === FLASK SETUP ===
app = Flask(__name__)
CORS(app)  # allow Wix/Netlify to call this API

# === SYSTEM INSTRUCTION ===
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
- If the question is non-academic, still answer politely and clearly.
"""

# === GEMINI FUNCTION ===
def ask_gemini(prompt):
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{SYSTEM_INSTRUCTION}\n\nStudent: {prompt}"}
                ],
            }
        ],
        "generationConfig": {"maxOutputTokens": 700, "temperature": 0.8},
    }

    response = requests.post(
        ENDPOINT,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
    )

    if response.status_code == 200:
        data = response.json()
        try:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            reply = re.sub(r"\*\*(.*?)\*\*", r"\1", reply)  # remove bold markdown
            return reply
        except (KeyError, IndexError):
            return "⚠️ Error: Could not parse Gemini response properly."
    else:
        return f"❌ API Error {response.status_code}: {response.text}"

# === API ROUTE ===
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        if not message:
            return jsonify({"reply": "⚠️ No message provided."})

        reply = ask_gemini(message)
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Internal server error: {str(e)}"})

# === RUN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
