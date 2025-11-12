import pandas as pd

# Read the final dataset
df = pd.read_csv('data/artist_collaborations_final.csv')

# Create a dictionary to store unique artists
artists_dict = {}

# Extract artists from Artist_01 columns
for _, row in df.iterrows():
    artist_name = row['artist_01']
    artist_tags = row['artist_01_tags']
    
    if artist_name not in artists_dict:
        artists_dict[artist_name] = artist_tags

# Extract artists from Artist_02 columns
for _, row in df.iterrows():
    artist_name = row['artist_02']
    artist_tags = row['artist_02_tags']
    
    if artist_name not in artists_dict:
        artists_dict[artist_name] = artist_tags

# Create DataFrame for artists
artists_data = []
for idx, (artist_name, artist_tags) in enumerate(sorted(artists_dict.items()), start=1):
    artists_data.append({
        'id': idx,
        'artist_name': artist_name,
        'artist_tags': artist_tags,
        'embedding': ''  # Empty for now, will be populated later
    })

artists_df = pd.DataFrame(artists_data)

# Save to CSV
artists_df.to_csv('data/artists.csv', index=False)

print(f"✅ Artist database created!")
print(f"Total unique artists: {len(artists_df)}")
print(f"File saved to: data/artists.csv")
print(f"\nFirst 5 artists:")
print(artists_df.head())
