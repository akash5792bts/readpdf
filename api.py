import fitz  # PyMuPDF for reading PDFs
import json
import csv
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}

    def extract_text(self):
        doc = fitz.open(self.file_path)
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

    def save_json(self, json_path):
        with open(json_path, "w") as json_file:
            json.dump(self.data, json_file, indent=4)

    def save_csv(self, csv_path):
        with open(csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Field", "Value"])
            
            for key, value in self.data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f"{key} - {sub_key}", sub_value])
                else:
                    writer.writerow([key, value])

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
    
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    
    processor = PDFProcessor(file_path)
    text = processor.extract_text()
    data = processor.parse_text_to_json(text)
    
    json_path = file_path.replace(".pdf", ".json")
    csv_path = file_path.replace(".pdf", ".csv")
    
    processor.save_json(json_path)
    processor.save_csv(csv_path)
    
    return jsonify({
        "message": "File processed successfully",
        "json_file": json_path,
        "csv_file": csv_path,
        "data": data
    })

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
