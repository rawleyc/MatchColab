import csv
import os
import random
from datetime import datetime
from typing import List, Dict, Tuple

# Reproducible randomness
random.seed(42)

# Output path (relative to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(PROJECT_ROOT, "data")
OUT_PATH = os.path.join(OUT_DIR, "artist_collaborations.csv")

# Dataset size and balance
TOTAL_ROWS = 600  # >= 500
SUCCESS_RATIO = 0.60  # 60% success, 40% failure
TARGET_SUCCESS = int(TOTAL_ROWS * SUCCESS_RATIO)
TARGET_FAILURE = TOTAL_ROWS - TARGET_SUCCESS
YEAR_MIN, YEAR_MAX = 2000, 2025

# Regions we'll use for geographic diversity
REGIONS = [
    "US", "UK", "Europe", "Africa", "Latin America", "Asia", "Global"
]

# Core artist catalog with tags and primary region
# Note: Tags are short genre/personality descriptors (3–6 items)
ARTISTS: List[Dict[str, str]] = [
    # Pop
    {"name": "The Weeknd", "tags": "pop, R&B, synthwave, alternative", "region": "US"},
    {"name": "Ariana Grande", "tags": "pop, soul, dance, mainstream", "region": "US"},
    {"name": "Taylor Swift", "tags": "pop, country, singer-songwriter, folk", "region": "US"},
    {"name": "Dua Lipa", "tags": "pop, dance, disco, electropop", "region": "UK"},
    {"name": "Ed Sheeran", "tags": "pop, singer-songwriter, acoustic", "region": "UK"},
    {"name": "Shawn Mendes", "tags": "pop, acoustic, teen pop, soft rock", "region": "US"},
    {"name": "Camila Cabello", "tags": "Latin pop, R&B, pop, dance", "region": "Latin America"},
    {"name": "Lady Gaga", "tags": "pop, dance, electronic, theatrical", "region": "US"},
    {"name": "Katy Perry", "tags": "pop, dance, mainstream", "region": "US"},
    {"name": "Justin Bieber", "tags": "pop, R&B, dance-pop", "region": "US"},
    # Hip-hop / Rap
    {"name": "Kendrick Lamar", "tags": "hip hop, conscious rap, jazz rap", "region": "US"},
    {"name": "Drake", "tags": "hip hop, pop rap, R&B", "region": "US"},
    {"name": "Nicki Minaj", "tags": "hip hop, pop, rap, Caribbean", "region": "US"},
    {"name": "Kanye West", "tags": "hip hop, experimental, gospel, rap", "region": "US"},
    {"name": "Lil Pump", "tags": "trap, mumble rap, pop rap", "region": "US"},
    {"name": "Travis Scott", "tags": "trap, psychedelic, hip hop", "region": "US"},
    {"name": "J. Cole", "tags": "hip hop, conscious rap, soul", "region": "US"},
    {"name": "Megan Thee Stallion", "tags": "hip hop, Southern rap, pop rap", "region": "US"},
    {"name": "Cardi B", "tags": "hip hop, pop rap, Latin", "region": "US"},
    {"name": "Doja Cat", "tags": "pop rap, R&B, dance", "region": "US"},
    # Rock / Metal
    {"name": "Coldplay", "tags": "alternative rock, pop rock, arena", "region": "UK"},
    {"name": "Imagine Dragons", "tags": "pop rock, alternative, arena", "region": "US"},
    {"name": "Linkin Park", "tags": "nu metal, alternative rock, rap rock", "region": "US"},
    {"name": "Metallica", "tags": "metal, hard rock, thrash, heavy", "region": "US"},
    {"name": "Muse", "tags": "alternative rock, prog, electronic", "region": "Europe"},
    {"name": "Arctic Monkeys", "tags": "indie rock, garage, alternative", "region": "UK"},
    {"name": "Paramore", "tags": "pop punk, emo, alternative", "region": "US"},
    # EDM
    {"name": "Calvin Harris", "tags": "EDM, house, dance, pop", "region": "UK"},
    {"name": "David Guetta", "tags": "EDM, house, dance, pop", "region": "Europe"},
    {"name": "Avicii", "tags": "EDM, progressive house, dance", "region": "Europe"},
    {"name": "Marshmello", "tags": "EDM, future bass, pop", "region": "US"},
    {"name": "Zedd", "tags": "EDM, electro house, pop", "region": "US"},
    {"name": "Kygo", "tags": "EDM, tropical house, chill", "region": "Europe"},
    {"name": "Skrillex", "tags": "EDM, dubstep, bass, experimental", "region": "US"},
    {"name": "Diplo", "tags": "EDM, dancehall, trap, global bass", "region": "US"},
    # R&B / Soul
    {"name": "SZA", "tags": "R&B, alt R&B, neo-soul", "region": "US"},
    {"name": "H.E.R.", "tags": "R&B, soul, contemporary", "region": "US"},
    {"name": "Usher", "tags": "R&B, pop, dance", "region": "US"},
    {"name": "Alicia Keys", "tags": "R&B, soul, piano, pop", "region": "US"},
    {"name": "The Isley Brothers", "tags": "R&B, soul, funk, classic", "region": "US"},
    # Country
    {"name": "Luke Combs", "tags": "country, contemporary, Southern", "region": "US"},
    {"name": "Carrie Underwood", "tags": "country, pop, powerhouse", "region": "US"},
    {"name": "Kacey Musgraves", "tags": "country, pop, folk, alt", "region": "US"},
    # Afrobeat / Afropop
    {"name": "Burna Boy", "tags": "Afrobeats, dancehall, reggae, pop", "region": "Africa"},
    {"name": "Wizkid", "tags": "Afrobeats, pop, R&B", "region": "Africa"},
    {"name": "Tems", "tags": "Afrobeats, alt R&B, soul", "region": "Africa"},
    {"name": "Rema", "tags": "Afrobeats, trap, pop", "region": "Africa"},
    # K-pop
    {"name": "BTS", "tags": "K-pop, pop, hip hop, dance", "region": "Asia"},
    {"name": "BLACKPINK", "tags": "K-pop, pop, EDM, hip hop", "region": "Asia"},
    {"name": "NewJeans", "tags": "K-pop, pop, R&B", "region": "Asia"},
    {"name": "SEVENTEEN", "tags": "K-pop, pop, performance", "region": "Asia"},
    # Latin
    {"name": "Bad Bunny", "tags": "Latin trap, reggaeton, pop", "region": "Latin America"},
    {"name": "J Balvin", "tags": "reggaeton, Latin pop, urbano", "region": "Latin America"},
    {"name": "Shakira", "tags": "Latin pop, dance, world", "region": "Latin America"},
    {"name": "Karol G", "tags": "reggaeton, Latin pop, urbano", "region": "Latin America"},
    # Alt/Indie/Experimental
    {"name": "Billie Eilish", "tags": "alt pop, electropop, dark pop", "region": "US"},
    {"name": "Lorde", "tags": "alt pop, art pop, electropop", "region": "Europe"},
    {"name": "Tame Impala", "tags": "psychedelic, indie, synth, pop", "region": "Australia"},
    {"name": "Grimes", "tags": "experimental, synthpop, art pop", "region": "US"},
    {"name": "FKA twigs", "tags": "experimental, alt R&B, art pop", "region": "UK"},
]

