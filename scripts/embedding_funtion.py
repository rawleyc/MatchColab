# embedding_funtion.py
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

# Initialize FastAPI app
app = FastAPI(title="Artist Collaboration Match API")

# Request schema
class ArtistPair(BaseModel):
    artist1_tags: str
    artist2_tags: str

@app.get("/")
def home():
    return {"message": "Artist Matchmaking API is running 🚀"}

@app.post("/predict")
def predict(pair: ArtistPair):
    """
    Predicts how compatible two artists are based on their music tags.
    Returns a similarity score between 0 and 1.
    """

    # Generate embeddings
    emb1 = client.embeddings.create(
        model="text-embedding-3-small",
        input=pair.artist1_tags
    ).data[0].embedding

    emb2 = client.embeddings.create(
        model="text-embedding-3-small",
        input=pair.artist2_tags
    ).data[0].embedding

    # Compute similarity
    similarity = cosine_similarity([emb1], [emb2])[0][0]
    score = round(float(similarity), 3)

    return {
        "artist_1_tags": pair.artist1_tags,
        "artist_2_tags": pair.artist2_tags,
        "compatibility_score": score
    }

# Run locally (if not deploying)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
