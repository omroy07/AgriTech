from flask import Flask, render_template_string, redirect, url_for, session
from Disease_prediction.disease_blueprint import disease_bp
from Crop_Recommendation.crop_recommendation_blueprint import crop_recommendation_bp
from Crop_Yield_Prediction.crop_yield_app.crop_yield_blueprint import crop_yield_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(disease_bp)
app.register_blueprint(crop_recommendation_bp)
app.register_blueprint(crop_yield_bp)

# Simple homepage with links to each module
@app.route('/')
def home():
    return render_template_string('''
        <h1>AgriTech Unified App</h1>
        <ul>
            <li><a href="/disease/">Disease Prediction</a></li>
            <li><a href="/crop-recommendation/">Crop Recommendation</a></li>
            <li><a href="/crop-yield/">Crop Yield Prediction</a></li>
        </ul>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/login')
def login():
    # Render your login template here
    return render_template_string('<h2>Login Page Placeholder</h2>')

@app.route('/farmer-connection')
def farmer_connection():
    return render_template_string('<h2>Farmer Connection Page Placeholder</h2>')

@app.route('/organic')
def organic():
    return render_template_string('<h2>Organic Farming Page Placeholder</h2>')

@app.route('/shopkeeper')
def shopkeeper():
    return render_template_string('<h2>Shopkeeper Listings Page Placeholder</h2>')

@app.route('/chat')
def chat():
    return render_template_string('<h2>ChatBot Page Placeholder</h2>')

@app.route('/plantation')
def plantation():
    return render_template_string('<h2>Plantation Page Placeholder</h2>')

if __name__ == '__main__':
    app.run(debug=True)