from flask import Flask, render_template, request, jsonify, make_response
import yt_dlp
import os
import re
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import uuid
from config import Config
from supabase_client import supabase_manager

app = Flask(__name__)

# 템플릿 자동 리로드 강제 활성화
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# 설정 로드
DOWNLOAD_FOLDER = Config.DOWNLOAD_FOLDER
YOUTUBE_API_KEY = Config.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_youtube_service():
    """YouTube API 서비스 객체 생성"""
    try:
        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        print(f"YouTube API 서비스 생성 오류: {e}")
        return None

# 채널 ID 캐시
channel_cache = {}

def get_channel_id_by_name(channel_name):
    """채널명으로 채널 ID를 찾기 (캐시 사용)"""
    # 캐시에서 먼저 확인
    if channel_name.lower() in channel_cache:
        cached_id = channel_cache[channel_name.lower()]
        print(f"캐시에서 채널 ID 발견: {channel_name} -> {cached_id}")
        return cached_id
    
    try:
        youtube = get_youtube_service()
        if not youtube:
            return None
        
        # 채널 검색 (더 많은 결과를 가져와서 정확한 매칭 찾기)
        search_response = youtube.search().list(
            q=channel_name,
            part="id,snippet",
            maxResults=5,  # 할당량 절약을 위해 5개로 줄임
            type="channel"
        ).execute()
        
        print(f"채널 검색 중: {channel_name}")
        
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#channel":
                channel_title = search_result["snippet"]["title"]
                channel_id = search_result["id"]["channelId"]
                print(f"찾은 채널: {channel_title}")
                
                # 캐시에 저장
                channel_cache[channel_title.lower()] = channel_id
                
                # 채널명이 정확히 일치하는지 확인 (대소문자 무시)
                if channel_title.lower() == channel_name.lower():
                    print(f"정확한 매칭 발견: {channel_title} -> {channel_id}")
                    return channel_id
        
        # 정확한 매칭을 찾지 못한 경우, 첫 번째 결과 반환
        if search_response.get("items"):
            first_channel = search_response["items"][0]
            if first_channel["id"]["kind"] == "youtube#channel":
                channel_id = first_channel["id"]["channelId"]
                channel_title = first_channel["snippet"]["title"]
                print(f"정확한 매칭 없음, 첫 번째 결과 사용: {channel_title} -> {channel_id}")
                return channel_id
        
        print(f"채널을 찾을 수 없음: {channel_name}")
        return None
        
    except Exception as e:
        print(f"채널 ID 검색 오류: {e}")
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

