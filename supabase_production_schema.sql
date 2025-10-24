-- =============================================
-- Supabase 프로덕션 스키마
-- 외부 접속 가능한 유튜브 다운로더 서비스
-- =============================================

-- 기존 테이블 삭제 (개발용)
DROP TABLE IF EXISTS playlist_videos CASCADE;
DROP TABLE IF EXISTS user_playlists CASCADE;
DROP TABLE IF EXISTS user_favorites CASCADE;
DROP TABLE IF EXISTS download_history CASCADE;
DROP TABLE IF EXISTS download_jobs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    subscription_plan TEXT DEFAULT 'free' CHECK (subscription_plan IN ('free', 'premium', 'pro')),
    download_limit INTEGER DEFAULT 10,
    downloads_used INTEGER DEFAULT 0,
    last_download_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 다운로드 작업 테이블
CREATE TABLE download_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    video_id TEXT,
    video_title TEXT,
    video_thumbnail TEXT,
    channel_name TEXT,
    channel_id TEXT,
    video_duration TEXT,
    video_description TEXT,
    video_quality TEXT DEFAULT 'best',
    file_format TEXT DEFAULT 'mp4',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'downloading', 'completed', 'failed', 'cancelled')),
    download_path TEXT,
    file_size BIGINT,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    download_speed TEXT,
    estimated_time TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 다운로드 히스토리 테이블
CREATE TABLE download_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES download_jobs(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('download_started', 'download_progress', 'download_completed', 'download_failed', 'download_cancelled')),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 사용자 즐겨찾기 테이블
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    video_id TEXT,
    video_title TEXT,
    video_thumbnail TEXT,
    channel_name TEXT,
    channel_id TEXT,
    video_duration TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, video_url)
);

-- 사용자 플레이리스트 테이블
CREATE TABLE user_playlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    thumbnail_url TEXT,
    video_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 플레이리스트 비디오 테이블
CREATE TABLE playlist_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    playlist_id UUID REFERENCES user_playlists(id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    video_id TEXT,
    video_title TEXT,
    video_thumbnail TEXT,
    channel_name TEXT,
    channel_id TEXT,
    video_duration TEXT,
    position INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 시스템 설정 테이블
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 사용자 세션 테이블
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_download_jobs_user_id ON download_jobs(user_id);
CREATE INDEX idx_download_jobs_status ON download_jobs(status);
CREATE INDEX idx_download_jobs_created_at ON download_jobs(created_at);
CREATE INDEX idx_download_jobs_video_id ON download_jobs(video_id);
CREATE INDEX idx_download_history_user_id ON download_history(user_id);
CREATE INDEX idx_download_history_job_id ON download_history(job_id);
CREATE INDEX idx_download_history_created_at ON download_history(created_at);
CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_video_url ON user_favorites(video_url);
CREATE INDEX idx_user_playlists_user_id ON user_playlists(user_id);
CREATE INDEX idx_user_playlists_public ON user_playlists(is_public);
CREATE INDEX idx_playlist_videos_playlist_id ON playlist_videos(playlist_id);
CREATE INDEX idx_playlist_videos_position ON playlist_videos(position);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

-- RLS (Row Level Security) 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE download_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE download_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_playlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE playlist_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- RLS 정책 생성
-- 사용자는 자신의 데이터만 접근 가능
CREATE POLICY "Users can view own data" ON users FOR ALL USING (auth.uid() = id);
CREATE POLICY "Users can view own download jobs" ON download_jobs FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own download history" ON download_history FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own favorites" ON user_favorites FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own playlists" ON user_playlists FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own playlist videos" ON playlist_videos FOR ALL USING (
    EXISTS (SELECT 1 FROM user_playlists WHERE id = playlist_id AND user_id = auth.uid())
);
CREATE POLICY "Users can view own sessions" ON user_sessions FOR ALL USING (auth.uid() = user_id);

-- 공개 플레이리스트는 모든 사용자가 볼 수 있음
CREATE POLICY "Public playlists are viewable by everyone" ON user_playlists FOR SELECT USING (is_public = TRUE);
CREATE POLICY "Public playlist videos are viewable by everyone" ON playlist_videos FOR SELECT USING (
    EXISTS (SELECT 1 FROM user_playlists WHERE id = playlist_id AND is_public = TRUE)
);

-- 시스템 설정은 모든 사용자가 읽을 수 있음
CREATE POLICY "System settings are readable by everyone" ON system_settings FOR SELECT USING (TRUE);

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
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
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
        'error_message', NEW.error_message,
        'file_size', NEW.file_size
      )
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 트리거: 다운로드 작업 상태 변경 시 히스토리 자동 생성
DROP TRIGGER IF EXISTS on_download_job_status_change ON download_jobs;
CREATE TRIGGER on_download_job_status_change
  AFTER UPDATE ON download_jobs
  FOR EACH ROW EXECUTE FUNCTION public.handle_download_job_update();

