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
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"  ❌ Failed to generate embedding after {max_retries} attempts")
                return None

def fetch_artists():
    """Fetch all artists from Supabase"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            url = f"{supabase_url}/rest/v1/artists?select=id,artist_name,artist_tags,embedding"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} - Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2)
    
    print(f"  ❌ Failed to fetch artists after {max_retries} attempts")
    return []

def update_artist_embedding(artist_id, embedding):
    """Update artist embedding in Supabase with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            url = f"{supabase_url}/rest/v1/artists?id=eq.{artist_id}"
            data = {"embedding": embedding}
            
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} - Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2)
    
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
    
    # Filter to only process artists without embeddings
    artists_to_process = []
    skipped_count = 0
    
    for artist in artists:
        # Check if embedding is None, empty, or null
        if not artist.get('embedding') or artist.get('embedding') == '':
            artists_to_process.append(artist)
        else:
            skipped_count += 1
    
    if skipped_count > 0:
        print(f"ℹ️  Skipping {skipped_count} artists that already have embeddings")
    
    if not artists_to_process:
        print("✅ All artists already have embeddings!")
        return
    
    print(f"Processing {len(artists_to_process)} artists that need embeddings\n")
    
    # Process each artist
    success_count = 0
    error_count = 0
    
    for i, artist in enumerate(artists_to_process, 1):
        artist_id = artist['id']
        artist_name = artist['artist_name']
        artist_tags = artist['artist_tags']
        
        print(f"[{i}/{len(artists_to_process)}] Processing: {artist_name}")
        
        # Generate embedding from artist tags
        embedding = generate_embedding(artist_tags)
        
        if embedding:
            # Update the embedding in Supabase
            if update_artist_embedding(artist_id, embedding):
                print(f"  ✅ Updated embedding for {artist_name}")
                success_count += 1
            else:
                print(f"  ❌ Failed to update {artist_name} in database")
                error_count += 1
            
            # Rate limiting - small delay to avoid hitting API limits
            time.sleep(0.5)
        else:
            print(f"  ❌ Failed to generate embedding for {artist_name}")
            error_count += 1
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total artists in database: {len(artists)}")
    print(f"Already had embeddings: {skipped_count}")
    print(f"Processed: {len(artists_to_process)}")
    print(f"Successfully updated: {success_count}")
    print(f"Errors: {error_count}")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
        print("\n✅ Process complete!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("You can run the script again - it will skip artists that already have embeddings")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("You can run the script again - it will skip artists that already have embeddings")
