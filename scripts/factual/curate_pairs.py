"""
Curate high-probability collaboration pairs from a large pairs file.
Filters for popular/mainstream artists more likely to have MusicBrainz recordings together.
"""
import csv
import sys
from typing import List, Tuple, Set

# High-collaboration-probability artists (mainstream, active 2000+, cross-genre appeal)
POPULAR_ARTISTS = {
    # Pop superstars
    "ariana grande", "taylor swift", "ed sheeran", "justin bieber", "dua lipa", "lady gaga",
    "katy perry", "bruno mars", "shawn mendes", "camila cabello", "charlie puth", "halsey",
    "billie eilish", "doja cat", "olivia rodrigo", "selena gomez", "miley cyrus",
    
    # Hip-hop/Rap (collaborative genre)
    "drake", "kendrick lamar", "nicki minaj", "cardi b", "megan thee stallion", "travis scott",
    "post malone", "21 savage", "lil wayne", "kanye west", "j. cole", "future", "lil baby",
    "dababy", "roddy ricch", "polo g", "juice wrld", "xxxtentacion", "eminem", "snoop dogg",
    
    # R&B/Soul
    "the weeknd", "sza", "h.e.r.", "khalid", "6lack", "summer walker", "jhené aiko",
    "usher", "alicia keys", "beyoncé", "rihanna", "chris brown", "frank ocean",
    
    # EDM (collab-heavy genre)
    "calvin harris", "david guetta", "zedd", "kygo", "marshmello", "the chainsmokers",
    "diplo", "skrillex", "martin garrix", "alan walker", "tiësto", "avicii",
    
    # Latin (collaborative scene)
    "bad bunny", "j balvin", "karol g", "shakira", "ozuna", "maluma", "daddy yankee",
    "anuel aa", "becky g", "nicky jam", "luis fonsi", "rauw alejandro", "rosalía",
    
    # Rock/Alternative (known for features)
    "imagine dragons", "twenty one pilots", "coldplay", "fall out boy", "panic! at the disco",
    "linkin park", "foo fighters", "muse", "arctic monkeys", "the killers",
    
    # K-pop (collab explosion recent years)
    "bts", "blackpink", "twice", "exo", "seventeen", "stray kids", "txt", "itzy",
    "newjeans", "ive", "aespa", "(g)i-dle",
    
    # Afrobeats (growing collab scene)
    "wizkid", "burna boy", "davido", "tems", "rema", "fireboy dml", "omah lay", "ckay",
    
    # Country-pop crossover
    "maren morris", "kane brown", "dan + shay", "florida georgia line", "thomas rhett",
    
    # Legacy artists with modern collabs
    "elton john", "paul mccartney", "stevie wonder", "sting", "rod stewart",
    "santana", "andrea bocelli", "céline dion", "mariah carey",
}

# Genre combos that are collab-friendly
COLLAB_FRIENDLY_COMBOS = [
    ("pop", "hip hop"), ("pop", "edm"), ("pop", "r&b"), ("pop", "latin"),
    ("hip hop", "r&b"), ("hip hop", "pop"), ("edm", "pop"), ("latin", "pop"),
    ("afrobeats", "pop"), ("afrobeats", "hip hop"), ("k-pop", "pop"),
]


def normalize_name(name: str) -> str:
    """Normalize artist name for comparison."""
    return name.lower().strip()


def is_popular_artist(name: str) -> bool:
    """Check if artist is in the popular list."""
    norm = normalize_name(name)
    return norm in POPULAR_ARTISTS


def read_pairs(path: str) -> List[Tuple[str, str]]:
    """Read pairs CSV and return list of (artist1, artist2) tuples."""
    pairs: List[Tuple[str, str]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) >= 2:
                pairs.append((row[0].strip(), row[1].strip()))
    return pairs


def write_pairs(pairs: List[Tuple[str, str]], path: str) -> None:
    """Write pairs to CSV."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Artist_01", "Artist_02"])
        writer.writerows(pairs)


def curate_pairs(input_path: str, output_path: str, min_pairs: int = 200, max_pairs: int = 500) -> None:
    """
    Filter pairs to keep only those with at least one popular artist.
    Stop when we have min_pairs, cap at max_pairs.
    """
    all_pairs = read_pairs(input_path)
    print(f"Loaded {len(all_pairs)} pairs from {input_path}")
    
    curated: List[Tuple[str, str]] = []
    seen: Set[Tuple[str, str]] = set()
    
    # Priority 1: Both artists popular
    for a1, a2 in all_pairs:
        if len(curated) >= max_pairs:
            break
        key = tuple(sorted([normalize_name(a1), normalize_name(a2)]))
        if key in seen:
            continue
        if is_popular_artist(a1) and is_popular_artist(a2):
            curated.append((a1, a2))
            seen.add(key)
    
    print(f"Found {len(curated)} pairs with both artists popular")
    
    # Priority 2: At least one artist popular
    if len(curated) < min_pairs:
        for a1, a2 in all_pairs:
            if len(curated) >= max_pairs:
                break
            key = tuple(sorted([normalize_name(a1), normalize_name(a2)]))
            if key in seen:
                continue
            if is_popular_artist(a1) or is_popular_artist(a2):
                curated.append((a1, a2))
                seen.add(key)
        print(f"After adding at-least-one-popular: {len(curated)} pairs")
    
    write_pairs(curated, output_path)
    print(f"Wrote {len(curated)} curated pairs to {output_path}")
    
    # Stats
    both_popular = sum(1 for a1, a2 in curated if is_popular_artist(a1) and is_popular_artist(a2))
    print(f"\nStats:")
    print(f"  Both popular: {both_popular}")
    print(f"  One popular: {len(curated) - both_popular}")


if __name__ == "__main__":
    input_file = "data/artist_pairs_5000.csv"
    output_file = "data/artist_pairs_curated.csv"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    curate_pairs(input_file, output_file, min_pairs=200, max_pairs=500)
