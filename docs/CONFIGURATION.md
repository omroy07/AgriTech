# ⚙️ AgriTech Centralized Configuration & Environment Management

This document provides a comprehensive guide to AgriTech's configuration architecture across the Python/Flask backend and JavaScript frontend.

---

## 🏗️ Architecture Overview

AgriTech utilizes a **two-tier typed configuration system**:

```
 ┌────────────────────────────────────────────────────────┐
 │                      .env File                         │
 └───────────────────────────┬────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
 ┌──────────────────────┐          ┌──────────────────────┐
 │   Backend Config     │          │   Public Endpoint    │
 │ (backend/settings.py)│─────────▶│  (GET /api/v1/config)│
 └──────────────────────┘          └──────────┬───────────┘
                                              │ (Sync)
                                              ▼
                                   ┌──────────────────────┐
                                   │   Frontend Config    │
                                   │    (js/config.js)    │
                                   └──────────────────────┘
```

1. **Backend (`backend/config/settings.py`)**:
   - Strongly-typed Python dataclasses (`AppConfig`, `DatabaseConfig`, `AuthConfig`, `AIModelConfig`, `FeatureFlags`, `ServicesConfig`, `StorageConfig`, `FirebaseConfig`, `MailConfig`).
   - Caching with `@lru_cache` for sub-millisecond access.
   - Safe masking that excludes passwords, secrets, and database credentials from public exposure.
2. **Frontend (`js/config.js`)**:
   - Immutable configuration singleton `window.AgriTechConfig`.
   - Automatic environment detection (`development`, `staging`, `production`).
   - Unified API routes and storage keys registry.
   - Dynamic synchronization with `/api/v1/config` on load.

---

## 🌿 Backend Configuration (`backend/config/settings.py`)

### Accessing Settings in Python Code
```python
from backend.config.settings import get_settings

settings = get_settings()

# Type-safe attributes
if settings.features.enable_ai_disease_diagnosis:
    threshold = settings.ai.default_confidence_threshold
    db_url = settings.database.url
```

---

## 🌐 Frontend Configuration (`js/config.js`)

### 1. Including in HTML
```html
<!-- Load before other app scripts -->
<script src="js/config.js"></script>
```

### 2. Usage Examples in JavaScript
```javascript
// 1. Get an API endpoint URL (automatically prefixes with correct host/base)
const authUrl = AgriTechConfig.getApiUrl('auth'); 
// => "http://127.0.0.1:5000/api/v1/auth" or "/api/v1/auth"

// 2. Check Feature Flags
if (AgriTechConfig.isFeatureEnabled('enablePredictionComparison')) {
  renderCompareButton();
}

// 3. Centralized Storage Keys
const token = localStorage.getItem(AgriTechConfig.storageKeys.token);

// 4. Model Parameters
const maxSize = AgriTechConfig.get('models.maxUploadSizeBytes');
```

---

## 🚩 Feature Flags Reference

| Feature Flag | Default | Description |
|:---|:---:|:---|
| `ENABLE_AI_DISEASE` | `True` | Plant disease computer vision & AI diagnosis pipeline. |
| `ENABLE_PREDICTION_COMPARISON` | `True` | Side-by-side historical diagnosis comparison & diffing. |
| `ENABLE_SEEDLING_CLASSIFICATION` | `True` | CNN seedling weed vs crop identification system. |
| `ENABLE_WEATHER_ADVISORY` | `True` | Dynamic real-time agricultural weather alert banner. |
| `ENABLE_SPATIAL_ANALYTICS` | `True` | Satellite & NDVI crop health field mapping. |
| `ENABLE_CROP_RECOMMENDATION` | `True` | ML-driven soil & climate crop advisory. |
| `ENABLE_CARBON_PORTAL` | `True` | Soil carbon credit calculation and marketplace. |
| `ENABLE_VOICE_INPUT` | `True` | Multilingual voice query interface for farmers. |
| `ENABLE_OFFLINE_CACHE` | `True` | Offline data caching via Service Worker / localStorage. |

---

## 🔒 Security Best Practices
- **Never commit `.env`**: Always add `.env` to `.gitignore`.
- **Public API Safety**: The `/api/v1/config` endpoint only returns the output of `settings.get_public_config()`, ensuring zero database passwords or JWT secrets are exposed.
