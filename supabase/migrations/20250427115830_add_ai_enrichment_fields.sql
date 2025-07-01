-- Add AI enrichment fields to jobs table
ALTER TABLE jobs
  -- Rich fields from job sources
  ADD COLUMN IF NOT EXISTS source text,
  ADD COLUMN IF NOT EXISTS salary_min integer,
  ADD COLUMN IF NOT EXISTS salary_max integer,
  ADD COLUMN IF NOT EXISTS salary_currency text DEFAULT 'USD',
  ADD COLUMN IF NOT EXISTS location_city text,
  ADD COLUMN IF NOT EXISTS location_state text,
  ADD COLUMN IF NOT EXISTS posted_date text,

  -- AI-enriched fields
  ADD COLUMN IF NOT EXISTS ai_quality_score float,
  ADD COLUMN IF NOT EXISTS ai_skills_extracted text[],
  ADD COLUMN IF NOT EXISTS ai_seniority_level text,
  ADD COLUMN IF NOT EXISTS ai_remote_friendly boolean,
  ADD COLUMN IF NOT EXISTS ai_estimated_salary_min integer,
  ADD COLUMN IF NOT EXISTS ai_estimated_salary_max integer,
  ADD COLUMN IF NOT EXISTS ai_company_type text,
  ADD COLUMN IF NOT EXISTS ai_industry text,
  ADD COLUMN IF NOT EXISTS ai_enrichment_timestamp timestamptz,
  ADD COLUMN IF NOT EXISTS ai_processing_time_ms integer;

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_jobs_ai_quality_score ON jobs (ai_quality_score);
CREATE INDEX IF NOT EXISTS idx_jobs_ai_seniority_level ON jobs (ai_seniority_level);
CREATE INDEX IF NOT EXISTS idx_jobs_ai_company_type ON jobs (ai_company_type);
CREATE INDEX IF NOT EXISTS idx_jobs_ai_industry ON jobs (ai_industry);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs (source);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs (posted_date);

-- Add GIN index for array fields
CREATE INDEX IF NOT EXISTS idx_jobs_ai_skills_extracted ON jobs USING gin (ai_skills_extracted);

-- Add composite indexes for common filtering scenarios
CREATE INDEX IF NOT EXISTS idx_jobs_seniority_quality ON jobs (ai_seniority_level, ai_quality_score);
CREATE INDEX IF NOT EXISTS idx_jobs_location_remote ON jobs (location_city, location_state, ai_remote_friendly);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_range ON jobs (salary_min, salary_max, ai_estimated_salary_min, ai_estimated_salary_max);

-- Add check constraints
ALTER TABLE jobs
  ADD CONSTRAINT chk_ai_quality_score CHECK (ai_quality_score >= 0 AND ai_quality_score <= 1),
  ADD CONSTRAINT chk_salary_range CHECK (
    (salary_min IS NULL AND salary_max IS NULL) OR
    (salary_min <= salary_max)
  ),
  ADD CONSTRAINT chk_ai_salary_range CHECK (
    (ai_estimated_salary_min IS NULL AND ai_estimated_salary_max IS NULL) OR
    (ai_estimated_salary_min <= ai_estimated_salary_max)
  );

-- Add enum for job status
DO $$ BEGIN
    CREATE TYPE job_status AS ENUM ('new', 'enriched', 'basic');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Update status column to use enum (handle existing data and default)
ALTER TABLE jobs 
  ALTER COLUMN status DROP DEFAULT,
  ALTER COLUMN status TYPE job_status 
  USING CASE 
    WHEN status = 'new' THEN 'new'::job_status
    WHEN status = 'enriched' THEN 'enriched'::job_status
    WHEN status = 'basic' THEN 'basic'::job_status
    ELSE 'new'::job_status
  END,
  ALTER COLUMN status SET DEFAULT 'new'::job_status;

-- Add comments for documentation
COMMENT ON COLUMN jobs.ai_quality_score IS 'AI-generated quality score (0-1) based on description completeness, clarity, etc.';
COMMENT ON COLUMN jobs.ai_skills_extracted IS 'Array of skills extracted by AI from job description';
COMMENT ON COLUMN jobs.ai_seniority_level IS 'AI-detected seniority level (junior, mid, senior, lead)';
COMMENT ON COLUMN jobs.ai_remote_friendly IS 'AI analysis of whether job is remote-friendly';
COMMENT ON COLUMN jobs.ai_company_type IS 'AI-categorized company type (startup, enterprise, government, etc.)';
COMMENT ON COLUMN jobs.ai_industry IS 'AI-detected industry classification';
COMMENT ON COLUMN jobs.ai_enrichment_timestamp IS 'When AI enrichment was performed';
COMMENT ON COLUMN jobs.ai_processing_time_ms IS 'Time taken for AI enrichment in milliseconds';
