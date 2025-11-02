from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "<h2>✅ Flask is working correctly on Render!</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
