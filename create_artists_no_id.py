import pandas as pd

# Read the artists CSV
df = pd.read_csv('data/artists.csv')

# Drop the id column - Supabase will auto-generate it
df_no_id = df.drop(columns=['id'])

# Save without the id column
df_no_id.to_csv('data/artists_no_id.csv', index=False)

print(f"✅ Created artists_no_id.csv without id column")
print(f"Total rows: {len(df_no_id)}")
print(f"Columns: {list(df_no_id.columns)}")
print(f"\nFirst 5 rows:")
print(df_no_id.head())
