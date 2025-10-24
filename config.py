import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # Supabase 설정
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qhrfefcthrogwdwpxkby.supabase.co')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocmZlZmN0aHJvZ3dkd3B4a2J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4MTg1ODUsImV4cCI6MjA3NTM5NDU4NX0.Do9gajWdwgP8PFSlajAUhZHb024nfNZNnx1IJz9yR5k')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFocmZlZmN0aHJvZ3dkd3B4a2J5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTgxODU4NSwiZXhwIjoyMDc1Mzk0NTg1fQ.wBg6ziXqViZHlXXfOryW12YbOpe54_cj5rD-4C1p7P8')
    
    # YouTube API 설정
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'AIzaSyA1v9qsqY3TLYrsjJngs6MHDBwnFvIURuA')
    
    # Flask 설정
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 다운로드 폴더 설정
    DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', r'C:\Faceon\video\down')
    
    # 데이터베이스 테이블명
    USERS_TABLE = 'users'
    DOWNLOAD_JOBS_TABLE = 'download_jobs'
    DOWNLOAD_HISTORY_TABLE = 'download_history'
