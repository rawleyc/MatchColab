# Quick test of the matchmaker system
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test with sample tags
test_tags = "hip hop, trap, southern hip hop"

print("Testing Artist Matchmaker System")
print("="*60)
print(f"Test tags: {test_tags}")
print("="*60)

# Import the matching function
from artist_matchmaker import find_best_matches, display_matches

# Run the test
matches = find_best_matches(test_tags, top_n=5)
display_matches(matches)
