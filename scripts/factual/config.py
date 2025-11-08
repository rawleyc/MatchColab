import os

# MusicBrainz username provided by user
MB_USERNAME = os.getenv("MB_USERNAME", "DartMouthWrld")

# Required for polite API usage (MusicBrainz asks for a descriptive UA)
# Compose a sensible default UA that includes the username. You can override via MB_USER_AGENT env var.
MB_USER_AGENT = os.getenv("MB_USER_AGENT", "CollabDataset/1.0 (MusicBrainz: DartMouthWrld)")

# Optional: YouTube Data API key for view counts
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Output size target
TARGET_ROWS = int(os.getenv("FACTUAL_TARGET_ROWS", "600"))

# Success threshold for YouTube views
YOUTUBE_SUCCESS_VIEWS = int(os.getenv("YOUTUBE_SUCCESS_VIEWS", "1000000"))  # 1M

# MusicBrainz rate limit: seconds to wait between requests
MB_RATE_LIMIT_SECONDS = float(os.getenv("MB_RATE_LIMIT_SECONDS", "1.0"))

# Use MusicBrainz recording ratings as fallback success signal when YouTube views are unavailable
USE_MB_RATINGS = os.getenv("USE_MB_RATINGS", "true").lower() in {"1", "true", "yes"}
# Minimum average rating (0-5) and minimum votes to consider a recording a Success
MB_RATING_MIN = float(os.getenv("MB_RATING_MIN", "3.8"))
MB_RATING_VOTES_MIN = int(os.getenv("MB_RATING_VOTES_MIN", "10"))

# Use release count as success proxy (popular songs have many releases/pressings/editions)
MIN_RELEASES_FOR_SUCCESS = int(os.getenv("MIN_RELEASES_FOR_SUCCESS", "5"))

# Artist discovery from MusicBrainz to broaden coverage
DISCOVER_FROM_MB = os.getenv("DISCOVER_FROM_MB", "true").lower() in {"1", "true", "yes"}
# Comma-separated tags to pull artists from (genre/style buckets)
DISCOVERY_TAGS = os.getenv(
	"DISCOVERY_TAGS",
	",".join([
		"pop", "hip hop", "rap", "rock", "metal", "edm", "electronic", "r&b", "soul",
		"country", "afrobeats", "afropop", "k-pop", "latin", "reggaeton", "trap",
		"indie", "alternative",
	])
)
ARTISTS_PER_TAG = int(os.getenv("ARTISTS_PER_TAG", "40"))
MAX_RECORDINGS_PER_PAIR = int(os.getenv("MAX_RECORDINGS_PER_PAIR", "12"))
MAX_CANDIDATE_PAIRS = int(os.getenv("MAX_CANDIDATE_PAIRS", "2000"))
