-- Migration: create_initial_tables
-- Description: Creates the initial 'jobs' and 'resumes' tables.

-- Create the 'jobs' table
CREATE TABLE jobs (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, -- Auto-incrementing primary key
    title text NOT NULL,                             -- Job title (cannot be empty)
    company text,                                    -- Company name (optional)
    description text NOT NULL,                       -- Job description (cannot be empty)
    url text,                                        -- URL to the job posting (optional)
    status text DEFAULT 'new' NOT NULL,              -- Current status (e.g., new, filtered, generating, applied)
    created_at timestamptz DEFAULT now() NOT NULL,   -- Timestamp when the record was created
    source_id text                                   -- Optional ID from the source (e.g., Apify/Firecrawl run ID)
);

-- Add comments to columns for clarity (optional but good practice)
COMMENT ON COLUMN jobs.status IS 'Tracks the processing state of the job listing.';
COMMENT ON COLUMN jobs.source_id IS 'Optional identifier from the scraping source.';


-- Create the 'resumes' table
CREATE TABLE resumes (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, -- Auto-incrementing primary key
    job_id bigint REFERENCES jobs(id) ON DELETE SET NULL, -- Foreign key linking to the jobs table (optional link)
                                                          -- ON DELETE SET NULL means if the job is deleted, job_id becomes NULL
    file_path text NOT NULL,                         -- Path to the generated resume file (e.g., in Supabase Storage)
    status text DEFAULT 'generated' NOT NULL,        -- Current status (e.g., generated, emailed, failed)
    created_at timestamptz DEFAULT now() NOT NULL    -- Timestamp when the record was created
);

-- Add comments to columns
COMMENT ON COLUMN resumes.job_id IS 'The specific job this resume was tailored for (if applicable).';
COMMENT ON COLUMN resumes.file_path IS 'Location of the generated resume document.';
COMMENT ON COLUMN resumes.status IS 'Tracks the state of the generated resume.';

-- Optional: Add indexes for frequently queried columns
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_resumes_job_id ON resumes(job_id);

