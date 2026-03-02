from collections import Counter

from app.engine.combat.simulator import simulate_combat


def _make_fighter(fighter_id: str, power=50, speed=50, technique=50, toughness=50) -> dict:
    return {
        "id": fighter_id,
        "ring_name": f"Fighter {fighter_id}",
        "stats": {
            "power": power,
            "speed": speed,
            "technique": technique,
            "toughness": toughness,
            "supernatural": 0,
        },
        "record": {"wins": 3, "losses": 2, "draws": 0},
        "condition": {"health_status": "healthy"},
    }


def test_outcome_distribution():
    f1 = _make_fighter("f_1", power=65, speed=60, technique=55, toughness=55)
    f2 = _make_fighter("f_2", power=45, speed=50, technique=50, toughness=50)

    winners = Counter()
    iterations = 100

    for seed in range(iterations):
        result = simulate_combat(f1, f2, seed=seed)
        winners[result.winner_id] += 1

    f1_win_rate = winners.get("f_1", 0) / iterations
    assert 0.40 < f1_win_rate < 0.90, f"Fighter 1 win rate {f1_win_rate} outside expected range"


def test_outcome_always_valid():
    f1 = _make_fighter("f_1", power=70, speed=60, technique=65, toughness=55)
    f2 = _make_fighter("f_2", power=40, speed=50, technique=45, toughness=50)

    for seed in range(50):
        result = simulate_combat(f1, f2, seed=seed)
        assert result.final_round >= 1
        assert result.method in ("ko", "tko", "submission")
        assert result.winner_id in ("f_1", "f_2")
        assert result.loser_id in ("f_1", "f_2")
        assert result.winner_id != result.loser_id
        assert len(result.tick_log) > 0
