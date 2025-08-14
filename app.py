from flask import Flask, render_template_string, redirect, url_for
import sys
import os

# Import blueprints directly without modifying sys.path
from disease_prediction.disease_blueprint import disease_bp
from Crop_Recommendation.crop_recommendation_blueprint import crop_recommendation_bp
from Crop_Yield_Prediction.crop_yield_app.crop_yield_blueprint import crop_yield_bp

app = Flask(__name__)

# Register blueprints with unique URL prefixes
app.register_blueprint(disease_bp, url_prefix='/disease')
app.register_blueprint(crop_recommendation_bp, url_prefix='/crop-recommendation')
app.register_blueprint(crop_yield_bp, url_prefix='/crop-yield')

# Beautiful landing page with modern design
@app.route('/')
def home():
    print("🎯 Home route accessed - rendering landing page")
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AgriTech - AI-Powered Agriculture Solutions</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                # background: green;
                background: green;
                min-height: 100vh;
                color: #333;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                padding: 40px 0;
                color: white;
            }
            
            .header h1 {
                font-size: 3.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
                max-width: 600px;
                margin: 0 auto;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 30px;
                margin-top: 50px;
            }
            
            .feature-card {
                background: white;
                border-radius: 20px;
                padding: 40px 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .feature-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #667eea, #764ba2);
            }
            
            .feature-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 20px;
                display: block;
            }
            
            .feature-card h3 {
                font-size: 1.5rem;
                margin-bottom: 15px;
                color: #333;
            }
            
            .feature-card p {
                color: #666;
                line-height: 1.6;
                margin-bottom: 25px;
            }
            
            .feature-btn {
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .feature-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                color: white;
                text-decoration: none;
            }
            
            .footer {
                text-align: center;
                padding: 40px 0;
                color: white;
                opacity: 0.8;
            }
            
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 2.5rem;
                }
                
                .features-grid {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }
                
                .feature-card {
                    padding: 30px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌾 AgriTech</h1>
                <p>AI-Powered Agriculture Solutions for Smart Farming</p>
            </div>
            
            <div class="features-grid">
                <div class="feature-card">
                    <span class="feature-icon">🔬</span>
                    <h3>Disease Prediction</h3>
                    <p>Upload plant images to detect diseases and get instant treatment recommendations using advanced AI models.</p>
                    <a href="/disease/" class="feature-btn">Detect Diseases</a>
                </div>
                
                <div class="feature-card">
                    <span class="feature-icon">🌱</span>
                    <h3>Crop Recommendation</h3>
                    <p>Get AI-powered crop suggestions based on soil nutrients, climate conditions, and environmental factors.</p>
                    <a href="/crop-recommendation/" class="feature-btn">Get Recommendations</a>
                </div>
                
                <div class="feature-card">
                    <span class="feature-icon">📊</span>
                    <h3>Crop Yield Prediction</h3>
                    <p>Predict expected crop yields using machine learning models trained on historical agricultural data.</p>
                    <a href="/crop-yield/" class="feature-btn">Predict Yield</a>
                </div>
            </div>
            
            <div class="footer">
                <p>&copy; 2024 AgriTech - Empowering Farmers with AI</p>
            </div>
        </div>
    </body>
    </html>
    ''')

# Test route to debug routing
@app.route('/test-crop-recommendation')
def test_crop_recommendation():
    return "This is a test route for Crop Recommendation - NOT Disease Prediction!"

@app.route('/test-crop-yield')
def test_crop_yield():
    return "This is a test route for Crop Yield - NOT Disease Prediction!"

@app.route('/test-disease')
def test_disease():
    return "This is a test route for Disease Prediction!"

@app.route('/debug-routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.endpoint}: {rule.rule}")
    return "<br>".join(routes)

if __name__ == '__main__':
    app.run(debug=True)