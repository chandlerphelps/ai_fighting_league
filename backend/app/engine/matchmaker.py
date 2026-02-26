from datetime import datetime, timedelta

from app.config import Config


def generate_fight_card(
    world_state: dict, fighters: list[dict], matches: list[dict], config: Config
) -> list[tuple[str, str]]:
    current_date = world_state.get("current_date", "")
    rankings = world_state.get("rankings", [])

    rank_map = {fid: i for i, fid in enumerate(rankings)}

    available = []
    for f in fighters:
        if f.get("condition", {}).get("health_status", "healthy") != "healthy":
            continue
        if f.get("condition", {}).get("recovery_days_remaining", 0) > 0:
            continue
        if world_state.get("active_injuries", {}).get(f["id"], 0) > 0:
            continue
        available.append(f)

    if len(available) < 2:
        return []

    recent_pairings = _get_recent_pairings(matches, current_date, config.rematch_cooldown_days)

    scored_pairs = []
    for i in range(len(available)):
        for j in range(i + 1, len(available)):
            f1 = available[i]
            f2 = available[j]
            pair_key = tuple(sorted([f1["id"], f2["id"]]))

            if pair_key in recent_pairings:
                continue

            score = _score_pairing(f1, f2, rank_map, world_state, current_date)
            scored_pairs.append((score, f1["id"], f2["id"]))

    scored_pairs.sort(reverse=True, key=lambda x: x[0])

    selected = []
    used_fighters = set()
    for score, f1_id, f2_id in scored_pairs:
        if f1_id in used_fighters or f2_id in used_fighters:
            continue
        selected.append((f1_id, f2_id))
        used_fighters.add(f1_id)
        used_fighters.add(f2_id)
        if len(selected) >= config.fights_per_event:
            break

    return selected


def _score_pairing(
    fighter1: dict, fighter2: dict, rank_map: dict, world_state: dict, current_date: str
) -> float:
    score = 0.0

    rank1 = rank_map.get(fighter1["id"], 99)
    rank2 = rank_map.get(fighter2["id"], 99)
    rank_diff = abs(rank1 - rank2)
    if rank_diff <= 4:
        score += 10
    elif rank_diff <= 8:
        score += 5

    rivalry_graph = world_state.get("rivalry_graph", [])
    for rivalry in rivalry_graph:
        ids = {rivalry.get("fighter1_id"), rivalry.get("fighter2_id")}
        if {fighter1["id"], fighter2["id"]} == ids and rivalry.get("is_rivalry"):
            score += 15
            break

    if current_date:
        try:
            today = datetime.strptime(current_date, "%Y-%m-%d")
            for f in [fighter1, fighter2]:
                last_fight = f.get("last_fight_date")
                if last_fight:
                    last = datetime.strptime(last_fight, "%Y-%m-%d")
                    idle_days = (today - last).days
                    if idle_days > 7:
                        score += min((idle_days - 7) * 2, 20)
                else:
                    score += 15
        except ValueError:
            pass

    return score


def _get_recent_pairings(
    matches: list[dict], current_date: str, cooldown_days: int
) -> set[tuple[str, str]]:
    recent = set()
    if not current_date:
        return recent

    try:
        today = datetime.strptime(current_date, "%Y-%m-%d")
    except ValueError:
        return recent

    cutoff = today - timedelta(days=cooldown_days)

    for match in matches:
        match_date_str = match.get("date", "")
        if not match_date_str:
            continue
        try:
            match_date = datetime.strptime(match_date_str, "%Y-%m-%d")
        except ValueError:
            continue

        if match_date >= cutoff:
            pair = tuple(sorted([match.get("fighter1_id", ""), match.get("fighter2_id", "")]))
            recent.add(pair)

    return recent
