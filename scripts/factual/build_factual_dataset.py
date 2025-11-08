import csv
import os
import random
import argparse
import re
import json
import signal
import sys
from typing import List, Dict, Tuple

from tqdm import tqdm

from .config import (
    TARGET_ROWS,
    DISCOVER_FROM_MB,
    DISCOVERY_TAGS,
    ARTISTS_PER_TAG,
    MAX_RECORDINGS_PER_PAIR,
    MAX_CANDIDATE_PAIRS,
)
from .musicbrainz_client import (
    search_recordings_by_two_artists,
    get_artist_info,
    search_artists_by_tag,
)
from .labeler import label_success

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(os.path.dirname(PROJECT_ROOT), "data")
OUT_PATH = os.path.join(OUT_DIR, "artist_collaborations_factual.csv")

CURATED_ARTISTS = [
    # Pop
    "The Weeknd", "Ariana Grande", "Taylor Swift", "Dua Lipa", "Ed Sheeran", "Shawn Mendes", "Camila Cabello", "Lady Gaga", "Katy Perry", "Justin Bieber",
    # Hip-hop
    "Kendrick Lamar", "Drake", "Nicki Minaj", "Kanye West", "Travis Scott", "J. Cole", "Megan Thee Stallion", "Cardi B", "Doja Cat", "Eminem",
    # Rock/Alt
    "Coldplay", "Imagine Dragons", "Linkin Park", "Metallica", "Muse", "Arctic Monkeys", "Paramore", "Tame Impala",
    # EDM
    "Calvin Harris", "David Guetta", "Avicii", "Marshmello", "Zedd", "Kygo", "Skrillex", "Diplo", "The Chainsmokers",
    # R&B
    "SZA", "H.E.R.", "Usher", "Alicia Keys", "Beyoncé", "Rihanna",
    # Country
    "Luke Combs", "Carrie Underwood", "Kacey Musgraves",
    # Afrobeat
    "Burna Boy", "Wizkid", "Tems", "Rema",
    # K-pop
    "BTS", "BLACKPINK", "NewJeans", "SEVENTEEN",
    # Latin
    "Bad Bunny", "J Balvin", "Shakira", "Karol G", "Daddy Yankee", "Luis Fonsi",
]

# Minimal tags and region lookup (kept short; optional enhancement: enrich via MusicBrainz artist lookups)
ARTIST_TAGS = {
    "The Weeknd": "pop, R&B, synthwave, alternative",
    "Ariana Grande": "pop, soul, dance, mainstream",
    "Taylor Swift": "pop, country, singer-songwriter",
    "Dua Lipa": "pop, dance, disco",
    "Ed Sheeran": "pop, singer-songwriter, acoustic",
    "Shawn Mendes": "pop, acoustic, soft rock",
    "Camila Cabello": "Latin pop, R&B, dance",
    "Lady Gaga": "pop, dance, electronic",
    "Katy Perry": "pop, dance, mainstream",
    "Justin Bieber": "pop, R&B, dance-pop",
    "Kendrick Lamar": "hip hop, conscious, jazz rap",
    "Drake": "hip hop, pop rap, R&B",
    "Nicki Minaj": "hip hop, pop, rap",
    "Kanye West": "hip hop, experimental, gospel",
    "Travis Scott": "trap, psychedelic, hip hop",
    "J. Cole": "hip hop, conscious, soul",
    "Megan Thee Stallion": "hip hop, Southern, pop rap",
    "Cardi B": "hip hop, pop rap, Latin",
    "Doja Cat": "pop rap, R&B, dance",
    "Eminem": "hip hop, rap, mainstream",
    "Coldplay": "alternative rock, pop rock, arena",
    "Imagine Dragons": "pop rock, alternative, arena",
    "Linkin Park": "nu metal, alternative rock, rap rock",
    "Metallica": "metal, hard rock, thrash",
    "Muse": "alternative rock, prog, electronic",
    "Arctic Monkeys": "indie rock, garage, alternative",
    "Paramore": "pop punk, emo, alternative",
    "Tame Impala": "psychedelic, indie, synth",
    "Calvin Harris": "EDM, house, dance, pop",
    "David Guetta": "EDM, house, dance, pop",
    "Avicii": "EDM, progressive house, dance",
    "Marshmello": "EDM, future bass, pop",
    "Zedd": "EDM, electro house, pop",
    "Kygo": "EDM, tropical house, chill",
    "Skrillex": "EDM, dubstep, bass",
    "Diplo": "EDM, dancehall, trap",
    "The Chainsmokers": "EDM, pop, dance",
    "SZA": "R&B, alt R&B, neo-soul",
    "H.E.R.": "R&B, soul, contemporary",
    "Usher": "R&B, pop, dance",
    "Alicia Keys": "R&B, soul, piano",
    "Beyoncé": "R&B, pop, soul",
    "Rihanna": "pop, R&B, dance",
    "Luke Combs": "country, contemporary",
    "Carrie Underwood": "country, pop",
    "Kacey Musgraves": "country, pop, folk",
    "Burna Boy": "Afrobeats, dancehall, reggae",
    "Wizkid": "Afrobeats, pop, R&B",
    "Tems": "Afrobeats, alt R&B, soul",
    "Rema": "Afrobeats, trap, pop",
    "BTS": "K-pop, pop, hip hop",
    "BLACKPINK": "K-pop, pop, EDM",
    "NewJeans": "K-pop, pop, R&B",
    "SEVENTEEN": "K-pop, pop, performance",
    "Bad Bunny": "Latin trap, reggaeton, pop",
    "J Balvin": "reggaeton, Latin pop, urbano",
    "Shakira": "Latin pop, dance, world",
    "Karol G": "reggaeton, Latin pop, urbano",
    "Daddy Yankee": "reggaeton, Latin, urbano",
    "Luis Fonsi": "Latin pop, ballad, dance",
}

