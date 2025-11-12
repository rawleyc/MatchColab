import pandas as pd

# Read both batch files
batch1 = pd.read_csv('data/artist_collaborations_500_batch1.csv')
batch2 = pd.read_csv('data/artist_collaborations_500_batch2.csv')

# Merge the datasets
merged = pd.concat([batch1, batch2], ignore_index=True)

# Remove duplicates if any (based on all columns)
merged = merged.drop_duplicates()

# Save the merged dataset
merged.to_csv('data/artist_collaborations_merged.csv', index=False)

print(f"Batch 1 rows: {len(batch1)}")
print(f"Batch 2 rows: {len(batch2)}")
print(f"Merged rows: {len(merged)}")
print(f"Duplicates removed: {len(batch1) + len(batch2) - len(merged)}")
print("\nMerged dataset saved to: data/artist_collaborations_merged.csv")
