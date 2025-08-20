
from datetime import date
from time_machine.config import Config, with_overrides
from time_machine.models import Song
from time_machine.spotify_playlist import build_playlist

class _FakeSpotify:
    def __init__(self):
        self.created = None
        self.added = []
    def current_user(self):
        return {"id": "me"}
    def user_playlist_create(self, user, name, public, description):
        self.created = {"user": user, "name": name, "public": public, "description": description, "id": "pl123"}
        return {"id": "pl123"}
    def playlist_add_items(self, pid, chunk):
        self.added.extend(chunk)

def _fake_search(sp, title, artist, chart_year, cfg):
    # pretend we only match tracks for even-numbered ranks by title suffix
    return f"id_{title}" if title.endswith("2") else None

def test_build_playlist_respects_size_and_dedup():
    cfg = with_overrides(Config(), playlist_size=3)
    songs = [
        Song(rank=1, title="T1", artist="A"),
        Song(rank=2, title="T2", artist="B"),
        Song(rank=2, title="T2", artist="B"),  # duplicate title to test dedup
        Song(rank=3, title="T3", artist="C"),
        Song(rank=4, title="T4", artist="D"),
    ]
    sp = _FakeSpotify()
    build_playlist(sp, songs, date(2000,1,1), public=False, search_track_id=_fake_search, cfg=cfg)
    # Only top 3 songs processed (T1, T2, T2). Only T2 matched, dedup leaves one item.
    assert sp.created["id"] == "pl123"
    assert sp.added == ["id_T2"]
