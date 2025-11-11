import pandas as pd

# Read your CSV file
df = pd.read_csv(r'C:\Users\nkosi\Desktop\lazaar beams\MatchColab\data\artists_collaborations_final.csv')

# Add row numbers
df.insert(0, 'row_number', range(1, len(df) + 1))

# Add an empty 'embedding' column
df['embedding'] = ''

# Save updated CSV
df.to_csv(r'C:\Users\nkosi\Desktop\lazaar beams\MatchColab\data\artists_collaboration_final2.csv', index=False)

print("✅ New columns added successfully!")
