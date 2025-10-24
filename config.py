import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase 설정
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qhrfefcthrogwdwpxkby.supabase.co')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocmZlZmN0aHJvZ3dkd3B4a2J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4MTg1ODUsImV4cCI6MjA3NTM5NDU4NX0.Do9gajWdwgP8PFSlajAUhZHb024nfNZNnx1IJz9yR5k')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocmZlZmN0aHJvZ3dkd3B4a2J5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTgxODU4NSwiZXhwIjoyMDc1Mzk0NTg1fQ.wBg6ziXqViZHlXXfOryW12YbOpe54_cj5rD-4C1p7P8')
    
    # YouTube API 설정
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'AIzaSyBQ95Zj_awq6A7CrpXXo2eW6GIAcPShQ9Y')
    
    # Flask 설정
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
    
    # 다운로드 폴더
    DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', './downloads')
