-- Migration: add_embeddings_and_components
-- Description: Adds embedding column to jobs and creates resume_components table.

-- Enable pgvector extension if not already enabled
-- (It's often enabled by default on Supabase, but good practice to include)
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

-- Add the embedding column to the jobs table
ALTER TABLE public.jobs
ADD COLUMN description_embedding vector(1536); -- Using 1536 for OpenAI Ada v2

COMMENT ON COLUMN public.jobs.description_embedding IS 'Vector embedding of the job description text.';

-- Create the resume_components table
CREATE TABLE public.resume_components (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    component_text text NOT NULL,                     -- The actual text snippet (bullet point, skill description, etc.)
    component_embedding vector(1536),                -- Vector embedding of the component_text
    created_at timestamptz DEFAULT now() NOT NULL     -- Timestamp when the component was added
);

COMMENT ON TABLE public.resume_components IS 'Stores reusable text components from user resumes/profiles and their vector embeddings.';
COMMENT ON COLUMN public.resume_components.component_text IS 'The actual text snippet (bullet point, skill description, etc.).';
COMMENT ON COLUMN public.resume_components.component_embedding IS 'Vector embedding of the component_text.';