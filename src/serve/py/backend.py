from flask import Flask, request, jsonify,make_response,send_file,Response
from flask_cors import CORS
import os
import io
import fitz  # PyMuPDF
app = Flask(__name__)
CORS(app)

# 确保上传目录存在
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = request.form.get('file_path')
    ensure_directory_exists(os.path.dirname(file_path))
   
    return jsonify({"message": f"{file.filename} file in {file_path}"}), 200


@app.route('/get-file-path', methods=['GET'])
def get_file_path():
    file_path = request.args.get('file_path')
    if not file_path:
        return jsonify({"error": "No file path provided"}), 400

    if os.path.exists(file_path):
        return jsonify({"message": f"File exists at {file_path}"}), 200
    else:
        return jsonify({"error": "File does not exist"}), 404

def read_pdf_as_blob(file_path):
    with open(file_path, "rb") as file:
        pdf_blob = file.read()
    return pdf_blob


@app.route('/showpdf', methods=['GET'])
def get_pdf():
    pdf_blob = read_pdf_as_blob("C:\\Users\\zy\\Desktop\\vi\\GRL_short.pdf")
    response = Response(io.BytesIO(pdf_blob), mimetype='application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename='sample.pdf')
    return response

if __name__ == "__main__":
    app.run(debug=True,port=5000)

