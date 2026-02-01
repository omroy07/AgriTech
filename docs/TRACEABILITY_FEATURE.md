# Supply Chain Traceability with QR Integrity

## Overview

This feature implements a comprehensive **Farm-to-Table** traceability system that enables transparent tracking of produce through the entire supply chain. Consumers and shopkeepers can verify the origin, quality, and journey of produce using encrypted QR codes.

## Features

### 1. Batch Lifecycle Management
- **State Machine**: Tracks produce through defined stages
  - `Harvested` → `Quality_Check` → `Logistics` → `In_Shop`
- **Immutable Records**: Each transition is permanently logged
- **Quality Tracking**: Records quality grades and inspection notes

### 2. Role-Based Access Control (RBAC)
- **Farmer**: Can create batches and move through Harvested → Quality_Check → Logistics
- **Shopkeeper**: Can mark batches as "Received" (In_Shop)
- **Admin**: Full control including rollback capabilities

### 3. QR Code Generation
- **Encrypted Data**: QR codes contain encrypted batch information
- **Tamper Detection**: HMAC signatures prevent data manipulation
- **Public Verification**: Anyone can scan and verify produce authenticity

### 4. Audit Trail
- **Complete History**: Every hand-off is recorded with timestamps
- **User Tracking**: Captures user ID, role, and IP address
- **Immutable Logs**: Cannot be modified after creation

## Architecture

### Core Components

```
backend/
├── models.py                    # ProduceBatch & AuditTrail models
├── services/
│   └── batch_service.py        # State-machine logic
├── utils/
│   └── qr_generator.py         # QR code encryption/generation
└── api/v1/
    └── traceability.py         # REST API endpoints
```

### Database Schema

#### ProduceBatch Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| batch_id | String(100) | Unique batch identifier |
| qr_code | Text | Encrypted QR data |
| produce_name | String(200) | Name of produce |
| produce_type | String(100) | Type (vegetable, fruit, grain) |
| quantity_kg | Float | Quantity in kilograms |
| origin_location | String(255) | Farm/origin location |
| status | String(50) | Current lifecycle stage |
| farmer_id | Integer | FK to users |
| shopkeeper_id | Integer | FK to users (nullable) |
| quality_grade | String(10) | A, B, or C |
| harvest_date | DateTime | Date of harvest |
| created_at | DateTime | Record creation time |

#### AuditTrail Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| batch_id | Integer | FK to produce_batches |
| event_type | String(50) | Type of event |
| from_status | String(50) | Previous status |
| to_status | String(50) | New status |
| user_id | Integer | FK to users |
| user_role | String(20) | Role at time of action |
| timestamp | DateTime | Event timestamp |
| ip_address | String(45) | User's IP address |
| signature | String(255) | HMAC for tamper detection |

## API Endpoints

### Authentication
All endpoints (except public verification) require JWT token:
```http
Authorization: Bearer <token>
```

### 1. Create Batch
**POST** `/api/v1/traceability/batches`

**Role**: Farmer, Admin

**Request Body**:
```json
{
  "produce_name": "Organic Tomatoes",
  "produce_type": "vegetable",
  "quantity_kg": 150.5,
  "origin_location": "Green Valley Farm, Punjab",
  "harvest_date": "2026-01-30T08:00:00",
  "certification": "organic",
  "quality_grade": "A",
  "quality_notes": "Fresh harvest, no defects"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Batch created successfully",
  "data": {
    "batch": {
      "batch_id": "BATCH-A1B2C3D4E5F6G7H8",
      "qr_code": "encrypted_data_string...",
      "status": "Harvested",
      "...": "..."
    },
    "qr_verification_url": "/api/v1/traceability/verify/BATCH-A1B2C3D4E5F6G7H8"
  }
}
```

### 2. Update Batch Status
**PUT** `/api/v1/traceability/batches/{batch_id}/status`

**Role**: Farmer (Harvested→Quality_Check→Logistics), Shopkeeper (Logistics→In_Shop), Admin (all)

**Request Body**:
```json
{
  "status": "Quality_Check",
  "notes": "Quality inspection completed",
  "location": "Inspection Facility, Delhi",
  "quality_grade": "A",
  "quality_notes": "Excellent quality batch"
}
```

