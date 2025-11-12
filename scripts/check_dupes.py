import csv

# Read the CSV
with open('data/test_deduped_10.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in CSV: {len(rows)}\n")

# Group by song title (case-insensitive)
from collections import defaultdict
songs = defaultdict(list)
for i, row in enumerate(rows):
    songs[row['Song_Title'].lower()].append((i+1, row))

# Find duplicates
print("Songs with multiple entries:")
for title, entries in songs.items():
    if len(entries) > 1:
        print(f"\n'{title}' ({len(entries)} variants):")
        for idx, row in entries:
            print(f"  Row {idx}: Status={row['Collaboration_Status']}, Year={row['Release_Year']}, Title={row['Song_Title']}")
