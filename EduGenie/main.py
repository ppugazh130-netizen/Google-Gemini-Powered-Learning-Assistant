import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from services.gemini_service import GeminiService, GeminiServiceError

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app)

try:
    gemini_service = GeminiService()
except GeminiServiceError as error:
    print(f"WARNING: {error}")
    gemini_service = None

@app.route("/")
def home():
    return send_from_directory(TEMPLATES_DIR, "index.html")

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "EduGenie",
        "gemini_configured": gemini_service is not None and gemini_service.is_configured(),
        "model": gemini_service.model_name if gemini_service else None
    })

@app.route("/api/ask", methods=["POST"])
def ask():
    try:
        if gemini_service is None:
            return jsonify({"success": False, "error": "Gemini service is not configured. Check GEMINI_API_KEY in .env."}), 503

        data = request.get_json(silent=True) or {}
        question = str(data.get("question", "")).strip()
        history = data.get("history", [])

        if not question:
            return jsonify({"success": False, "error": "Please enter a question."}), 400

        if not isinstance(history, list):
            history = []

        answer = gemini_service.ask(question, history[-10:])
        return jsonify({"success": True, "answer": answer})

    except GeminiServiceError as error:
        return jsonify({"success": False, "error": str(error)}), 503
    except Exception as error:
        app.logger.exception(error)
        return jsonify({"success": False, "error": "Unexpected server error."}), 500

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    print("=" * 60)
    print("EDUGENIE - AI LEARNING ASSISTANT")
    print("=" * 60)
    print(f"Open: http://{host}:{port}")
    print("Press CTRL+C to stop.")
    app.run(host=host, port=port, debug=True)
