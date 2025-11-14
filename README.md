# MatchColab - Artist Collaboration Matchmaker

A full-stack application that helps artists find the perfect collaborators based on their music style using AI embeddings and historical collaboration data.

## 🌟 Features

### Web Application
- **Modern Frontend UI**: Beautiful, responsive interface with real-time health monitoring
- **AI-Powered Matching**: Uses OpenAI embeddings to find semantically similar artists
- **Historical Analysis**: Leverages past collaboration success/failure data
- **Advanced Filtering**: Customize results by similarity threshold and success rate
- **Artist Profiles**: Save your profile for future matching

### API Endpoints
- `GET /` - Web interface
- `GET /health` - System health check with database and API verification
- `POST /match` - Find artist matches based on style tags

## 🚀 Quick Start

### Prerequisites
- Node.js 20.x
- Supabase account (for database)
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/rawleyc/MatchColab.git
cd MatchColab
```

2. **Install backend dependencies**
```bash
cd backend
npm install
```

3. **Set up environment variables**

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
PORT=5000
CORS_ORIGIN=  # Optional: comma-separated allowed origins for production
```

4. **Start the server**
```bash
npm run dev  # Development with auto-reload
# or
npm start    # Production
```

5. **Open your browser**

Navigate to `http://localhost:5000`

## 📖 Usage

### Web Interface

1. Enter your music style tags (e.g., "pop, r&b, contemporary r&b")
2. Adjust parameters:
   - Number of results (1-50)
   - Minimum similarity threshold (0-1)
   - Filter by successful collaborations only
3. Optionally save your artist profile
4. Click "Find Matches" to get recommendations

### API Usage

**Find Matches:**
```bash
curl -X POST http://localhost:5000/match \
  -H "Content-Type: application/json" \
  -d '{
    "tags": "pop, r&b",
    "top_n": 10,
    "min_similarity": 0.3,
    "only_successful": false,
    "artist_name": "Your Name",
    "persist_artist": false
  }'
```

**Check Health:**
```bash
curl http://localhost:5000/health
```

## 🏗️ Architecture

### Backend (`/backend`)
- **Express.js** server with RESTful API
- **Supabase** for vector database and collaboration history
- **OpenAI** embeddings for semantic similarity
- Static file serving for frontend

### Frontend (`/frontend`)
- Pure HTML/CSS/JavaScript (no build required)
- Modern dark theme with responsive design
- Real-time health monitoring
- Smooth animations and transitions

### Database Schema
- **artists** table: Artist profiles with embeddings
- **maindb** table: Historical collaboration records
- **rank_artists_by_embedding** function: Vector similarity search

## 📊 Scoring System

The matching algorithm combines two key factors:

1. **Semantic Similarity (60%)**: Cosine similarity between tag embeddings
2. **Historical Success Rate (40%)**: Based on past collaboration outcomes

**Recommendation Levels:**
- **≥ 0.7**: HIGHLY RECOMMENDED - Strong compatibility
- **0.5-0.7**: GOOD MATCH - Moderate compatibility  
- **< 0.5**: RISKY - Lower compatibility, but innovative potential

## 📁 Project Structure

```
MatchColab/
├── backend/
│   ├── server.js           # Express server & routes
│   ├── routes/
│   │   └── match.js        # Match endpoint logic
│   └── package.json
├── frontend/
│   ├── index.html          # Web UI
│   ├── styles.css          # Styling
│   ├── app.js              # Frontend logic
│   └── README.md           # Frontend documentation
├── data/                   # Dataset files
├── scripts/                # Data generation scripts
└── README.md               # This file
```

## 🚢 Deployment

See [DEPLOY_RENDER.md](DEPLOY_RENDER.md) for detailed deployment instructions on Render.

### Quick Deploy to Render

1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy using the included `render.yaml` blueprint
4. Health checks run automatically at `/health`

## 🔧 Development

### Running Tests
```bash
cd backend
npm test
```

### Environment Setup
- Node.js 20.x required
- All dependencies managed via npm
- Environment variables in `.env` (never commit this file)

## 📚 Additional Documentation

- [Frontend Documentation](frontend/README.md)
- [Deployment Guide](DEPLOY_RENDER.md)
- [Matchmaker System Details](MATCHMAKER_README.md)
- [Database Setup](PGVECTOR_GUIDE.md)

## 🛡️ Security

- Never commit `.env` files
- Use `SUPABASE_SERVICE_KEY` only on backend
- Set `CORS_ORIGIN` in production to restrict frontend access
- Rotate API keys regularly

## 📄 License

MIT

---

# Artist Collaboration Dataset Generator

This project also includes tools to generate CSV datasets of artist collaborations labeled by success, with tags and optional metadata.

