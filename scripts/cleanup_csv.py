import pandas as pd

# Read the CSV file
df = pd.read_csv('data/artist_collaborations_final.csv')

print("Before cleanup:")
print(f"Columns: {list(df.columns)}")
print(f"Total: {len(df.columns)}")

# Keep only the columns we want (up to and including 'embedding')
columns_to_keep = ['id', 'artist_01', 'artist_01_tags', 'artist_02', 'artist_02_tags', 
                   'song_title', 'collaboration_status', 'release_year', 'region', 
                   'mb_rating_value', 'mb_rating_votes', 'peak_chart_position', 'embedding']

df = df[columns_to_keep]

# Save back to the same file
df.to_csv('data/artist_collaborations_final.csv', index=False)

print("\nAfter cleanup:")
print(f"Columns: {list(df.columns)}")
print(f"Total: {len(df.columns)}")
