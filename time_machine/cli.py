
import argparse
from pathlib import Path
import logging

from .config import Config, with_overrides
from .validation import prompt_travel_date, parse_and_validate_date
from .billboard_client import fetch_hot100
from .spotify_auth import get_client
from .spotify_search import search_track_id
from .spotify_playlist import build_playlist
from .io_utils import save_to_csv, save_to_json
from .logging_setup import setup_logging

def _print_preview(songs, week, limit: int) -> None:
    print(f"\n🎵 Billboard Hot 100 — Week of {week.isoformat()}")
    print("-" * 64)
    for s in songs[:limit]:
        print(f"{s.rank:>3}. {s.title} — {s.artist}")
    print("-" * 64)
    if len(songs) > limit:
        print(f"Showing top {limit} of {len(songs)} rows.\n")

def get_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Musical Time Machine CLI")
    p.add_argument("--date", help="Target date in YYYY-MM-DD format (overrides interactive prompt)")
    p.add_argument("--playlist-size", type=int, default=None, help="How many songs to include (preview + playlist)")
    p.add_argument("--preview", type=int, default=None, help="How many songs to print in preview (defaults to playlist size)")
    p.add_argument("--save", choices=["none", "csv", "json"], default="none", help="Save chart to a file")
    p.add_argument("--outdir", default="charts", help="Output directory for saved files")
    p.add_argument("--dry-run", action="store_true", help="Skip Spotify calls; fetch and print only")
    p.add_argument("--public", action="store_true", help="Create a public playlist (default is private)")
    p.add_argument("--market", choices=["BA", "US", "from_token"], default=None, help="Override default search market")
    p.add_argument("--verbose", action="store_true", help="Verbose logging")
    return p.parse_args()

def main() -> None:
    args = get_args()
    setup_logging(args.verbose)

    cfg = Config()
    overrides = {}
    if args.playlist_size is not None:
        overrides["playlist_size"] = max(1, int(args.playlist_size))
    if args.market is not None:
        overrides["search_market_default"] = args.market
    if overrides:
        cfg = with_overrides(cfg, **overrides)

    try:
        travel = parse_and_validate_date(args.date, cfg) if args.date else prompt_travel_date(cfg)
        songs, week = fetch_hot100(travel, cfg)
        preview_n = args.preview if args.preview is not None else cfg.playlist_size
        _print_preview(songs, week, limit=preview_n)
    except Exception as exc:
        logging.error("Failed before Spotify step: %s", exc)
        raise SystemExit(1)

    # Optional persistence
    if args.save != "none":
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        out_path = outdir / f"{cfg.chart_name}_{week.isoformat()}.{args.save}"
        if args.save == "csv":
            save_to_csv(songs, out_path)
        else:
            save_to_json(songs, out_path)
        print(f"💾 Saved chart to: {out_path}")

    if args.dry_run:
        print("ℹ️ Dry-run: skipping Spotify playlist creation.")
        return

    try:
        sp = get_client(cfg)
        build_playlist(sp, songs, week, public=args.public, search_track_id=search_track_id, cfg=cfg)
    except Exception as exc:
        logging.error("Spotify step failed: %s", exc)
        raise SystemExit(1)
