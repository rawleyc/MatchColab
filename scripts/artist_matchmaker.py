import os
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import requests

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

# Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

# Supabase API headers
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

def generate_embedding(tags):
    """Generate embedding for given tags using OpenAI"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=tags
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def fetch_artists():
    """Fetch all artists with embeddings from Supabase"""
    url = f"{supabase_url}/rest/v1/artists?select=id,artist_name,artist_tags,embedding"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching artists: {response.status_code}")
        return []

def fetch_collaboration_history():
    """Fetch historical collaboration data from Supabase"""
    url = f"{supabase_url}/rest/v1/maindb?select=*"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        print(f"Error fetching collaboration history: {response.status_code}")
        return pd.DataFrame()

def analyze_artist_pair_history(user_tags, artist_tags, history_df):
    """
    Analyze historical patterns for similar tag combinations
    Returns a success probability based on historical data
    """
    if history_df.empty:
        return 0.5  # Neutral score if no history
    
    # Combine user tags and artist tags
    combined_tags_set = set(user_tags.lower().split(', ')) | set(artist_tags.lower().split(', '))
    
    # Find relevant collaborations with similar genres
    relevant_collabs = []
    
    for _, row in history_df.iterrows():
        artist1_tags = set(str(row['artist_01_tags']).lower().split(', '))
        artist2_tags = set(str(row['artist_02_tags']).lower().split(', '))
        collab_tags = artist1_tags | artist2_tags
        
        # Calculate tag overlap
        overlap = len(combined_tags_set & collab_tags)
        if overlap > 0:
            relevant_collabs.append({
                'overlap': overlap,
                'status': row['collaboration_status']
            })
    
    if not relevant_collabs:
        return 0.5  # Neutral score if no similar collaborations found
    
    # Weight by overlap - more similar collaborations have more influence
    total_weight = 0
    success_weight = 0
    
    for collab in relevant_collabs:
        weight = collab['overlap']
        total_weight += weight
        if collab['status'] == 'Success':
            success_weight += weight
    
    # Calculate weighted success probability
    historical_score = success_weight / total_weight if total_weight > 0 else 0.5
    
    return historical_score

def find_best_matches(user_tags, top_n=10):
    """
    Find best artist matches for the user based on:
    1. Embedding similarity (semantic matching)
    2. Historical collaboration patterns
    """
    print(f"\n{'='*60}")
    print(f"Finding best artist matches for tags: {user_tags}")
    print(f"{'='*60}\n")
    
    # Step 1: Generate embedding for user tags
    print("Step 1: Generating embedding for your tags...")
    user_embedding = generate_embedding(user_tags)
    if not user_embedding:
        print("❌ Failed to generate embedding")
        return []
    print("✅ Embedding generated\n")
    
    # Step 2: Fetch all artists with embeddings
    print("Step 2: Fetching artists from database...")
    artists = fetch_artists()
    if not artists:
        print("❌ No artists found")
        return []
    
    # Filter artists that have embeddings
    artists_with_embeddings = [a for a in artists if a.get('embedding')]
    print(f"✅ Found {len(artists_with_embeddings)} artists with embeddings\n")
    
    # Step 3: Fetch collaboration history
    print("Step 3: Fetching historical collaboration data...")
    history_df = fetch_collaboration_history()
    print(f"✅ Loaded {len(history_df)} historical collaborations\n")
    
    # Step 4: Calculate scores for each artist
    print("Step 4: Calculating compatibility scores...\n")
    results = []
    
    for artist in artists_with_embeddings:
        # Calculate embedding similarity (semantic similarity)
        artist_embedding = artist['embedding']
        similarity = cosine_similarity([user_embedding], [artist_embedding])[0][0]
        
        # Calculate historical success probability
        historical_score = analyze_artist_pair_history(user_tags, artist['artist_tags'], history_df)
        
        # Combined score: 60% semantic similarity + 40% historical patterns
        # You can adjust these weights based on preference
        combined_score = (0.6 * similarity) + (0.4 * historical_score)
        
        results.append({
            'artist_name': artist['artist_name'],
            'artist_tags': artist['artist_tags'],
            'semantic_similarity': round(similarity, 3),
            'historical_success_rate': round(historical_score, 3),
            'combined_score': round(combined_score, 3)
        })
    
    # Sort by combined score
    results.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # Return top N matches
    return results[:top_n]

def display_matches(matches):
    """Display the match results in a formatted way"""
    if not matches:
        print("No matches found")
        return
    
    print(f"\n{'='*60}")
    print(f"TOP {len(matches)} ARTIST MATCHES")
    print(f"{'='*60}\n")
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match['artist_name']}")
        print(f"   Tags: {match['artist_tags']}")
        print(f"   📊 Combined Score: {match['combined_score']}")
        print(f"   🎯 Semantic Similarity: {match['semantic_similarity']}")
        print(f"   📈 Historical Success Rate: {match['historical_success_rate']}")
        
        # Recommendation based on scores
        if match['combined_score'] >= 0.7:
            print(f"   ✅ HIGHLY RECOMMENDED - Strong compatibility!")
        elif match['combined_score'] >= 0.5:
            print(f"   👍 GOOD MATCH - Moderate compatibility")
        else:
            print(f"   ⚠️  RISKY - Lower compatibility, but could be innovative")
        
        print()

def main():
    """Main function to run the artist matching system"""
    print("\n" + "="*60)
    print("🎵 ARTIST COLLABORATION MATCHMAKING SYSTEM 🎵")
    print("="*60)
    
    # Get user input
    print("\nEnter your music style tags (comma-separated):")
    print("Example: pop, dance-pop, r&b, contemporary r&b")
    user_tags = input("\nYour tags: ").strip()
    
    if not user_tags:
        print("❌ No tags provided. Exiting...")
        return
    
    # Find best matches
    matches = find_best_matches(user_tags, top_n=10)
    
    # Display results
    display_matches(matches)
    
    print("="*60)
    print("💡 Tip: The combined score considers both how well your styles")
    print("   align (semantic similarity) AND historical collaboration")
    print("   success patterns from the database.")
    print("="*60)

if __name__ == "__main__":
    main()
