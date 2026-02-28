import json
import re
from dataclasses import asdict
from pathlib import Path

from app.config import Config


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


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


def _fighter_filename(fighter_id: str, ring_name: str = "") -> str:
    if ring_name:
        return f"{fighter_id}_{_slugify(ring_name)}.json"
    return f"{fighter_id}.json"


def _find_fighter_path(fighters_dir: Path, fighter_id: str) -> Path | None:
    matches = list(fighters_dir.glob(f"{fighter_id}*.json"))
    if matches:
        return matches[0]
    return None


def save_fighter(fighter, config: Config = None):
    data_dir = _get_data_dir(config)
    fighter_id = fighter.id if hasattr(fighter, "id") else fighter["id"]
    ring_name = fighter.ring_name if hasattr(fighter, "ring_name") else fighter.get("ring_name", "")
    fighters_dir = data_dir / "fighters"
    old = _find_fighter_path(fighters_dir, fighter_id)
    new_path = fighters_dir / _fighter_filename(fighter_id, ring_name)
    if old and old != new_path:
        old.unlink()
    _save_json(new_path, fighter)


def load_fighter(fighter_id: str, config: Config = None) -> dict | None:
    data_dir = _get_data_dir(config)
    path = _find_fighter_path(data_dir / "fighters", fighter_id)
    if path:
        return _load_json(path)
    return None


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
