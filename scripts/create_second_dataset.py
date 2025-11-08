"""
Create a second 500-row dataset excluding pairs used in the first dataset.
"""
import csv
import sys

def extract_used_pairs(csv_file):
    """Extract unique artist pairs from existing dataset."""
    used_pairs = set()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Sort artists to create canonical pair representation
            artists = tuple(sorted([row['Artist_01'], row['Artist_02']]))
            used_pairs.add(artists)
    
    return used_pairs

def create_exclude_pairs_file(used_pairs, all_pairs_file, output_file):
    """Create a new pairs file excluding already-used pairs."""
    available_pairs = []
    
    with open(all_pairs_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                # Sort to match the canonical representation
                pair = tuple(sorted([row[0], row[1]]))
                if pair not in used_pairs:
                    available_pairs.append(row)
    
    print(f"Total pairs in source file: {len(available_pairs) + len(used_pairs)}")
    print(f"Used pairs (excluded): {len(used_pairs)}")
    print(f"Available pairs: {len(available_pairs)}")
    
    # Write available pairs to new file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for pair in available_pairs:
            writer.writerow(pair)
    
    print(f"\nCreated new pairs file: {output_file}")
    return len(available_pairs)

if __name__ == "__main__":
    print("Extracting used pairs from first dataset...")
    used_pairs = extract_used_pairs('data/artist_collaborations_500.csv')
    
    print(f"Found {len(used_pairs)} unique pairs in first dataset\n")
    print("Sample used pairs:")
    for i, pair in enumerate(list(used_pairs)[:5]):
        print(f"  {pair[0]} + {pair[1]}")
    
    print("\n" + "="*60)
    print("Creating new pairs file with unused pairs...")
    print("="*60 + "\n")
    
    available = create_exclude_pairs_file(
        used_pairs,
        'data/artist_pairs_curated_high_prob.csv',
        'data/artist_pairs_curated_batch2.csv'
    )
    
    if available > 0:
        print(f"\n✅ Ready to generate second dataset with {available} available pairs!")
    else:
        print("\n⚠️ Warning: No available pairs remaining!")
        sys.exit(1)
