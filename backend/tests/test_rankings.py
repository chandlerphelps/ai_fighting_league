from app.engine.rankings import calculate_rankings


def _make_fighter(fid: str, wins: int, losses: int, draws: int = 0, last_fight: str = "") -> dict:
    return {
        "id": fid,
        "record": {"wins": wins, "losses": losses, "draws": draws, "kos": 0, "submissions": 0},
        "last_fight_date": last_fight,
    }


def test_basic_ranking_order():
    fighters = [
        _make_fighter("f_a", wins=5, losses=1),
        _make_fighter("f_b", wins=3, losses=3),
        _make_fighter("f_c", wins=4, losses=2),
    ]

    rankings = calculate_rankings(fighters, [])

    assert rankings[0] == "f_a"
    assert rankings[1] == "f_c"
    assert rankings[2] == "f_b"


def test_tiebreak_by_total_wins():
    fighters = [
        _make_fighter("f_a", wins=3, losses=1),
        _make_fighter("f_b", wins=6, losses=2),
    ]

    rankings = calculate_rankings(fighters, [])
    assert rankings[0] == "f_b"


def test_no_fights_ranked_last():
    fighters = [
        _make_fighter("f_a", wins=0, losses=0),
        _make_fighter("f_b", wins=1, losses=0),
        _make_fighter("f_c", wins=0, losses=0),
    ]

    rankings = calculate_rankings(fighters, [])
    assert rankings[0] == "f_b"
    assert "f_a" in rankings[1:]
    assert "f_c" in rankings[1:]


def test_recent_form_matters():
    fighters = [
        _make_fighter("f_a", wins=5, losses=5, last_fight="2026-01-20"),
        _make_fighter("f_b", wins=5, losses=5, last_fight="2026-01-10"),
    ]

    recent_matches = [
        {"date": "2026-01-20", "fighter1_id": "f_a", "fighter2_id": "f_x", "outcome": {"winner_id": "f_a"}},
        {"date": "2026-01-19", "fighter1_id": "f_a", "fighter2_id": "f_y", "outcome": {"winner_id": "f_a"}},
        {"date": "2026-01-18", "fighter1_id": "f_a", "fighter2_id": "f_z", "outcome": {"winner_id": "f_a"}},
        {"date": "2026-01-10", "fighter1_id": "f_b", "fighter2_id": "f_x", "outcome": {"winner_id": "f_x"}},
        {"date": "2026-01-09", "fighter1_id": "f_b", "fighter2_id": "f_y", "outcome": {"winner_id": "f_y"}},
    ]

    rankings = calculate_rankings(fighters, recent_matches)
    assert rankings[0] == "f_a"
