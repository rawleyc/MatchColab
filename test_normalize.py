import re

def normalize_title(title: str) -> str:
    """Normalize song title by removing variants like (instrumental), [remix], etc."""
    # Convert to lowercase
    title = title.lower().strip()
    
    # Remove content in parentheses and brackets (often variants/features)
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^\]]*\]', '', title)
    
    # Remove common separators and extra content after colon/dash
    # But keep the main title before these markers
    parts = re.split(r'[:|–—]', title)
    if parts:
        title = parts[0]  # Keep only the part before : or —
    
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Remove trailing punctuation
    title = title.rstrip('.,;:-–—!?')
    
    return title

# Test with actual titles from the CSV
titles = [
    "Creepin'",
    "Creepin' (ChoppedNotSlopped)",
    "UN DÍA (ONE DAY)",
    "Un Día",
    "Another One of Me"
]

print("Normalization test:")
for t in titles:
    print(f"'{t}' -> '{normalize_title(t)}'")