def search_youtube_api(query, max_results=10, page_token=None, sort_by='relevance', channel_filter=None, creative_commons=False, duration_filters=None):
    """YouTube Data API v3를 사용한 실제 검색"""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return search_youtube_mock(query)
        
        # 정렬 옵션 설정
        order = 'relevance'  # 기본값
        if sort_by == 'date':
            order = 'date'
        elif sort_by == 'rating':
            order = 'rating'
        elif sort_by == 'viewCount':
            order = 'viewCount'
        elif sort_by == 'title':
            order = 'title'
        
        # 채널 필터가 있으면 채널 ID로 검색
        search_query = query
        channel_id = None
        use_channel_filter = False
        
        if channel_filter:
            # 먼저 채널명으로 채널 ID를 찾기
            channel_id = get_channel_id_by_name(channel_filter)
            if channel_id:
                # 채널 ID가 있으면 해당 채널의 비디오만 검색
                if query:
                    search_query = f"{query} channel:{channel_id}"
                else:
                    # 검색어가 없으면 채널 이름만으로 검색
                    search_query = channel_filter
                use_channel_filter = True
                print(f"채널 필터 적용: {channel_filter} -> {channel_id}")
                print(f"검색 쿼리: {search_query}")
            else:
                # 채널 ID를 찾지 못한 경우 일반 검색 후 필터링
                if query:
                    search_query = query
                else:
                    search_query = channel_filter
                use_channel_filter = True
                print(f"채널 ID를 찾지 못함, 일반 검색 후 필터링: {channel_filter}")
        
        # 크리에이티브 커먼즈 필터는 별도 파라미터로 처리
        if creative_commons:
            print(f"크리에이티브 커먼즈 필터 적용")
        
        # 검색 요청
        search_params = {
            'q': search_query,
            'part': "id,snippet",
            'maxResults': max_results,
            'type': "video",
            'order': order
        }
        
        # 채널 ID가 있으면 channelId 파라미터로 직접 지정
        if channel_id:
            search_params['channelId'] = channel_id
            print(f"channelId 파라미터 추가: {channel_id}")
        
        # 크리에이티브 커먼즈 라이선스 필터 적용
        if creative_commons:
            search_params['videoLicense'] = 'creativeCommon'
            print(f"videoLicense 파라미터 추가: creativeCommon")
        
        # 다중 duration 필터 처리
        if duration_filters and len(duration_filters) > 0:
            print(f"비디오 길이 필터 적용: {duration_filters}")
            all_results = []
            seen_video_ids = set()
            
            # 각 duration 필터별로 검색 수행
            for duration_filter in duration_filters:
                duration_search_params = search_params.copy()
                duration_search_params['videoDuration'] = duration_filter
                duration_search_params['maxResults'] = max_results // len(duration_filters) + 10  # 각 필터당 적절한 결과 수
                
                # 크리에이티브 커먼즈 라이선스 필터도 각 검색에 적용
                if creative_commons:
                    duration_search_params['videoLicense'] = 'creativeCommon'
                
                if page_token:
                    duration_search_params['pageToken'] = page_token
                
                print(f"길이 필터 '{duration_filter}' 검색 중...")
                duration_response = youtube.search().list(**duration_search_params).execute()
                
                # 결과를 all_results에 추가 (중복 제거)
                for item in duration_response.get("items", []):
                    if item["id"]["kind"] == "youtube#video":
                        video_id = item["id"]["videoId"]
                        if video_id not in seen_video_ids:
                            seen_video_ids.add(video_id)
                            all_results.append(item)
            
            # 결과를 max_results만큼 제한
            search_results = all_results[:max_results]
            search_response = {
                "items": search_results,
                "nextPageToken": duration_response.get('nextPageToken') if duration_response else None,
                "prevPageToken": duration_response.get('prevPageToken') if duration_response else None,
                "pageInfo": {"totalResults": len(all_results)}
            }
        else:
            # duration 필터가 없는 경우 일반 검색
            if page_token:
                search_params['pageToken'] = page_token
            
            search_response = youtube.search().list(**search_params).execute()
        
        results = []
        total_videos = 0
        filtered_videos = 0
        
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                total_videos += 1
                video_id = search_result["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_channel_id = search_result["snippet"]["channelId"]
                video_channel_title = search_result["snippet"]["channelTitle"]
                
                print(f"비디오: {search_result['snippet']['title']}")
                print(f"채널: {video_channel_title} (ID: {video_channel_id})")
                
                # 채널 필터가 있으면 채널 확인
                if use_channel_filter:
                    print(f"채널 필터 확인 중: '{channel_filter}' vs '{video_channel_title}'")
                    
                    if channel_id:
                        # 채널 ID로 정확한 매칭 확인
                        print(f"채널 ID 비교: {video_channel_id} vs {channel_id}")
                        if video_channel_id != channel_id:
                            print(f"채널 불일치로 스킵: {video_channel_id} != {channel_id}")
                            continue  # 다른 채널의 비디오는 스킵
                        else:
                            print(f"채널 일치: {video_channel_id} == {channel_id}")
                    else:
                        # 채널 ID가 없으면 채널명으로 확인 (정확한 매칭)
                        print(f"채널명 비교: '{channel_filter.lower()}' vs '{video_channel_title.lower()}'")
                        # 정확한 매칭만 허용 (TED는 정확히 TED여야 함)
                        if channel_filter.lower() != video_channel_title.lower():
                            print(f"채널명 불일치로 스킵: '{channel_filter}' != '{video_channel_title}'")
                            continue
                        else:
                            print(f"채널명 일치: '{channel_filter}' == '{video_channel_title}'")
                    
                    print(f"비디오 통과: {search_result['snippet']['title']}")
                
                filtered_videos += 1
                
                # 비디오 상세 정보 가져오기
                video_info = get_video_info_from_api(video_id)
                if video_info:
                    results.append(video_info)
                else:
                    # 기본 정보만 사용
                    results.append({
                        'title': search_result["snippet"]["title"],
                        'duration': '00:00',  # API에서 직접 제공하지 않음
                        'url': video_url,
                        'thumbnail': search_result["snippet"]["thumbnails"]["medium"]["url"],
                        'description': search_result["snippet"]["description"][:100] + "...",
                        'channel_title': search_result["snippet"]["channelTitle"],
                        'view_count': '0',
                        'upload_date': search_result["snippet"]["publishedAt"][:10]
                    })
        
        print(f"총 비디오: {total_videos}, 필터링 후: {filtered_videos}, 결과: {len(results)}")
        
        # 페이지네이션 정보 추가
        next_page_token = search_response.get('nextPageToken')
        prev_page_token = search_response.get('prevPageToken')
        
        return {
            'results': results,
            'next_page_token': next_page_token,
            'prev_page_token': prev_page_token,
            'total_results': search_response.get('pageInfo', {}).get('totalResults', 0)
        }
        
    except HttpError as e:
        print(f"YouTube API 오류: {e}")
        return search_youtube_mock(query)
    except Exception as e:
        print(f"검색 오류: {e}")
        return search_youtube_mock(query)

def get_video_info_from_api(video_id):
    """YouTube Data API v3를 사용하여 비디오 정보 가져오기"""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return None
        
        # 비디오 상세 정보 요청
        video_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()
        
        if not video_response.get("items"):
            return None
        
        video = video_response["items"][0]
        snippet = video["snippet"]
        content_details = video["contentDetails"]
        
        # ISO 8601 형식의 duration을 초 단위로 변환
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
        print(f"비디오 정보 가져오기 오류: {e}")
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

def search_youtube_mock(query):
    """YouTube API 실패 시 사용할 mock 데이터"""
    mock_results = [
        {
            'title': f'검색 결과 1: {query}',
            'duration': '10:30',
            'url': f'https://www.youtube.com/watch?v=sample1',
            'thumbnail': 'https://via.placeholder.com/120x90',
            'channel_title': '채널명 1',
            'view_count': '1,234,567',
            'upload_date': '2024-01-15',
            'like_count': '12,345',
            'comment_count': '1,234'
        },
        {
            'title': f'검색 결과 2: {query}',
            'duration': '5:15',
            'url': f'https://www.youtube.com/watch?v=sample2',
            'thumbnail': 'https://via.placeholder.com/120x90',
            'channel_title': '채널명 2',
            'view_count': '987,654',
            'upload_date': '2024-01-10',
            'like_count': '8,765',
            'comment_count': '987'
        },
        {
            'title': f'검색 결과 3: {query}',
            'duration': '15:45',
            'url': f'https://www.youtube.com/watch?v=sample3',
            'thumbnail': 'https://via.placeholder.com/120x90',
            'channel_title': '채널명 3',
            'view_count': '2,345,678',
            'upload_date': '2024-01-20',
            'like_count': '23,456',
            'comment_count': '2,345'
        }
    ]
    return {
        'results': mock_results,
        'next_page_token': None,
        'prev_page_token': None,
        'total_results': len(mock_results)
    }

def get_video_info(url):
    """유튜브 비디오 정보 가져오기 (API 우선, yt-dlp 백업)"""
    # 먼저 YouTube Data API로 시도
    video_id = extract_video_id(url)
    if video_id:
        api_info = get_video_info_from_api(video_id)
        if api_info:
            return api_info
    
    # API 실패 시 yt-dlp로 시도 (백업)
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
        print(f"yt-dlp 오류: {e}")
        return None

def download_video(url, output_path=None):
    """유튜브 비디오 다운로드 (yt-dlp 사용)"""
    if not output_path:
        output_path = DOWNLOAD_FOLDER
    
    # 다운로드 폴더가 존재하지 않으면 생성
    os.makedirs(output_path, exist_ok=True)
    
    # 먼저 파일명을 미리 확인하여 중복 체크
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
            
            # 파일이 이미 존재하는지 확인
            if os.path.exists(filepath):
                return {'status': 'skipped', 'filename': filename, 'reason': 'File already exists'}
    except Exception as e:
        print(f"파일 정보 확인 오류: {e}")
        # 정보 확인 실패 시 그냥 다운로드 시도
    
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'best[ext=mp4]/best',
        'progress_hooks': [],
        'overwrites': False,  # 동일한 파일명이 있으면 스킵
        'no_warnings': True,  # 스킵 경고 메시지 비활성화
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return {'status': 'success', 'filename': filename if 'filename' in locals() else 'Unknown'}
    except Exception as e:
        print(f"다운로드 오류: {e}")
        return {'status': 'error', 'error': str(e)}

@app.route('/')
def index():
    """메인 페이지"""
    response = make_response(render_template('index_test.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/search', methods=['POST'])
def search():
    """유튜브 검색 API"""
    data = request.get_json()
    query = data.get('query', '').strip()
    page_token = data.get('page_token', None)
    sort_by = data.get('sort_by', 'relevance')
    max_results = data.get('max_results', 50)  # 기본 50개
    channel_filter = data.get('channel_filter', None)
    creative_commons = data.get('creative_commons', False)
    duration_filters = data.get('duration_filters', [])
    
    if not query and not channel_filter:
        return jsonify({'error': '검색어를 입력하거나 채널을 선택해주세요'}), 400
    
    # URL인지 검색어인지 확인
    if query and is_valid_youtube_url(query):
        # 단일 URL 처리
        video_info = get_video_info(query)
        if video_info:
            results = {
                'results': [video_info],
                'next_page_token': None,
                'prev_page_token': None,
                'total_results': 1
            }
        else:
            results = {
                'results': [],
                'next_page_token': None,
                'prev_page_token': None,
                'total_results': 0
            }
    else:
        # 검색어 또는 채널 필터로 검색 (YouTube Data API v3 사용)
        results = search_youtube_api(query or '', max_results, page_token, sort_by, channel_filter, creative_commons, duration_filters)
    
    return jsonify(results)

@app.route('/download', methods=['POST'])
def download():
    """비디오 다운로드 API (Supabase 연동)"""
    data = request.get_json()
    urls = data.get('urls', [])
    download_folder = data.get('download_folder', DOWNLOAD_FOLDER)
    user_id = data.get('user_id')  # 사용자 ID (선택사항)
    
    if not urls:
        return jsonify({'error': '다운로드할 URL을 선택해주세요'}), 400
    
    # 다운로드 폴더 유효성 검사
    if not os.path.isabs(download_folder):
        # 상대 경로인 경우 현재 프로젝트 폴더 기준으로 절대 경로로 변환
        download_folder = os.path.join(os.getcwd(), download_folder)
    
    # 폴더 생성 시도
    try:
        os.makedirs(download_folder, exist_ok=True)
    except Exception as e:
        return jsonify({'error': f'다운로드 폴더를 생성할 수 없습니다: {str(e)}'}), 400
    
    success_count = 0
    skipped_count = 0
    failed_count = 0
    failed_urls = []
    skipped_files = []
    job_ids = []
    
    for url in urls:
        # Supabase에 다운로드 작업 기록 (사용자 ID가 있는 경우)
        job_id = None
        if user_id and supabase_manager.is_connected():
            # 비디오 정보 먼저 가져오기
            video_info = get_video_info(url)
            job_data = {
                'user_id': user_id,
                'video_url': url,
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
        result = download_video(url, download_folder)
        
        if isinstance(result, dict):
            if result['status'] == 'success':
                success_count += 1
                # Supabase 작업 상태 업데이트
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'completed',
                        'download_path': result.get('file_path'),
                        'file_size': result.get('file_size'),
                        'file_format': result.get('file_format'),
                        'completed_at': datetime.now().isoformat()
                    })
            elif result['status'] == 'skipped':
                skipped_count += 1
                skipped_files.append({
                    'url': url,
                    'filename': result.get('filename', 'Unknown'),
                    'reason': result.get('reason', 'File already exists')
                })
                # Supabase 작업 상태 업데이트
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'completed',
                        'download_path': result.get('file_path'),
                        'file_size': result.get('file_size'),
                        'file_format': result.get('file_format'),
                        'completed_at': datetime.now().isoformat()
                    })
            elif result['status'] == 'error':
                failed_count += 1
                failed_urls.append({
                    'url': url,
                    'error': result.get('error', 'Unknown error')
                })
                # Supabase 작업 상태 업데이트
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'failed',
                        'error_message': result.get('error', 'Unknown error'),
                        'completed_at': datetime.now().isoformat()
                    })
        else:
            # 이전 버전 호환성
            if result:
                success_count += 1
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'completed',
                        'completed_at': datetime.now().isoformat()
                    })
            else:
                failed_count += 1
                failed_urls.append({'url': url, 'error': 'Download failed'})
                if job_id and supabase_manager.is_connected():
                    supabase_manager.update_download_job(job_id, {
                        'status': 'failed',
                        'error_message': 'Download failed',
                        'completed_at': datetime.now().isoformat()
                    })
    
    # 결과 메시지 생성
    messages = []
    if success_count > 0:
        messages.append(f'{success_count}개 비디오가 성공적으로 다운로드되었습니다')
    if skipped_count > 0:
        messages.append(f'{skipped_count}개 파일이 이미 존재하여 스킵되었습니다')
    if failed_count > 0:
        messages.append(f'{failed_count}개 비디오 다운로드에 실패했습니다')
    
    message = '. '.join(messages) + f' (저장 위치: {download_folder})'
    
    return jsonify({
        'success_count': success_count,
        'skipped_count': skipped_count,
        'failed_count': failed_count,
        'failed_urls': failed_urls,
        'skipped_files': skipped_files,
        'download_folder': download_folder,
        'message': message,
        'job_ids': job_ids
    })

