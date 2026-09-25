"""
Typed Configuration & Environment Management for AgriTech Backend.
Provides strict type-casting, validation, default fallbacks, and feature flags.
"""

import os
from dataclasses import dataclass, field, asdict
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load .env file
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


def _get_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on", "t"}


def _get_int(key: str, default: int) -> int:
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def _get_float(key: str, default: float) -> float:
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def _get_list(key: str, default: List[str]) -> List[str]:
    val = os.environ.get(key)
    if not val:
        return default
    return [item.strip() for item in val.split(",") if item.strip()]


@dataclass(frozen=True)
class AppConfig:
    """Core Application & Server Configuration"""
    app_name: str = "AgriTech"
    version: str = "1.0.0"
    env: str = os.environ.get("FLASK_ENV", "development").lower()
    debug: bool = _get_bool("DEBUG", os.environ.get("FLASK_ENV") != "production")
    testing: bool = _get_bool("TESTING", False)
    secret_key: str = os.environ.get("SECRET_KEY", "agritech-dev-secret-key-change-in-prod-2026")
    host: str = os.environ.get("HOST", "0.0.0.0")
    port: int = _get_int("PORT", 5000)
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = field(
        default_factory=lambda: _get_list("CORS_ORIGINS", ["http://localhost:5000", "http://127.0.0.1:5000", "http://127.0.0.1:5500", "http://localhost:3000", "http://localhost:8501"])
    )


@dataclass(frozen=True)
class DatabaseConfig:
    """Database & Connection Pool Settings"""
    url: str = os.environ.get("DATABASE_URL", "sqlite:///agritech_dev.db")
    dev_url: str = os.environ.get("DEV_DATABASE_URL", "sqlite:///agritech_dev.db")
    echo: bool = _get_bool("DATABASE_ECHO", False)
    track_modifications: bool = False
    pool_size: int = _get_int("DATABASE_POOL_SIZE", 10)
    max_overflow: int = _get_int("DATABASE_MAX_OVERFLOW", 20)
    pool_recycle: int = _get_int("DATABASE_POOL_RECYCLE", 1800)


@dataclass(frozen=True)
class AuthConfig:
    """Authentication & JWT Settings"""
    jwt_secret: str = os.environ.get("JWT_SECRET", os.environ.get("SECRET_KEY", "agritech-jwt-secret"))
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = _get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)  # 24 hours
    refresh_token_expire_days: int = _get_int("REFRESH_TOKEN_EXPIRE_DAYS", 30)
    password_hash_rounds: int = _get_int("PASSWORD_HASH_ROUNDS", 12)


@dataclass(frozen=True)
class AIModelConfig:
    """AI Models & Inference Settings"""
    gemini_api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")
    gemini_model_id: str = os.environ.get("GEMINI_MODEL_ID", "gemini-2.5-flash")
    default_confidence_threshold: float = _get_float("DISEASE_CONFIDENCE_THRESHOLD", 75.0)
    max_image_upload_size_mb: int = _get_int("MAX_IMAGE_UPLOAD_SIZE_MB", 10)
    supported_image_types: List[str] = field(
        default_factory=lambda: ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    )


@dataclass(frozen=True)
class FeatureFlags:
    """System Feature Flags for Gradual Rollout & Environment Control"""
    enable_ai_disease_diagnosis: bool = _get_bool("ENABLE_AI_DISEASE", True)
    enable_prediction_comparison: bool = _get_bool("ENABLE_PREDICTION_COMPARISON", True)
    enable_seedling_classification: bool = _get_bool("ENABLE_SEEDLING_CLASSIFICATION", True)
    enable_weather_advisory: bool = _get_bool("ENABLE_WEATHER_ADVISORY", True)
    enable_spatial_analytics: bool = _get_bool("ENABLE_SPATIAL_ANALYTICS", True)
    enable_crop_recommendation: bool = _get_bool("ENABLE_CROP_RECOMMENDATION", True)
    enable_carbon_portal: bool = _get_bool("ENABLE_CARBON_PORTAL", True)
    enable_voice_input: bool = _get_bool("ENABLE_VOICE_INPUT", True)
    enable_offline_cache: bool = _get_bool("ENABLE_OFFLINE_CACHE", True)
    enable_rate_limiter: bool = _get_bool("ENABLE_RATE_LIMITER", True)
    enable_multilingual_support: bool = _get_bool("ENABLE_MULTILINGUAL_SUPPORT", True)


