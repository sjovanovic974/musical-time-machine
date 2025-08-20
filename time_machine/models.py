
from dataclasses import dataclass

@dataclass(frozen=True)
class Song:
    """Simple value object for a chart entry."""
    rank: int
    title: str
    artist: str

class AppError(Exception):
    """Base app error."""

class FetchError(AppError):
    """External fetch (network/API) error."""
