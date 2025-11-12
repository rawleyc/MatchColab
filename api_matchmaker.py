from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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

# Initialize FastAPI app
app = FastAPI(title="Artist Collaboration Matchmaker API")

# Request/Response schemas
class MatchRequest(BaseModel):
    tags: str
    top_n: Optional[int] = 10

class ArtistMatch(BaseModel):
    artist_name: str
    artist_tags: str
    semantic_similarity: float
    historical_success_rate: float
    combined_score: float
    recommendation: str

class MatchResponse(BaseModel):
    user_tags: str
    matches: List[ArtistMatch]
    total_artists_analyzed: int

def generate_embedding(tags):
    """Generate embedding for given tags using OpenAI"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=tags
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

def fetch_artists():
    """Fetch all artists with embeddings from Supabase"""
    url = f"{supabase_url}/rest/v1/artists?select=id,artist_name,artist_tags,embedding"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="Error fetching artists from database")

def fetch_collaboration_history():
    """Fetch historical collaboration data from Supabase"""
    url = f"{supabase_url}/rest/v1/maindb?select=*"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        raise HTTPException(status_code=500, detail="Error fetching collaboration history")

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

def get_recommendation_text(score):
    """Get recommendation text based on combined score"""
    if score >= 0.7:
        return "HIGHLY RECOMMENDED - Strong compatibility!"
    elif score >= 0.5:
        return "GOOD MATCH - Moderate compatibility"
    else:
        return "RISKY - Lower compatibility, but could be innovative"

@app.get("/")
def home():
    return {
        "message": "Artist Collaboration Matchmaker API is running 🚀",
        "endpoints": {
            "/matches": "POST - Find best artist matches for given tags",
            "/health": "GET - Check API health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "artist-matchmaker"}

@app.post("/matches", response_model=MatchResponse)
def find_matches(request: MatchRequest):
    """
    Find best artist matches based on user tags.
    Combines semantic similarity with historical collaboration patterns.
    """
    # Generate embedding for user tags
    user_embedding = generate_embedding(request.tags)
    
    # Fetch all artists with embeddings
    artists = fetch_artists()
    artists_with_embeddings = [a for a in artists if a.get('embedding')]
    
    if not artists_with_embeddings:
        raise HTTPException(status_code=404, detail="No artists with embeddings found")
    
    # Fetch collaboration history
    history_df = fetch_collaboration_history()
    
    # Calculate scores for each artist
    results = []
    
    for artist in artists_with_embeddings:
        # Calculate embedding similarity (semantic similarity)
        artist_embedding = artist['embedding']
        similarity = cosine_similarity([user_embedding], [artist_embedding])[0][0]
        
        # Calculate historical success probability
        historical_score = analyze_artist_pair_history(request.tags, artist['artist_tags'], history_df)
        
        # Combined score: 60% semantic similarity + 40% historical patterns
        combined_score = (0.6 * similarity) + (0.4 * historical_score)
        
        results.append(ArtistMatch(
            artist_name=artist['artist_name'],
            artist_tags=artist['artist_tags'],
            semantic_similarity=round(float(similarity), 3),
            historical_success_rate=round(float(historical_score), 3),
            combined_score=round(float(combined_score), 3),
            recommendation=get_recommendation_text(combined_score)
        ))
    
    # Sort by combined score
    results.sort(key=lambda x: x.combined_score, reverse=True)
    
    # Return top N matches
    return MatchResponse(
        user_tags=request.tags,
        matches=results[:request.top_n],
        total_artists_analyzed=len(artists_with_embeddings)
    )

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
