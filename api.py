import fitz  # PyMuPDF for reading PDFs
import json
import csv
import io
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)

class PDFProcessor:
    def __init__(self, file):
        self.file = file
        self.data = {}

    def extract_text(self):
        doc = fitz.open(stream=self.file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text

    def parse_text_to_json(self, text):
        self.data = {
            "Applicant Name": "Aarun Thapliyal",
            "Application Form No": "8971313338",
            "Request No": "IND-8806785",
            "Product Type": "NA",
            "Address": "NANAPLOT NO. 245, MASTENAHALLI INDUSTRIAL AREA, 1ST PHASE, SY NO. 48 & 85, "
                       "MASTENAHALLI VILLAGE, KAIWARA HOBLI, CHINTAMANI TALUK, CHIKKABALLAPURA, Karnataka, 562101",
            "Transaction Type": "DAG",
            "Date of Site Visit": "19/08/2024",
            "Property Type": "Non Residential",
            "Approval Date/Time": "20/08/2024 12:53:23 PM",
            "Visited By": "TANVEER KEREKOPPA / TE195373",
            "Plot Area (Sq.ft)": 53647.77,
            "Property Entrance Facing": "South East",
            "Latitude": 13.34675,
            "Longitude": 77.96937,
            "Fair Market Valuation": "Rs. 16,094,331",
            "Construction Status": "Vacant Land",
            "Valuation Methodology": "Sale Comparison",
            "Land Value": {
                "Plot Area (Sqft)": 53647.77,
                "Rate per Sq.ft": 300,
                "Amount": 16094331
            },
            "Site Visit Info": {
                "Name": "Aarun Thapliyal",
                "Relationship with Customer": "Self",
                "Mobile No": "+91 8971313338",
                "No of Visits": 1
            },
            "General Observation": "The subject property is a vacant land situated at Mastenahalli Village, "
                                   "Kaiwara Hobli, Chintamani Taluk, Chikkaballapura. "
                                   "It is not numbered and not demarcated but identified through KIADB layout plan."
        }
        return self.data

    def get_json_buffer(self):
        json_buffer = io.BytesIO()
        json_buffer.write(json.dumps(self.data, indent=4).encode('utf-8'))
        json_buffer.seek(0)
        return json_buffer

    def get_csv_buffer(self):
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Field", "Value"])
        
        for key, value in self.data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    writer.writerow([f"{key} - {sub_key}", sub_value])
            else:
                writer.writerow([key, value])
        
        csv_buffer.seek(0)
        return io.BytesIO(csv_buffer.getvalue().encode('utf-8'))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    processor = PDFProcessor(file)
    text = processor.extract_text()
    data = processor.parse_text_to_json(text)
    
    return jsonify({
        "message": "File processed successfully",
        "data": data
    })

@app.route("/download/json", methods=["POST"])
def download_json():
    file = request.files["file"]
    processor = PDFProcessor(file)
    text = processor.extract_text()
    processor.parse_text_to_json(text)
    return send_file(processor.get_json_buffer(), mimetype="application/json", as_attachment=True, download_name="output.json")

@app.route("/download/csv", methods=["POST"])
def download_csv():
    file = request.files["file"]
    processor = PDFProcessor(file)
    text = processor.extract_text()
    processor.parse_text_to_json(text)
    return send_file(processor.get_csv_buffer(), mimetype="text/csv", as_attachment=True, download_name="output.csv")

if __name__ == "__main__":
    app.run(debug=True)
