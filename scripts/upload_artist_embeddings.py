import os
from openai import OpenAI
from dotenv import load_dotenv
import time
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

supabase: Client = create_client(supabase_url, supabase_key)

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

def update_artist_embeddings():
    """Fetch artists, generate embeddings, and update Supabase"""
    
    # Fetch all artists from Supabase
    print("Fetching artists from Supabase...")
    response = supabase.table('artists').select('id, artist_name, artist_tags').execute()
    artists = response.data
    
    print(f"Found {len(artists)} artists")
    
    # Process each artist
    success_count = 0
    error_count = 0
    
    for i, artist in enumerate(artists, 1):
        artist_id = artist['id']
        artist_name = artist['artist_name']
        artist_tags = artist['artist_tags']
        
        print(f"\n[{i}/{len(artists)}] Processing: {artist_name}")
        
        # Generate embedding from artist tags
        embedding = generate_embedding(artist_tags)
        
        if embedding:
            try:
                # Update the embedding in Supabase
                supabase.table('artists').update({
                    'embedding': embedding
                }).eq('id', artist_id).execute()
                
                print(f"✅ Updated embedding for {artist_name}")
                success_count += 1
                
                # Rate limiting - small delay to avoid hitting API limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error updating {artist_name}: {e}")
                error_count += 1
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
    print("Starting artist embedding generation and upload...")
    print("="*50)
    update_artist_embeddings()
    print("\n✅ Process complete!")
