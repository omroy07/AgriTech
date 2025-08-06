from flask import Flask, render_template, request, jsonify, redirect
import requests

app = Flask(__name__)

# Global API config
API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_PARAMS = {
    "api-key": "579b464db66ec23bdd000001c43ef34767ce496343897dfb1893102b",
    "format": "json",
    "limit": 1000
}

# Load data once (to avoid repeated API hits)
def load_data():
    response = requests.get(API_URL, params=API_PARAMS)
    return response.json().get("records", [])

DATA = load_data()

@app.route('/')
def home():
    return redirect('/crop_price_tracker')

@app.route('/crop_price_tracker', methods=['GET', 'POST'])
def crop_price_tracker():
    crops = sorted({record['commodity'] for record in DATA if record.get('commodity')})
    result = []
    error = None

    if request.method == 'POST':
        crop = request.form.get('crop')
        state = request.form.get('state')
        market = request.form.get('market')

        result = [
            r for r in DATA
            if r.get('commodity', '').lower() == crop.lower()
            and r.get('state', '').lower() == state.lower()
            and r.get('market', '').lower() == market.lower()
        ]

        if not result:
            error = "No data found for the given crop, state, and market."

    return render_template('crop_price_tracker.html', crops=crops, result=result, error=error)

@app.route('/get_states')
def get_states():
    crop = request.args.get('crop', '').lower()
    states = sorted({r['state'] for r in DATA if r.get('commodity', '').lower() == crop})
    return jsonify(states)

@app.route('/get_markets')
def get_markets():
    crop = request.args.get('crop', '').lower()
    state = request.args.get('state', '').lower()
    markets = sorted({
        r['market'] for r in DATA
        if r.get('commodity', '').lower() == crop and r.get('state', '').lower() == state
    })
    return jsonify(markets)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