# Known real-world collaborations we can label with high confidence
# Note: This is a SMALL seed; the generator will synthesize the rest while preserving constraints.
KNOWN_COLLABS: List[Dict[str, str]] = [
    {"a1": "The Weeknd", "a2": "Ariana Grande", "title": "Save Your Tears (Remix)", "status": "Success", "year": 2021, "region": "US", "peak": 1},
    {"a1": "Kanye West", "a2": "Lil Pump", "title": "I Love It", "status": "Success", "year": 2018, "region": "US", "peak": 3},
    {"a1": "Madonna", "a2": "Nicki Minaj", "title": "Bitch I'm Madonna", "status": "Failure", "year": 2015, "region": "US", "peak": 84},
    {"a1": "Shawn Mendes", "a2": "Camila Cabello", "title": "Señorita", "status": "Success", "year": 2019, "region": "Global", "peak": 1},
    {"a1": "Metallica", "a2": "Lou Reed", "title": "The View", "status": "Failure", "year": 2011, "region": "US", "peak": ""},
    {"a1": "Coldplay", "a2": "BTS", "title": "My Universe", "status": "Success", "year": 2021, "region": "Global", "peak": 1},
    {"a1": "Ed Sheeran", "a2": "Justin Bieber", "title": "I Don't Care", "status": "Success", "year": 2019, "region": "Global", "peak": 2},
    {"a1": "Billie Eilish", "a2": "Khalid", "title": "lovely", "status": "Success", "year": 2018, "region": "Global", "peak": 64},
    {"a1": "Drake", "a2": "Rihanna", "title": "Work", "status": "Success", "year": 2016, "region": "US", "peak": 1},
    {"a1": "Calvin Harris", "a2": "Dua Lipa", "title": "One Kiss", "status": "Success", "year": 2018, "region": "UK", "peak": 1},
    {"a1": "David Guetta", "a2": "Sia", "title": "Titanium", "status": "Success", "year": 2011, "region": "Global", "peak": 7},
    {"a1": "Beyoncé", "a2": "Shakira", "title": "Beautiful Liar", "status": "Success", "year": 2007, "region": "Global", "peak": 3},
    {"a1": "Jay-Z", "a2": "Linkin Park", "title": "Numb/Encore", "status": "Success", "year": 2004, "region": "US", "peak": 20},
    {"a1": "Kendrick Lamar", "a2": "SZA", "title": "All The Stars", "status": "Success", "year": 2018, "region": "US", "peak": 7},
    {"a1": "Post Malone", "a2": "Swae Lee", "title": "Sunflower", "status": "Success", "year": 2018, "region": "US", "peak": 1},
    {"a1": "Luis Fonsi", "a2": "Daddy Yankee", "title": "Despacito", "status": "Success", "year": 2017, "region": "Latin America", "peak": 1},
    {"a1": "Bad Bunny", "a2": "Drake", "title": "MIA", "status": "Success", "year": 2018, "region": "Latin America", "peak": 5},
    {"a1": "Shakira", "a2": "Karol G", "title": "TQG", "status": "Success", "year": 2023, "region": "Latin America", "peak": 7},
    {"a1": "Wizkid", "a2": "Tems", "title": "Essence", "status": "Success", "year": 2020, "region": "Africa", "peak": 9},
    {"a1": "Burna Boy", "a2": "Ed Sheeran", "title": "For My Hand", "status": "Success", "year": 2022, "region": "Global", "peak": 26},
    {"a1": "The Chainsmokers", "a2": "Halsey", "title": "Closer", "status": "Success", "year": 2016, "region": "US", "peak": 1},
    {"a1": "Lady Gaga", "a2": "Beyoncé", "title": "Telephone", "status": "Success", "year": 2010, "region": "US", "peak": 3},
    {"a1": "Rihanna", "a2": "Britney Spears", "title": "S&M (Remix)", "status": "Success", "year": 2011, "region": "US", "peak": 1},
    {"a1": "Katy Perry", "a2": "Nicki Minaj", "title": "Swish Swish", "status": "Success", "year": 2017, "region": "US", "peak": 46},
    {"a1": "Taylor Swift", "a2": "Kendrick Lamar", "title": "Bad Blood (Remix)", "status": "Success", "year": 2015, "region": "US", "peak": 1},
    {"a1": "Skrillex", "a2": "Justin Bieber", "title": "Where Are Ü Now", "status": "Success", "year": 2015, "region": "Global", "peak": 8},
    {"a1": "Kanye West", "a2": "Paul McCartney", "title": "Only One", "status": "Success", "year": 2014, "region": "US", "peak": 35},
    {"a1": "Eminem", "a2": "Rihanna", "title": "Love the Way You Lie", "status": "Success", "year": 2010, "region": "US", "peak": 1},
    {"a1": "Alicia Keys", "a2": "Jay-Z", "title": "Empire State of Mind", "status": "Success", "year": 2009, "region": "US", "peak": 1},
    {"a1": "Marshmello", "a2": "Bastille", "title": "Happier", "status": "Success", "year": 2018, "region": "UK", "peak": 2},
    {"a1": "Kygo", "a2": "Whitney Houston", "title": "Higher Love", "status": "Success", "year": 2019, "region": "Global", "peak": 2},
    {"a1": "Zedd", "a2": "Katy Perry", "title": "365", "status": "Failure", "year": 2019, "region": "Global", "peak": 86},
    {"a1": "Maroon 5", "a2": "Cardi B", "title": "Girls Like You", "status": "Success", "year": 2018, "region": "US", "peak": 1},
    {"a1": "DJ Khaled", "a2": "Justin Bieber", "title": "I'm the One", "status": "Success", "year": 2017, "region": "US", "peak": 1},
    {"a1": "Kanye West", "a2": "Lil Pump", "title": "I Love It", "status": "Success", "year": 2018, "region": "US", "peak": 3},
    {"a1": "Metallica", "a2": "Lou Reed", "title": "Lulu", "status": "Failure", "year": 2011, "region": "US", "peak": ""},
    {"a1": "Madonna", "a2": "M.I.A.", "title": "Give Me All Your Luvin'", "status": "Success", "year": 2012, "region": "US", "peak": 10},
    {"a1": "Usher", "a2": "will.i.am", "title": "OMG", "status": "Success", "year": 2010, "region": "US", "peak": 1},
]

