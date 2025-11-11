import pandas as pd
import os

# Ask the user for the file path
file_path = input(r"C:\Users\nkosi\Desktop\lazaar beams\MatchColab\data\artist_collaborations_final.csv").strip()

# Check if the file exists
if not os.path.isfile(file_path):
    print("File not found. Please check the path and try again.")
    exit()

# Load the CSV
try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Error reading the file: {e}")
    exit()

# Add a RowNumber column starting from 1
df.insert(0, "RowNumber", range(1, len(df) + 1))

# Create a new file name
base, ext = os.path.splitext(file_path)
new_file = f"{base}_with_rows{ext}"

# Save the new CSV
try:
    df.to_csv(new_file, index=False)
    print(f"Row numbers added successfully! Saved as: {new_file}")
except Exception as e:
    print(f"Error saving the file: {e}")
