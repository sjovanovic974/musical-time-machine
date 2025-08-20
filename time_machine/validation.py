
from datetime import datetime, date
from .config import Config

def parse_and_validate_date(raw: str, cfg: Config) -> date:
    """Parse user string into a date and enforce business rules."""
    try:
        parsed_date = datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Invalid date format! Please use YYYY-MM-DD.") from exc

    if parsed_date > date.today():
        raise ValueError("Date cannot be in the future.")
    if parsed_date < cfg.billboard_min_date:
        raise ValueError(
            f"Billboard charts are not available before {cfg.billboard_min_date.isoformat()}."
        )
    return parsed_date

def prompt_travel_date(cfg: Config) -> date:
    """Prompt up to cfg.max_attempts for a valid date; exit on abuse."""
    attempt_count = 0
    while attempt_count < cfg.max_attempts:
        raw_value = input("What year would you like to travel to? (YYYY-MM-DD): ")
        try:
            valid_date = parse_and_validate_date(raw_value, cfg)
            print(f"✅ Valid date entered: {valid_date.isoformat()}")
            return valid_date
        except ValueError as val_err:
            attempt_count += 1
            remaining = cfg.max_attempts - attempt_count
            print(f"❌ {val_err}")
            if remaining <= 0:
                print("Misuse of the application is not allowed!")
                raise SystemExit(1)
            print(f"Please try again. Attempts left: {remaining}")
    raise SystemExit(1)
