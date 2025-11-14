# MatchColab - Quick Start Guide

This guide will help you get started with the MatchColab Artist Collaboration Finder.

## 🚀 Starting the Application

### 1. Install Dependencies

```bash
cd backend
npm install
```

### 2. Configure Environment

Create a `.env` file in the root directory with your credentials:

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
PORT=5000
```

### 3. Start the Server

**Development mode (with auto-reload):**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

You should see:
```
✅ Server running on port 5000
```

## 🌐 Accessing the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

You'll see the MatchColab web interface with:
- **Health Status** at the top showing system status
- **Find Your Match** form for searching artists

## 🎯 Finding Artist Matches

### Step 1: Enter Your Music Style

In the "Music Style Tags" field, enter comma-separated tags that describe your music style:

**Examples:**
- `pop, dance-pop, r&b`
- `hip hop, trap, southern hip hop`
- `electronic, edm, house`
- `rock, alternative rock, indie`

### Step 2: Adjust Parameters (Optional)

**Number of Results:** How many artist matches to return (1-50)
- Default: 10

**Min Similarity:** Minimum compatibility threshold (0-1)
- 0.3 (default) - More results, including experimental matches
- 0.5 - Moderate compatibility
- 0.7 - Only highly compatible matches

**Only Successful Collaborations:** Check this to filter only artists with proven collaboration success

### Step 3: Save Your Profile (Optional)

If you want to save your artist profile for future searches:
1. Enter your artist name in "Your Artist Name"
2. Check "Save my artist profile to database"

### Step 4: Find Matches

Click the **"🔍 Find Matches"** button

The system will:
1. Generate an AI embedding of your tags
2. Search the database for compatible artists
3. Rank results by compatibility score
4. Display matches with recommendations

## 📊 Understanding Results

Each match shows:

### Overall Score (0-100%)
Combined score based on:
- 60% Semantic Similarity (AI embedding match)
- 40% Historical Success Rate (past collaboration data)

### Recommendation Levels

**HIGHLY RECOMMENDED (≥70%)**
- 🟢 Strong compatibility
- Similar style and proven success
- Best collaboration potential

**GOOD MATCH (50-70%)**
- 🔵 Moderate compatibility
- Decent chance of success
- Worth exploring

**RISKY (<50%)**
- 🟡 Lower compatibility
- Could be innovative
- Experimental collaboration

### Artist Information
- Artist name
- Their music tags
- Semantic similarity percentage
- Historical success rate (if available)

## 🏥 Health Check

The health status indicator shows:

**✓ System is healthy** (Green)
- All systems operational
- Database connected
- OpenAI API configured

**⚠ System degraded** (Yellow)
- Partial functionality
- Database or API issues
- Service may be limited

**✗ System error** (Red)
- Cannot connect to server
- Major service disruption

## 🔌 Using the API Directly

### Health Check
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-14T14:30:00.000Z",
  "checks": {
    "server": "ok",
    "database": "ok",
    "openai": "configured"
  }
}
```

### Find Matches
```bash
curl -X POST http://localhost:5000/match \
  -H "Content-Type: application/json" \
  -d '{
    "tags": "pop, r&b",
    "top_n": 10,
    "min_similarity": 0.3,
    "only_successful": false
  }'
```

**Response:**
```json
{
  "user_tags": "pop, r&b",
  "parameters": {
    "top_n": 10,
    "only_successful": false,
    "min_similarity": 0.3
  },
  "matches": [
    {
      "artist_name": "Ariana Grande",
      "artist_tags": "contemporary r&b, dance-pop, pop, r&b",
      "semantic_similarity": 0.892,
      "historical_success_rate": 0.654,
      "final_score": 0.797,
      "recommendation": "HIGHLY RECOMMENDED - Strong compatibility!"
    }
  ],
  "total_matches": 10
}
```

## 🛠️ Troubleshooting

### Health shows "degraded"
- Check that `.env` file has correct Supabase credentials
- Verify OpenAI API key is valid
- Ensure Supabase database has `artists` table

### "No matches found"
- Try lowering the minimum similarity (e.g., 0.2)
- Use broader, more common tags
- Verify artists are in the database with embeddings

### Cannot connect to server
- Ensure server is running (`npm run dev`)
- Check that port 5000 is not in use
- Try a different port: `PORT=5001 npm start`

### CORS errors in browser
- In production, set `CORS_ORIGIN` in `.env`
- Example: `CORS_ORIGIN=https://yourfrontend.com`

## 📱 Browser Compatibility

The frontend works on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🚢 Deploying to Production

See [DEPLOY_RENDER.md](../DEPLOY_RENDER.md) for deployment instructions.

## 💡 Tips

1. **Start broad, then narrow**: Begin with general tags, then increase minimum similarity
2. **Mix genres**: Try combinations like "jazz, r&b" for interesting matches
3. **Save your profile**: Let other artists find you in their searches
4. **Experiment**: Lower compatibility can lead to innovative collaborations
5. **Check history**: Use "only successful" filter to see proven collaborators

## 📚 More Information

- [Frontend Documentation](README.md)
- [Main Project README](../README.md)
- [Matchmaker System Details](../MATCHMAKER_README.md)
- [Database Setup](../PGVECTOR_GUIDE.md)

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review server logs for error details
3. Verify environment variables are set correctly
4. Ensure database and API keys are valid

---

**Enjoy finding your perfect collaboration match! 🎵**
