#!/usr/bin/env python3
"""
Supabase 연결 테스트 스크립트
"""
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
    from supabase_client import supabase_manager
    print("✅ 모듈 import 성공")
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    sys.exit(1)

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print("\n🔍 Supabase 연결 테스트 중...")
    
    if not supabase_manager.is_connected():
        print("❌ Supabase 연결 실패")
        print("   config.py 파일에서 Supabase 설정을 확인하세요.")
        return False
    
    print("✅ Supabase 연결 성공")
    return True

def test_config():
    """설정 파일 테스트"""
    print("\n🔍 설정 파일 테스트 중...")
    
    if Config.SUPABASE_URL == "your-supabase-url-here":
        print("❌ Supabase URL이 설정되지 않았습니다")
        return False
    
    if Config.SUPABASE_ANON_KEY == "your-supabase-anon-key-here":
        print("❌ Supabase Anon Key가 설정되지 않았습니다")
        return False
    
    print("✅ 설정 파일 검증 완료")
    return True

def test_database_tables():
    """데이터베이스 테이블 테스트"""
    print("\n🔍 데이터베이스 테이블 테스트 중...")
    
    try:
        # 사용자 테이블 테스트
        result = supabase_manager.client.table('users').select('id').limit(1).execute()
        print("✅ users 테이블 접근 성공")
        
        # 다운로드 작업 테이블 테스트
        result = supabase_manager.client.table('download_jobs').select('id').limit(1).execute()
        print("✅ download_jobs 테이블 접근 성공")
        
        # 다운로드 히스토리 테이블 테스트
        result = supabase_manager.client.table('download_history').select('id').limit(1).execute()
        print("✅ download_history 테이블 접근 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 테이블 테스트 실패: {e}")
        return False

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n🔍 API 엔드포인트 테스트 중...")
    
    try:
        import requests
        
        # 헬스 체크 엔드포인트 테스트
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ /api/health 엔드포인트 응답 성공")
            data = response.json()
            print(f"   시스템 상태: {data.get('status')}")
            print(f"   Supabase 상태: {data.get('supabase')}")
            print(f"   YouTube API 상태: {data.get('youtube_api')}")
        else:
            print(f"❌ /api/health 엔드포인트 응답 실패: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Flask 서버가 실행되지 않았습니다")
        print("   'python app.py' 명령으로 서버를 시작하세요")
        return False
    except Exception as e:
        print(f"❌ API 엔드포인트 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Supabase 연동 유튜브 다운로더 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("설정 파일", test_config),
        ("Supabase 연결", test_supabase_connection),
        ("데이터베이스 테이블", test_database_tables),
        ("API 엔드포인트", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류 발생: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 시스템이 정상적으로 설정되었습니다.")
        print("\n📝 다음 단계:")
        print("1. 웹 브라우저에서 http://localhost:5001 접속")
        print("2. 이메일로 로그인/등록")
        print("3. 유튜브 비디오 검색 및 다운로드 테스트")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 설정을 확인하세요.")
        print("\n🔧 문제 해결:")
        print("1. config.py에서 Supabase 설정 확인")
        print("2. supabase_schema.sql이 실행되었는지 확인")
        print("3. Flask 서버가 실행 중인지 확인")

if __name__ == "__main__":
    main()