@dataclass(frozen=True)
class ServicesConfig:
    """External Services, Caching & Message Queues"""
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    cache_type: str = os.environ.get("CACHE_TYPE", "SimpleCache" if os.environ.get("FLASK_ENV") != "production" else "RedisCache")
    cache_default_timeout: int = _get_int("CACHE_DEFAULT_TIMEOUT", 3600)
    celery_broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    weather_api_key: Optional[str] = os.environ.get("WEATHER_API_KEY")
    weather_api_url: str = os.environ.get("WEATHER_API_URL", "https://api.weatherapi.com/v1")
    fx_api_url: str = os.environ.get("FX_API_URL", "https://api.exchangerate-api.com/v4/latest")
    google_translation_api_key: Optional[str] = os.environ.get("GOOGLE_TRANSLATION_API_KEY")


@dataclass(frozen=True)
class StorageConfig:
    """File Storage & Cloud Assets Configuration"""
    storage_type: str = os.environ.get("STORAGE_TYPE", "local").lower()  # 'local' or 's3'
    upload_folder: str = os.path.join(os.getcwd(), "uploads")
    max_content_length: int = _get_int("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)  # 10MB
    s3_bucket: Optional[str] = os.environ.get("S3_BUCKET")
    s3_access_key: Optional[str] = os.environ.get("S3_ACCESS_KEY")
    s3_secret_key: Optional[str] = os.environ.get("S3_SECRET_KEY")
    s3_region: str = os.environ.get("S3_REGION", "us-east-1")
    s3_endpoint_url: Optional[str] = os.environ.get("S3_ENDPOINT_URL")


@dataclass(frozen=True)
class FirebaseConfig:
    """Firebase Frontend & Backend Configuration"""
    api_key: Optional[str] = os.environ.get("FIREBASE_API_KEY")
    auth_domain: Optional[str] = os.environ.get("FIREBASE_AUTH_DOMAIN")
    project_id: Optional[str] = os.environ.get("FIREBASE_PROJECT_ID")
    storage_bucket: Optional[str] = os.environ.get("FIREBASE_STORAGE_BUCKET")
    messaging_sender_id: Optional[str] = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
    app_id: Optional[str] = os.environ.get("FIREBASE_APP_ID")
    measurement_id: Optional[str] = os.environ.get("FIREBASE_MEASUREMENT_ID")


@dataclass(frozen=True)
class MailConfig:
    """Mail Server Settings"""
    server: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    port: int = _get_int("MAIL_PORT", 587)
    use_tls: bool = _get_bool("MAIL_USE_TLS", True)
    username: Optional[str] = os.environ.get("MAIL_USERNAME")
    password: Optional[str] = os.environ.get("MAIL_PASSWORD")
    default_sender: Optional[str] = os.environ.get("MAIL_DEFAULT_SENDER")


@dataclass(frozen=True)
class Settings:
    """Master Typed Configuration Container"""
    app: AppConfig = field(default_factory=AppConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    ai: AIModelConfig = field(default_factory=AIModelConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    services: ServicesConfig = field(default_factory=ServicesConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    firebase: FirebaseConfig = field(default_factory=FirebaseConfig)
    mail: MailConfig = field(default_factory=MailConfig)

    def get_public_config(self) -> Dict[str, Any]:
        """
        Returns a sanitized, safe public dictionary of configurations and
        feature flags suitable for exposure to frontend clients via `/api/v1/config`.
        Never exposes secrets, database URLs, or private tokens.
        """
        return {
            "appName": self.app.app_name,
            "version": self.app.version,
            "env": self.app.env,
            "apiPrefix": self.app.api_prefix,
            "featureFlags": asdict(self.features),
            "ai": {
                "confidenceThreshold": self.ai.default_confidence_threshold,
                "maxUploadSizeMb": self.ai.max_image_upload_size_mb,
                "supportedImageTypes": self.ai.supported_image_types,
            },
            "firebase": {
                "apiKey": self.firebase.api_key or "",
                "authDomain": self.firebase.auth_domain or "",
                "projectId": self.firebase.project_id or "",
                "storageBucket": self.firebase.storage_bucket or "",
                "messagingSenderId": self.firebase.messaging_sender_id or "",
                "appId": self.firebase.app_id or "",
                "measurementId": self.firebase.measurement_id or "",
            },
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached singleton accessor for application settings.
    Guarantees consistent, type-safe configuration throughout application lifecycle.
    """
    return Settings()
