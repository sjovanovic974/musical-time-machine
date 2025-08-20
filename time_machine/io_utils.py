
from pathlib import Path
from typing import List
import csv, json
from .models import Song

def save_to_csv(songs: List[Song], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "title", "artist"])
        for s in songs:
            w.writerow([s.rank, s.title, s.artist])

def save_to_json(songs: List[Song], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [{"rank": s.rank, "title": s.title, "artist": s.artist} for s in songs]
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
