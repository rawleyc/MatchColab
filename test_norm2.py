import re

def normalize_title(title: str) -> str:
    # Convert to lowercase
    title = title.lower().strip()
    
    # Normalize apostrophes and quotes (many Unicode variants)
    title = title.replace("'", "'").replace("'", "'").replace("`", "'")
    title = title.replace(""", '"').replace(""", '"').replace("«", '"').replace("»", '"')
    
    # Remove content in parentheses and brackets
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^\]]*\]', '', title)
    
    # Remove common separators
    parts = re.split(r'[:|–—]', title)
    if parts:
        title = parts[0]
    
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Remove trailing punctuation
    title = title.rstrip('.,;:-–—!?')
    
    return title

# Test the two Creepin' variants
title1 = "Creepin'"  # With right single quote
title2 = "Creepin'"  # With apostrophe

print(f"Title 1: {repr(title1)}")
print(f"Title 2: {repr(title2)}")
print(f"Normalized 1: {repr(normalize_title(title1))}")
print(f"Normalized 2: {repr(normalize_title(title2))}")
print(f"Are they equal after normalization? {normalize_title(title1) == normalize_title(title2)}")
