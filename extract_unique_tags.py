import pandas as pd

# Read the final dataset
df = pd.read_csv('data/artist_collaborations_final.csv')

# Collect all tags from both Artist_01_Tags and Artist_02_Tags columns
all_tags = set()

# Process Artist_01_Tags
for tags in df['Artist_01_Tags'].dropna():
    # Split by comma and strip whitespace
    tag_list = [tag.strip() for tag in str(tags).split(',')]
    all_tags.update(tag_list)

# Process Artist_02_Tags
for tags in df['Artist_02_Tags'].dropna():
    # Split by comma and strip whitespace
    tag_list = [tag.strip() for tag in str(tags).split(',')]
    all_tags.update(tag_list)

# Convert to sorted list
unique_tags = sorted(list(all_tags))

# Create DataFrame
tags_df = pd.DataFrame({'Tag': unique_tags})

# Save to CSV
tags_df.to_csv('data/unique_tags.csv', index=False)

print(f"Total unique tags found: {len(unique_tags)}")
print(f"\nUnique tags saved to: data/unique_tags.csv")
print(f"\nFirst 10 tags:")
for i, tag in enumerate(unique_tags[:10], 1):
    print(f"{i}. {tag}")
