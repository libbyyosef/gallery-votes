SET search_path TO public;

-- Single table: images with built-in counters
CREATE TABLE IF NOT EXISTS public.images (
  image_id       INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  picsum_id      TEXT NOT NULL UNIQUE,  -- e.g., "237" for /id/237/...
  label          TEXT,
  like_count     INT  NOT NULL DEFAULT 0,
  dislike_count  INT  NOT NULL DEFAULT 0,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Optional view so existing code that selects likes/dislikes still works
DROP VIEW IF EXISTS public.image_vote_counts;
CREATE VIEW public.image_vote_counts AS
SELECT
  image_id,
  picsum_id,
  like_count     AS likes,
  dislike_count  AS dislikes
FROM public.images;
