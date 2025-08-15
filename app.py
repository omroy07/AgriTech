# --- All necessary imports for the Flask app and password reset ---
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
# IMPORTANT: Replace this with a strong, random key in a production environment
app.config['SECRET_KEY'] = 'your_very_secret_key_here'

# --- In-memory user data (simulating a database) ---
# This data is not persistent. In a real application, you would use a database.
# The 'password' value should be a hashed password in a real application.
users = {
    'testuser@example.com': {
        'password': 'hashed_password_placeholder',
        'reset_token': None,
        'reset_token_expiration': None
    }
}
# --- End of in-memory data ---

# --- Email configuration ---
# You MUST replace these with your actual email service details
# Example for Gmail: EMAIL_HOST = 'smtp.gmail.com', EMAIL_PORT = 587
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USERNAME = 'your_email@example.com'
EMAIL_PASSWORD = 'your_email_password'
SENDER_EMAIL = 'your_email@example.com'

# --- Email Sending Function ---
def send_reset_email(user_email, reset_link):
    """Sends a password reset email to the user."""
    try:
        msg = MIMEText(f"Click the link to reset your password: {reset_link}")
        msg['Subject'] = "Password Reset Request"
        msg['From'] = SENDER_EMAIL
        msg['To'] = user_email

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, [user_email], msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# ------------------------------------------------------------------
# --- Your Original Application Routes Go Here ---
# You can copy your existing routes (e.g., '/', '/main', '/disease') here.
# For example:
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/login')
# def login():
#     return render_template('login.html')
# ------------------------------------------------------------------

# --- New Password Reset Routes ---
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handles the request for a password reset email."""
    if request.method == 'POST':
        email = request.form.get('email')
        user = users.get(email)

        if user:
            # Generate a secure token with a one-hour expiration time
            token = secrets.token_urlsafe(32)
            expiration_time = datetime.now() + timedelta(hours=1)
            
            user['reset_token'] = token
            user['reset_token_expiration'] = expiration_time

            reset_link = url_for('reset_password', token=token, _external=True)
            
            if send_reset_email(email, reset_link):
                flash("A password reset link has been sent to your email.", "success")
            else:
                flash("Failed to send email. Please try again.", "danger")
        else:
            flash("If the email is valid, a password reset link will be sent.", "info")

        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handles the password reset form and logic."""
    user_to_reset = None
    for email, user in users.items():
        # Find the user with the valid, non-expired token
        if user['reset_token'] == token and user['reset_token_expiration'] > datetime.now():
            user_to_reset = user
            break
    
    if not user_to_reset:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('reset_password.html', token=token)
        
        # In a real app, you would hash the password before storing it
        user_to_reset['password'] = new_password
        
        # Invalidate the token after use
        user_to_reset['reset_token'] = None
        user_to_reset['reset_token_expiration'] = None

        flash("Your password has been reset successfully.", "success")
        return redirect(url_for('forgot_password'))

    return render_template('reset_password.html', token=token)

# --- App entry point ---
if __name__ == '__main__':
    app.run(debug=True)
