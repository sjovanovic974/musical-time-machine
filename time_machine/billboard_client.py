
from datetime import datetime, date
from typing import List, Tuple
import billboard
from .models import Song, FetchError
from .config import Config

def fetch_hot100(target: date, cfg: Config) -> Tuple[List[Song], date]:
    """Fetch Billboard Hot 100 aligned to the chart week on/before the given date."""
    try:
        chart = billboard.ChartData(cfg.chart_name, date=target.isoformat())
    except Exception as exc:
        raise FetchError(f"Failed to fetch Billboard {cfg.chart_name} for {target}: {exc}") from exc
    if not chart:
        raise FetchError(f"No Billboard {cfg.chart_name} data for {target}.")

    week_str = getattr(chart, "date", None)
    chart_week = datetime.strptime(week_str, "%Y-%m-%d").date() if week_str else target

    songs = [Song(rank=int(entry.rank), title=entry.title, artist=entry.artist) for entry in chart]
    return songs, chart_week
