# YouTube Downloader - Supabase

완전 Supabase 기반 YouTube 다운로더 웹 애플리케이션

## 🚀 배포 방법

### GitHub Pages
1. 이 저장소를 GitHub에 업로드
2. Settings → Pages → Source: Deploy from a branch
3. Branch: main, Folder: / (root)
4. Save 클릭
5. 몇 분 후 `https://[username].github.io/[repository-name]` 접속 가능

### Netlify
1. [Netlify](https://netlify.com) 접속
2. "Add new site" → "Deploy manually"
3. `index.html` 파일 드래그 앤 드롭
4. 즉시 배포 완료

### Vercel
1. [Vercel](https://vercel.com) 접속
2. "New Project" → "Import Git Repository"
3. GitHub 저장소 연결
4. 자동 배포 완료

## 🔧 Supabase 설정

1. Supabase 대시보드 → SQL Editor
2. `supabase_production_schema.sql` 실행
3. Edge Functions → Create Function
4. Function name: `youtube-downloader`
5. `supabase_edge_function_code.ts` 내용 복사

## 📱 사용법

1. 이메일로 로그인/등록
2. YouTube URL 또는 검색어 입력
3. 원하는 비디오 선택
4. 다운로드 버튼 클릭

## 🛠️ 기술 스택

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Supabase Edge Functions
- **Database**: Supabase PostgreSQL
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage