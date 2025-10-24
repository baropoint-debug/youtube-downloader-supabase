# 🚀 Supabase CLI 자동 배포 설정

## 📦 **Supabase CLI 설치**

### **Windows:**
```bash
# Scoop 사용
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# 또는 NPM 사용
npm install -g supabase
```

### **Mac/Linux:**
```bash
npm install -g supabase
```

---

## 🔧 **프로젝트 초기 설정**

### **Step 1: Supabase 로그인**
```bash
supabase login
```

### **Step 2: 프로젝트 연결**
```bash
cd C:\Faceon\video
supabase link --project-ref qhrfefcthrogwdwpxkby
```

**Project Reference ID**: `qhrfefcthrogwdwpxkby`

### **Step 3: Edge Functions 폴더 구조 생성**
```bash
mkdir supabase
mkdir supabase\functions
mkdir supabase\functions\youtube-downloader
```

### **Step 4: Edge Function 코드 이동**
```bash
copy supabase_edge_function_FINAL.ts supabase\functions\youtube-downloader\index.ts
```

---

## 🚀 **자동 배포 명령어**

### **한 번에 배포:**
```bash
supabase functions deploy youtube-downloader
```

### **환경 변수 설정:**
```bash
supabase secrets set YOUTUBE_API_KEY=AIzaSyBQ95Zj_awq6A7CrpXXo2eW6GIAcPShQ9Y
```

---

## 📝 **배포 스크립트 (deploy.bat)**

프로젝트 루트에 `deploy.bat` 파일 생성:

```batch
@echo off
echo 🚀 Edge Function 배포 시작...

REM Edge Function 코드 복사
copy supabase_edge_function_FINAL.ts supabase\functions\youtube-downloader\index.ts

REM Supabase에 배포
supabase functions deploy youtube-downloader

echo ✅ 배포 완료!
pause
```

**사용 방법:**
```bash
deploy.bat
```

---

## 🔄 **Git Push + 자동 배포 스크립트**

`deploy-all.bat` 파일 생성:

```batch
@echo off
echo 📦 프론트엔드 빌드...
copy index.html public\index.html /Y

echo 📤 Git 푸시...
git add .
git commit -m "Update: %date% %time%"
git push origin main

echo 🚀 Edge Function 배포...
copy supabase_edge_function_FINAL.ts supabase\functions\youtube-downloader\index.ts
supabase functions deploy youtube-downloader

echo ✅ 모든 배포 완료!
pause
```

**사용 방법:**
```bash
deploy-all.bat
```

---

## 💡 **현재 vs 자동화 비교**

### **현재 (수동):**
1. ❌ 코드 수정
2. ❌ Git push
3. ❌ Supabase 대시보드 접속
4. ❌ Edge Function 페이지 이동
5. ❌ Edit 클릭
6. ❌ 코드 복사/붙여넣기
7. ❌ Deploy 클릭

### **자동화 후 (CLI):**
1. ✅ 코드 수정
2. ✅ `deploy-all.bat` 실행 (한 번 클릭!)

---

## 🎯 **추천 방법:**

### **개발 중:**
- **프론트엔드 변경**: `git push`만 (GitHub Pages 자동 배포)
- **Edge Function 변경**: `supabase functions deploy youtube-downloader`

### **완성 후:**
- **한 번에 배포**: `deploy-all.bat`

---

## 🔍 **배포 확인:**
```bash
# 배포된 함수 목록
supabase functions list

# 함수 로그 확인
supabase functions logs youtube-downloader
```

---

## 📋 **요약:**

| 방법 | 장점 | 단점 |
|------|------|------|
| **Supabase 대시보드 (현재)** | 간단, 설치 불필요 | 매번 수동 복사/붙여넣기 |
| **Supabase CLI (권장)** | 자동화, 빠름, Git과 통합 | 초기 설정 필요 |

---

## 🚀 **지금 바로 설치하려면:**

```bash
# 1. NPM으로 CLI 설치
npm install -g supabase

# 2. 로그인
supabase login

# 3. 프로젝트 연결
supabase link --project-ref qhrfefcthrogwdwpxkby

# 4. 배포
supabase functions deploy youtube-downloader
```

**설치하면 앞으로는 한 줄로 배포 가능합니다!** 🎉