@app.route('/video_info', methods=['POST'])
def video_info():
    """비디오 정보 가져오기 API"""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL을 입력해주세요'}), 400
    
    if not is_valid_youtube_url(url):
        return jsonify({'error': '유효한 유튜브 URL이 아닙니다'}), 400
    
    video_info = get_video_info(url)
    if video_info:
        return jsonify({'video': video_info})
    else:
        return jsonify({'error': '비디오 정보를 가져올 수 없습니다'}), 400

@app.route('/download_folders', methods=['GET'])
def get_download_folders():
    """사용 가능한 다운로드 폴더 목록 반환"""
    import os
    import platform
    
    # 기본 폴더들
    folders = [
        {
            'name': '기본 다운로드 폴더',
            'path': DOWNLOAD_FOLDER,
            'type': 'default'
        }
    ]
    
    # 시스템별 기본 다운로드 폴더들
    system = platform.system()
    if system == "Windows":
        user_home = os.path.expanduser("~")
        folders.extend([
            {
                'name': '바탕화면',
                'path': os.path.join(user_home, 'Desktop'),
                'type': 'system'
            },
            {
                'name': '다운로드 폴더',
                'path': os.path.join(user_home, 'Downloads'),
                'type': 'system'
            },
            {
                'name': '문서',
                'path': os.path.join(user_home, 'Documents'),
                'type': 'system'
            }
        ])
    elif system == "Darwin":  # macOS
        user_home = os.path.expanduser("~")
        folders.extend([
            {
                'name': '바탕화면',
                'path': os.path.join(user_home, 'Desktop'),
                'type': 'system'
            },
            {
                'name': '다운로드 폴더',
                'path': os.path.join(user_home, 'Downloads'),
                'type': 'system'
            },
            {
                'name': '문서',
                'path': os.path.join(user_home, 'Documents'),
                'type': 'system'
            }
        ])
    elif system == "Linux":
        user_home = os.path.expanduser("~")
        folders.extend([
            {
                'name': '바탕화면',
                'path': os.path.join(user_home, 'Desktop'),
                'type': 'system'
            },
            {
                'name': '다운로드 폴더',
                'path': os.path.join(user_home, 'Downloads'),
                'type': 'system'
            },
            {
                'name': '문서',
                'path': os.path.join(user_home, 'Documents'),
                'type': 'system'
            }
        ])
    
    # 현재 프로젝트 내 폴더들도 추가
    project_folders = [
        'downloads',
        'videos',
        'youtube_downloads',
        'media'
    ]
    
    for folder_name in project_folders:
        folder_path = os.path.join(os.getcwd(), folder_name)
        folders.append({
            'name': f'프로젝트/{folder_name}',
            'path': folder_path,
            'type': 'project'
        })
    
    return jsonify({'folders': folders})

@app.route('/search_channels', methods=['POST'])
def search_channels():
    """채널명 검색 API (자동완성용)"""
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'channels': []})
    
    try:
        youtube = get_youtube_service()
        if not youtube:
            return jsonify({'channels': []})
        
        # 채널 검색
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=10,
            type="channel"
        ).execute()
        
        channels = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#channel":
                channel_title = search_result["snippet"]["title"]
                # 정확한 매칭을 위해 채널명에 정확도 점수 추가
                is_exact_match = channel_title.lower() == query.lower()
                
                channels.append({
                    'channel_id': search_result["id"]["channelId"],
                    'channel_title': channel_title,
                    'description': search_result["snippet"]["description"][:100] + "..." if len(search_result["snippet"]["description"]) > 100 else search_result["snippet"]["description"],
                    'thumbnail': search_result["snippet"]["thumbnails"]["default"]["url"],
                    'exact_match': is_exact_match
                })
        
        # 정확한 매칭이 있는 경우 우선순위로 정렬
        channels.sort(key=lambda x: (not x['exact_match'], x['channel_title']))
        
        return jsonify({'channels': channels})
        
    except Exception as e:
        print(f"채널 검색 오류: {e}")
        return jsonify({'channels': []})

@app.route('/test_folder', methods=['POST'])
def test_folder():
    """폴더 경로 유효성 테스트 API"""
    data = request.get_json()
    folder_path = data.get('folder_path', '').strip()
    
    if not folder_path:
        return jsonify({'success': False, 'error': '폴더 경로를 입력해주세요'}), 400
    
    try:
        # 절대 경로로 변환
        if not os.path.isabs(folder_path):
            folder_path = os.path.join(os.getcwd(), folder_path)
        
        # 폴더 생성 시도
        os.makedirs(folder_path, exist_ok=True)
        
        # 폴더가 실제로 존재하는지 확인
        if os.path.isdir(folder_path):
            return jsonify({
                'success': True, 
                'folder_path': folder_path,
                'message': '폴더가 유효합니다'
            })
        else:
            return jsonify({'success': False, 'error': '폴더를 생성할 수 없습니다'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'폴더 오류: {str(e)}'}), 400