# Make sure artist catalog contains all artists referenced above
def ensure_artist_in_catalog(name: str, default_region: str = "Global", default_tags: str = "pop, contemporary") -> None:
    if not any(a["name"].lower() == name.lower() for a in ARTISTS):
        ARTISTS.append({"name": name, "tags": default_tags, "region": default_region})

for row in KNOWN_COLLABS:
    ensure_artist_in_catalog(row["a1"])
    ensure_artist_in_catalog(row["a2"])

# Synthetic title generator bits (for filler rows)
TITLE_WORDS_1 = [
    "Midnight", "Neon", "Golden", "Echo", "Velvet", "Electric", "Silent", "Crimson", "Diamond", "Violet",
    "Fever", "Cosmic", "Urban", "Desert", "Ocean", "Paper", "Lunar", "Magnetic", "Parallel", "Hidden",
]
TITLE_WORDS_2 = [
    "Dreams", "Lights", "Voices", "Paradise", "Storm", "Shadows", "Lines", "Heat", "Rhythm", "Whispers",
    "Fire", "Pulse", "Waves", "Fantasy", "Nights", "Hearts", "Mirrors", "Motion", "Gravity", "Reflections",
]
TITLE_LINKERS = ["of", "in", "and", "for", "without", "under"]


def synth_title() -> str:
    # 70% two-word title, 30% three/four word title
    if random.random() < 0.7:
        return f"{random.choice(TITLE_WORDS_1)} {random.choice(TITLE_WORDS_2)}"
    else:
        parts = [random.choice(TITLE_WORDS_1), random.choice(TITLE_LINKERS), random.choice(TITLE_WORDS_2)]
        if random.random() < 0.4:
            parts.insert(1, random.choice(TITLE_WORDS_1))
        return " ".join(parts)


