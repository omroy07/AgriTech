# Quick Start: Supply Chain Traceability

This guide will help you get the traceability feature running in 5 minutes.

## Prerequisites

- Python 3.8+
- Flask application already set up
- Virtual environment activated

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

New packages installed:
- `qrcode[pil]` - QR code generation
- `cryptography` - Encryption for QR codes

## Step 2: Set Environment Variables

Create or update your `.env` file:

```bash
# Add these to your .env file
QR_SECRET_KEY=your_secure_random_key_change_this_in_production
JWT_SECRET=agritech_secret_key
DATABASE_URL=sqlite:///agritech.db
```

**Important**: Generate a secure random key for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Initialize Database

```bash
python migrations/init_traceability_db.py
```

This will:
- Create `produce_batches` table
- Create `audit_trails` table
- Create sample users (farmer, shopkeeper, admin)

## Step 4: Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Step 5: Test the Feature

### Option A: Use the Web UI

Open your browser:
```
http://localhost:5000/verify-produce.html
```

Enter a batch ID to verify produce.

### Option B: Use the API

#### 1. Get a JWT Token (Simplified for testing)

```python
import jwt

# Generate farmer token
farmer_token = jwt.encode(
    {'user_id': 1, 'role': 'farmer', 'email': 'farmer.john@example.com'},
    'agritech_secret_key',
    algorithm='HS256'
)
print(f"Farmer Token: {farmer_token}")
```

#### 2. Create a Batch

```bash
curl -X POST http://localhost:5000/api/v1/traceability/batches \
  -H "Authorization: Bearer YOUR_FARMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "produce_name": "Organic Tomatoes",
    "produce_type": "vegetable",
    "quantity_kg": 150.5,
    "origin_location": "Green Valley Farm",
    "certification": "organic"
  }'
```

Response:
```json
{
  "status": "success",
  "data": {
    "batch": {
      "batch_id": "BATCH-A1B2C3D4E5F6G7H8",
      "status": "Harvested",
      ...
    }
  }
}
```

#### 3. Verify Publicly (No Auth Required)

```bash
curl http://localhost:5000/api/v1/traceability/verify/BATCH-A1B2C3D4E5F6G7H8
```

### Option C: Run Example Workflow

```bash
# Edit examples/traceability_workflow.py and add your tokens
python examples/traceability_workflow.py
```

## Complete Workflow Example

### 1. Farmer Creates Batch
```http
POST /api/v1/traceability/batches
Authorization: Bearer <farmer_token>

{
  "produce_name": "Organic Tomatoes",
  "produce_type": "vegetable",
  "quantity_kg": 150,
  "origin_location": "Green Valley Farm"
}
```

### 2. Farmer Moves to Quality Check
```http
PUT /api/v1/traceability/batches/BATCH-XXX/status
Authorization: Bearer <farmer_token>

{
  "status": "Quality_Check",
  "quality_grade": "A",
  "notes": "Quality inspection passed"
}
```

### 3. Farmer Approves for Logistics
```http
PUT /api/v1/traceability/batches/BATCH-XXX/status
Authorization: Bearer <farmer_token>

{
  "status": "Logistics",
  "location": "Distribution Center"
}
```

### 4. Shopkeeper Receives Batch
```http
PUT /api/v1/traceability/batches/BATCH-XXX/status
Authorization: Bearer <shopkeeper_token>

{
  "status": "In_Shop",
  "location": "City Market Store #5"
}
```

### 5. Anyone Verifies Publicly
```http
GET /api/v1/traceability/verify/BATCH-XXX
(No authentication required)
```

## API Endpoints Summary

| Endpoint | Method | Auth | Role | Description |
|----------|--------|------|------|-------------|
| `/batches` | POST | ✓ | Farmer, Admin | Create batch |
| `/batches/{id}/status` | PUT | ✓ | Depends on status | Update status |
| `/batches/{id}/quality` | PUT | ✓ | Farmer, Admin | Update quality |
| `/batches/{id}` | GET | ✓ | Any | Get batch details |
| `/batches` | GET | ✓ | Any | List batches |
| `/verify/{id}` | GET | ✗ | Public | Public verification |
| `/verify-qr` | POST | ✗ | Public | Verify QR code |
| `/stats` | GET | ✓ | Any | Get statistics |

## State Machine

```
Harvested → Quality_Check → Logistics → In_Shop

Farmers: Can move Harvested → Quality_Check → Logistics
Shopkeepers: Can move Logistics → In_Shop
Admins: Can do everything including rollbacks
```

## Testing

Run automated tests:
```bash
pytest tests/test_traceability.py -v
```

## Troubleshooting

### Issue: "Token is missing!"
- Add Authorization header: `Authorization: Bearer <token>`
- Generate token using JWT with user info

### Issue: "Batch not found"
- Check batch_id is correct
- Run database migration script
- Verify database connection

### Issue: "User role cannot transition batch"
- Review state machine rules
- Check user role in token
- Verify current batch status

### Issue: "Invalid or tampered QR code"
- Ensure QR_SECRET_KEY is consistent
- Don't modify QR code data
- Check encryption/decryption

## Next Steps

1. **Integrate with Frontend**: Add batch creation UI for farmers
2. **Mobile App**: Create QR scanner app
3. **Notifications**: Alert users on status changes
4. **Analytics**: Build dashboard for supply chain metrics
5. **Blockchain**: Consider blockchain integration for enhanced security

## Documentation

- Full documentation: [docs/TRACEABILITY_FEATURE.md](../docs/TRACEABILITY_FEATURE.md)
- API reference: See full docs for detailed API specs
- Examples: [examples/traceability_workflow.py](../examples/traceability_workflow.py)

## Support

For issues or questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the logs for security events

---

**Ready to trace your supply chain!** 🌾📦🚚🛒