# ===== Supabase 연동 API 엔드포인트들 =====

@app.route('/api/user/register', methods=['POST'])
def register_user():
    """사용자 등록 API"""
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    
    if not email:
        return jsonify({'error': '이메일을 입력해주세요'}), 400
    
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    # 기존 사용자 확인
    existing_user = supabase_manager.get_user_by_email(email)
    if existing_user:
        return jsonify({'error': '이미 등록된 이메일입니다'}), 400
    
    # 새 사용자 생성
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

@app.route('/api/user/<user_id>/jobs', methods=['GET'])
def get_user_jobs(user_id):
    """사용자의 다운로드 작업 목록 조회"""
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    jobs = supabase_manager.get_user_download_jobs(user_id, limit, offset)
    return jsonify({'jobs': jobs})

@app.route('/api/user/<user_id>/history', methods=['GET'])
def get_user_history(user_id):
    """사용자의 다운로드 히스토리 조회"""
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    history = supabase_manager.get_user_download_history(user_id, limit, offset)
    return jsonify({'history': history})

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

@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """다운로드 작업 상태 조회"""
    if not supabase_manager.is_connected():
        return jsonify({'error': '데이터베이스 연결이 없습니다'}), 500
    
    job = supabase_manager.get_download_job(job_id)
    if job:
        return jsonify({'job': job})
    else:
        return jsonify({'error': '작업을 찾을 수 없습니다'}), 404

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
        'folder_exists': os.path.exists(DOWNLOAD_FOLDER)
    })

if __name__ == '__main__':
    # 다운로드 폴더가 없으면 생성
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    # Supabase 연결 상태 확인
    if supabase_manager.is_connected():
        print("✅ Supabase 연결 성공")
    else:
        print("⚠️  경고: Supabase 연결 실패 - 일부 기능이 제한될 수 있습니다.")
        print("   config.py 파일에서 Supabase 설정을 확인하세요.")
    
    # API 키 확인
    if YOUTUBE_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  경고: YouTube Data API 키가 설정되지 않았습니다.")
        print("   app.py 파일에서 YOUTUBE_API_KEY 변수를 실제 API 키로 교체하세요.")
        print("   API 키 없이도 mock 데이터로 검색은 가능하지만, 실제 YouTube 검색은 작동하지 않습니다.")
    
    print(f"Flask 앱이 시작되었습니다.")
    print(f"다운로드 폴더: {DOWNLOAD_FOLDER}")
    print(f"웹 브라우저에서 http://localhost:5001 으로 접속하세요.")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
