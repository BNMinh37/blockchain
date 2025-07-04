from flask import Flask, request, render_template
import cv2
from pyzbar.pyzbar import decode
import json
import os
import io
import pandas as pd
from flask import send_file

app = Flask(__name__)

def read_qr_code(file_path):
    img = cv2.imread(file_path)
    decoded = decode(img)
    if decoded:
        return decoded[0].data.decode('utf-8')
    return None

def verify_certificate_from_hash(hash_text, blockchain_file="blockchain_data.json"):
    try:
        with open(blockchain_file, "r") as f:
            chain = json.load(f)
            for block in chain:
                if hash_text.strip().endswith(block['hash']):
                    return {
                        "valid": True,
                        "student": block['data']['student'],
                        "course": block['data']['course'],
                        "institution": block['data']['institution'],
                        "issue_date": block['data']['issue_date']
                    }
        return {"valid": False}
    except:
        return {"valid": False}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        file = request.files.get("qr_image")
        if file:
            path = os.path.join("static", file.filename)
            file.save(path)
            qr_text = read_qr_code(path)
            if qr_text:
                result = verify_certificate_from_hash(qr_text)
                result["hash"] = qr_text.strip().split()[-1]
            else:
                result = {"valid": False, "error": "Không đọc được mã QR!"}
    return render_template("index.html", result=result)

@app.route("/all")
def view_all_certificates():
    try:
        with open("blockchain_data.json", "r") as f:
            chain = json.load(f)
            # Bỏ Genesis Block nếu cần
            certs = [block for block in chain if block['index'] != 0]
        return render_template("all.html", certificates=certs)
    except:
        return "Không thể đọc file blockchain_data.json"

@app.route("/search", methods=["GET", "POST"])
def search_certificates():
    result = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("student_name", "").strip().lower()
        with open("blockchain_data.json", "r") as f:
            chain = json.load(f)
            result = [
                block for block in chain
                if block["index"] != 0 and keyword in block["data"]["student"].lower()
            ]
    return render_template("search.html", results=result, keyword=keyword)


@app.route("/download")
def download_excel():
    try:
        with open("blockchain_data.json", "r") as f:
            chain = json.load(f)
            certs = [block for block in chain if block["index"] != 0]

        df = pd.DataFrame([{
            "Họ tên": b["data"]["student"],
            "Khóa học": b["data"]["course"],
            "Tổ chức": b["data"]["institution"],
            "Ngày cấp": b["data"]["issue_date"],
            "Hash": b["hash"]
        } for b in certs])

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="ChungChi")
        output.seek(0)
        return send_file(output, as_attachment=True, download_name="chungchi.xlsx")
    except Exception as e:
        return str(e)




if __name__ == "__main__":
    app.run(debug=True)