### 3. Update Quality Information
**PUT** `/api/v1/traceability/batches/{batch_id}/quality`

**Role**: Farmer, Admin

**Request Body**:
```json
{
  "quality_grade": "B",
  "quality_notes": "Minor cosmetic imperfections"
}
```

### 4. Get Batch Details
**GET** `/api/v1/traceability/batches/{batch_id}?include_audit=true`

**Role**: Authenticated users

**Response**: Returns batch details with optional audit trail

### 5. List Batches
**GET** `/api/v1/traceability/batches?status=Harvested`

**Role**: 
- Farmers: See their own batches
- Shopkeepers: See received batches
- Admin: See all batches

**Query Parameters**:
- `status`: Filter by status
- `farmer_id`: (Admin only) Filter by farmer
- `shopkeeper_id`: (Admin only) Filter by shopkeeper

### 6. Public Verification (No Auth Required)
**GET** `/api/v1/traceability/verify/{batch_id}`

**Response**: Traceability passport with full journey

```json
{
  "status": "success",
  "data": {
    "passport": {
      "batch_id": "BATCH-A1B2C3D4E5F6G7H8",
      "produce": {
        "name": "Organic Tomatoes",
        "type": "vegetable",
        "quantity": 150.5,
        "certification": "organic"
      },
      "origin": {
        "location": "Green Valley Farm, Punjab",
        "harvest_date": "2026-01-30T08:00:00"
      },
      "journey": [
        {
          "timestamp": "2026-01-30T08:15:00",
          "event": "BATCH_CREATED",
          "to_status": "Harvested",
          "handler_role": "farmer"
        },
        {
          "timestamp": "2026-01-30T14:30:00",
          "event": "STATUS_CHANGE",
          "from_status": "Harvested",
          "to_status": "Quality_Check",
          "handler_role": "farmer"
        }
      ],
      "current_status": "Quality_Check"
    }
  }
}
```

### 7. Verify QR Code
**POST** `/api/v1/traceability/verify-qr`

**Request Body**:
```json
{
  "qr_data": "encrypted_qr_code_data_string"
}
```

### 8. Get Statistics
**GET** `/api/v1/traceability/stats`

**Role**: Authenticated users

Returns role-specific statistics (batch counts, quantities, etc.)

## Security Features

### 1. Encryption
- **Fernet Symmetric Encryption**: QR codes use cryptography.fernet
- **PBKDF2 Key Derivation**: Secure key generation from secret
- **Base64 Encoding**: For QR code data transmission

### 2. Integrity Verification
- **HMAC Signatures**: Detect tampered data
- **Audit Log Signatures**: Prevent modification of history
- **Signature Comparison**: Constant-time comparison to prevent timing attacks

### 3. Access Control
- **JWT Token Authentication**: Required for all non-public endpoints
- **Role-Based Permissions**: Enforced at API and service layers
- **Ownership Validation**: Users can only modify their own batches
- **Security Event Logging**: All unauthorized attempts are logged

### 4. Input Validation
- **Sanitization**: All user inputs are sanitized
- **Type Checking**: Strict type validation
- **Rate Limiting**: Prevents abuse (configurable per endpoint)

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

New dependencies added:
- `qrcode[pil]>=7.4.2` - QR code generation
- `cryptography>=41.0.0` - Encryption and key derivation

### 2. Set Environment Variables
```bash
# .env file
QR_SECRET_KEY=your_secure_random_key_here
JWT_SECRET=your_jwt_secret_key
DATABASE_URL=sqlite:///agritech.db  # or PostgreSQL URL
```

### 3. Initialize Database
```bash
python migrations/init_traceability_db.py
```

This creates:
- `produce_batches` table
- `audit_trails` table
- Sample users (farmer, shopkeeper, admin)

### 4. Start Server
```bash
python app.py
```

## Usage Examples