def pick_two_distinct_artists() -> Tuple[Dict[str, str], Dict[str, str]]:
    a1, a2 = random.sample(ARTISTS, 2)
    # sort by name for deterministic uniqueness key later
    return a1, a2


def status_to_peak(status: str) -> str:
    if status == "Success":
        # plausible chart peak (1-100)
        return str(random.randint(1, 100))
    else:
        # leave empty when data unavailable
        return ""


def derive_region(a1_region: str, a2_region: str) -> str:
    if a1_region == a2_region:
        return a1_region
    if "Global" in (a1_region, a2_region):
        return "Global"
    # cross-region collabs marked Global 50% of time
    return "Global" if random.random() < 0.5 else random.choice([a1_region, a2_region])


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    header = [
        "Artist_01",
        "Artist_01_Tags",
        "Artist_02",
        "Artist_02_Tags",
        "Song_Title",
        "Collaboration_Status",
        "Release_Year",
        "Region",
        "Peak_Chart_Position",
    ]

    # We'll build a set of used pairs (lowercased, sorted) to ensure uniqueness
    used_pairs = set()

    rows: List[List[str]] = []

    # 1) Seed with known collabs
    for kc in KNOWN_COLLABS:
        a1 = next(a for a in ARTISTS if a["name"].lower() == kc["a1"].lower())
        a2 = next(a for a in ARTISTS if a["name"].lower() == kc["a2"].lower())
        key = tuple(sorted([a1["name"].lower(), a2["name"].lower()]))
        if key in used_pairs:
            continue
        used_pairs.add(key)
        rows.append([
            a1["name"], a1["tags"],
            a2["name"], a2["tags"],
            kc["title"],
            kc["status"],
            str(kc.get("year", "")),
            kc.get("region", derive_region(a1["region"], a2["region"])),
            str(kc.get("peak", "")),
        ])

    # Count current successes/failures
    success_ct = sum(1 for r in rows if r[5] == "Success")
    failure_ct = sum(1 for r in rows if r[5] == "Failure")

    # 2) Synthesize the remainder to reach target counts
    def need_more_success() -> bool:
        return success_ct < TARGET_SUCCESS

    def need_more_failure() -> bool:
        return failure_ct < TARGET_FAILURE

    # keep looping until total rows reach TOTAL_ROWS with required balance
    safety = 0
    while len(rows) < TOTAL_ROWS and safety < TOTAL_ROWS * 10:
        safety += 1
        a1, a2 = pick_two_distinct_artists()
        key = tuple(sorted([a1["name"].lower(), a2["name"].lower()]))
        if key in used_pairs:
            continue

        # Choose status to approach target ratio
        if need_more_success() and need_more_failure():
            status = "Success" if random.random() < SUCCESS_RATIO else "Failure"
        elif need_more_success():
            status = "Success"
        elif need_more_failure():
            status = "Failure"
        else:
            status = random.choice(["Success", "Failure"])  # fallback

        year = random.randint(YEAR_MIN, YEAR_MAX)
        region = derive_region(a1["region"], a2["region"])
        title = synth_title()
        peak = status_to_peak(status)

        used_pairs.add(key)
        rows.append([
            a1["name"], a1["tags"],
            a2["name"], a2["tags"],
            title,
            status,
            str(year),
            region,
            peak,
        ])
        if status == "Success":
            success_ct += 1
        else:
            failure_ct += 1

    # 3) Randomize order
    random.shuffle(rows)

    # 4) Write CSV with proper quoting
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        # Quote all fields to satisfy strict CSV formatting (wrap multi-word fields)
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(rows)

    # 5) Print a small summary
    print("Wrote:", OUT_PATH)
    print("Rows:", len(rows))
    print("Success:", success_ct, "Failure:", failure_ct)
    # Sanity checks
    assert len(rows) >= 500, "Dataset too small"
    assert abs(success_ct / len(rows) - SUCCESS_RATIO) < 0.1, "Balance off by >10%"


if __name__ == "__main__":
    main()