REGION_DEFAULT = "Global"


def map_country_to_region(country: str) -> str:
    if not country:
        return REGION_DEFAULT
    country = country.upper()
    if country in {"US", "CA"}:
        return "US"
    if country in {"GB", "UK", "IE"}:
        return "UK"
    if country in {"DE", "FR", "SE", "NO", "FI", "DK", "NL", "BE", "IT", "ES", "PT", "PL", "AT", "CH"}:
        return "Europe"
    if country in {"NG", "ZA", "GH", "KE", "TZ", "ET"}:
        return "Africa"
    if country in {"MX", "AR", "BR", "CL", "CO", "PE", "VE", "PR"}:
        return "Latin America"
    if country in {"KR", "JP", "CN", "IN", "SG", "PH", "TH"}:
        return "Asia"
    if country in {"AU", "NZ"}:
        return "Asia"
    return REGION_DEFAULT


def discover_artists() -> List[str]:
    if not DISCOVER_FROM_MB:
        return CURATED_ARTISTS
    discovered: List[str] = []
    seen = set()
    tags = [t.strip() for t in DISCOVERY_TAGS.split(",") if t.strip()]
    for tag in tags:
        arts = search_artists_by_tag(tag, limit=ARTISTS_PER_TAG)
        for a in arts:
            name = a.get("name")
            if name and name.lower() not in seen:
                seen.add(name.lower())
                discovered.append(name)
    # Always include curated fallback set
    for name in CURATED_ARTISTS:
        if name.lower() not in seen:
            seen.add(name.lower())
            discovered.append(name)
    return discovered


def pick_pairs(artists: List[str], n: int) -> List[Tuple[str, str]]:
    pairs = set()
    attempts = 0
    while len(pairs) < n and attempts < n * 10:
        if len(artists) < 2:
            break
        a1, a2 = random.sample(artists, 2)
        key = tuple(sorted([a1, a2]))
        pairs.add(key)
        attempts += 1
    return list(pairs)


