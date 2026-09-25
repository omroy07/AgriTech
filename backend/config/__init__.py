import os
from .settings import get_settings, Settings

_settings = get_settings()

class Config:
    """Base Configuration mapped from typed Settings"""
    SECRET_KEY = _settings.app.secret_key
    DEBUG = _settings.app.debug
    TESTING = _settings.app.testing
    
    # Database
    SQLALCHEMY_DATABASE_URI = _settings.database.url
    SQLALCHEMY_TRACK_MODIFICATIONS = _settings.database.track_modifications
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": _settings.database.pool_size,
        "max_overflow": _settings.database.max_overflow,
        "pool_recycle": _settings.database.pool_recycle,
    } if not _settings.database.url.startswith("sqlite") else {}

    # Mail
    MAIL_SERVER = _settings.mail.server
    MAIL_PORT = _settings.mail.port
    MAIL_USE_TLS = _settings.mail.use_tls
    MAIL_USERNAME = _settings.mail.username
    MAIL_PASSWORD = _settings.mail.password
    MAIL_DEFAULT_SENDER = _settings.mail.default_sender

    # Storage Configuration
    STORAGE_TYPE = _settings.storage.storage_type
    UPLOAD_FOLDER = _settings.storage.upload_folder
    MAX_CONTENT_LENGTH = _settings.storage.max_content_length
    
    # S3 Settings
    S3_BUCKET = _settings.storage.s3_bucket
    S3_ACCESS_KEY = _settings.storage.s3_access_key
    S3_SECRET_KEY = _settings.storage.s3_secret_key
    S3_REGION = _settings.storage.s3_region
    S3_ENDPOINT_URL = _settings.storage.s3_endpoint_url
    
    # Gemini API
    GEMINI_API_KEY = _settings.ai.gemini_api_key
    GEMINI_MODEL_ID = _settings.ai.gemini_model_id
    
    # Weather API
    WEATHER_API_KEY = _settings.services.weather_api_key
    WEATHER_API_URL = _settings.services.weather_api_url
    
    # Firebase
    FIREBASE_API_KEY = _settings.firebase.api_key
    FIREBASE_AUTH_DOMAIN = _settings.firebase.auth_domain
    FIREBASE_PROJECT_ID = _settings.firebase.project_id
    FIREBASE_STORAGE_BUCKET = _settings.firebase.storage_bucket
    FIREBASE_MESSAGING_SENDER_ID = _settings.firebase.messaging_sender_id
    FIREBASE_APP_ID = _settings.firebase.app_id
    FIREBASE_MEASUREMENT_ID = _settings.firebase.measurement_id

    # Redis & Caching
    REDIS_URL = _settings.services.redis_url
    CACHE_TYPE = _settings.services.cache_type
    CACHE_REDIS_URL = _settings.services.redis_url
    CACHE_DEFAULT_TIMEOUT = _settings.services.cache_default_timeout


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _settings.database.dev_url or 'sqlite:///agritech_dev.db'
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        pass


class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def validate_required_config(app):
    """
    Validates required configuration keys at startup.
    Fails fast with ValueError if critical keys like GEMINI_API_KEY are missing.
    """
    if not app.config.get('TESTING'):
        gemini_key = app.config.get('GEMINI_API_KEY')
        if not gemini_key or not str(gemini_key).strip():
            raise ValueError(
                "CRITICAL STARTUP ERROR: GEMINI_API_KEY is missing or empty. "
                "The AgriTech backend requires a valid GEMINI_API_KEY to initialize AI services. "
                "Please configure GEMINI_API_KEY in your .env file or environment variables before starting the server."
            )
