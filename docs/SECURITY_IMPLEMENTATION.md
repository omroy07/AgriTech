# AgriTech Security Documentation

## Overview

This document outlines the security measures implemented across all AgriTech Flask applications to prevent common web vulnerabilities including SQL injection, XSS attacks, file upload vulnerabilities, and input validation bypasses.

## Security Vulnerabilities Fixed

### 1. Input Validation Vulnerabilities

**Before Fix:**
```python
@app.route('/predict', methods=['POST'])
def predict():
    data = [
        float(request.form['N']),  # No validation - crashes if missing
        float(request.form['P']),  # No validation
        # ... more fields
    ]
```

**After Fix:**
```python
@app.route('/predict', methods=['POST'])
@validate_required_fields(['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
def predict():
    try:
        data = [
            sanitize_numeric_input(request.form['N'], 0, 200, "Nitrogen (N)"),
            sanitize_numeric_input(request.form['P'], 0, 200, "Phosphorus (P)"),
            # ... more validated fields
        ]
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### 2. SQL Injection Prevention

**Before Fix:**
```python
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
cursor.execute(query)  # DANGEROUS
```

**After Fix:**
```python
query = "SELECT id, username, password_hash FROM users WHERE username = ?"
cursor.execute(query, (username,))  # SAFE - Parameterized query
```

### 3. File Upload Security

**Before Fix:**
```python
filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
file.save(filepath)  # DANGEROUS - No validation
```

**After Fix:**
```python
# Validate file extension
if not allowed_file(file.filename):
    return jsonify({'error': 'Invalid file type'}), 400

# Validate file size
if not validate_file_size(file):
    return jsonify({'error': 'File too large'}), 400

# Sanitize filename
filename = sanitize_filename(file.filename)
unique_filename = f"{uuid.uuid4().hex}_{filename}"
filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
```

### 4. XSS Prevention

**Before Fix:**
```python
return render_template('result.html', user_input=user_input)  # DANGEROUS
```

**After Fix:**
```python
sanitized_input = sanitize_input(user_input, 255)
return render_template('result.html', user_input=sanitized_input)  # SAFE
```

## Security Measures Implemented

### 1. Input Validation Functions

#### `validate_required_fields(required_fields)`
Decorator that ensures all required form fields are present and non-empty.

#### `sanitize_input(text, max_length=255)`
Removes dangerous characters and limits input length to prevent XSS and injection attacks.

#### `sanitize_numeric_input(value, min_val, max_val, field_name)`
Validates and sanitizes numeric inputs with range checking.

### 2. File Upload Security

#### `allowed_file(filename)`
Validates file extensions against a whitelist.

#### `validate_file_size(file, max_size_bytes)`
Ensures uploaded files don't exceed size limits.

#### `sanitize_filename(filename)`
Removes dangerous characters from filenames to prevent path traversal attacks.

### 3. Error Handling

All applications now include proper error handling that:
- Returns appropriate HTTP status codes
- Logs errors without exposing sensitive information
- Provides user-friendly error messages
- Prevents information disclosure

### 4. Security Headers

Applications include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## Applications Secured

### 1. Crop Recommendation (`Crop Recommendation/app.py`)
- ✅ Input validation for all form fields
- ✅ Numeric range validation
- ✅ Error handling for missing/invalid data
- ✅ PDF generation security

### 2. Crop Yield Prediction (`Crop Yield Prediction/crop_yield_app/app.py`)
- ✅ Form field validation
- ✅ Encoder validation
- ✅ Numeric input sanitization
- ✅ Comprehensive error handling

### 3. Crop Prices Tracker (`Crop_Prices_Tracker/app.py`)
- ✅ Input sanitization
- ✅ API error handling
- ✅ Timeout protection
- ✅ Data validation

### 4. Forum (`Forum/app.py`)
- ✅ JSON validation
- ✅ Content length limits
- ✅ XSS prevention
- ✅ Input sanitization

### 5. Disease Prediction (`Disease prediction/app.py`)
- ✅ File upload validation
- ✅ File type restrictions
- ✅ File size limits
- ✅ Path traversal prevention
- ✅ Filename sanitization

### 6. Crop Planning (`Crop_Planning/app.py`)
- ✅ JSON input validation
- ✅ AI prompt sanitization
- ✅ Error handling
- ✅ Input length limits

### 7. Labour Alerts (`Labour_Alerts/app.py`)
- ✅ API timeout protection
- ✅ Retry logic with exponential backoff
- ✅ Response caching
- ✅ Error handling

## Security Testing

### Running Security Tests

```bash
python security_test.py
```

The security test script validates:
- Missing field handling
- SQL injection prevention
- XSS prevention
- File upload security
- Numeric input validation
- JSON validation
- Error handling
- API endpoint availability

### Test Payloads

#### SQL Injection Tests
```python
SQL_INJECTION_PAYLOADS = [
    "admin'; DROP TABLE users; --",
    "' OR '1'='1",
    "admin' UNION SELECT * FROM users --",
    # ... more payloads
]
```

#### XSS Tests
```python
XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    # ... more payloads
]
```

## Security Best Practices

### 1. Always Validate Input
- Use the provided validation decorators
- Sanitize all user inputs
- Validate data types and ranges

### 2. Use Parameterized Queries
- Never use string formatting for SQL queries
- Always use parameterized queries or ORM

### 3. Implement Proper Error Handling
- Don't expose sensitive information in error messages
- Log errors for debugging
- Return appropriate HTTP status codes

### 4. Secure File Uploads
- Validate file types and sizes
- Sanitize filenames
- Store files outside web root when possible

### 5. Use HTTPS in Production
- Enable HTTPS for all communications
- Use secure cookies
- Implement HSTS headers

## Dependencies Added

```txt
# Security dependencies
bcrypt==4.0.1
email-validator==2.0.0
flask-limiter==3.5.0
werkzeug==2.3.7
requests==2.31.0
```

## Monitoring and Maintenance

### 1. Regular Security Audits
- Run security tests monthly
- Review access logs
- Monitor for suspicious activity

### 2. Dependency Updates
- Keep all dependencies updated
- Monitor for security advisories
- Use `pip-audit` to check for vulnerabilities

### 3. Log Monitoring
- Monitor application logs for errors
- Set up alerts for security events
- Review failed authentication attempts

## Incident Response

### 1. Security Breach Response
1. Immediately isolate affected systems
2. Preserve evidence
3. Assess the scope of the breach
4. Notify relevant stakeholders
5. Implement fixes
6. Document lessons learned

### 2. Vulnerability Disclosure
- Report vulnerabilities to the development team
- Provide detailed reproduction steps
- Allow reasonable time for fixes
- Coordinate public disclosure

## Contact Information

For security issues, please contact the development team or create a security issue in the project repository.

---

**Last Updated:** December 2024
**Version:** 1.0