Deliverable: `data/artist_collaborations.csv` (synthetic demo, UTF-8) and `data/artist_collaborations_factual.csv` (built from live sources when configured)

Columns:
- Artist_01
- Artist_01_Tags
- Artist_02
- Artist_02_Tags
- Song_Title
- Collaboration_Status ("Success" | "Failure")
- Release_Year
- Region (US, UK, Europe, Africa, Latin America, Asia, Global)
- Peak_Chart_Position (numeric for successes when available, blank otherwise)

Notes and assumptions:
- A small seed of well-known real collaborations is included with confident labels.
- The remainder is synthesized to meet scale, balance (≈60/40), uniqueness, and diversity requirements. Titles for synthetic rows are plausible but not tied to a specific real-world track.
- Use this dataset for modeling, prototyping, or educational analysis. If you need strictly factual rows only, expand the seed list and reduce synthesis.

How to generate (synthetic demo)

Windows PowerShell:

```
# Create/refresh the CSV
python .\scripts\generate_collab_dataset.py

# Quick check: row count and class balance are printed at the end
```

Validation snippets (optional)

```
# Count rows (including header) and show first 5 lines
python - << 'PY'
import csv, pathlib
p = pathlib.Path('data/artist_collaborations.csv')
with p.open('r', encoding='utf-8') as f:
    rows = list(csv.reader(f))
print('Total lines (incl header):', len(rows))
print('Header:', rows[0])
for r in rows[1:6]:
    print(r)
PY
```

License: The generated CSV is provided for educational and research purposes. Song titles and artist names appearing in seed rows are factual references.

Factual dataset pipeline (MusicBrainz + YouTube)

Overview
- Discovers real collaboration tracks from MusicBrainz by searching for recordings credited to two artists.
- Labels Success using YouTube view counts (>= 50M views => Success). Peak chart positions can be added later via Wikipedia parsing if needed.
- **NEW: Checkpoint/Resume support** to prevent data loss from interruptions or connectivity issues

Setup
1) Install dependencies into your environment
```
pip install -r requirements.txt
```
2) Set environment variables (PowerShell)
```
$env:MB_USERNAME = "DartMouthWrld"  # your MusicBrainz username
# Optional: override full UA; otherwise default is: CollabDataset/1.0 (MusicBrainz user: DartMouthWrld)
# $env:MB_USER_AGENT = "YourAppName/1.0 (contact-url-or-email)"
# Optional, for YouTube view counts
$env:YOUTUBE_API_KEY = "<your-youtube-data-api-key>"
# Optional, change output size (default 600)
$env:FACTUAL_TARGET_ROWS = "600"
```
3) Run the factual builder (as a module so package imports work)
```
& "C:/Users/chiru/OneDrive/Documents/cOdiNG ProJeCTs/LeArnING PytHON/.venv/Scripts/python.exe" -m scripts.factual.build_factual_dataset
```

Checkpoint/Resume Feature
To protect against connectivity issues or interruptions:

**Automatic checkpointing:**
- Progress is saved every 10 pairs processed
- Checkpoint file created automatically (same name as output + `_checkpoint.json`)
- On Ctrl+C interrupt, checkpoint is saved before exit

**Resume from checkpoint:**
```powershell
# If interrupted, resume with:
$env:FACTUAL_TARGET_ROWS = "500"
& "C:/Users/chiru/OneDrive/Documents/cOdiNG ProJeCTs/LeArnING PytHON/.venv/Scripts/python.exe" -m scripts.factual.build_factual_dataset --pairs-file data\artist_pairs_curated_high_prob.csv --out data\artist_collaborations_500.csv --resume
```

**Custom checkpoint location:**
```powershell
# Specify custom checkpoint file:
... --checkpoint data\my_checkpoint.json --resume
```

**What's saved in checkpoint:**
- All collected rows so far
- Processed artist pairs (to skip on resume)
- Progress counters
- Target row count

The checkpoint file is automatically deleted on successful completion.

Notes
- The MusicBrainz API requires a polite User-Agent; this project defaults to including your username (MB_USERNAME) in the UA. You may also set MB_USER_AGENT directly.
- If YOUTUBE_API_KEY is not provided, the script will still discover real collaborations but will default most rows to Failure (no view signal). Provide the key to get meaningful Success labels.
- The script currently sets Region="Global" and leaves Peak_Chart_Position blank. If you want peak chart data, we can add a Wikipedia-based enrichment step.

Optional: OAuth redirect URL
- Read-only fetching from MusicBrainz does not require OAuth. If you plan to perform user actions (e.g., edit collections), register a callback like:
    - Development Flask: http://localhost:5000/musicbrainz/callback
    - Node/Express: http://localhost:3000/auth/musicbrainz/callback
    - Postman: https://oauth.pstmn.io/v1/callback
