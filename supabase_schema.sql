-- Supabase 데이터베이스 스키마
-- 이 파일의 SQL을 Supabase SQL Editor에서 실행하세요

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 다운로드 작업 테이블
CREATE TABLE IF NOT EXISTS download_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    video_title TEXT,
    video_thumbnail TEXT,
    channel_name TEXT,
    video_duration TEXT,
    video_description TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'downloading', 'completed', 'failed', 'cancelled')),
    download_path TEXT,
    file_size BIGINT,
    file_format TEXT,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 다운로드 히스토리 테이블
CREATE TABLE IF NOT EXISTS download_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES download_jobs(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('download_started', 'download_progress', 'download_completed', 'download_failed', 'download_cancelled')),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 사용자 즐겨찾기 테이블
CREATE TABLE IF NOT EXISTS user_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    video_title TEXT,
    video_thumbnail TEXT,
    channel_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, video_url)
);

-- 사용자 플레이리스트 테이블
CREATE TABLE IF NOT EXISTS user_playlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 플레이리스트 비디오 테이블
CREATE TABLE IF NOT EXISTS playlist_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    playlist_id UUID REFERENCES user_playlists(id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    video_title TEXT,
    video_thumbnail TEXT,
    channel_name TEXT,
    position INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_download_jobs_user_id ON download_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_download_jobs_status ON download_jobs(status);
CREATE INDEX IF NOT EXISTS idx_download_jobs_created_at ON download_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_download_history_user_id ON download_history(user_id);
CREATE INDEX IF NOT EXISTS idx_download_history_job_id ON download_history(job_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_playlists_user_id ON user_playlists(user_id);
CREATE INDEX IF NOT EXISTS idx_playlist_videos_playlist_id ON playlist_videos(playlist_id);

-- RLS (Row Level Security) 정책 설정
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE download_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE download_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_playlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE playlist_videos ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 데이터만 접근 가능
CREATE POLICY "Users can view own data" ON users FOR ALL USING (auth.uid() = id);
CREATE POLICY "Users can view own download jobs" ON download_jobs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own download history" ON download_history FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own favorites" ON user_favorites FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own playlists" ON user_playlists FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own playlist videos" ON playlist_videos FOR ALL USING (
    EXISTS (SELECT 1 FROM user_playlists WHERE id = playlist_id AND user_id = auth.uid())
);

-- 공개 플레이리스트는 모든 사용자가 볼 수 있음
CREATE POLICY "Public playlists are viewable by everyone" ON user_playlists FOR SELECT USING (is_public = TRUE);
CREATE POLICY "Public playlist videos are viewable by everyone" ON playlist_videos FOR SELECT USING (
    EXISTS (SELECT 1 FROM user_playlists WHERE id = playlist_id AND is_public = TRUE)
);

-- 함수: 사용자 생성 시 자동으로 사용자 레코드 생성
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, avatar_url)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'name', NEW.raw_user_meta_data->>'avatar_url');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 트리거: 새 사용자 등록 시 자동으로 users 테이블에 레코드 생성
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 함수: 다운로드 작업 상태 업데이트 시 히스토리 자동 생성
CREATE OR REPLACE FUNCTION public.handle_download_job_update()
RETURNS TRIGGER AS $$
BEGIN
  -- 상태가 변경된 경우 히스토리에 기록
  IF OLD.status IS DISTINCT FROM NEW.status THEN
    INSERT INTO public.download_history (user_id, job_id, action, details)
    VALUES (
      NEW.user_id,
      NEW.id,
      CASE NEW.status
        WHEN 'downloading' THEN 'download_started'
        WHEN 'completed' THEN 'download_completed'
        WHEN 'failed' THEN 'download_failed'
        WHEN 'cancelled' THEN 'download_cancelled'
        ELSE 'download_progress'
      END,
      jsonb_build_object(
        'old_status', OLD.status,
        'new_status', NEW.status,
        'progress', NEW.progress,
        'error_message', NEW.error_message
      )
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 트리거: 다운로드 작업 상태 변경 시 히스토리 자동 생성
CREATE TRIGGER on_download_job_status_change
  AFTER UPDATE ON download_jobs
  FOR EACH ROW EXECUTE FUNCTION public.handle_download_job_update();

