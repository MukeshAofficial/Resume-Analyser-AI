from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename
import PyPDF2
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure Gemini AI
genai.configure(api_key="AIzaSyBJQL2jiLkEz8CCbPpOtps6KhPz9ivt4-U")
model = genai.GenerativeModel("gemini-1.5-pro")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(resume_text):
    prompt = f"""
    Analyze the following resume and provide:
    1. An overall score out of 100
    2. Detailed feedback on strengths
    3. Areas for improvement
    4. Formatting and structure review
    5. Keywords and skills analysis
    
    Resume:
    {resume_text}
    """
    
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['GET'])
def analyze_page():
    return render_template('analyze.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    try:
        # Read PDF content
        resume_text = extract_text_from_pdf(file)
        
        # Analyze resume using Gemini
        analysis = analyze_resume(resume_text)
        
        return jsonify({'analysis': analysis})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
