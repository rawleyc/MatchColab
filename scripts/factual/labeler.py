from typing import Optional

from .config import (
    YOUTUBE_SUCCESS_VIEWS,
    USE_MB_RATINGS,
    MB_RATING_MIN,
    MB_RATING_VOTES_MIN,
    MIN_RELEASES_FOR_SUCCESS,
)


def label_success(
    yt_views: Optional[int],
    rating_value: Optional[float] = None,
    rating_votes: Optional[int] = None,
    has_youtube: bool = False,
    release_count: int = 0,
) -> str:
    """Label Success using only MusicBrainz-sourced signals (no external views):
    - Prefer MusicBrainz recording ratings when enabled and present.
    - Otherwise, treat presence of a YouTube relation in MusicBrainz as Success (proxy for official video/cultural impact).
    - Otherwise, if recording has many releases (MIN_RELEASES_FOR_SUCCESS+), label Success (popular songs get many pressings).
    - Else Failure.
    Note: yt_views is ignored in this MB-only mode; kept for signature compatibility.
    """
    if USE_MB_RATINGS and rating_value is not None and rating_votes is not None:
        try:
            if float(rating_value) >= MB_RATING_MIN and int(rating_votes) >= MB_RATING_VOTES_MIN:
                return "Success"
        except Exception:
            pass
    if has_youtube:
        return "Success"
    if release_count >= MIN_RELEASES_FOR_SUCCESS:
        return "Success"
    return "Failure"
