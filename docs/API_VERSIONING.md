# API Versioning Guide

## Overview

The AgriTech API uses URL-based versioning to ensure backward compatibility as the API evolves.

## Current Versions

| Version | Status | Base URL |
|---------|--------|----------|
| v1 | **Active** | `/api/v1/` |

## Endpoints

### v1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/config/firebase` | Get Firebase configuration |
| POST | `/api/v1/loan/process` | Process loan eligibility |
| GET | `/api/v1/tasks/<task_id>` | Check async task status |

### Legacy Endpoints (Deprecated)

The following endpoints are deprecated and will be removed in future versions:

| Method | Endpoint | Migration |
|--------|----------|-----------|
| GET | `/api/firebase-config` | Use `/api/v1/config/firebase` |
| POST | `/process-loan` | Use `/api/v1/loan/process` |

## Response Headers

All API responses include the following headers:

- `X-API-Version`: Current API version (e.g., "1.0")
- `X-Deprecated`: Set to "true" if endpoint is deprecated
- `X-Deprecation-Message`: Migration instructions for deprecated endpoints

## Example Usage

### JavaScript

```javascript
// New versioned endpoint
fetch('/api/v1/loan/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ loan_type: 'Crop Cultivation' })
});
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:5000/api/v1/loan/process',
    json={'loan_type': 'Crop Cultivation'}
)
```

## Versioning Policy

1. **Major versions** (v1, v2) indicate breaking changes
2. **Minor updates** within a version are backward compatible
3. **Deprecated endpoints** remain functional for at least 6 months
4. **Sunset notices** are provided via response headers