def write_pairs_file(pairs: List[Tuple[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Artist_01", "Artist_02"])
        for a1, a2 in pairs:
            writer.writerow([a1, a2])


def read_pairs_file(path: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    if not os.path.exists(path):
        raise FileNotFoundError(f"Pairs file not found: {path}")
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if not rows:
            return pairs
        # Detect header optionally
        start_idx = 0
        header = [c.strip().lower() for c in rows[0]]
        if len(header) >= 2 and ("artist_01" in header[0] and "artist_02" in header[1] or "artist1" in header[0] and "artist2" in header[1]):
            start_idx = 1
        for r in rows[start_idx:]:
            if len(r) < 2:
                continue
            a1 = r[0].strip()
            a2 = r[1].strip()
            if a1 and a2 and a1.lower() != a2.lower():
                key = tuple(sorted([a1, a2]))
                pairs.append(key)
    # Deduplicate while preserving order
    seen = set()
    unique_pairs: List[Tuple[str, str]] = []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            unique_pairs.append(p)
    return unique_pairs


def normalize_title(title: str) -> str:
    """Normalize song title by removing variants like (instrumental), [remix], etc."""
    # Convert to lowercase
    title = title.lower().strip()
    
    # Normalize apostrophes and quotes (many Unicode variants)
    title = title.replace("'", "'").replace("'", "'").replace("`", "'")
    title = title.replace(""", '"').replace(""", '"').replace("«", '"').replace("»", '"')
    
    # Remove content in parentheses and brackets (often variants/features)
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^\]]*\]', '', title)
    
    # Remove common separators and extra content after colon/dash
    # But keep the main title before these markers
    parts = re.split(r'[:|–—]', title)
    if parts:
        title = parts[0]  # Keep only the part before : or —
    
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Remove trailing punctuation
    title = title.rstrip('.,;:-–—!?')
    
    # Remove accents for better matching (optional - keeps "día" = "dia")
    # Uncomment if you want stricter matching:
    # import unicodedata
    # title = ''.join(c for c in unicodedata.normalize('NFD', title) if unicodedata.category(c) != 'Mn')
    
    return title


def deduplicate_recordings(recs: List[Dict]) -> List[Dict]:
    """Keep only one recording per unique normalized title, preferring the one with most releases."""
    title_groups: Dict[str, List[Dict]] = {}
    for rec in recs:
        norm_title = normalize_title(rec["title"])
        if norm_title not in title_groups:
            title_groups[norm_title] = []
        title_groups[norm_title].append(rec)
    
    # Pick the best variant from each group (most releases, then earliest year)
    best_recs: List[Dict] = []
    for norm_title, group in title_groups.items():
        # Sort by: release_count desc, then year asc (earliest), then title length asc (shortest/canonical)
        best = sorted(
            group,
            key=lambda r: (
                -r.get("release_count", 0),
                int(r.get("year") or "9999"),
                len(r["title"])
            )
        )[0]
        best_recs.append(best)
    
    return best_recs


def main():
    parser = argparse.ArgumentParser(description="Build factual artist collaboration dataset from MusicBrainz")
    parser.add_argument("--pairs-file", type=str, default=None, help="Path to CSV file with columns: Artist_01,Artist_02 to use as input pairs")
    parser.add_argument("--num-pairs", type=int, default=None, help="If set, generate this many unique artist pairs (overrides heuristic caps)")
    parser.add_argument("--dump-pairs", type=str, default=None, help="If set, write the generated candidate pairs to this CSV path before building")
    parser.add_argument("--only-dump-pairs", action="store_true", help="Only generate and write pairs, then exit without building the dataset")
    parser.add_argument("--out", type=str, default=OUT_PATH, help="Output CSV path for the resulting dataset")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to checkpoint file for resume capability (default: auto-generated)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint if it exists")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    
    # Setup checkpoint file
    out_path = args.out or OUT_PATH
    if args.checkpoint:
        checkpoint_path = args.checkpoint
    else:
        # Auto-generate checkpoint name based on output file
        checkpoint_path = out_path.replace(".csv", "_checkpoint.json")
    
    # Load checkpoint if resuming
    checkpoint_data = {}
    if args.resume and os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)
            print(f"Resuming from checkpoint: {checkpoint_path}")
            print(f"  Pairs processed: {checkpoint_data.get('pairs_processed', 0)}")
            print(f"  Rows collected: {len(checkpoint_data.get('rows', []))}")
        except Exception as e:
            print(f"Warning: Could not load checkpoint ({e}), starting fresh")
            checkpoint_data = {}

    header = [
        "Artist_01",
        "Artist_01_Tags",
        "Artist_02",
        "Artist_02_Tags",
        "Song_Title",
        "Collaboration_Status",
        "Release_Year",
        "Region",
        "MB_Rating_Value",
        "MB_Rating_Votes",
        "Peak_Chart_Position",
    ]

    rows: List[List[str]] = checkpoint_data.get("rows", [])
    used_pairs = set(tuple(p) for p in checkpoint_data.get("used_pairs", []))
    # Determine target pairs: either read from file or discover+sample
    if args.pairs_file:
        target_pairs = read_pairs_file(args.pairs_file)
        if not target_pairs:
            print(f"No pairs loaded from {args.pairs_file}")
            return
    else:
        all_artists = discover_artists()
        # Target pairs; either explicit or heuristic scaling
        if args.num_pairs and args.num_pairs > 0:
            candidate_pairs = args.num_pairs
        else:
            candidate_pairs = max(200, min(MAX_CANDIDATE_PAIRS, TARGET_ROWS * 10))
        target_pairs = pick_pairs(all_artists, candidate_pairs)

    # Optionally dump pairs to a CSV for a two-phase workflow
    if args.dump_pairs:
        write_pairs_file(target_pairs, args.dump_pairs)
        print(f"Wrote {len(target_pairs)} pairs to {args.dump_pairs}")
        if args.only_dump_pairs:
            return

    # Setup checkpoint save function
    def save_checkpoint():
        try:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump({
                    "rows": rows,
                    "used_pairs": [list(p) for p in used_pairs],
                    "pairs_processed": len(used_pairs),
                    "target_rows": TARGET_ROWS,
                }, f, ensure_ascii=False)
        except Exception as e:
            print(f"\nWarning: Could not save checkpoint: {e}")
    
    # Setup graceful interrupt handler
    interrupted = False
    def signal_handler(sig, frame):
        nonlocal interrupted
        interrupted = True
        print("\n\nInterrupted! Saving checkpoint...")
        save_checkpoint()
        print(f"Checkpoint saved to: {checkpoint_path}")
        print(f"Resume with: --resume --checkpoint {checkpoint_path}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Skip already processed pairs if resuming
    start_idx = checkpoint_data.get("pairs_processed", 0)
    if start_idx > 0:
        print(f"Skipping first {start_idx} pairs (already processed)")
    
    # Progress bars: pairs scanned and rows produced
    pairs_bar = tqdm(total=len(target_pairs), desc="Pairs", unit="pair", initial=start_idx)
    rows_bar = tqdm(total=TARGET_ROWS, desc="Rows", unit="row", initial=len(rows))

    pairs_processed = start_idx
    for (a1, a2) in target_pairs[start_idx:]:
        if interrupted:
            break
            
        key = tuple(sorted([a1.lower(), a2.lower()]))
        if key in used_pairs:
            pairs_bar.update(1)
            pairs_processed += 1
            continue
        # First, search for actual collaboration recordings (saves extra artist lookups when none found)
        recs = search_recordings_by_two_artists(a1, a2, limit=MAX_RECORDINGS_PER_PAIR)
        if not recs:
            pairs_bar.update(1)
            pairs_processed += 1
            continue
        
        # Deduplicate recordings by normalized title (remove instrumental/remix/etc variants)
        recs = deduplicate_recordings(recs)
        
        # Enrich artist info only when we have at least one recording
        info1 = get_artist_info(a1)
        info2 = get_artist_info(a2)
        tags1 = (info1.get("tags") or ARTIST_TAGS.get(a1, "pop")).split(", ")
        tags2 = (info2.get("tags") or ARTIST_TAGS.get(a2, "pop")).split(", ")
        tags1 = tags1[:6]
        tags2 = tags2[:6]
        region = map_country_to_region(info1.get("country") or info2.get("country"))

        for rec in recs:
            # Use only MusicBrainz signals (ratings, YouTube links, release count) for Success/Failure
            status = label_success(
                None,
                rating_value=rec.get("rating_value"),
                rating_votes=rec.get("rating_votes"),
                has_youtube=bool(rec.get("youtube_video_ids")),
                release_count=rec.get("release_count", 0),
            )

            rows.append([
                a1, ", ".join(tags1),
                a2, ", ".join(tags2),
                rec["title"],
                status,
                str(rec["year"]) if rec["year"] else "",
                region,
                str(rec.get("rating_value")) if rec.get("rating_value") is not None else "",
                str(rec.get("rating_votes")) if rec.get("rating_votes") is not None else "",
                "",  # peak unknown in this pass
            ])
            rows_bar.update(1)
            if len(rows) >= TARGET_ROWS:
                break
        used_pairs.add(key)
        pairs_bar.update(1)
        pairs_processed += 1
        
        # Save checkpoint every 10 pairs
        if pairs_processed % 10 == 0:
            save_checkpoint()
        
        if len(rows) >= TARGET_ROWS:
            break

    # Final deduplication at row level by normalized title + artist pair
    # Keep only the best variant of each song (prefer Success status, then most complete metadata)
    song_map: Dict[Tuple[str, Tuple[str, str]], List[str]] = {}  # (normalized_title, artist_pair) -> best_row
    
    for row in rows:
        # Create a key from normalized title and sorted artist names
        title_norm = normalize_title(row[4])  # Song_Title is at index 4
        artist_key = tuple(sorted([row[0].lower(), row[2].lower()]))  # Artist_01, Artist_02
        song_key = (title_norm, artist_key)
        
        if song_key in song_map:
            # Compare with existing entry - keep better one
            existing = song_map[song_key]
            
            # Prefer Success over Failure
            if row[5] == "Success" and existing[5] != "Success":
                song_map[song_key] = row
            elif row[5] == existing[5]:
                # If same status, prefer one with more metadata (year, ratings, etc.)
                existing_data_count = sum(1 for x in existing[6:10] if x)
                new_data_count = sum(1 for x in row[6:10] if x)
                if new_data_count > existing_data_count:
                    song_map[song_key] = row
        else:
            # New song - add it
            song_map[song_key] = row
    
    # Convert back to list
    final_rows = list(song_map.values())
    
    # Write CSV (quote all fields)
    out_path = args.out or OUT_PATH
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(final_rows[:TARGET_ROWS])  # Ensure we don't exceed target

    # Close progress bars cleanly
    pairs_bar.close()
    rows_bar.close()

    print("Wrote factual CSV:", out_path)
    print("Rows:", len(final_rows[:TARGET_ROWS]))
    
    # Clean up checkpoint file on successful completion
    if os.path.exists(checkpoint_path):
        try:
            os.remove(checkpoint_path)
            print(f"Checkpoint file removed: {checkpoint_path}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
