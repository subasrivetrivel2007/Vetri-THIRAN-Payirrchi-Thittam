import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    app_name = os.getenv("APP_NAME", "PocketSmart AI")
    secret_key = os.getenv("APP_SECRET_KEY", "dev-only-change-this-secret")
    database_path = os.getenv("DATABASE_PATH", "./pocketsmart.db")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "5"))
settings = Settings()
