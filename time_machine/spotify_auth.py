
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import Config

def get_client(cfg: Config) -> spotipy.Spotify:
    missing = [k for k, v in {
        "SPOTIPY_CLIENT_ID": cfg.client_id,
        "SPOTIPY_CLIENT_SECRET": cfg.client_secret,
        "SPOTIPY_REDIRECT_URI": cfg.redirect_uri,
    }.items() if not v]
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

    auth = SpotifyOAuth(
        client_id=cfg.client_id,
        client_secret=cfg.client_secret,
        redirect_uri=cfg.redirect_uri,   # e.g., http://127.0.0.1:8888/callback
        scope=cfg.scopes,
        cache_path=cfg.token_cache_path,
        open_browser=True,
        show_dialog=False,
    )
    return spotipy.Spotify(auth_manager=auth)
