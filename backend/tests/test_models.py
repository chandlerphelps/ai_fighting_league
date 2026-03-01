import json
from dataclasses import asdict

from app.models.fighter import (
    Fighter, Stats, Record, Injury, Condition,
)
from app.models.match import Match, MatchupAnalysis, MatchOutcome, FightMoment
from app.models.event import Event, EventMatch
from app.models.world_state import WorldState, RivalryRecord


def test_fighter_roundtrip():
    fighter = Fighter(
        id="f_test1234",
        ring_name="The Phantom",
        real_name="John Smith",
        age=28,
        origin="Chicago, USA",
        gender="male",
        height="6'2\"",
        weight="205 lbs",
        build="athletic",
        distinguishing_features="scar across left eye",
        ring_attire="black trunks with silver trim",
        stats=Stats(power=75, speed=80, technique=70, toughness=65, supernatural=0),
        record=Record(wins=5, losses=2, draws=0, kos=3, submissions=0),
        condition=Condition(health_status="healthy"),
        storyline_log=["Won debut fight by KO"],
        rivalries=["f_rival001"],
        last_fight_date="2026-01-15",
        ranking=3,
    )

    data = asdict(fighter)
    json_str = json.dumps(data)
    loaded = json.loads(json_str)
    restored = Fighter.from_dict(loaded)

    assert restored.id == fighter.id
    assert restored.ring_name == fighter.ring_name
    assert restored.stats.power == 75
    assert restored.stats.speed == 80
    assert restored.record.wins == 5
    assert restored.condition.health_status == "healthy"
    assert len(restored.storyline_log) == 1
    assert restored.rivalries == ["f_rival001"]


def test_fighter_total_core_stats():
    fighter = Fighter(
        stats=Stats(power=60, speed=60, technique=60, toughness=60, supernatural=0),
    )
    assert fighter.total_core_stats() == 240


def test_match_roundtrip():
    match = Match(
        id="m_test1234",
        event_id="e_test1234",
        date="2026-01-20",
        fighter1_id="f_a",
        fighter1_name="Fighter A",
        fighter2_id="f_b",
        fighter2_name="Fighter B",
        analysis=MatchupAnalysis(
            fighter1_win_prob=0.55,
            fighter2_win_prob=0.45,
            key_factors=["striking advantage", "ground game edge"],
        ),
        outcome=MatchOutcome(
            winner_id="f_a",
            loser_id="f_b",
            method="ko_tko",
            round_ended=2,
            fighter1_performance="dominant",
            fighter2_performance="poor",
        ),
        moments=[
            FightMoment(
                moment_number=1,
                description="Fighter A lands right cross on Fighter B",
                attacker_id="f_a",
                action="right cross to the jaw",
            ),
        ],
    )

    data = asdict(match)
    json_str = json.dumps(data)
    loaded = json.loads(json_str)
    restored = Match.from_dict(loaded)

    assert restored.id == match.id
    assert restored.analysis.fighter1_win_prob == 0.55
    assert restored.outcome.winner_id == "f_a"
    assert restored.outcome.method == "ko_tko"
    assert len(restored.moments) == 1
    assert restored.moments[0].action == "right cross to the jaw"


def test_event_roundtrip():
    event = Event(
        id="e_test1234",
        date="2026-01-20",
        name="AFL Event 1",
        matches=[
            EventMatch(
                match_id="m_test1234",
                fighter1_id="f_a",
                fighter1_name="Fighter A",
                fighter2_id="f_b",
                fighter2_name="Fighter B",
                completed=True,
                winner_id="f_a",
                method="ko_tko",
            )
        ],
        completed=True,
        summary="Exciting night of fights",
    )

    data = asdict(event)
    json_str = json.dumps(data)
    loaded = json.loads(json_str)
    restored = Event.from_dict(loaded)

    assert restored.id == event.id
    assert len(restored.matches) == 1
    assert restored.matches[0].winner_id == "f_a"


def test_world_state_roundtrip():
    ws = WorldState(
        current_date="2026-01-20",
        day_number=5,
        rankings=["f_a", "f_b", "f_c"],
        upcoming_events=["e_1"],
        completed_events=["e_0"],
        active_injuries={"f_b": 7},
        rivalry_graph=[
            RivalryRecord(
                fighter1_id="f_a",
                fighter2_id="f_c",
                fights=2,
                fighter1_wins=1,
                fighter2_wins=1,
                is_rivalry=True,
            )
        ],
        last_daily_summary="Day 5 complete",
        event_counter=2,
    )

    data = asdict(ws)
    json_str = json.dumps(data)
    loaded = json.loads(json_str)
    restored = WorldState.from_dict(loaded)

    assert restored.current_date == "2026-01-20"
    assert restored.day_number == 5
    assert len(restored.rankings) == 3
    assert restored.active_injuries["f_b"] == 7
    assert restored.rivalry_graph[0].is_rivalry is True
    assert restored.event_counter == 2


def test_condition_with_injuries_roundtrip():
    condition = Condition(
        health_status="injured",
        injuries=[
            Injury(type="concussion", severity="moderate", recovery_days_remaining=14)
        ],
        recovery_days_remaining=14,
        morale="low",
        momentum="negative",
    )

    data = asdict(condition)
    json_str = json.dumps(data)
    loaded = json.loads(json_str)
    restored = Condition.from_dict(loaded)

    assert restored.health_status == "injured"
    assert len(restored.injuries) == 1
    assert restored.injuries[0].severity == "moderate"
    assert restored.injuries[0].recovery_days_remaining == 14
