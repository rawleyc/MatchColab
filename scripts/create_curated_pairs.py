"""
Create a curated list of artist pairs that are likely to have real collaborations.
Focus on mainstream, popular artists from the last 20 years.
"""
import csv
import os
from itertools import combinations

# High-profile artists known for collaborations
CURATED_ARTISTS = [
    # Pop superstars
    "Ariana Grande", "Taylor Swift", "Ed Sheeran", "Justin Bieber", "Selena Gomez",
    "Dua Lipa", "The Weeknd", "Billie Eilish", "Shawn Mendes", "Camila Cabello",
    "Lady Gaga", "Katy Perry", "Miley Cyrus", "Demi Lovato", "Halsey",
    
    # Hip-hop/R&B
    "Drake", "Kanye West", "Jay-Z", "Kendrick Lamar", "J. Cole", "Travis Scott",
    "Post Malone", "Megan Thee Stallion", "Cardi B", "Nicki Minaj", "Lil Wayne",
    "Future", "21 Savage", "Metro Boomin", "Snoop Dogg", "Eminem",
    "Rihanna", "Beyoncé", "SZA", "H.E.R.", "The Weeknd", "Frank Ocean",
    
    # Rock/Alternative
    "Coldplay", "Imagine Dragons", "Twenty One Pilots", "Fall Out Boy",
    "Panic! at the Disco", "Linkin Park", "Foo Fighters",
    
    # EDM/Electronic
    "Calvin Harris", "David Guetta", "The Chainsmokers", "Marshmello",
    "Zedd", "Kygo", "Avicii", "Diplo", "Skrillex", "Martin Garrix",
    
    # Latin
    "Bad Bunny", "J Balvin", "Shakira", "Daddy Yankee", "Ozuna",
    "Maluma", "Karol G", "Luis Fonsi", "Nicky Jam",
    
    # K-pop
    "BTS", "BLACKPINK", "Stray Kids",
    
    # Country/Crossover
    "Taylor Swift", "Kacey Musgraves", "Maren Morris",
    
    # UK/Global
    "Ed Sheeran", "Dua Lipa", "Sam Smith", "Ellie Goulding", "Rita Ora",
]

# Remove duplicates while preserving order
seen = set()
unique_artists = []
for artist in CURATED_ARTISTS:
    if artist.lower() not in seen:
        seen.add(artist.lower())
        unique_artists.append(artist)

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "artist_pairs_curated_high_prob.csv"
)

def main():
    # Generate all unique pairs
    pairs = list(combinations(unique_artists, 2))
    
    # Write to CSV
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Artist_01", "Artist_02"])
        writer.writerows(pairs)
    
    print(f"Created {len(pairs)} curated pairs from {len(unique_artists)} popular artists")
    print(f"Output: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
