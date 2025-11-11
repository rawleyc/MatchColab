import pandas as pd

# Load your CSV file
df = pd.read_csv("data/artist_collaborations_final.csv")

# Replace or create the Row_Number column with correct sequence
df['Row_Number'] = range(1, len(df) + 1)

# Save the fixed file
df.to_csv("data/artist_collaborations_fixed.csv", index=False)

print(f"✅ Row numbers updated successfully. {len(df)} rows numbered 1 to {len(df)}.")