### Example 1: Farmer Creates Batch
```bash
curl -X POST http://localhost:5000/api/v1/traceability/batches \
  -H "Authorization: Bearer <farmer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "produce_name": "Organic Tomatoes",
    "produce_type": "vegetable",
    "quantity_kg": 150,
    "origin_location": "Green Valley Farm",
    "harvest_date": "2026-01-30T08:00:00",
    "certification": "organic"
  }'
```

### Example 2: Farmer Moves to Quality Check
```bash
curl -X PUT http://localhost:5000/api/v1/traceability/batches/BATCH-XXX/status \
  -H "Authorization: Bearer <farmer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Quality_Check",
    "quality_grade": "A",
    "notes": "Inspection completed successfully"
  }'
```

### Example 3: Shopkeeper Marks as Received
```bash
curl -X PUT http://localhost:5000/api/v1/traceability/batches/BATCH-XXX/status \
  -H "Authorization: Bearer <shopkeeper_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In_Shop",
    "location": "City Market Store #5",
    "notes": "Received in good condition"
  }'
```

### Example 4: Public Verification (No Auth)
```bash
curl http://localhost:5000/api/v1/traceability/verify/BATCH-XXX
```

## State Machine Diagram

```
┌───────────┐     Farmer     ┌──────────────┐     Farmer     ┌───────────┐
│ Harvested │ ─────────────> │Quality_Check │ ─────────────> │ Logistics │
└───────────┘                └──────────────┘                └───────────┘
                                                                    │
                                                                    │ Shopkeeper
                                                                    ▼
                                                              ┌──────────┐
                                                              │ In_Shop  │
                                                              └──────────┘

Admin can rollback at any stage
```

## Testing

### Manual Testing
Use the provided sample users:
- **Farmer**: `farmer.john@example.com`
- **Shopkeeper**: `shopkeeper.mary@example.com`
- **Admin**: `admin@agritech.com`

### Automated Tests
```bash
pytest tests/test_traceability.py -v
```

## Frontend Integration

### QR Code Display
The API returns QR codes as base64-encoded images:

```html
<img src="data:image/png;base64,iVBORw0K..." alt="Batch QR Code" />
```

### Verification Page
Create a public verification page at `/verify/{batch_id}` that displays the traceability passport.

### Mobile App Integration
QR codes can be scanned using any standard QR scanner. The encrypted data can then be sent to `/api/v1/traceability/verify-qr` for verification.

## Monitoring & Logs

### Security Events
All security-related events are logged:
- Unauthorized access attempts
- Invalid state transitions
- Tampered QR codes

### Audit Trail
Complete audit trail is maintained for:
- Batch creation
- Status changes
- Quality updates

## Future Enhancements

1. **Blockchain Integration**: Store audit logs on blockchain for enhanced immutability
2. **IoT Sensors**: Integrate temperature and humidity sensors
3. **Smart Contracts**: Automate payments on status changes
4. **Mobile App**: Dedicated mobile apps for farmers and shopkeepers
5. **Analytics Dashboard**: Visualize supply chain metrics
6. **Multi-language Support**: Localize for different regions
7. **Geolocation**: GPS tracking for logistics stage
8. **Photo Evidence**: Attach images at each stage

## Troubleshooting

### Issue: "Invalid or tampered QR code"
- Ensure QR_SECRET_KEY is consistent across all servers
- Check that QR code data hasn't been modified
- Verify encryption/decryption using the same key

### Issue: "User role cannot transition batch"
- Check RBAC rules in [batch_service.py](backend/services/batch_service.py)
- Verify user role in JWT token
- Review state machine transitions

### Issue: "Batch not found"
- Verify batch_id is correct
- Check database connection
- Ensure migrations have been run

## Contributing

When adding features:
1. Update models in [backend/models.py](backend/models.py)
2. Add service layer logic in [backend/services/batch_service.py](backend/services/batch_service.py)
3. Create API endpoints in [backend/api/v1/traceability.py](backend/api/v1/traceability.py)
4. Update documentation
5. Add tests

## License

Part of the AgriTech platform. See main LICENSE file.

## Contact

For issues or questions about this feature, please open an issue on GitHub.

---

**Issue Reference**: #1193 - Decentralized Supply Chain Traceability with QR Integrity
