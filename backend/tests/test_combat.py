import random
import pytest

from app.engine.combat.models import (
    FighterCombatState,
    EmotionalState,
    Position,
    TickOutcome,
    FinishMethod,
    CombatResult,
)
from app.engine.combat.moves import (
    MoveDefinition,
    UNIVERSAL_MOVES,
    get_available_moves,
)
from app.engine.combat.damage import (
    calculate_hit_chance,
    calculate_damage,
    resolve_attack,
    apply_damage,
    apply_attacker_costs,
)
from app.engine.combat.conditions import (
    update_emotions_on_hit,
    update_emotions_on_miss,
    update_mana,
    apply_emotional_modifiers,
)
from app.engine.combat.win_conditions import check_ko, check_tko, check_submission
from app.engine.combat.strategy import WeightedStrategy
from app.engine.combat.simulator import simulate_combat


def _make_fighter_data(
    fighter_id="f1",
    ring_name="Test Fighter",
    power=50, speed=50, technique=50, toughness=50, supernatural=0,
):
    return {
        "id": fighter_id,
        "ring_name": ring_name,
        "stats": {
            "power": power,
            "speed": speed,
            "technique": technique,
            "toughness": toughness,
            "supernatural": supernatural,
        },
    }


class TestFighterCombatState:
    def test_from_fighter_data_defaults(self):
        data = _make_fighter_data()
        state = FighterCombatState.from_fighter_data(data)

        assert state.fighter_id == "f1"
        assert state.max_hp == 80.0 + 50 * 0.7
        assert state.max_stamina == 80.0 + (50 + 50) * 0.3
        assert state.max_mana == 0.0
        assert state.mana == 0.0
        assert state.hp == state.max_hp
        assert state.position == Position.STANDING
        assert state.stun_ticks == 0
        assert state.combo_counter == 0

    def test_from_fighter_data_high_stats(self):
        data = _make_fighter_data(power=90, speed=80, technique=85, toughness=75, supernatural=40)
        state = FighterCombatState.from_fighter_data(data)

        assert state.max_hp == 80.0 + 75 * 0.7
        assert state.max_stamina == 80.0 + (80 + 75) * 0.3
        assert state.max_mana == 80.0
        assert state.mana == 0.0

    def test_snapshot_returns_dict(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        snap = state.snapshot()
        assert isinstance(snap, dict)
        assert "hp" in snap
        assert "emotions" in snap


class TestMoves:
    def test_universal_catalog_has_expected_moves(self):
        expected = ["jab", "cross", "hook", "uppercut", "block", "slip", "recover"]
        for move_id in expected:
            assert move_id in UNIVERSAL_MOVES

    def test_move_catalog_count(self):
        assert len(UNIVERSAL_MOVES) >= 25

    def test_get_available_moves_standing(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        available = get_available_moves(state)
        move_ids = {m.id for m in available}
        assert "jab" in move_ids
        assert "cross" in move_ids
        assert "block" in move_ids
        assert "ground_and_pound" not in move_ids

    def test_get_available_moves_ground(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        state.position = Position.GROUND
        available = get_available_moves(state)
        move_ids = {m.id for m in available}
        assert "ground_and_pound" in move_ids
        assert "jab" not in move_ids

    def test_get_available_moves_no_mana(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data(supernatural=0))
        available = get_available_moves(state)
        move_ids = {m.id for m in available}
        assert "spirit_blast" not in move_ids

    def test_get_available_moves_with_mana(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data(supernatural=40))
        state.mana = 50.0
        available = get_available_moves(state)
        move_ids = {m.id for m in available}
        assert "spirit_blast" in move_ids

    def test_low_stamina_filters_expensive_moves(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        state.stamina = 3.0
        available = get_available_moves(state)
        for move in available:
            assert move.stamina_cost <= 3.0 or move.stamina_cost < 0


class TestDamage:
    def test_hit_chance_in_range(self):
        attacker = FighterCombatState.from_fighter_data(_make_fighter_data(technique=80))
        defender = FighterCombatState.from_fighter_data(_make_fighter_data(speed=80))
        jab = UNIVERSAL_MOVES["jab"]
        chance = calculate_hit_chance(jab, attacker, defender)
        assert 0.05 <= chance <= 0.95

    def test_higher_technique_more_accurate(self):
        defender = FighterCombatState.from_fighter_data(_make_fighter_data())
        att_low = FighterCombatState.from_fighter_data(_make_fighter_data(technique=20))
        att_high = FighterCombatState.from_fighter_data(_make_fighter_data(technique=90))
        jab = UNIVERSAL_MOVES["jab"]
        chance_low = calculate_hit_chance(jab, att_low, defender)
        chance_high = calculate_hit_chance(jab, att_high, defender)
        assert chance_high > chance_low

    def test_damage_scales_with_power(self):
        defender = FighterCombatState.from_fighter_data(_make_fighter_data())
        att_low = FighterCombatState.from_fighter_data(_make_fighter_data(power=20))
        att_high = FighterCombatState.from_fighter_data(_make_fighter_data(power=90))
        hook = UNIVERSAL_MOVES["hook"]
        dmg_low = calculate_damage(hook, att_low, defender)
        dmg_high = calculate_damage(hook, att_high, defender)
        assert dmg_high > dmg_low

    def test_toughness_reduces_damage(self):
        attacker = FighterCombatState.from_fighter_data(_make_fighter_data(power=70))
        def_soft = FighterCombatState.from_fighter_data(_make_fighter_data(toughness=20))
        def_tough = FighterCombatState.from_fighter_data(_make_fighter_data(toughness=90))
        hook = UNIVERSAL_MOVES["hook"]
        dmg_soft = calculate_damage(hook, attacker, def_soft)
        dmg_tough = calculate_damage(hook, attacker, def_tough)
        assert dmg_soft > dmg_tough

    def test_resolve_attack_returns_valid_outcome(self):
        rng = random.Random(42)
        attacker = FighterCombatState.from_fighter_data(_make_fighter_data())
        defender = FighterCombatState.from_fighter_data(_make_fighter_data())
        jab = UNIVERSAL_MOVES["jab"]
        outcome, damage = resolve_attack(jab, attacker, defender, None, rng)
        assert outcome in (TickOutcome.HIT, TickOutcome.BLOCKED, TickOutcome.DODGED, TickOutcome.COUNTER)
        assert damage >= 0.0


class TestConditions:
    def test_mana_stays_zero_without_supernatural(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data(supernatural=0))
        update_mana(state)
        assert state.mana == 0.0

    def test_mana_builds_with_supernatural(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data(supernatural=40))
        initial = state.mana
        for _ in range(10):
            update_mana(state)
        assert state.mana > initial

    def test_mana_capped_at_max(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data(supernatural=20))
        for _ in range(200):
            update_mana(state)
        assert state.mana <= state.max_mana

    def test_emotions_on_hit_shifts_confidence(self):
        attacker = FighterCombatState.from_fighter_data(_make_fighter_data())
        defender = FighterCombatState.from_fighter_data(_make_fighter_data())
        att_conf_before = attacker.emotional_state.confidence
        update_emotions_on_hit(attacker, defender, 15.0)
        assert attacker.emotional_state.confidence > att_conf_before

    def test_emotions_on_hit_builds_rage(self):
        attacker = FighterCombatState.from_fighter_data(_make_fighter_data())
        defender = FighterCombatState.from_fighter_data(_make_fighter_data())
        rage_before = defender.emotional_state.rage
        update_emotions_on_hit(attacker, defender, 15.0)
        assert defender.emotional_state.rage > rage_before

    def test_emotional_modifiers_rage(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        state.emotional_state.rage = 80.0
        mods = apply_emotional_modifiers(state)
        assert mods["damage_mult"] > 1.0
        assert mods["accuracy_mult"] < 1.0


class TestWinConditions:
    def test_ko_at_zero_hp(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        state.hp = 0
        assert check_ko(state) is True

    def test_no_ko_with_hp(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        assert check_ko(state) is False

    def test_tko_conditions(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data(toughness=50))
        state.accumulated_damage = 100
        state.hp = state.max_hp * 0.05
        rng = random.Random(31)
        assert check_tko(state, round_number=5, rng=rng) is True

    def test_no_tko_when_healthy(self):
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        assert check_tko(state, round_number=1) is False

    def test_submission_requires_low_stats(self):
        rng = random.Random(42)
        move = UNIVERSAL_MOVES["armbar_attempt"]
        attacker = FighterCombatState.from_fighter_data(_make_fighter_data(technique=80))
        defender = FighterCombatState.from_fighter_data(_make_fighter_data(technique=30))
        defender.hp = defender.max_hp * 0.20
        defender.stamina = defender.max_stamina * 0.10
        assert check_submission(move, attacker, defender, rng) is True

    def test_no_submission_when_healthy(self):
        rng = random.Random(42)
        move = UNIVERSAL_MOVES["armbar_attempt"]
        attacker = FighterCombatState.from_fighter_data(_make_fighter_data())
        defender = FighterCombatState.from_fighter_data(_make_fighter_data())
        assert check_submission(move, attacker, defender, rng) is False


class TestStrategy:
    def test_weighted_strategy_returns_valid_move(self):
        rng = random.Random(42)
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        opponent = FighterCombatState.from_fighter_data(_make_fighter_data())
        available = get_available_moves(state)
        strategy = WeightedStrategy()
        move = strategy.select_move(state, opponent, available, 1, 1, rng)
        assert isinstance(move, MoveDefinition)
        assert move in available

    def test_strategy_prefers_recovery_when_exhausted(self):
        rng = random.Random(42)
        state = FighterCombatState.from_fighter_data(_make_fighter_data())
        state.stamina = 5.0
        opponent = FighterCombatState.from_fighter_data(_make_fighter_data())
        available = get_available_moves(state)
        strategy = WeightedStrategy()

        recover_count = 0
        total = 100
        for i in range(total):
            move = strategy.select_move(state, opponent, available, 1, 1, random.Random(i))
            if move.id == "recover":
                recover_count += 1

        assert recover_count > total * 0.2


class TestSimulator:
    def test_determinism_same_seed(self):
        f1 = _make_fighter_data("f1", "Fighter A", power=70, speed=60, technique=55, toughness=65)
        f2 = _make_fighter_data("f2", "Fighter B", power=55, speed=75, technique=70, toughness=50)

        result1 = simulate_combat(f1, f2, seed=12345)
        result2 = simulate_combat(f1, f2, seed=12345)

        assert result1.winner_id == result2.winner_id
        assert result1.method == result2.method
        assert result1.final_round == result2.final_round
        assert result1.final_tick == result2.final_tick
        assert len(result1.tick_log) == len(result2.tick_log)

    def test_different_seeds_different_results(self):
        f1 = _make_fighter_data("f1", "Fighter A", power=50, speed=50, technique=50, toughness=50)
        f2 = _make_fighter_data("f2", "Fighter B", power=50, speed=50, technique=50, toughness=50)

        results = set()
        for seed in range(20):
            result = simulate_combat(f1, f2, seed=seed)
            results.add(result.winner_id)

        assert len(results) > 1

    def test_fight_always_ends(self):
        f1 = _make_fighter_data("f1", "Fighter A")
        f2 = _make_fighter_data("f2", "Fighter B")

        result = simulate_combat(f1, f2, seed=42)
        assert result.winner_id in ("f1", "f2")
        assert result.method in ("ko", "tko", "submission")
        assert len(result.tick_log) > 0
        assert len(result.round_summaries) > 0

    def test_stronger_fighter_wins_more(self):
        strong = _make_fighter_data("strong", "Strong", power=90, speed=85, technique=80, toughness=85)
        weak = _make_fighter_data("weak", "Weak", power=20, speed=25, technique=20, toughness=20)

        strong_wins = 0
        trials = 50
        for seed in range(trials):
            result = simulate_combat(strong, weak, seed=seed)
            if result.winner_id == "strong":
                strong_wins += 1

        assert strong_wins > trials * 0.7

    def test_convergence_reasonable_rounds(self):
        f1 = _make_fighter_data("f1", "Fighter A", power=50, speed=50, technique=50, toughness=50)
        f2 = _make_fighter_data("f2", "Fighter B", power=50, speed=50, technique=50, toughness=50)

        max_rounds = 0
        for seed in range(20):
            result = simulate_combat(f1, f2, seed=seed)
            max_rounds = max(max_rounds, result.final_round)

        assert max_rounds <= 20

    def test_combat_result_has_round_summaries(self):
        f1 = _make_fighter_data("f1", "Fighter A")
        f2 = _make_fighter_data("f2", "Fighter B")

        result = simulate_combat(f1, f2, seed=42)
        assert len(result.round_summaries) >= 1
        first_round = result.round_summaries[0]
        assert first_round.round_number == 1
        assert first_round.fighter1_id == "f1"

    def test_zero_supernatural_no_mana(self):
        f1 = _make_fighter_data("f1", "Fighter A", supernatural=0)
        f2 = _make_fighter_data("f2", "Fighter B", supernatural=0)

        result = simulate_combat(f1, f2, seed=42)
        assert result.fighter1_final_state.get("mana", 0) == 0.0
        assert result.fighter2_final_state.get("mana", 0) == 0.0

    def test_supernatural_builds_mana(self):
        f1 = _make_fighter_data("f1", "Fighter A", supernatural=40)
        f2 = _make_fighter_data("f2", "Fighter B", supernatural=0)

        result = simulate_combat(f1, f2, seed=42)
        has_mana = False
        for tick in result.tick_log:
            att_state = tick.attacker_state_after if tick.attacker_id == "f1" else tick.defender_state_after
            if att_state.get("mana", 0) > 0:
                has_mana = True
                break
        assert has_mana
