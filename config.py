import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Konfigurasi Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-rahasia-ganti-di-produksi')
    
    # Konfigurasi Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfigurasi Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    VIDEOS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'videos')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max untuk upload foto profil
    
    # Konfigurasi Google Drive
    GOOGLE_DRIVE_API_KEY = os.getenv('GOOGLE_DRIVE_API_KEY')
    
    # Konfigurasi Streaming
    FACEBOOK_STREAM_URL = os.getenv('FACEBOOK_STREAM_URL')
    YOUTUBE_STREAM_URL = os.getenv('YOUTUBE_STREAM_URL')
    
    # Pastikan direktori upload ada
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.VIDEOS_FOLDER, exist_ok=True)