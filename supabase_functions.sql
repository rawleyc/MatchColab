-- ============================================
-- SUPABASE PGVECTOR FUNCTIONS FOR MATCHCOLAB
-- ============================================

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 1. BASIC SIMILARITY SEARCH FUNCTION
-- ============================================

CREATE OR REPLACE FUNCTION find_compatible_artists(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  artist_name text,
  artist_tags text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    artists.id,
    artists.artist_name,
    artists.artist_tags,
    1 - (artists.embedding <=> query_embedding) AS similarity
  FROM artists
  WHERE artists.embedding IS NOT NULL
    AND 1 - (artists.embedding <=> query_embedding) > match_threshold
  ORDER BY artists.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ============================================
-- 2. FUNCTION WITH HISTORICAL SUCCESS DATA
-- ============================================

CREATE OR REPLACE FUNCTION match_artists_with_history(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10,
  only_successful bool DEFAULT false
)
RETURNS TABLE (
  id bigint,
  artist_name text,
  artist_tags text,
  similarity float,
  historical_success_rate float,
  total_collaborations int,
  successful_collaborations int
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH artist_similarities AS (
    SELECT
      artists.id,
      artists.artist_name,
      artists.artist_tags,
      1 - (artists.embedding <=> query_embedding) AS similarity
    FROM artists
    WHERE artists.embedding IS NOT NULL
      AND 1 - (artists.embedding <=> query_embedding) > match_threshold
  ),
  artist_history AS (
    SELECT
      a.id,
      COUNT(m.id) as total_collabs,
      SUM(CASE WHEN m.collaboration_status = 'Success' THEN 1 ELSE 0 END) as successful_collabs,
      CASE 
        WHEN COUNT(m.id) > 0 THEN 
          SUM(CASE WHEN m.collaboration_status = 'Success' THEN 1 ELSE 0 END)::float / COUNT(m.id)
        ELSE 0.5
      END as success_rate
    FROM artists a
    LEFT JOIN maindb m ON (a.artist_name = m.artist_01 OR a.artist_name = m.artist_02)
    GROUP BY a.id
  )
  SELECT
    asi.id,
    asi.artist_name,
    asi.artist_tags,
    asi.similarity,
    COALESCE(ah.success_rate, 0.5)::float as historical_success_rate,
    COALESCE(ah.total_collabs, 0)::int as total_collaborations,
    COALESCE(ah.successful_collabs, 0)::int as successful_collaborations
  FROM artist_similarities asi
  LEFT JOIN artist_history ah ON asi.id = ah.id
  WHERE 
    CASE 
      WHEN only_successful = true THEN COALESCE(ah.success_rate, 0) >= 0.5
      ELSE true
    END
  ORDER BY asi.similarity DESC
  LIMIT match_count;
END;
$$;

-- ============================================
-- 3. COMBINED SCORE FUNCTION (60% Semantic + 40% Historical)
-- ============================================

CREATE OR REPLACE FUNCTION match_artists_combined_score(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.3,
  match_count int DEFAULT 10,
  semantic_weight float DEFAULT 0.6,
  historical_weight float DEFAULT 0.4
)
RETURNS TABLE (
  id bigint,
  artist_name text,
  artist_tags text,
  semantic_similarity float,
  historical_success_rate float,
  combined_score float,
  total_collaborations int,
  successful_collaborations int
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH artist_similarities AS (
    SELECT
      artists.id,
      artists.artist_name,
      artists.artist_tags,
      1 - (artists.embedding <=> query_embedding) AS similarity
    FROM artists
    WHERE artists.embedding IS NOT NULL
  ),
  artist_history AS (
    SELECT
      a.id,
      COUNT(m.id) as total_collabs,
      SUM(CASE WHEN m.collaboration_status = 'Success' THEN 1 ELSE 0 END) as successful_collabs,
      CASE 
        WHEN COUNT(m.id) > 0 THEN 
          SUM(CASE WHEN m.collaboration_status = 'Success' THEN 1 ELSE 0 END)::float / COUNT(m.id)
        ELSE 0.5
      END as success_rate
    FROM artists a
    LEFT JOIN maindb m ON (a.artist_name = m.artist_01 OR a.artist_name = m.artist_02)
    GROUP BY a.id
  ),
  scored_artists AS (
    SELECT
      asi.id,
      asi.artist_name,
      asi.artist_tags,
      asi.similarity,
      COALESCE(ah.success_rate, 0.5) as hist_rate,
      (semantic_weight * asi.similarity) + (historical_weight * COALESCE(ah.success_rate, 0.5)) as combo_score,
      COALESCE(ah.total_collabs, 0) as total_collabs,
      COALESCE(ah.successful_collabs, 0) as successful_collabs
    FROM artist_similarities asi
    LEFT JOIN artist_history ah ON asi.id = ah.id
  )
  SELECT
    sa.id,
    sa.artist_name,
    sa.artist_tags,
    sa.similarity::float as semantic_similarity,
    sa.hist_rate::float as historical_success_rate,
    sa.combo_score::float as combined_score,
    sa.total_collabs::int as total_collaborations,
    sa.successful_collabs::int as successful_collaborations
  FROM scored_artists sa
  WHERE sa.combo_score >= match_threshold
  ORDER BY sa.combo_score DESC
  LIMIT match_count;
END;
$$;

-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- Example 1: Basic search with string vector
-- SELECT * FROM find_compatible_artists(
--   '[0.1, 0.2, 0.3, ..., 0.5]'::vector(1536),
--   0.5,
--   10
-- );

-- Example 2: Search using an existing artist's embedding
-- SELECT * FROM find_compatible_artists(
--   (SELECT embedding FROM artists WHERE artist_name = 'Ariana Grande' LIMIT 1),
--   0.5,
--   10
-- );

-- Example 3: Combined score search
-- SELECT * FROM match_artists_combined_score(
--   (SELECT embedding FROM artists WHERE artist_name = 'Drake' LIMIT 1),
--   0.3,
--   10,
--   0.6,
--   0.4
-- );

-- ============================================
-- CREATE INDEX FOR PERFORMANCE
-- ============================================

-- Create an HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS artists_embedding_idx 
ON artists 
USING hnsw (embedding vector_cosine_ops);

-- Alternative: IVFFlat index (good for smaller datasets)
-- CREATE INDEX IF NOT EXISTS artists_embedding_idx 
-- ON artists 
-- USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

-- ============================================
-- 4. DYNAMIC RANK FUNCTION (EMBEDDING + HISTORY)
-- ============================================
-- This function is tailored for real-time user queries: you supply an embedding
-- and it produces a combined score (60% semantic + 40% historical success).
-- Parameters allow filtering for minimum semantic similarity and optionally
-- restricting results to artists with at least one successful collaboration.

CREATE OR REPLACE FUNCTION public.rank_artists_by_embedding(
  query_embedding vector(1536),
  only_successful_collabs boolean DEFAULT false,
  match_count integer DEFAULT 10,
  min_semantic_similarity float DEFAULT 0.0
)
RETURNS TABLE (
  artist_id bigint,
  artist_name text,
  artist_tags text,
  semantic_similarity float,
  historical_success float,
  final_score float
)
LANGUAGE sql
STABLE
AS $$
WITH success_rates AS (
  -- Aggregate success rate per artist across both positions
  SELECT artist_name,
       (SUM(success_flag)::float / COUNT(*)) AS success_rate
  FROM (
    SELECT lower(m.artist_01) AS artist_name,
         CASE WHEN lower(m.collaboration_status) = 'success' THEN 1 ELSE 0 END AS success_flag
    FROM maindb m
    UNION ALL
    SELECT lower(m.artist_02) AS artist_name,
         CASE WHEN lower(m.collaboration_status) = 'success' THEN 1 ELSE 0 END AS success_flag
    FROM maindb m
  ) x
  GROUP BY artist_name
)
SELECT
  a.id AS artist_id,
  a.artist_name,
  a.artist_tags,
  (1 - (a.embedding <=> query_embedding)) AS semantic_similarity,
  COALESCE(sr.success_rate, 0.5) AS historical_success,  -- neutral prior 0.5 for unseen
  ((1 - (a.embedding <=> query_embedding)) * 0.6
     + COALESCE(sr.success_rate, 0.5) * 0.4) AS final_score
FROM artists a
LEFT JOIN success_rates sr ON lower(a.artist_name) = sr.artist_name
WHERE a.embedding IS NOT NULL
  AND (1 - (a.embedding <=> query_embedding)) >= min_semantic_similarity
  AND (
    only_successful_collabs = FALSE
    OR EXISTS (
      SELECT 1
      FROM maindb m2
      WHERE (lower(m2.artist_01) = lower(a.artist_name)
           OR lower(m2.artist_02) = lower(a.artist_name))
        AND lower(m2.collaboration_status) = 'success'
    )
    )
ORDER BY final_score DESC
LIMIT match_count;
$$;

-- Example usage:
-- SELECT * FROM rank_artists_by_embedding(
--   (SELECT embedding FROM artists WHERE artist_name = 'Ariana Grande' LIMIT 1),
--   false,
--   10,
--   0.3
-- );
