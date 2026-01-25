from flask import Blueprint, request, jsonify, current_app
import google.generativeai as genai
from backend.utils.validation import sanitize_input, validate_input

loan_bp = Blueprint('loan', __name__)


@loan_bp.route('/loan/process', methods=['POST'])
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
        
        API_KEY = current_app.config.get('GEMINI_API_KEY')
        if not API_KEY:
            return jsonify({
                "status": "error",
                "message": "API key not configured"
            }), 500
        
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(current_app.config.get('GEMINI_MODEL_ID', 'gemini-2.5-flash'))
        
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
