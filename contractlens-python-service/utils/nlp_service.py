import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from utils.extractor import extract_text_from_file, extract_clauses
from utils.summarizer import summarize_text, simplify_text

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

session_store = {
    "raw_text": "",
    "summary": "",
    "clauses": [],
    "filename": "",
}

def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "ContractLens Python NLP Service is running ✅",
        "port": 8000
    })

@app.route("/process", methods=["POST"])
def process_file():
    """
    Receives file from Node.js backend.
    Extracts text, generates summary, extracts clauses.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file received."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file type. Use PDF, DOCX, or TXT."
        }), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:

        raw_text = extract_text_from_file(filepath)

        if not raw_text or len(raw_text.strip()) < 50:
            return jsonify({
                "error": "Not enough text extracted. "
                         "File may be empty or image-based."
            }), 422

        summary = summarize_text(raw_text)

        clauses = extract_clauses(raw_text)

        session_store["raw_text"] = raw_text
        session_store["summary"] = summary
        session_store["clauses"] = clauses
        session_store["filename"] = filename

        os.remove(filepath)

        return jsonify({
            "message": "Processing complete.",
            "filename": filename,
            "summary": summary,
            "clauses": clauses,
            "word_count": len(raw_text.split()),
            "clauses_found": len(clauses),
        }), 200

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

@app.route("/summary", methods=["GET"])
def get_summary():
    if not session_store["summary"]:
        return jsonify({
            "error": "No document processed yet."
        }), 404

    return jsonify({
        "filename": session_store["filename"],
        "summary": session_store["summary"],
        "word_count": len(session_store["raw_text"].split()),
    }), 200

@app.route("/clauses", methods=["GET"])
def get_clauses():
    if not session_store["raw_text"]:
        return jsonify({
            "error": "No document processed yet."
        }), 404

    return jsonify({
        "filename": session_store["filename"],
        "clauses": session_store["clauses"],
        "total": len(session_store["clauses"]),
    }), 200

@app.route("/resummarize", methods=["POST"])
def resummarize():
    if not session_store["raw_text"]:
        return jsonify({
            "error": "No document uploaded yet."
        }), 404

    try:
        summary = summarize_text(session_store["raw_text"])
        session_store["summary"] = summary
        return jsonify({
            "message": "Re-summarization complete.",
            "summary": summary,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/simplify", methods=["POST"])
def simplify():
    if not session_store["raw_text"]:
        return jsonify({
            "error": "No document uploaded yet."
        }), 404

    try:
        plain = simplify_text(session_store["raw_text"])
        return jsonify({
            "message": "Plain English version generated.",
            "plain_english": plain,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset():
    session_store["raw_text"] = ""
    session_store["summary"] = ""
    session_store["clauses"] = []
    session_store["filename"] = ""
    return jsonify({
        "message": "Session cleared. Ready for new document."
    }), 200

if __name__ == "__main__":
    print("\n🐍 ContractLens Python NLP Service starting...")
    print("📡 Running at: http://localhost:8000\n")
    app.run(debug=True, host="0.0.0.0", port=8000)