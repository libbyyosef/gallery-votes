-- db/schema.sql
-- PostgreSQL 14+. Idempotent, Docker-friendly schema.

-- Use the public schema by default
SET search_path TO public;

-- 0) Enum type for vote actions (safe to run multiple times)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vote_action') THEN
    CREATE TYPE vote_action AS ENUM ('like', 'dislike');
  END IF;
END $$ LANGUAGE plpgsql;

-- 1) IMAGES: fixed catalog (you'll seed 1..100)
CREATE TABLE IF NOT EXISTS public.images (
  image_id   INT PRIMARY KEY,                 -- 1..100
  source_url TEXT NOT NULL UNIQUE,            -- e.g., https://picsum.photos/id/XX/600/400
  label      TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2) VOTES: each button click = one row, anonymous
CREATE TABLE IF NOT EXISTS public.votes (
  vote_id    BIGSERIAL PRIMARY KEY,
  image_id   INT NOT NULL REFERENCES public.images(image_id) ON DELETE CASCADE,
  action     vote_action NOT NULL,            -- 'like' OR 'dislike' (independent)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Helpful indexes for fast per-image counts
CREATE INDEX IF NOT EXISTS votes_image_id_idx          ON public.votes(image_id);
CREATE INDEX IF NOT EXISTS votes_image_id_action_idx   ON public.votes(image_id, action);
CREATE INDEX IF NOT EXISTS votes_image_id_created_idx  ON public.votes(image_id, created_at);

-- 3) VIEW: per-image aggregates (no inference; only actual clicks counted)
DROP VIEW IF EXISTS public.image_vote_counts;
CREATE VIEW public.image_vote_counts AS
SELECT
  i.image_id,
  i.source_url,
  COUNT(*) FILTER (WHERE v.action = 'like')    AS likes,
  COUNT(*) FILTER (WHERE v.action = 'dislike') AS dislikes,
  (COUNT(*) FILTER (WHERE v.action = 'like')    > 0) AS is_liked,     -- at least one like
  (COUNT(*) FILTER (WHERE v.action = 'dislike') > 0) AS is_disliked,  -- at least one dislike
  (COUNT(*) FILTER (WHERE v.action = 'like')
   - COUNT(*) FILTER (WHERE v.action = 'dislike')) AS net_score
FROM public.images i
LEFT JOIN public.votes v ON v.image_id = i.image_id
GROUP BY i.image_id, i.source_url;
