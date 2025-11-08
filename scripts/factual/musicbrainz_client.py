import time
import requests
from typing import Dict, List, Optional
import re

from .config import MB_USER_AGENT, MB_RATE_LIMIT_SECONDS

BASE = "https://musicbrainz.org/ws/2"
HEADERS = {"User-Agent": MB_USER_AGENT}


def _get(url: str, params: Dict[str, str]) -> Dict:
    """GET helper with polite pacing and basic retry. Respects MB_RATE_LIMIT_SECONDS."""
    params = dict(params)
    params.setdefault("fmt", "json")
    last_exc = None
    for attempt in range(4):
        try:
            # fixed-rate pacing: ~1 req/sec by default
            time.sleep(MB_RATE_LIMIT_SECONDS)
            r = requests.get(url, params=params, headers=HEADERS, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_exc = e
            # brief backoff between retries as well
            time.sleep(MB_RATE_LIMIT_SECONDS)
            continue
    if last_exc:
        raise last_exc
    return {}


def search_artist(name: str, limit: int = 1) -> List[Dict]:
    data = _get(f"{BASE}/artist", {"query": f"artist:{name}", "limit": str(limit)})
    return data.get("artists", [])


def search_artists_by_tag(tag: str, limit: int = 25) -> List[Dict]:
    """Return a list of artist dicts for a given MusicBrainz tag (genre)."""
    data = _get(f"{BASE}/artist", {"query": f"tag:{tag}", "limit": str(limit)})
    return data.get("artists", [])


def get_artist_by_mbid(mbid: str, inc: str = "") -> Dict:
    params: Dict[str, str] = {}
    if inc:
        params["inc"] = inc
    return _get(f"{BASE}/artist/{mbid}", params)


def get_release_group_by_mbid(mbid: str, inc: str = "") -> Dict:
    params: Dict[str, str] = {}
    if inc:
        params["inc"] = inc
    return _get(f"{BASE}/release-group/{mbid}", params)


def get_artist_info(name: str) -> Dict[str, Optional[str]]:
    """Return canonical name, country, and up to 6 tags/genres for the artist."""
    arts = search_artist(name, limit=1)
    if not arts:
        return {"name": name, "country": None, "tags": None}
    a = arts[0]
    mbid = a.get("id")
    country = a.get("country")
    canon = a.get("name") or name
    tags_out: List[str] = []
    if mbid:
        full = get_artist_by_mbid(mbid, inc="tags+genres")
        # Prefer genres, then tags
        for g in full.get("genres", []) or []:
            n = g.get("name")
            if n:
                tags_out.append(n)
        if not tags_out:
            for t in full.get("tags", []) or []:
                n = t.get("name")
                if n:
                    tags_out.append(n)
    tags_str = ", ".join(tags_out[:6]) if tags_out else None
    return {"name": canon, "country": country, "tags": tags_str}


YOUTUBE_HOSTS = ("youtube.com", "youtu.be")


def _extract_youtube_id(url: str) -> Optional[str]:
    if not url:
        return None
    try:
        # Patterns: https://www.youtube.com/watch?v=ID, https://youtu.be/ID, embed forms, with extra params
        m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", url)
        if m:
            return m.group(1)
        m = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", url)
        if m:
            return m.group(1)
        m = re.search(r"/embed/([A-Za-z0-9_-]{11})", url)
        if m:
            return m.group(1)
    except Exception:
        return None
    return None


def search_recordings_by_two_artists(artist1: str, artist2: str, limit: int = 10) -> List[Dict]:
    """
    Find recordings that credit BOTH artists.
    Uses MusicBrainz Lucene query: artist:"A" AND artist:"B"
    Returns list of recordings with title, artist-credit names, first release year if available.
    """
    q = f'artist:"{artist1}" AND artist:"{artist2}"'
    data = _get(
        f"{BASE}/recording",
        {"query": q, "limit": str(limit), "inc": "artist-credits+releases+release-groups+ratings+url-rels"}
    )
    out: List[Dict] = []
    for rec in data.get("recordings", [])[:limit]:
        ac = rec.get("artist-credit", [])
        names = [a.get("name") for a in ac if isinstance(a, dict) and a.get("name")]
        if not names:
            continue
        lower = [n.lower() for n in names]
        if artist1.lower() not in lower or artist2.lower() not in lower:
            continue
        title = rec.get("title") or ""
        rec_mbid = rec.get("id")
        year: Optional[str] = None
        if rec.get("releases"):
            dates = []
            for rel in rec["releases"]:
                d = rel.get("date")
                if d and len(d) >= 4:
                    dates.append(d[:4])
            if dates:
                year = sorted(dates)[0]
        rg = rec.get("release-group")
        rg_mbid = None
        if rg:
            rg_mbid = rg.get("id")
        if not year and rg and rg.get("first-release-date"):
            d = rg.get("first-release-date")
            if d and len(d) >= 4:
                year = d[:4]
        # Ratings (optional)
        rating = rec.get("rating") or {}
        rating_value = rating.get("value")
        rating_votes = rating.get("votes-count") or rating.get("count")

        # Count releases (popularity proxy: more releases = more popular)
        release_count = len(rec.get("releases", []))

        # YouTube relations (optional)
        yt_ids: List[str] = []
        for rel in rec.get("relations", []) or []:
            target = rel.get("url", {}).get("resource") or rel.get("target") or ""
            if any(h in target for h in YOUTUBE_HOSTS):
                vid = _extract_youtube_id(target)
                if vid:
                    yt_ids.append(vid)
        # If no recording-level YouTube URL, try release-group level
        if not yt_ids and rg_mbid:
            try:
                rg_full = get_release_group_by_mbid(rg_mbid, inc="url-rels+ratings")
                for rel in rg_full.get("relations", []) or []:
                    target = rel.get("url", {}).get("resource") or rel.get("target") or ""
                    if any(h in target for h in YOUTUBE_HOSTS):
                        vid = _extract_youtube_id(target)
                        if vid:
                            yt_ids.append(vid)
                # if recording rating missing, consider release-group rating as fallback
                if rating_value is None:
                    rg_rating = rg_full.get("rating") or {}
                    rv = rg_rating.get("value")
                    if rv is not None:
                        rating_value = rv
                if rating_votes is None:
                    rg_rating = rg_full.get("rating") or {}
                    rc = rg_rating.get("votes-count") or rg_rating.get("count")
                    if rc is not None:
                        rating_votes = rc
            except Exception:
                pass

        out.append({
            "title": title,
            "artists": names,
            "year": year or "",
            "recording_mbid": rec_mbid,
            "rating_value": rating_value,
            "rating_votes": rating_votes,
            "youtube_video_ids": yt_ids,
            "release_count": release_count,
        })
    return out
