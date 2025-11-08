# Artist Collaboration Dataset Generator

This project generates a CSV dataset of artist collaborations labeled by success, with tags and optional metadata.

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
