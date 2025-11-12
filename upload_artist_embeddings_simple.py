import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
import time
import json

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
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def generate_embedding(text):
    """Generate embedding for given text using OpenAI"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def fetch_artists():
    """Fetch all artists from Supabase"""
    url = f"{supabase_url}/rest/v1/artists?select=id,artist_name,artist_tags"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching artists: {response.status_code}")
        print(response.text)
        return []

def update_artist_embedding(artist_id, embedding):
    """Update artist embedding in Supabase"""
    url = f"{supabase_url}/rest/v1/artists?id=eq.{artist_id}"
    data = {"embedding": embedding}
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code in [200, 204]:
        return True
    else:
        print(f"Error updating artist {artist_id}: {response.status_code}")
        print(response.text)
        return False

def main():
    """Main function to process all artists"""
    print("Starting artist embedding generation and upload...")
    print("="*50)
    
    # Fetch all artists
    print("Fetching artists from Supabase...")
    artists = fetch_artists()
    
    if not artists:
        print("No artists found or error fetching artists")
        return
    
    print(f"Found {len(artists)} artists\n")
    
    # Process each artist
    success_count = 0
    error_count = 0
    
    for i, artist in enumerate(artists, 1):
        artist_id = artist['id']
        artist_name = artist['artist_name']
        artist_tags = artist['artist_tags']
        
        print(f"[{i}/{len(artists)}] Processing: {artist_name}")
        
        # Generate embedding from artist tags
        embedding = generate_embedding(artist_tags)
        
        if embedding:
            # Update the embedding in Supabase
            if update_artist_embedding(artist_id, embedding):
                print(f"✅ Updated embedding for {artist_name}")
                success_count += 1
            else:
                print(f"❌ Failed to update {artist_name}")
                error_count += 1
            
            # Rate limiting - small delay to avoid hitting API limits
            time.sleep(0.5)
        else:
            print(f"❌ Failed to generate embedding for {artist_name}")
            error_count += 1
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total artists: {len(artists)}")
    print(f"Successfully updated: {success_count}")
    print(f"Errors: {error_count}")
    print("="*50)

if __name__ == "__main__":
    main()
    print("\n✅ Process complete!")
