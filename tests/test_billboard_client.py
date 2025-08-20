
from datetime import date
from time_machine.config import Config
from time_machine.billboard_client import fetch_hot100
from time_machine.models import Song

class _FakeEntry:
    def __init__(self, rank, title, artist):
        self.rank = str(rank)
        self.title = title
        self.artist = artist

class _FakeChart:
    def __init__(self):
        self.date = "2000-01-01"
        self._items = [
            _FakeEntry(1, "One", "Artist A"),
            _FakeEntry(2, "Two", "Artist B"),
        ]
    def __len__(self): return len(self._items)
    def __iter__(self):
        return iter(self._items)

def test_fetch_hot100_monkeypatch(monkeypatch):
    cfg = Config()
    def _fake_chartdata(name, date=None):
        assert name == cfg.chart_name
        return _FakeChart()
    monkeypatch.setattr("time_machine.billboard_client.billboard.ChartData", _fake_chartdata)
    songs, week = fetch_hot100(date(2000,1,1), cfg)
    assert week.isoformat() == "2000-01-01"
    assert isinstance(songs[0], Song)
    assert songs[0].title == "One"
