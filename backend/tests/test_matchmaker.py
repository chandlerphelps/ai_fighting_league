from app.config import Config
from app.engine.matchmaker import generate_fight_card


def _make_fighter(fid: str, healthy: bool = True, last_fight: str = "") -> dict:
    return {
        "id": fid,
        "ring_name": f"Fighter {fid}",
        "record": {"wins": 3, "losses": 2, "draws": 0},
        "condition": {
            "health_status": "healthy" if healthy else "injured",
            "recovery_days_remaining": 0 if healthy else 14,
        },
        "last_fight_date": last_fight,
    }


def _make_world_state(fighter_ids: list[str], injuries: dict = None) -> dict:
    return {
        "current_date": "2026-02-01",
        "rankings": fighter_ids,
        "active_injuries": injuries or {},
        "rivalry_graph": [],
    }


def test_no_injured_fighters_matched():
    config = Config(fights_per_event=2)
    fighters = [
        _make_fighter("f_1", healthy=True),
        _make_fighter("f_2", healthy=False),
        _make_fighter("f_3", healthy=True),
        _make_fighter("f_4", healthy=True),
        _make_fighter("f_5", healthy=True),
    ]
    ws = _make_world_state(["f_1", "f_2", "f_3", "f_4", "f_5"])

    card = generate_fight_card(ws, fighters, [], config)

    matched_ids = set()
    for f1, f2 in card:
        matched_ids.add(f1)
        matched_ids.add(f2)

    assert "f_2" not in matched_ids


def test_no_double_booking():
    config = Config(fights_per_event=3)
    fighters = [_make_fighter(f"f_{i}") for i in range(8)]
    ws = _make_world_state([f"f_{i}" for i in range(8)])

    card = generate_fight_card(ws, fighters, [], config)

    matched_ids = []
    for f1, f2 in card:
        matched_ids.extend([f1, f2])

    assert len(matched_ids) == len(set(matched_ids))


def test_respects_rematch_cooldown():
    config = Config(fights_per_event=1, rematch_cooldown_days=14)
    fighters = [
        _make_fighter("f_1"),
        _make_fighter("f_2"),
        _make_fighter("f_3"),
    ]
    ws = _make_world_state(["f_1", "f_2", "f_3"])

    recent_matches = [{
        "date": "2026-01-25",
        "fighter1_id": "f_1",
        "fighter2_id": "f_2",
        "outcome": {"winner_id": "f_1"},
    }]

    card = generate_fight_card(ws, fighters, recent_matches, config)

    for f1, f2 in card:
        pair = {f1, f2}
        assert pair != {"f_1", "f_2"}, "Should not rematch within cooldown"


def test_active_injuries_excluded():
    config = Config(fights_per_event=1)
    fighters = [
        _make_fighter("f_1", healthy=True),
        _make_fighter("f_2", healthy=True),
        _make_fighter("f_3", healthy=True),
    ]
    ws = _make_world_state(["f_1", "f_2", "f_3"], injuries={"f_2": 7})

    card = generate_fight_card(ws, fighters, [], config)

    matched_ids = set()
    for f1, f2 in card:
        matched_ids.add(f1)
        matched_ids.add(f2)

    assert "f_2" not in matched_ids


def test_handles_too_few_fighters():
    config = Config(fights_per_event=3)
    fighters = [_make_fighter("f_1")]
    ws = _make_world_state(["f_1"])

    card = generate_fight_card(ws, fighters, [], config)
    assert len(card) == 0


def test_rivalry_prioritized():
    config = Config(fights_per_event=1)
    fighters = [
        _make_fighter("f_1"),
        _make_fighter("f_2"),
        _make_fighter("f_3"),
    ]
    ws = _make_world_state(
        ["f_1", "f_2", "f_3"],
    )
    ws["rivalry_graph"] = [{
        "fighter1_id": "f_1",
        "fighter2_id": "f_3",
        "fights": 3,
        "fighter1_wins": 2,
        "fighter2_wins": 1,
        "is_rivalry": True,
    }]

    card = generate_fight_card(ws, fighters, [], config)
    assert len(card) == 1
    pair = {card[0][0], card[0][1]}
    assert pair == {"f_1", "f_3"}
