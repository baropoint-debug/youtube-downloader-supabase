"""
프로덕션 환경용 Flask 애플리케이션
외부 접속 가능한 유튜브 다운로더 서비스
"""
from flask import Flask, render_template, request, jsonify, make_response, session
from flask_cors import CORS
import yt_dlp
import os
import re
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
from config import Config
from supabase_client import supabase_manager
import logging
from functools import wraps

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# CORS 설정 (외부 접속 허용)
CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# 설정 로드
DOWNLOAD_FOLDER = Config.DOWNLOAD_FOLDER
YOUTUBE_API_KEY = Config.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# 요청 제한 데코레이터
def rate_limit(max_requests=100, window=3600):
    """API 요청 제한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 간단한 IP 기반 요청 제한 (실제로는 Redis 등을 사용하는 것이 좋음)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_youtube_service():
    """YouTube API 서비스 객체 생성"""
    try:
        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        logger.error(f"YouTube API 서비스 생성 오류: {e}")
        return None

# 채널 ID 캐시
channel_cache = {}

def get_channel_id_by_name(channel_name):
    """채널명으로 채널 ID를 찾기 (캐시 사용)"""
    if channel_name.lower() in channel_cache:
        cached_id = channel_cache[channel_name.lower()]
        logger.info(f"캐시에서 채널 ID 발견: {channel_name} -> {cached_id}")
        return cached_id
    
    try:
        youtube = get_youtube_service()
        if not youtube:
            return None
        
        search_response = youtube.search().list(
            q=channel_name,
            part="id,snippet",
            maxResults=5,
            type="channel"
        ).execute()
        
        logger.info(f"채널 검색 중: {channel_name}")
        
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#channel":
                channel_title = search_result["snippet"]["title"]
                channel_id = search_result["id"]["channelId"]
                logger.info(f"찾은 채널: {channel_title}")
                
                channel_cache[channel_title.lower()] = channel_id
                
                if channel_title.lower() == channel_name.lower():
                    logger.info(f"정확한 매칭 발견: {channel_title} -> {channel_id}")
                    return channel_id
        
        if search_response.get("items"):
            first_channel = search_response["items"][0]
            if first_channel["id"]["kind"] == "youtube#channel":
                channel_id = first_channel["id"]["channelId"]
                channel_title = first_channel["snippet"]["title"]
                logger.info(f"정확한 매칭 없음, 첫 번째 결과 사용: {channel_title} -> {channel_id}")
                return channel_id
        
        logger.warning(f"채널을 찾을 수 없음: {channel_name}")
        return None
        
    except Exception as e:
        logger.error(f"채널 ID 검색 오류: {e}")
        return None

def is_valid_youtube_url(url):
    """유튜브 URL이 유효한지 확인"""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False

def extract_video_id(url):
    """유튜브 URL에서 비디오 ID 추출"""
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'www.youtube.com' and parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def get_video_info_from_api(video_id):
    """YouTube Data API v3를 사용하여 비디오 정보 가져오기"""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return None
        
        video_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()
        
        if not video_response.get("items"):
            return None
        
        video = video_response["items"][0]
        snippet = video["snippet"]
        content_details = video["contentDetails"]
        
        duration_iso = content_details["duration"]
        duration_seconds = parse_duration(duration_iso)
        duration_formatted = format_duration(duration_seconds)
        
        return {
            'title': snippet["title"],
            'duration': duration_formatted,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'thumbnail': snippet["thumbnails"]["high"]["url"],
            'description': snippet["description"][:200] + "..." if len(snippet["description"]) > 200 else snippet["description"],
            'view_count': video.get("statistics", {}).get("viewCount", "0"),
            'upload_date': snippet["publishedAt"][:10],
            'channel_title': snippet["channelTitle"],
            'channel_id': snippet["channelId"],
            'like_count': video.get("statistics", {}).get("likeCount", "0"),
            'comment_count': video.get("statistics", {}).get("commentCount", "0")
        }
        
    except Exception as e:
        logger.error(f"비디오 정보 가져오기 오류: {e}")
        return None

def parse_duration(duration_iso):
    """ISO 8601 duration을 초 단위로 변환"""
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_iso)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def format_duration(seconds):
    """초를 HH:MM:SS 형식으로 변환"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def get_video_info(url):
    """유튜브 비디오 정보 가져오기 (API 우선, yt-dlp 백업)"""
    video_id = extract_video_id(url)
    if video_id:
        api_info = get_video_info_from_api(video_id)
        if api_info:
            return api_info
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown Title'),
                'duration': format_duration(info.get('duration', 0)),
                'url': url,
                'thumbnail': info.get('thumbnail', ''),
                'description': info.get('description', '')[:200] + "..." if info.get('description') and len(info.get('description', '')) > 200 else info.get('description', ''),
                'channel_title': info.get('uploader', 'Unknown Channel'),
                'view_count': str(info.get('view_count', 0)),
                'upload_date': info.get('upload_date', ''),
                'like_count': str(info.get('like_count', 0)),
                'comment_count': str(info.get('comment_count', 0))
            }
    except Exception as e:
        logger.error(f"yt-dlp 오류: {e}")
        return None

