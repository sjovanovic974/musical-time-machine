
from dataclasses import dataclass, replace
from datetime import date
import os

@dataclass(frozen=True)
class Config:
    # Billboard / general
    billboard_min_date: date = date(1958, 8, 4)  # Hot 100 start
    chart_name: str = "hot-100"
    max_attempts: int = 5
    playlist_size: int = 10  # how many songs to include in preview & playlist

    # Search behavior
    search_market_default: str = "BA"  # Try Bosnia and Herzegovina first, fallback to US
    year_window: int = 1               # search between [year-1 .. year+1]

    # Spotify OAuth/env (must match your Spotify Dashboard Redirect URI exactly)
    client_id: str = os.environ.get("SPOTIPY_CLIENT_ID", "").strip()
    client_secret: str = os.environ.get("SPOTIPY_CLIENT_SECRET", "").strip()
    redirect_uri: str = os.environ.get("SPOTIPY_REDIRECT_URI", "").strip()
    scopes: str = "playlist-modify-private playlist-modify-public"
    token_cache_path: str = ".spotify_cache"

def with_overrides(cfg: Config, **kwargs) -> Config:
    """Return a copy of cfg with provided overrides."""
    return replace(cfg, **kwargs)
