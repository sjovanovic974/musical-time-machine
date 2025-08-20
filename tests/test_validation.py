
import pytest
from datetime import date, timedelta
from time_machine.config import Config
from time_machine.validation import parse_and_validate_date

def test_valid_date_parses():
    cfg = Config()
    assert parse_and_validate_date("2000-01-01", cfg).isoformat() == "2000-01-01"

def test_future_date_rejected():
    cfg = Config()
    future = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError):
        parse_and_validate_date(future, cfg)

def test_before_min_date_rejected():
    cfg = Config()
    with pytest.raises(ValueError):
        parse_and_validate_date("1950-01-01", cfg)

def test_invalid_format_rejected():
    cfg = Config()
    with pytest.raises(ValueError):
        parse_and_validate_date("01-01-2000", cfg)