def download_video(url, output_path=None):
    """유튜브 비디오 다운로드 (yt-dlp 사용)"""
    if not output_path:
        output_path = DOWNLOAD_FOLDER
    
    os.makedirs(output_path, exist_ok=True)
    
    try:
        ydl_info_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            ext = info.get('ext', 'mp4')
            filename = f"{title}.{ext}"
            filepath = os.path.join(output_path, filename)
            
            if os.path.exists(filepath):
                return {'status': 'skipped', 'filename': filename, 'reason': 'File already exists', 'file_path': filepath}
    except Exception as e:
        logger.error(f"파일 정보 확인 오류: {e}")
    
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'best[ext=mp4]/best',
        'progress_hooks': [],
        'overwrites': False,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return {'status': 'success', 'filename': filename if 'filename' in locals() else 'Unknown', 'file_path': filepath if 'filepath' in locals() else None}
    except Exception as e:
        logger.error(f"다운로드 오류: {e}")
        return {'status': 'error', 'error': str(e)}

# ===== API 엔드포인트들 =====

@app.route('/')
def index():
    """메인 페이지"""
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/health', methods=['GET'])
def health_check():
    """시스템 상태 확인"""
    supabase_status = supabase_manager.is_connected()
    youtube_status = get_youtube_service() is not None
    
    return jsonify({
        'status': 'healthy' if supabase_status and youtube_status else 'degraded',
        'supabase': 'connected' if supabase_status else 'disconnected',
        'youtube_api': 'connected' if youtube_status else 'disconnected',
        'download_folder': DOWNLOAD_FOLDER,
        'folder_exists': os.path.exists(DOWNLOAD_FOLDER),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/register', methods=['POST'])
@rate_limit(max_requests=10, window=3600)
def register_user():
    """사용자 등록 API"""
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    
    if not email:
        return jsonify({'error': '이메일을 입력해주세요'}), 400
    
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    existing_user = supabase_manager.get_user_by_email(email)
    if existing_user:
        return jsonify({'error': '이미 등록된 이메일입니다'}), 400
    
    user_data = {
        'email': email,
        'name': name or email.split('@')[0]
    }
    user = supabase_manager.create_user(user_data)
    
    if user:
        return jsonify({
            'success': True,
            'user': user,
            'message': '사용자가 성공적으로 등록되었습니다'
        })
    else:
        return jsonify({'error': '사용자 등록에 실패했습니다'}), 500

@app.route('/api/user/login', methods=['POST'])
@rate_limit(max_requests=20, window=3600)
def login_user():
    """사용자 로그인 API"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': '이메일을 입력해주세요'}), 400
    
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    user = supabase_manager.get_user_by_email(email)
    if user:
        return jsonify({
            'success': True,
            'user': user,
            'message': '로그인 성공'
        })
    else:
        return jsonify({'error': '등록되지 않은 사용자입니다'}), 404

@app.route('/api/search', methods=['POST'])
@rate_limit(max_requests=50, window=3600)
def search_videos():
    """유튜브 비디오 검색 API"""
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': '검색어를 입력해주세요'}), 400
    
    if is_valid_youtube_url(query):
        # 단일 URL 처리
        video_info = get_video_info(query)
        if video_info:
            return jsonify({
                'results': [video_info],
                'total_results': 1
            })
        else:
            return jsonify({'error': '비디오 정보를 가져올 수 없습니다'}), 400
    
    # 검색어로 검색
    try:
        youtube = get_youtube_service()
        if not youtube:
            return jsonify({'error': 'YouTube API를 사용할 수 없습니다'}), 500
        
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=20,
            type="video"
        ).execute()
        
        results = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_id = search_result["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                video_info = get_video_info_from_api(video_id)
                if video_info:
                    results.append(video_info)
                else:
                    results.append({
                        'title': search_result["snippet"]["title"],
                        'duration': '00:00',
                        'url': video_url,
                        'thumbnail': search_result["snippet"]["thumbnails"]["medium"]["url"],
                        'description': search_result["snippet"]["description"][:100] + "...",
                        'channel_title': search_result["snippet"]["channelTitle"],
                        'view_count': '0',
                        'upload_date': search_result["snippet"]["publishedAt"][:10]
                    })
        
        return jsonify({
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        logger.error(f"검색 오류: {e}")
        return jsonify({'error': '검색 중 오류가 발생했습니다'}), 500

@app.route('/api/download', methods=['POST'])
@rate_limit(max_requests=10, window=3600)
def download_video_api():
    """비디오 다운로드 API"""
    data = request.get_json()
    urls = data.get('urls', [])
    user_id = data.get('user_id')
    
    if not urls:
        return jsonify({'error': '다운로드할 URL을 선택해주세요'}), 400
    
    success_count = 0
    failed_count = 0
    job_ids = []
    
    for url in urls:
        # Supabase에 다운로드 작업 기록
        job_id = None
        if user_id and supabase_manager.is_connected():
            video_info = get_video_info(url)
            job_data = {
                'user_id': user_id,
                'video_url': url,
                'video_id': extract_video_id(url),
                'status': 'pending',
                'video_title': video_info.get('title') if video_info else None,
                'video_thumbnail': video_info.get('thumbnail') if video_info else None,
                'channel_name': video_info.get('channel_title') if video_info else None,
                'video_duration': video_info.get('duration') if video_info else None,
                'video_description': video_info.get('description') if video_info else None
            }
            job = supabase_manager.create_download_job(job_data)
            if job:
                job_id = job['id']
                job_ids.append(job_id)
        
        # 실제 다운로드 수행
        result = download_video(url, DOWNLOAD_FOLDER)
        
        if isinstance(result, dict):
            if result['status'] == 'success':
                success_count += 1
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'completed',
                        'download_path': result.get('file_path'),
                        'file_size': os.path.getsize(result.get('file_path')) if result.get('file_path') and os.path.exists(result.get('file_path')) else None,
                        'file_format': 'mp4',
                        'completed_at': datetime.now().isoformat()
                    })
            elif result['status'] == 'skipped':
                success_count += 1
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'completed',
                        'download_path': result.get('file_path'),
                        'file_size': os.path.getsize(result.get('file_path')) if result.get('file_path') and os.path.exists(result.get('file_path')) else None,
                        'file_format': 'mp4',
                        'completed_at': datetime.now().isoformat()
                    })
            elif result['status'] == 'error':
                failed_count += 1
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'failed',
                        'error_message': result.get('error', 'Unknown error'),
                        'completed_at': datetime.now().isoformat()
                    })
        else:
            if result:
                success_count += 1
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'completed',
                        'completed_at': datetime.now().isoformat()
                    })
            else:
                failed_count += 1
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'failed',
                        'error_message': 'Download failed',
                        'completed_at': datetime.now().isoformat()
                    })
    
    return jsonify({
        'success_count': success_count,
        'failed_count': failed_count,
        'job_ids': job_ids,
        'message': f'{success_count}개 성공, {failed_count}개 실패'
    })

@app.route('/api/user/<user_id>/jobs', methods=['GET'])
def get_user_jobs(user_id):
    """사용자의 다운로드 작업 목록 조회"""
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    jobs = supabase_manager.get_user_download_jobs(user_id, limit, offset)
    return jsonify({'jobs': jobs})

@app.route('/api/user/<user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    """사용자의 즐겨찾기 목록 조회"""
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    favorites = supabase_manager.get_user_favorites(user_id)
    return jsonify({'favorites': favorites})

@app.route('/api/user/<user_id>/favorites', methods=['POST'])
def add_to_favorites(user_id):
    """즐겨찾기에 비디오 추가"""
    data = request.get_json()
    video_data = data.get('video')
    
    if not video_data:
        return jsonify({'error': '비디오 정보가 필요합니다'}), 400
    
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    favorite = supabase_manager.add_to_favorites(user_id, video_data)
    if favorite:
        return jsonify({
            'success': True,
            'favorite': favorite,
            'message': '즐겨찾기에 추가되었습니다'
        })
    else:
        return jsonify({'error': '즐겨찾기 추가에 실패했습니다'}), 500

@app.route('/api/user/<user_id>/favorites', methods=['DELETE'])
def remove_from_favorites(user_id):
    """즐겨찾기에서 비디오 제거"""
    data = request.get_json()
    video_url = data.get('video_url')
    
    if not video_url:
        return jsonify({'error': '비디오 URL이 필요합니다'}), 400
    
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    success = supabase_manager.remove_from_favorites(user_id, video_url)
    if success:
        return jsonify({
            'success': True,
            'message': '즐겨찾기에서 제거되었습니다'
        })
    else:
        return jsonify({'error': '즐겨찾기 제거에 실패했습니다'}), 500

if __name__ == '__main__':
    # 다운로드 폴더 생성
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    # Supabase 연결 상태 확인
    if supabase_manager.is_connected():
        logger.info("✅ Supabase 연결 성공")
    else:
        logger.warning("⚠️ Supabase 연결 실패 - 일부 기능이 제한될 수 있습니다.")
    
    # YouTube API 상태 확인
    if get_youtube_service():
        logger.info("✅ YouTube API 연결 성공")
    else:
        logger.warning("⚠️ YouTube API 연결 실패")
    
    logger.info(f"🚀 프로덕션 서버 시작")
    logger.info(f"📁 다운로드 폴더: {DOWNLOAD_FOLDER}")
    logger.info(f"🌐 서버 주소: http://0.0.0.0:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
