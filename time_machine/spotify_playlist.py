
from typing import List
from datetime import date
from spotipy import Spotify
from .models import Song

def create_playlist(sp: Spotify, user_id: str, name: str, public: bool, desc: str) -> str:
    return sp.user_playlist_create(user=user_id, name=name, public=public, description=desc)["id"]

def add_tracks(sp: Spotify, playlist_id: str, tids: List[str], chunk: int = 100) -> None:
    for i in range(0, len(tids), chunk):
        sp.playlist_add_items(playlist_id, tids[i:i+chunk])

def build_playlist(sp: Spotify, songs: List[Song], week: date, *, public: bool, search_track_id, cfg) -> None:
    """Create 'Time Machine YYYY-MM-DD — Hot 100' and fill it with matched tracks.
    Respects cfg.playlist_size for how many songs to include.
    """
    user_id = sp.current_user()["id"]
    name = f"Time Machine {week.isoformat()} — Hot 100"
    desc = f"Billboard Hot 100 for the week of {week.isoformat()} (generated)."
    print(f"🟢 Creating playlist: {name}")
    pid = create_playlist(sp, user_id, name, public, desc)

    subset = songs[: cfg.playlist_size]

    found_ids: List[str] = []
    missing: List[Song] = []
    for s in subset:
        tid = search_track_id(sp, s.title, s.artist, chart_year=week.year, cfg=cfg)
        if tid:
            found_ids.append(tid)
            print(f" + Matched #{s.rank}: {s.title} — {s.artist}")
        else:
            missing.append(s)
            print(f" - Not found: {s.title} — {s.artist}")

    unique_ids = list(dict.fromkeys(found_ids))
    if unique_ids:
        print(f"🎯 Adding {len(unique_ids)} tracks to playlist (deduped).")
        add_tracks(sp, pid, unique_ids)
    else:
        print("⚠️ No tracks were matched; playlist will remain empty.")
    if missing:
        print(f"⚠️ Unmatched tracks: {len(missing)}")
    print(f"✅ Done. Open Spotify and check the playlist: {name}")
