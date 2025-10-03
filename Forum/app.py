from flask import Flask, request, jsonify
from auth_utils import token_required, roles_required
from flask_cors import CORS
import re
from functools import wraps
import json

app = Flask(__name__)
CORS(app)  # Allow frontend (Live Server) to call API

# Input validation helper functions
def sanitize_input(text, max_length=1000):
    """Sanitize text input"""
    if not isinstance(text, str):
        return ""
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\']', '', text.strip())
    return cleaned[:max_length]

def validate_required_fields(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field in required_fields:
                if field not in request.get_json() or not request.get_json()[field].strip():
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_post_data(data):
    """Validate forum post data"""
    required_fields = ['title', 'content', 'author']
    for field in required_fields:
        if field not in data or not data[field].strip():
            return False, f"Missing required field: {field}"
    
    # Validate field lengths
    if len(data['title']) > 200:
        return False, "Title too long (max 200 characters)"
    if len(data['content']) > 5000:
        return False, "Content too long (max 5000 characters)"
    if len(data['author']) > 100:
        return False, "Author name too long (max 100 characters)"
    
    return True, "Valid"

forum_posts = []

@app.route('/forum', methods=['GET', 'POST'])
@token_required
def forum_api():
    try:
        if request.method == 'POST':
            # Only allow farmers and admins to create posts
            user = getattr(request, 'user', {})
            if user.get('role') not in ['farmer', 'admin']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            # Validate content type
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Sanitize inputs
            sanitized_data = {
                'title': sanitize_input(data.get('title', ''), 200),
                'content': sanitize_input(data.get('content', ''), 5000),
                'author': sanitize_input(data.get('author', ''), 100),
                'timestamp': data.get('timestamp', '')
            }
            
            # Validate data
            is_valid, message = validate_post_data(sanitized_data)
            if not is_valid:
                return jsonify({'error': message}), 400
            
            # Add to posts (in a real app, this would go to a database)
            forum_posts.append(sanitized_data)
            
            return jsonify({"status": "success", "message": "Post created successfully"}), 201
        else:
            return jsonify(forum_posts)
            
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'}), 400
    except Exception as e:
        app.logger.error(f"Forum API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Global error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)