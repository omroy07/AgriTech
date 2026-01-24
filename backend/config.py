import os

class Config:
    """Base Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///agritech.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL_ID = 'gemini-2.5-flash'
    
    # Firebase
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET')
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID')
    FIREBASE_MEASUREMENT_ID = os.environ.get('FIREBASE_MEASUREMENT_ID')

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///agritech_dev.db')
    SQLALCHEMY_ECHO = True  # Log SQL queries in development

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Ensure critical keys are present
    @classmethod
    def init_app(cls, app):
        if not os.environ.get('GEMINI_API_KEY'):
            raise RuntimeError("GEMINI_API_KEY is not set in production!")
        if not os.environ.get('DATABASE_URL'):
            raise RuntimeError("DATABASE_URL is not set in production!")

class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for testing

# Configuration Dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
