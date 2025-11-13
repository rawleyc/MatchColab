# MatchColab Functions & Local Testing Guide

This document describes the core functions (database + backend route) and shows how to run and test the local server. It also includes sample requests, responses, and troubleshooting tips.

---
## 1. Overview
MatchColab provides real‑time artist compatibility recommendations by combining:
- Semantic similarity of tag embeddings (OpenAI `text-embedding-3-small`)
- Historical collaboration success (from `maindb` table)

The blended score currently = `0.6 * semantic_similarity + 0.4 * historical_success_rate` with a neutral prior of `0.5` when no history exists.

---
## 2. Environment Requirements
Ensure these environment variables exist in your `.env` (loaded by `server.js`):
```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_SERVICE_KEY=<service_role_key>
PORT=5000   # optional, defaults as configured in server
```

Install dependencies (from backend folder):
```powershell
npm install
```

Start the server (development watch):
```powershell
npx nodemon server.js
```
Or without nodemon:
```powershell
node server.js
```

---
## 3. Backend Route Functions (`backend/routes/match.js`)
### 3.1 `POST /match`
Generates an embedding for provided `tags`, optionally persists an artist, then calls the Supabase RPC `rank_artists_by_embedding` and decorates each row with a recommendation label.

Request Body Fields:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| tags | string | yes | — | Comma/space separated descriptive tags for the querying artist. |
| top_n | number | no | 10 | Max number of matches to return. |
| only_successful | boolean | no | false | If true, restrict to artists with at least one successful collaboration. |
| min_similarity | number | no | 0.3 | Minimum semantic similarity filter. |
| persist_artist | boolean | no | false | If true, upsert the querying artist into `artists` table. |
| artist_name | string | conditional | null | Name used when persisting; required if `persist_artist=true`. |

Response Shape:
```
{
  "user_tags": "hip hop, r&b, melodic",
  "parameters": { "top_n": 10, "only_successful": false, "min_similarity": 0.3 },
  "matches": [
    {
      "artist_id": 12,
      "artist_name": "Artist X",
      "semantic_similarity": 0.78,
      "historical_success": 0.55,
      "final_score": 0.71,
      "recommendation": "HIGHLY RECOMMENDED - Strong compatibility!"
    }
  ],
  "total_matches": 10
}
```

### 3.2 Helper Functions
| Function | Purpose | Notes |
|----------|---------|-------|
| `getOpenAIClient()` | Lazy init OpenAI client | Throws if `OPENAI_API_KEY` missing. |
| `getSupabaseClient()` | Lazy init Supabase client | Requires URL + Service Key. |
| `recommendationLabel(score)` | Adds human-friendly label | Thresholds: `>=0.7` high, `>=0.5` good, else risky. |

Error Handling:
- Missing `tags` → `400` JSON error
- RPC failure → `500` with `details`
- Uncaught server error → `500` with message

---
## 4. Supabase SQL Functions (`supabase_functions.sql`)
Enable pgvector (once):
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
### 4.1 `find_compatible_artists(query_embedding, match_threshold=0.5, match_count=10)`
Returns basic semantic similarity results.

### 4.2 `match_artists_with_history(query_embedding, match_threshold=0.5, match_count=10, only_successful=false)`
Adds historical success metrics (success rate, counts) with optional success-only filter.

### 4.3 `match_artists_combined_score(query_embedding, match_threshold=0.3, match_count=10, semantic_weight=0.6, historical_weight=0.4)`
Computes combined score with configurable weights.

### 4.4 `rank_artists_by_embedding(query_embedding, only_successful_collabs=false, match_count=10, min_semantic_similarity=0.0)` (Primary RPC)
Real-time ranking used by `/match`. Output columns:
| Column | Description |
|--------|-------------|
| artist_id | ID from `artists` table |
| artist_name | Name of artist |
| semantic_similarity | Cosine similarity (1 - distance) |
| historical_success | Success rate, prior 0.5 if none |
| final_score | Weighted combined score (0.6 / 0.4) |

Index (performance):
```sql
CREATE INDEX IF NOT EXISTS artists_embedding_idx
ON artists USING hnsw (embedding vector_cosine_ops);
```

Embedding Parameter Format:
- When calling directly: `'[v1, v2, ...]'::vector(1536)` or use an existing stored embedding.

Example Direct Query:
```sql
SELECT * FROM rank_artists_by_embedding(
  (SELECT embedding FROM artists WHERE artist_name = 'Ariana Grande' LIMIT 1),
  false,
  10,
  0.3
);
```

