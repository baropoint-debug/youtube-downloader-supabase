"""
Supabase 클라이언트 설정 및 헬퍼 함수들
"""
from supabase import create_client, Client
from config import Config
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        """Supabase 클라이언트 초기화"""
        try:
            self.client: Client = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_ANON_KEY
            )
            logger.info("Supabase 클라이언트가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logger.error(f"Supabase 클라이언트 초기화 실패: {e}")
            self.client = None
    
    def is_connected(self):
        """Supabase 연결 상태 확인"""
        return self.client is not None
    
    def create_user(self, user_data):
        """새 사용자 생성"""
        try:
            result = self.client.table(Config.USERS_TABLE).insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"사용자 생성 실패: {e}")
            return None
    
    def get_user_by_email(self, email):
        """이메일로 사용자 조회"""
        try:
            result = self.client.table(Config.USERS_TABLE).select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"사용자 조회 실패: {e}")
            return None
    
    def create_download_job(self, job_data):
        """다운로드 작업 생성"""
        try:
            result = self.client.table(Config.DOWNLOAD_JOBS_TABLE).insert(job_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"다운로드 작업 생성 실패: {e}")
            return None
    
    def update_download_job(self, job_id, update_data):
        """다운로드 작업 업데이트"""
        try:
            result = self.client.table(Config.DOWNLOAD_JOBS_TABLE).update(update_data).eq("id", job_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"다운로드 작업 업데이트 실패: {e}")
            return None
    
    def get_user_download_jobs(self, user_id, limit=50, offset=0):
        """사용자의 다운로드 작업 목록 조회"""
        try:
            result = self.client.table(Config.DOWNLOAD_JOBS_TABLE)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .offset(offset)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"다운로드 작업 목록 조회 실패: {e}")
            return []
    
    def get_download_job(self, job_id):
        """특정 다운로드 작업 조회"""
        try:
            result = self.client.table(Config.DOWNLOAD_JOBS_TABLE).select("*").eq("id", job_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"다운로드 작업 조회 실패: {e}")
            return None
    
    def create_download_history(self, history_data):
        """다운로드 히스토리 생성"""
        try:
            result = self.client.table(Config.DOWNLOAD_HISTORY_TABLE).insert(history_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"다운로드 히스토리 생성 실패: {e}")
            return None
    
    def get_user_download_history(self, user_id, limit=50, offset=0):
        """사용자의 다운로드 히스토리 조회"""
        try:
            result = self.client.table(Config.DOWNLOAD_HISTORY_TABLE)\
                .select("*, download_jobs(*)")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .offset(offset)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"다운로드 히스토리 조회 실패: {e}")
            return []
    
    def add_to_favorites(self, user_id, video_data):
        """즐겨찾기에 비디오 추가"""
        try:
            favorite_data = {
                "user_id": user_id,
                "video_url": video_data.get("url"),
                "video_title": video_data.get("title"),
                "video_thumbnail": video_data.get("thumbnail"),
                "channel_name": video_data.get("channel_title")
            }
            result = self.client.table("user_favorites").insert(favorite_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"즐겨찾기 추가 실패: {e}")
            return None
    
    def get_user_favorites(self, user_id):
        """사용자의 즐겨찾기 목록 조회"""
        try:
            result = self.client.table("user_favorites")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"즐겨찾기 목록 조회 실패: {e}")
            return []
    
    def remove_from_favorites(self, user_id, video_url):
        """즐겨찾기에서 비디오 제거"""
        try:
            result = self.client.table("user_favorites")\
                .delete()\
                .eq("user_id", user_id)\
                .eq("video_url", video_url)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"즐겨찾기 제거 실패: {e}")
            return False

# 전역 Supabase 매니저 인스턴스
supabase_manager = SupabaseManager()

