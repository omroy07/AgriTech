from flask import Flask, render_template, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Configuration for Unified Pipeline
# In production, this would be an env variable pointing to the main backend service
PIPELINE_API_URL = "http://localhost:5000/api/v1/ingest/upload"
PIPELINE_STATUS_URL = "http://localhost:5000/api/v1/ingest/status/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Proxies the prediction request to the Unified Data Extraction Pipeline.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Forward to Central Pipeline
        files = {'file': (file.filename, file.stream, file.mimetype)}
        data = {
            'type': 'DISEASE',
            'metadata': json.dumps({'source': 'web_legacy_app'})
        }
        
        # Note: In a real microservice mesh, we'd use mutual TLS or internal tokens.
        # Here we assume an internal call.
        response = requests.post(PIPELINE_API_URL, files=files, data=data)
        
        if response.status_code != 202:
            return jsonify({'error': f"Pipeline Error: {response.text}"}), response.status_code
            
        result_data = response.json()
        tracking_id = result_data.get('tracking_id')
        
        # Poll for result (Simple implementation for legacy compatibility)
        # In a real app, we'd use WebSockets or redirect the user to a status page
        import time
        for _ in range(10): # Try for 10 seconds
            time.sleep(1)
            status_resp = requests.get(PIPELINE_STATUS_URL + tracking_id)
            if status_resp.status_code == 200:
                status_data = status_resp.json().get('data', {})
                if status_data.get('status') == 'COMPLETED':
                    result = status_data.get('result', {})
                    return render_template('result.html',
                                           prediction=result.get('prediction'),
                                           description=result.get('recommendation'),
                                           image_path=status_data.get('filename')) # Path might need adjustment for serving
                elif status_data.get('status') == 'FAILED':
                   return jsonify({'error': 'Processing Failed'}), 500

        return jsonify({'message': 'Processing started. Check status later.', 'tracking_id': tracking_id}), 202

    except Exception as e:
        app.logger.error(f"Proxy error: {str(e)}")
        return jsonify({'error': 'Internal Proxy Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Run on different port to main app
