from typing import Optional
import requests

from .config import YOUTUBE_API_KEY

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def get_best_video_view_count(query: str) -> Optional[int]:
    """Return the highest-view single video result's viewCount for a query, or None if API key missing/failed."""
    if not YOUTUBE_API_KEY:
        return None
    try:
        s = requests.get(SEARCH_URL, params={
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 1,
            "order": "viewCount",
        }, timeout=30)
        s.raise_for_status()
        items = s.json().get("items", [])
        if not items:
            return None
        vid = items[0]["id"]["videoId"]
        v = requests.get(VIDEOS_URL, params={
            "key": YOUTUBE_API_KEY,
            "part": "statistics",
            "id": vid,
        }, timeout=30)
        v.raise_for_status()
        vitems = v.json().get("items", [])
        if not vitems:
            return None
        stats = vitems[0].get("statistics", {})
        vc = stats.get("viewCount")
        return int(vc) if vc is not None else None
    except Exception:
        return None
