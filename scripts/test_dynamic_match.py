import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

"""Quick test script for dynamic artist matching.
Run after backend server is up (nodemon backend/server.js).
"""

load_dotenv()

API_URL = os.getenv("MATCHCOLAB_API_URL", "http://localhost:5000/match")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    raise SystemExit("OPENAI_API_KEY missing in environment.")

client = OpenAI(api_key=OPENAI_KEY)

def run_test(tags: str, top_n: int = 5):
    payload = {
        "tags": tags,
        "top_n": top_n,
        "only_successful": False,
        "min_similarity": 0.3,
        "persist_artist": False
    }
    print(f"\n>>> Matching for: {tags}")
    resp = requests.post(API_URL, json=payload, timeout=60)
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
    except Exception:
        print("Non-JSON response:\n", resp.text)
        return
    print(json.dumps(data, indent=2)[:4000])  # truncate output if huge

if __name__ == "__main__":
    test_inputs = [
        " ",
        "hip hop, trap, southern hip hop",
        "electropop, synthpop, alternative pop"
    ]
    for t in test_inputs:
        run_test(t)
    print("\nTest complete.")
