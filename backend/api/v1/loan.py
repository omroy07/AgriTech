import os
import re
from flask import Blueprint, request, jsonify
import google.generativeai as genai

from auth_utils import token_required, roles_required

loan_bp = Blueprint('loan', __name__)


def sanitize_input(text):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    if len(text) > 1000:
        text = text[:1000]
    return text.strip()


def validate_input(data):
    """Validate input data structure and content"""
    if not data:
        return False, "No data provided"
    return True, "Valid input"


@loan_bp.route('/loan/process', methods=['POST'])
@token_required
@roles_required('farmer', 'admin')
def process_loan():
    """Process loan eligibility request."""
    try:
        json_data = request.get_json(force=True)
        
        is_valid, validation_message = validate_input(json_data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "message": validation_message
            }), 400
        
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    json_data[key] = sanitize_input(value)
        
        API_KEY = os.environ.get('GEMINI_API_KEY')
        if not API_KEY:
            return jsonify({
                "status": "error",
                "message": "API key not configured"
            }), 500
        
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
You are a financial loan eligibility advisor specializing in agricultural loans for farmers in India.
JSON Data = {json_data}
Analyze the farmer's provided details and assess their loan eligibility.
Respond in a structured format with labeled sections: Loan Type, Eligibility Status, Loan Range, Improvements, Schemes.
"""
        
        response = model.generate_content(prompt)
        
        if not response.candidates:
            return jsonify({
                "status": "error",
                "message": "No response generated from Gemini API"
            }), 500

        reply = response.candidates[0].content.parts[0].text
        return jsonify({
            "status": "success",
            "message": "Loan processed successfully",
            "result": reply
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
