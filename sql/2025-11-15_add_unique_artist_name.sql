-- Add a UNIQUE constraint to artists.artist_name so upsert onConflict("artist_name") works
-- Safe migration: normalize whitespace, remove exact duplicates, then add constraint.

BEGIN;

-- 1) Normalize whitespace in artist_name
UPDATE public.artists
SET artist_name = trim(artist_name)
WHERE artist_name IS NOT NULL;

-- 2) Remove exact duplicates (keep lowest id)
WITH ranked AS (
  SELECT id, artist_name,
         ROW_NUMBER() OVER (PARTITION BY artist_name ORDER BY id) AS rn
  FROM public.artists
  WHERE artist_name IS NOT NULL
)
DELETE FROM public.artists a
USING ranked r
WHERE a.id = r.id
  AND r.rn > 1;

-- 3) Add UNIQUE constraint if it doesn't already exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'artists_artist_name_key'
      AND conrelid = 'public.artists'::regclass
  ) THEN
    ALTER TABLE public.artists
    ADD CONSTRAINT artists_artist_name_key UNIQUE (artist_name);
  END IF;
END$$;

COMMIT;

-- Optional (commented): make case-insensitive uniqueness by using CITEXT
-- Requires: CREATE EXTENSION IF NOT EXISTS citext;
-- ALTER TABLE public.artists ALTER COLUMN artist_name TYPE citext;
-- Then the same UNIQUE constraint will be case-insensitive.
