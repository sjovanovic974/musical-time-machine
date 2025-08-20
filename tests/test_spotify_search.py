
from time_machine.config import Config
from time_machine.spotify_search import search_track_id

class _FakeSpotify:
    def __init__(self, items):
        self._items = items
    def search(self, q, type, limit, market):
        return {"tracks": {"items": self._items}}

def test_search_track_id_exact_match():
    cfg = Config()
    fake_items = [{
        "id": "track123",
        "name": "My Song",
        "artists": [{"name": "The Artist"}],
    }]
    sp = _FakeSpotify(fake_items)
    tid = search_track_id(sp, "My Song", "The Artist", chart_year=2000, cfg=cfg)
    assert tid == "track123"