-- 함수: 플레이리스트에 비디오 추가 시 카운트 업데이트
CREATE OR REPLACE FUNCTION public.update_playlist_video_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE user_playlists 
    SET video_count = video_count + 1 
    WHERE id = NEW.playlist_id;
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE user_playlists 
    SET video_count = video_count - 1 
    WHERE id = OLD.playlist_id;
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 트리거: 플레이리스트 비디오 카운트 자동 업데이트
DROP TRIGGER IF EXISTS update_playlist_video_count_trigger ON playlist_videos;
CREATE TRIGGER update_playlist_video_count_trigger
  AFTER INSERT OR DELETE ON playlist_videos
  FOR EACH ROW EXECUTE FUNCTION public.update_playlist_video_count();

-- 초기 시스템 설정 데이터 삽입
INSERT INTO system_settings (key, value, description) VALUES
('app_name', '"YouTube Downloader Pro"', '애플리케이션 이름'),
('app_version', '"1.0.0"', '애플리케이션 버전'),
('max_downloads_free', '10', '무료 사용자 최대 다운로드 수'),
('max_downloads_premium', '100', '프리미엄 사용자 최대 다운로드 수'),
('max_downloads_pro', '1000', '프로 사용자 최대 다운로드 수'),
('supported_formats', '["mp4", "webm", "mkv", "avi"]', '지원되는 비디오 포맷'),
('max_file_size_mb', '500', '최대 파일 크기 (MB)'),
('maintenance_mode', 'false', '유지보수 모드'),
('feature_flags', '{"favorites": true, "playlists": true, "sharing": true}', '기능 플래그');

-- 뷰 생성: 사용자 통계
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.email,
    u.name,
    u.subscription_plan,
    u.download_limit,
    u.downloads_used,
    COUNT(dj.id) as total_downloads,
    COUNT(CASE WHEN dj.status = 'completed' THEN 1 END) as successful_downloads,
    COUNT(CASE WHEN dj.status = 'failed' THEN 1 END) as failed_downloads,
    COUNT(uf.id) as total_favorites,
    COUNT(up.id) as total_playlists,
    u.created_at,
    u.last_download_at
FROM users u
LEFT JOIN download_jobs dj ON u.id = dj.user_id
LEFT JOIN user_favorites uf ON u.id = uf.user_id
LEFT JOIN user_playlists up ON u.id = up.user_id
GROUP BY u.id, u.email, u.name, u.subscription_plan, u.download_limit, u.downloads_used, u.created_at, u.last_download_at;

-- 뷰 생성: 인기 비디오
CREATE VIEW popular_videos AS
SELECT 
    video_url,
    video_title,
    video_thumbnail,
    channel_name,
    COUNT(*) as download_count,
    COUNT(DISTINCT user_id) as unique_users,
    MAX(created_at) as last_downloaded
FROM download_jobs
WHERE status = 'completed'
GROUP BY video_url, video_title, video_thumbnail, channel_name
ORDER BY download_count DESC, unique_users DESC;

-- 뷰 생성: 채널 통계
CREATE VIEW channel_stats AS
SELECT 
    channel_name,
    channel_id,
    COUNT(*) as total_downloads,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT video_url) as unique_videos,
    MAX(created_at) as last_downloaded
FROM download_jobs
WHERE status = 'completed' AND channel_name IS NOT NULL
GROUP BY channel_name, channel_id
ORDER BY total_downloads DESC, unique_users DESC;
