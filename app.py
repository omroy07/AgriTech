from flask import Flask, request, jsonify, send_from_directory
from google import genai
import traceback
import os
import re
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

# Input validation and sanitization functions
def sanitize_input(text):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    # Limit length
    if len(text) > 1000:
        text = text[:1000]
    
    return text.strip()

def validate_input(data):
    """Validate input data structure and content"""
    if not data:
        return False, "No data provided"
    
    # Check for required fields if needed
    # Add specific validation rules here
    
    return True, "Valid input"

# Initialize Gemini API
API_KEY = os.environ.get('GEMINI_API_KEY')
MODEL_ID = 'gemini-2.5-flash'

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

# Configure Gemini Client
client = genai.Client(api_key=API_KEY)


"""Secure endpoint to provide Firebase configuration to client"""
@app.route('/api/firebase-config')
def get_firebase_config():
    try:
        return jsonify({
            'apikey': os.environ['FIREBASE_API_KEY'],
            'authDomain': os.environ('FIREBASE_AUTH_DOMAIN'),
            'projectId': os.environ('FIREBASE_PROJECT_ID'),
            'storageBucket': os.environ('FIREBASE_STORAGE_BUCKET'),
            'messagingSenderId': os.environ('FIREBASE_MESSAGING_SENDER_ID'),
            'appId': os.environ('FIREBASE_APP_ID'),
            'measurementId': os.environ('FIREBASE_MEASUREMENT_ID')

        })
    except KeyError as e:
        return jsonify({
            "status": "error",
            "message":f"Missing environment variable: {str(e)}"
        }),500


@app.route('/process-loan', methods=['POST'])
def process_loan():
    try:
        json_data = request.get_json(force=True)
        
        # Validate and sanitize input
        is_valid, validation_message = validate_input(json_data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "message": validation_message
                }), 400
        
        # Sanitize any text fields in the JSON data
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    json_data[key] = sanitize_input(value)
        
        print(f"Received JSON: {json_data}")

        prompt = f"""
You are a financial loan eligibility advisor specializing in agricultural loans for farmers in India.

You will be given a JSON object that contains information about a farmer's loan application. The fields in this JSON will vary depending on the loan type (e.g., Crop Cultivation, Farm Equipment, Water Resources, Land Purchase).
You will focus only on loan schemes and eligibility criteria followed by:
1. Indian nationalized banks (e.g., SBI, Bank of Baroda)
2. Private sector Indian banks (e.g., ICICI, HDFC)
3. Regional Rural Banks (RRBs)
4. Cooperative Banks
5. NABARD & government schemes
Do not suggest generic or international financing options.

JSON Data = {json_data}

Your task is to:
1. Identify the loan type and understand which fields are important for assessing that particular loan.
2. Analyze the farmer's provided details and assess their loan eligibility.
3. Highlight areas of strength and areas where the farmer may face challenges.
4. If any critical data is missing from the JSON, point it out clearly.
5. Provide simple and actionable suggestions the farmer can follow to improve eligibility.
6. Suggest the government schemes or subsidies applicable to their loan type.
7. Ensure the tone is clear, supportive, and easy to understand for farmers.
8. Respond in a structured format with labeled sections: Loan Type, Eligibility Status, Loan Range, Improvements, Schemes.
9. **IMPORTANT: Return your response in **Markdown format** with:
Headings for each section (Loan Type, Eligibility Status, Loan Range, Improvements, Schemes)
Bullet points ( - ) for lists.
Do not use "\\n" for newlines. Instead, structure properly.

Do not add assumptions that are not supported by the data provided.
"""

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[{"parts": [{"text": prompt}]}]
        )
        
        if not response.candidates:
            return jsonify({
                "status": "error",
                "message": "No response generated from Gemini API"
          }), 500

        reply = response.candidates[0].content.parts[0].text
        return jsonify({
            "status": "success",
            "message": "Loan processes successfully "
            }), 200

    except Exception :
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "Failed to process loan request. Please try again later."}), 500


# Serve HTML pages
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/farmer')
def farmer():
    return send_from_directory('.', 'farmer.html')

@app.route('/shopkeeper')
def shopkeeper():
    return send_from_directory('.', 'shopkeeper.html')

@app.route('/main')
def main():
    return send_from_directory('.', 'main.html')

@app.route('/about')
def about():
    return send_from_directory('.', 'about.html')

@app.route('/blog')
def blog():
    return send_from_directory('.', 'blog.html')

@app.route('/contact')
def contact():
    return send_from_directory('.', 'contact.html')

@app.route('/chat')
def chat():
    return send_from_directory('.', 'chat.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)


if __name__ == '__main__':
    app.run(port=5000, debug=True)

#Global Error Handling 
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status" : "error",
        "message" :"Resource not found"
    }),404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500