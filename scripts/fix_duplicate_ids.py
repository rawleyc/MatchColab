import pandas as pd

# Read the CSV file
df = pd.read_csv('data/artist_collaborations_final.csv')

print(f"Total rows: {len(df)}")
print(f"Unique IDs: {df['id'].nunique()}")
print(f"Duplicate IDs: {len(df) - df['id'].nunique()}")

# Check for duplicate IDs
duplicates = df[df.duplicated(subset=['id'], keep=False)]
if len(duplicates) > 0:
    print(f"\nFound {len(duplicates)} rows with duplicate IDs:")
    print(duplicates[['id', 'artist_01', 'artist_02', 'song_title']].sort_values('id'))
    
    # Show which IDs are duplicated
    duplicate_ids = duplicates['id'].value_counts()
    print(f"\nDuplicate ID counts:")
    print(duplicate_ids)

# Reset IDs to be sequential from 1
df['id'] = range(1, len(df) + 1)

# Save back to the same file
df.to_csv('data/artist_collaborations_final.csv', index=False)

print(f"\n✅ IDs have been reset to sequential values from 1 to {len(df)}")
print(f"New ID range: {df['id'].min()} to {df['id'].max()}")
