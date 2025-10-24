# Python 3.11 기반 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 다운로드 폴더 생성
RUN mkdir -p /app/downloads

# 포트 노출
EXPOSE 5001

# 환경 변수 설정
ENV FLASK_APP=app_production.py
ENV FLASK_ENV=production
ENV DOWNLOAD_FOLDER=/app/downloads

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/health || exit 1

# 애플리케이션 실행
CMD ["python", "app_production.py"]
