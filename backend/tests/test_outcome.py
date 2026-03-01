from collections import Counter

from app.config import Config
from app.models.match import MatchupAnalysis
from app.engine.fight_simulator import determine_outcome


def _make_fighter(fighter_id: str) -> dict:
    return {
        "id": fighter_id,
        "ring_name": f"Fighter {fighter_id}",
        "record": {"wins": 3, "losses": 2, "draws": 0},
        "condition": {"health_status": "healthy"},
    }


def test_outcome_distribution():
    config = Config()
    analysis = MatchupAnalysis(
        fighter1_win_prob=0.6,
        fighter2_win_prob=0.4,
        key_factors=["striking edge", "ground game"],
    )

    f1 = _make_fighter("f_1")
    f2 = _make_fighter("f_2")

    winners = Counter()
    injury_count = 0
    iterations = 1000

    for _ in range(iterations):
        outcome = determine_outcome(f1, f2, analysis, config)

        if outcome.is_draw:
            winners["draw"] += 1
        else:
            winners[outcome.winner_id] += 1

        assert outcome.method == "ko_tko"

        if outcome.fighter1_injuries or outcome.fighter2_injuries:
            injury_count += 1

    f1_win_rate = winners.get("f_1", 0) / iterations
    assert 0.45 < f1_win_rate < 0.75, f"Fighter 1 win rate {f1_win_rate} outside expected range"

    draw_rate = winners.get("draw", 0) / iterations
    assert draw_rate == 0, f"Draw rate {draw_rate} should be 0 (all fights end in KO)"

    injury_rate = injury_count / iterations
    assert 0.05 < injury_rate < 0.60, f"Injury rate {injury_rate} outside expected range"


def test_outcome_always_valid():
    config = Config()
    analysis = MatchupAnalysis(
        fighter1_win_prob=0.8,
        fighter2_win_prob=0.2,
    )

    f1 = _make_fighter("f_1")
    f2 = _make_fighter("f_2")

    for _ in range(200):
        outcome = determine_outcome(f1, f2, analysis, config)
        assert outcome.round_ended >= 3
        assert outcome.round_ended <= 6
        assert outcome.method == "ko_tko"
        assert outcome.is_draw is False
        assert outcome.fighter1_performance in ["dominant", "competitive", "poor"]
        assert outcome.fighter2_performance in ["dominant", "competitive", "poor"]
        assert outcome.winner_id in ["f_1", "f_2"]
        assert outcome.loser_id in ["f_1", "f_2"]
        assert outcome.winner_id != outcome.loser_id