---
## 5. Running the Local Server
From project root or `backend` folder (ensure `.env` exists one directory up if required by your `server.js` path logic):
```powershell
# Install deps
npm install

# Start with auto-reload
npx nodemon server.js

# Or plain Node
node server.js
```
Server should log listening port (default 5000). Confirm with:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
```
Expect JSON like:
```json
{ "status": "ok" }
```

---
## 6. Testing the /match Endpoint
### 6.1 PowerShell (Recommended for Windows)
```powershell
$body = '{
  "tags": "hip hop, r&b, melodic",
  "top_n": 5,
  "min_similarity": 0.3,
  "only_successful": false
}'
Invoke-RestMethod -Uri "http://localhost:5000/match" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6
```

### 6.2 curl (Git Bash / WSL / PowerShell with quoting care)
```powershell
curl -X POST http://localhost:5000/match `
  -H "Content-Type: application/json" `
  -d '{"tags":"hip hop, r&b, melodic","top_n":5,"min_similarity":0.3}'
```
(For PowerShell native quoting, escaping can be tricky; Invoke-RestMethod is simpler.)

### 6.3 Persist an Artist While Querying
```powershell
$body = '{
  "tags": "afrobeat, dance, rhythmic",
  "top_n": 10,
  "persist_artist": true,
  "artist_name": "New Query Artist"
}'
Invoke-RestMethod -Uri "http://localhost:5000/match" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6
```
This will upsert into `artists` (ensuring embedding is stored for future similarity queries).

### 6.4 Filtering to Artists With Successful Collabs Only
```powershell
$body = '{
  "tags": "pop, vocal, energetic",
  "only_successful": true,
  "top_n": 10
}'
Invoke-RestMethod -Uri "http://localhost:5000/match" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6
```

### 6.5 Python Script (Example)
Create a quick test (already have `scripts/test_dynamic_match.py`):
```python
import requests
payload = {"tags": "indie rock, atmospheric", "top_n": 3}
r = requests.post("http://localhost:5000/match", json=payload)
print(r.json())
```
Run:
```powershell
python scripts\test_dynamic_match.py
```

---
## 7. Interpreting Results
- `semantic_similarity`: Range 0→1 (higher is closer)
- `historical_success`: Empirical success ratio or 0.5 prior if no collaborations
- `final_score`: Weighted blend; drives recommendation label
- `recommendation`: Human-readable tier

Score Thresholds (current):
| Range | Label |
|-------|-------|
| >= 0.7 | HIGHLY RECOMMENDED |
| 0.5 – 0.69 | GOOD MATCH |
| < 0.5 | RISKY |

---
## 8. Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| 500 error: RPC failed | Function name mismatch or not deployed | Re-run SQL in Supabase SQL editor; confirm function exists. |
| Missing env error | `.env` not loaded or wrong path | Ensure `server.js` loads correct relative path, restart server. |
| Empty matches | `min_similarity` too high or sparse embeddings | Lower `min_similarity` (e.g., 0.2) or verify embeddings stored. |
| PowerShell JSON parse problems | Incorrect quoting/escaping | Use multi-line single-quoted string or `Invoke-RestMethod` as shown. |
| Low historical success everywhere | Sparse `maindb` data | Add more collaboration records; consider Bayesian smoothing later. |
| Upsert warning | Unique constraint conflict details | Check `artists` table; confirm `artist_name` is correct. |

---
## 9. Next Suggested Enhancements
1. Add Bayesian smoothing (e.g., `(successes + α) / (total + α + β)`).
2. Include tag overlap count in RPC output for interpretability.
3. Add caching layer for repeated identical tag queries.
4. Parameterize weights in `rank_artists_by_embedding` (e.g., `semantic_w`, `history_w`).

---
## 10. Quick Reference Summary
| Component | File | Purpose |
|-----------|------|---------|
| `/match` route | `backend/routes/match.js` | Orchestrates embedding → RPC → response decoration |
| Ranking RPC | `rank_artists_by_embedding` | Core blended scoring logic in Postgres |
| Legacy functions | `find_compatible_artists`, `match_artists_with_history`, `match_artists_combined_score` | Earlier/alternative scoring paths |
| HNSW index | `artists_embedding_idx` | Performance acceleration for similarity search |
| Test script | `scripts/test_dynamic_match.py` | Programmatic endpoint verification |

---
## 11. Sample Minimal End-to-End Flow
```powershell
# 1. Start server
npx nodemon server.js

# 2. Query for matches
$body = '{"tags":"lofi, chill, ambient","top_n":5}'
Invoke-RestMethod -Uri "http://localhost:5000/match" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6
```

---
If you need additional metrics or fields surfaced, extend the SQL (add columns) and adjust the mapping in `match.js`.

*Document last updated: 2025-11-13*
