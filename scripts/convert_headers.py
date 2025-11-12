import pandas as pd

# Read the CSV file
df = pd.read_csv('data/artist_collaborations_final.csv')

# Convert all column names to lowercase
df.columns = df.columns.str.lower()

# Save back to the same file
df.to_csv('data/artist_collaborations_final.csv', index=False)

print("Headers converted to lowercase:")
print(list(df.columns))
