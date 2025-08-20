
import re
import time
from typing import Optional, List
from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from .config import Config

_FEAT = re.compile(r"\s*(feat\.|featuring|ft\.)\s+.*$", re.I)
_PAREN = re.compile(r"\s*\([^)]*\)")

def _simp(s: str) -> str:
    import re as _re
    return _re.sub(r"\s+", " ", s.casefold()).strip()

def _clean_title(t: str) -> str:
    return _simp(_PAREN.sub("", t))

def _clean_artist(a: str) -> str:
    return _simp(_FEAT.sub("", a))

def _backoff(i: int, base: float = 1.0):
    time.sleep(base * (2 ** i))

def _search(sp: Spotify, q: str, market: Optional[str], retries: int = 3):
    """Spotify search with 403/429/5xx handling and market fallbacks."""
    last = None
    for i in range(retries):
        try:
            return sp.search(q=q, type="track", limit=5, market=market)
        except SpotifyException as se:
            last = se
            if se.http_status == 403 and market == "from_token":
                # token missing user-read-private -> try BA then US
                try:
                    return sp.search(q=q, type="track", limit=5, market="BA")
                except SpotifyException:
                    return sp.search(q=q, type="track", limit=5, market="US")
            if se.http_status == 429:
                retry_after = int(se.headers.get("Retry-After", "1"))
                time.sleep(retry_after + 0.5); continue
            if 500 <= se.http_status < 600:
                _backoff(i); continue
            raise
        except Exception as ge:
            last = ge; _backoff(i)
    if last: raise last
    return {"tracks": {"items": []}}

def search_track_id(sp: Spotify, title: str, artist: str, *, chart_year: int, cfg: Config) -> Optional[str]:
    t = _clean_title(title); a = _clean_artist(artist)
    y1, y2 = chart_year - cfg.year_window, chart_year + cfg.year_window
    queries = [
        f'track:"{t}" artist:"{a}" year:{y1}-{y2}',
        f'{t} {a} year:{y1}-{y2}',
        f'track:"{t}" artist:"{a}"',
        f'{t} {a}', f'track:"{t}"', t,
    ]
    markets: List[str] = [cfg.search_market_default, "US"]
    if cfg.search_market_default == "from_token":
        markets = ["from_token", "BA", "US"]

    for q in queries:
        for m in markets:
            items = _search(sp, q, m).get("tracks", {}).get("items", [])
            for it in items:
                rt = _clean_title(it["name"])
                ra = _clean_artist(", ".join(u["name"] for u in it["artists"]))
                if t == rt and (a in ra or ra in a):
                    return it["id"]
                if t == rt and any(_simp(u["name"]) in a for u in it["artists"]):
                    return it["id"]
    return None
