# Working with pgvector in Supabase - Complete Guide

## Problem: Vector Syntax Errors

### ❌ Common Mistakes

```sql
-- DON'T: Use ARRAY[...] for large vectors
SELECT * FROM find_compatible_artists(
    ARRAY[0.1, 0.2, ..., 0.999]::vector
);

-- DON'T: Forget dimension specification
'[0.1, 0.2, ...]'::vector  -- Missing dimension
```

### ✅ Correct Approaches

```sql
-- Method 1: String casting (RECOMMENDED for function calls)
SELECT * FROM find_compatible_artists(
    '[0.1, 0.2, 0.3, ..., 0.5]'::vector(1536)
);

-- Method 2: Use existing embeddings
SELECT * FROM find_compatible_artists(
    (SELECT embedding FROM artists WHERE artist_name = 'Drake' LIMIT 1)
);

-- Method 3: From application (Supabase JS handles conversion)
const { data } = await supabase.rpc('find_compatible_artists', {
    query_embedding: [0.1, 0.2, 0.3, ...], // Array of floats
    match_threshold: 0.5,
    match_count: 10
});
```

---

## Best Practices

### 1. **Always Specify Vector Dimensions**

```sql
-- ✅ Correct
embedding vector(1536)

-- ❌ Wrong
embedding vector  -- Dimension required
```

### 2. **Use String Format for Large Vectors in SQL**

```sql
-- When you have a large embedding array like:
-- [0.123, -0.456, 0.789, ..., 0.321]

-- Convert to string:
'[0.123, -0.456, 0.789, ..., 0.321]'::vector(1536)
```

### 3. **Create Indexes for Performance**

```sql
-- HNSW Index (Best for most use cases)
CREATE INDEX artists_embedding_idx 
ON artists 
USING hnsw (embedding vector_cosine_ops);

-- IVFFlat Index (Good for smaller datasets < 1M rows)
CREATE INDEX artists_embedding_idx 
ON artists 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 4. **Use Cosine Distance Operator (<=>)**

```sql
-- Calculate similarity
1 - (embedding1 <=> embedding2) AS similarity

-- Order by similarity (ascending distance = more similar)
ORDER BY embedding <=> query_vector
```

---

## Complete Examples

### Example 1: Insert Vectors

```sql
-- Insert a new artist with embedding
INSERT INTO artists (artist_name, artist_tags, embedding)
VALUES (
    'New Artist',
    'pop, dance-pop, r&b',
    '[0.123, -0.456, 0.789, ...]'::vector(1536)
);
```

### Example 2: Query from JavaScript/TypeScript

```javascript
// Method 1: Using Supabase RPC
const embedding = await generateEmbedding(userTags); // Array of floats

const { data, error } = await supabase
  .rpc('match_artists_combined_score', {
    query_embedding: embedding,  // JS array
    match_threshold: 0.3,
    match_count: 10,
    semantic_weight: 0.6,
    historical_weight: 0.4
  });

// Method 2: Direct query (not recommended for production)
const { data, error } = await supabase
  .from('artists')
  .select('id, artist_name, artist_tags')
  .order('embedding <=> ' + JSON.stringify(embedding))
  .limit(10);
```

### Example 3: Update Existing Embeddings

```javascript
// Update embedding for a specific artist
const { data, error } = await supabase
  .from('artists')
  .update({ embedding: embeddingArray })
  .eq('id', artistId);
```

### Example 4: Query with SQL

```sql
-- Find top 10 most similar artists to a given embedding
SELECT 
    id,
    artist_name,
    artist_tags,
    1 - (embedding <=> '[0.1, 0.2, ...]'::vector(1536)) AS similarity
FROM artists
WHERE embedding IS NOT NULL
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector(1536)
LIMIT 10;
```

---

## Troubleshooting

### Error: "syntax error at or near '..'"

**Cause:** Using `ARRAY[...]` with too many elements or improper formatting

**Solution:** Use string format instead:
```sql
-- Instead of:
ARRAY[0.1, 0.2, ..., 0.5]::vector(1536)

-- Use:
'[0.1, 0.2, ..., 0.5]'::vector(1536)
```

### Error: "expected 1536 dimensions, not X"

**Cause:** Vector dimension mismatch

**Solution:** 
1. Check your embedding model output size
2. Ensure all vectors have same dimensions
3. Specify correct dimension in table definition

```sql
-- If using text-embedding-3-small (1536 dimensions)
embedding vector(1536)

-- If using text-embedding-3-large (3072 dimensions)
embedding vector(3072)
```

### Error: "operator does not exist: vector <=> double precision[]"

**Cause:** Trying to compare vector with regular array

**Solution:** Cast to vector type:
```sql
-- Wrong:
embedding <=> ARRAY[0.1, 0.2]

-- Right:
embedding <=> '[0.1, 0.2]'::vector(1536)
```

---

## Performance Tips

### 1. **Use Appropriate Index**

For < 1 million rows:
```sql
CREATE INDEX ON artists USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

For > 1 million rows:
```sql
CREATE INDEX ON artists USING hnsw (embedding vector_cosine_ops);
```

### 2. **Filter Before Similarity Search**

```sql
-- Better performance
SELECT * FROM artists
WHERE category = 'pop'
ORDER BY embedding <=> query_vector
LIMIT 10;

-- vs slower
SELECT * FROM artists
ORDER BY embedding <=> query_vector
LIMIT 10;
```

### 3. **Use RPC Functions**

Encapsulate complex queries in PostgreSQL functions for:
- Better performance
- Cleaner code
- Easier maintenance

---

## Distance Operators

| Operator | Distance Type | Use Case |
|----------|---------------|----------|
| `<->` | L2 (Euclidean) | General similarity |
| `<=>` | Cosine | Text embeddings (RECOMMENDED) |
| `<#>` | Inner product | Some ML models |

For OpenAI embeddings, **always use cosine distance (`<=>`)**:

```sql
-- Calculate similarity (0 = identical, 2 = opposite)
embedding1 <=> embedding2

-- Convert to similarity score (0-1, higher = more similar)
1 - (embedding1 <=> embedding2)
```

---

## Migration Example

If you need to change vector dimensions:

```sql
-- 1. Add new column
ALTER TABLE artists ADD COLUMN embedding_new vector(3072);

-- 2. Populate new column (you'll need to regenerate embeddings)
-- UPDATE artists SET embedding_new = ...

-- 3. Drop old column
ALTER TABLE artists DROP COLUMN embedding;

-- 4. Rename new column
ALTER TABLE artists RENAME COLUMN embedding_new TO embedding;

-- 5. Recreate index
CREATE INDEX artists_embedding_idx ON artists 
USING hnsw (embedding vector_cosine_ops);
```

---

## Summary

✅ **DO:**
- Use string format for vectors in SQL: `'[0.1, 0.2, ...]'::vector(1536)`
- Specify dimensions: `vector(1536)`
- Create appropriate indexes
- Use cosine distance for embeddings
- Use RPC functions for complex queries

❌ **DON'T:**
- Use `ARRAY[...]` for large vectors in SQL
- Forget dimension specification
- Mix different vector dimensions
- Skip indexing on large tables

---

## Files Created

1. **`supabase_functions.sql`** - All PostgreSQL functions for your project
2. **Updated `backend/routes/match.js`** - Correct RPC usage

Run the SQL file in Supabase SQL Editor to create all functions!
