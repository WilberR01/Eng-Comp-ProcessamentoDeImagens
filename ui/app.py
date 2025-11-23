from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from services.runner import run_analysis
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__, template_folder="templates", static_folder="static")

# Upload configuration
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff", "gif"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", result=None)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename: str):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/analyze", methods=["POST"])
def analyze():
    # Expect a file upload named 'file'
    uploaded = request.files.get("file")
    if not uploaded or uploaded.filename == "":
        return render_template("index.html", result={
            "success": False,
            "error": {"message": "Nenhum arquivo enviado.", "suggestion": "Selecione um arquivo de imagem para enviar.", "can_retry": "yes"}
        })

    if not allowed_file(uploaded.filename):
        return render_template("index.html", result={
            "success": False,
            "error": {"message": "Tipo de arquivo não suportado.", "suggestion": "Envie um arquivo de imagem (png, jpg, jpeg, bmp, tif, tiff, gif).", "can_retry": "yes"}
        })

    filename = secure_filename(uploaded.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    saved_path = os.path.join(UPLOAD_FOLDER, unique_name)
    uploaded.save(saved_path)

    try:
        result = run_analysis(saved_path)
        # Attach uploaded filename to result for UI
        if isinstance(result, dict):
            result["_uploaded_filename"] = unique_name
        return render_template("index.html", result=result)
    finally:
        # Remove uploaded file to avoid accumulation
        try:
            if os.path.exists(saved_path):
                os.remove(saved_path)
        except Exception:
            # Non-fatal; just continue
            pass


def run(port: int = 5000):
    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    run()
