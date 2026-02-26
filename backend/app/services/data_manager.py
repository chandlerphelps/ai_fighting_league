import json
from dataclasses import asdict
from pathlib import Path

from app.config import Config


def _get_data_dir(config: Config = None) -> Path:
    if config:
        return config.data_dir
    return Path(__file__).resolve().parent.parent.parent.parent / "data"


def ensure_data_dirs(config: Config = None):
    data_dir = _get_data_dir(config)
    (data_dir / "fighters").mkdir(parents=True, exist_ok=True)
    (data_dir / "matches").mkdir(parents=True, exist_ok=True)
    (data_dir / "events").mkdir(parents=True, exist_ok=True)


def _save_json(path: Path, data):
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    elif hasattr(data, "__dataclass_fields__"):
        data = asdict(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def save_fighter(fighter, config: Config = None):
    data_dir = _get_data_dir(config)
    fighter_id = fighter.id if hasattr(fighter, "id") else fighter["id"]
    _save_json(data_dir / "fighters" / f"{fighter_id}.json", fighter)


def load_fighter(fighter_id: str, config: Config = None) -> dict | None:
    data_dir = _get_data_dir(config)
    return _load_json(data_dir / "fighters" / f"{fighter_id}.json")


def load_all_fighters(config: Config = None) -> list[dict]:
    data_dir = _get_data_dir(config)
    fighters_dir = data_dir / "fighters"
    if not fighters_dir.exists():
        return []
    fighters = []
    for path in sorted(fighters_dir.glob("*.json")):
        data = _load_json(path)
        if data:
            fighters.append(data)
    return fighters


def save_match(match, config: Config = None):
    data_dir = _get_data_dir(config)
    match_id = match.id if hasattr(match, "id") else match["id"]
    _save_json(data_dir / "matches" / f"{match_id}.json", match)


def load_match(match_id: str, config: Config = None) -> dict | None:
    data_dir = _get_data_dir(config)
    return _load_json(data_dir / "matches" / f"{match_id}.json")


def load_all_matches(config: Config = None) -> list[dict]:
    data_dir = _get_data_dir(config)
    matches_dir = data_dir / "matches"
    if not matches_dir.exists():
        return []
    matches = []
    for path in sorted(matches_dir.glob("*.json")):
        data = _load_json(path)
        if data:
            matches.append(data)
    return matches


def save_event(event, config: Config = None):
    data_dir = _get_data_dir(config)
    event_id = event.id if hasattr(event, "id") else event["id"]
    _save_json(data_dir / "events" / f"{event_id}.json", event)


def load_event(event_id: str, config: Config = None) -> dict | None:
    data_dir = _get_data_dir(config)
    return _load_json(data_dir / "events" / f"{event_id}.json")


def load_all_events(config: Config = None) -> list[dict]:
    data_dir = _get_data_dir(config)
    events_dir = data_dir / "events"
    if not events_dir.exists():
        return []
    events = []
    for path in sorted(events_dir.glob("*.json")):
        data = _load_json(path)
        if data:
            events.append(data)
    return events


def save_world_state(world_state, config: Config = None):
    data_dir = _get_data_dir(config)
    _save_json(data_dir / "world_state.json", world_state)


def load_world_state(config: Config = None) -> dict | None:
    data_dir = _get_data_dir(config)
    return _load_json(data_dir / "world_state.json")
