import os

class Config:
    ENV = os.getenv("ENV", "development")

    API_URL = os.getenv("API_URL", "http://localhost:5000")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    MODEL_PATH = os.getenv("MODEL_PATH", "models/crop_model.pkl")