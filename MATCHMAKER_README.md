# Artist Collaboration Matchmaker System

## Overview

This system helps find the best artist matches for collaborations by combining:
1. **Semantic Similarity** - Uses OpenAI embeddings to match music styles
2. **Historical Patterns** - Analyzes past collaboration successes/failures

## Architecture

### Databases
- **`artists` table** - Contains artists with their tags and embeddings
- **`maindb` table** - Historical collaboration records (success/failure)

### Scoring System
- **Semantic Similarity (60%)** - Cosine similarity between tag embeddings
- **Historical Success Rate (40%)** - Weighted by similar genre combinations
- **Combined Score** - Final compatibility score (0-1)

## Files

### 1. `artist_matchmaker.py` (CLI Version)
Interactive command-line tool for finding artist matches.

**Usage:**
```bash
python artist_matchmaker.py
```

Then enter your tags when prompted:
```
Example: pop, dance-pop, r&b, contemporary r&b
```

**Output:**
- Top 10 artist matches
- Semantic similarity score
- Historical success rate
- Combined compatibility score
- Recommendations

---

### 2. `api_matchmaker.py` (API Version)
FastAPI REST API for integration with web applications.

**Start the API:**
```bash
python api_matchmaker.py
```
or
```bash
uvicorn api_matchmaker:app --reload
```

**Endpoints:**

#### GET `/`
Returns API information

#### GET `/health`
Health check endpoint

#### POST `/matches`
Find artist matches

**Request:**
```json
{
  "tags": "pop, dance-pop, r&b",
  "top_n": 10
}
```

**Response:**
```json
{
  "user_tags": "pop, dance-pop, r&b",
  "total_artists_analyzed": 66,
  "matches": [
    {
      "artist_name": "Ariana Grande",
      "artist_tags": "contemporary r&b, dance-pop, pop, r&b, trap soul",
      "semantic_similarity": 0.892,
      "historical_success_rate": 0.654,
      "combined_score": 0.797,
      "recommendation": "HIGHLY RECOMMENDED - Strong compatibility!"
    }
  ]
}
```

**Test with curl:**
```bash
curl -X POST "http://localhost:8000/matches" \
  -H "Content-Type: application/json" \
  -d '{"tags": "pop, dance-pop, r&b", "top_n": 5}'
```

---

## How It Works

### 1. Embedding Generation
User tags are converted to embeddings using OpenAI's `text-embedding-3-small` model.

### 2. Semantic Matching
Cosine similarity is computed between user embedding and all artist embeddings.

### 3. Historical Analysis
The system analyzes the collaboration history database to find:
- Similar genre combinations
- Success/failure patterns
- Weighted success probability based on tag overlap

### 4. Score Combination
```
Combined Score = (0.6 × Semantic Similarity) + (0.4 × Historical Success Rate)
```

You can adjust these weights in the code based on your preference.

### 5. Ranking
Artists are ranked by combined score, returning the top N matches.

---

## Recommendation Levels

| Score Range | Recommendation | Meaning |
|------------|----------------|---------|
| ≥ 0.7 | HIGHLY RECOMMENDED | Strong compatibility based on both style match and historical success |
| 0.5 - 0.7 | GOOD MATCH | Moderate compatibility, decent chance of success |
| < 0.5 | RISKY | Lower compatibility, but could lead to innovative combinations |

---

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

3. Ensure your Supabase databases are set up:
   - `artists` table with embeddings populated
   - `maindb` table with collaboration history

---

## Example Use Cases

### CLI Example
```
$ python artist_matchmaker.py

Enter your music style tags (comma-separated):
Example: pop, dance-pop, r&b, contemporary r&b

Your tags: hip hop, trap, southern hip hop

Finding best artist matches...

TOP 10 ARTIST MATCHES
=====================

1. Travis Scott
   Tags: experimental hip hop, hip hop, pop rap, southern hip hop, trap
   📊 Combined Score: 0.845
   🎯 Semantic Similarity: 0.921
   📈 Historical Success Rate: 0.712
   ✅ HIGHLY RECOMMENDED - Strong compatibility!
```

### API Example (Python)
```python
import requests

response = requests.post(
    "http://localhost:8000/matches",
    json={"tags": "hip hop, trap, southern hip hop", "top_n": 5}
)

matches = response.json()
for match in matches['matches']:
    print(f"{match['artist_name']}: {match['combined_score']}")
```

---

## Customization

### Adjust Score Weights
In both `artist_matchmaker.py` and `api_matchmaker.py`, modify:

```python
# Current: 60% semantic, 40% historical
combined_score = (0.6 * similarity) + (0.4 * historical_score)

# Example: Prioritize historical data more
combined_score = (0.4 * similarity) + (0.6 * historical_score)
```

### Change Number of Results
```python
# CLI version
matches = find_best_matches(user_tags, top_n=20)  # Get 20 matches

# API version - set default
top_n: Optional[int] = 20  # Change default from 10 to 20
```

---

## Performance

- **Embedding Generation**: ~200-500ms per request
- **Database Queries**: ~100-300ms total
- **Similarity Computation**: ~50-100ms for 66 artists
- **Total Response Time**: ~500ms - 1s

For production with thousands of artists, consider:
- Caching embeddings
- Pre-computing similarity matrices
- Using vector databases (Pinecone, Weaviate)

---

## Future Enhancements

1. **Machine Learning Model**: Train a model on historical data for better predictions
2. **Feature Engineering**: Add more features (release year, chart position, etc.)
3. **User Feedback Loop**: Learn from user selections to improve recommendations
4. **Collaborative Filtering**: Add user-based recommendations
5. **A/B Testing**: Test different scoring weight combinations

---

## Troubleshooting

**"No artists with embeddings found"**
- Run `upload_artist_embeddings_v2.py` to populate embeddings

**"Error fetching collaboration history"**
- Check Supabase credentials in `.env`
- Verify `maindb` table exists and has data

**"Error generating embedding"**
- Verify OPENAI_API_KEY is valid
- Check internet connection

---

## License
MIT

## Author
Built with ❤️ for artist collaboration matching
