import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase 설정
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'your-anon-key')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'your-service-role-key')
    
    # YouTube API 설정
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'your-youtube-api-key')
    
    # Flask 설정
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')
    
    # 다운로드 폴더
    DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', './downloads')
