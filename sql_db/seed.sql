-- db/seed.sql
-- Idempotent seed for images 1..100 with deterministic URLs.
SET search_path TO public;

INSERT INTO public.images (image_id, source_url, label)
SELECT gs AS image_id,
       format('https://picsum.photos/id/%s/600/400', gs) AS source_url,
       NULL::text AS label
FROM generate_series(1, 100) AS gs
ON CONFLICT (image_id) DO NOTHING;   -- safe to run multiple times
