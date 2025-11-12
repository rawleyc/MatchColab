import pandas as pd

# Read the CSV file
df = pd.read_csv('data/artist_collaborations_final.csv')

print("Before formatting:")
print(f"Release_year dtype: {df['release_year'].dtype}")
print(f"Sample values: {df['release_year'].head(10).tolist()}")

# Convert release_year to integer, handling NaN values
df['release_year'] = df['release_year'].fillna(0).astype(int)

# Replace 0 with empty string if you want to keep missing years as empty
# Uncomment the next line if you prefer empty cells instead of 0
# df['release_year'] = df['release_year'].replace(0, '')

# Save back to the same file
df.to_csv('data/artist_collaborations_final.csv', index=False)

print("\nAfter formatting:")
print(f"Release_year dtype: {df['release_year'].dtype}")
print(f"Sample values: {df['release_year'].head(10).tolist()}")
print("\nRelease years formatted to integers!")
