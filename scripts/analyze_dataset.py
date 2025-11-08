"""Quick analysis of a collaboration dataset CSV."""
import csv
import sys
from collections import Counter

def analyze(filepath):
    with open(filepath, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    print(f'Total rows: {len(rows)}')
    
    statuses = [r['Collaboration_Status'] for r in rows]
    print(f'Status distribution: {Counter(statuses)}')
    
    print('\nUnique songs:')
    unique_songs = set()
    for r in rows:
        song = f"{r['Artist_01']} + {r['Artist_02']}: {r['Song_Title']}"
        unique_songs.add(song)
    for s in sorted(unique_songs):
        print(f'  {s}')
    
    ratings_present = sum(1 for r in rows if r.get('MB_Rating_Value'))
    years_present = sum(1 for r in rows if r.get('Release_Year'))
    
    print(f'\nMetadata:')
    print(f'  Ratings present: {ratings_present}/{len(rows)}')
    print(f'  Years present: {years_present}/{len(rows)}')
    
    if any(r['Collaboration_Status'] == 'Success' for r in rows):
        print('\nSuccess examples:')
        for r in [r for r in rows if r['Collaboration_Status'] == 'Success'][:3]:
            print(f"  {r['Artist_01']} + {r['Artist_02']}: {r['Song_Title']} ({r.get('Release_Year', 'N/A')})")
            print(f"    Rating: {r.get('MB_Rating_Value', 'N/A')}, Votes: {r.get('MB_Rating_Votes', 'N/A')}")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'data/test_curated_10.csv'
    analyze(filepath)
