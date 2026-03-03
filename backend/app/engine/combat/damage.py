import random as _random

from app.engine.combat.models import FighterCombatState, TickOutcome
from app.engine.combat.moves import MoveDefinition
from app.engine.combat.conditions import apply_emotional_modifiers


def calculate_hit_chance(
    move: MoveDefinition,
    attacker: FighterCombatState,
    defender: FighterCombatState,
) -> float:
    att_mods = apply_emotional_modifiers(attacker)

    technique_factor = 0.7 + 0.3 * (attacker.technique / 95.0)
    stamina_factor = 0.8 + 0.2 * (attacker.stamina / attacker.max_stamina)
    combo_accuracy = 1.0 + min(0.1, attacker.combo_counter * 0.02)

    hit_chance = (
        move.accuracy
        * technique_factor
        * stamina_factor
        * att_mods["accuracy_mult"]
        * combo_accuracy
    )

    def_mods = apply_emotional_modifiers(defender)
    evasion = (
        0.05
        + 0.15 * (defender.speed / 95.0)
        * (defender.stamina / defender.max_stamina)
        * def_mods["evasion_mult"]
    )

    if defender.stun_ticks > 0:
        evasion *= 0.3

    return max(0.05, min(0.95, hit_chance - evasion))


def calculate_block_chance(
    move: MoveDefinition,
    defender: FighterCombatState,
) -> float:
    def_mods = apply_emotional_modifiers(defender)
    base_block = 0.3 * (defender.technique / 95.0) * move.block_modifier
    guard_factor = defender.guard / defender.max_guard if defender.max_guard > 0 else 0.5
    return base_block * guard_factor * def_mods["block_mult"]


def calculate_damage(
    move: MoveDefinition,
    attacker: FighterCombatState,
    defender: FighterCombatState,
) -> float:
    if move.base_damage <= 0:
        return 0.0

    att_mods = apply_emotional_modifiers(attacker)

    raw = move.base_damage
    scaling_total = 0.0
    scaling_weight_sum = sum(move.stat_scaling.values()) if move.stat_scaling else 1.0

    for stat_name, weight in move.stat_scaling.items():
        stat_val = getattr(attacker, stat_name, 50)
        scaling_total += (0.5 + 0.5 * stat_val / 95.0) * (weight / max(scaling_weight_sum, 0.01))

    if not move.stat_scaling:
        scaling_total = 1.0

    stamina_factor = 0.7 + 0.3 * (attacker.stamina / attacker.max_stamina)
    combo_bonus = 1.0 + min(0.3, attacker.combo_counter * 0.05)

    raw *= scaling_total * stamina_factor * att_mods["damage_mult"] * combo_bonus * 0.45

    reduction = 0.10 + 0.25 * (defender.toughness / 95.0)
    if defender.guard > 20:
        reduction += 0.05 * (defender.guard / defender.max_guard if defender.max_guard > 0 else 0)

    return max(1.0, raw * (1.0 - reduction))


def calculate_block_damage(full_damage: float) -> float:
    return full_damage * 0.15


def resolve_attack(
    move: MoveDefinition,
    attacker: FighterCombatState,
    defender: FighterCombatState,
    defender_move: MoveDefinition | None,
    rng: _random.Random,
) -> tuple[TickOutcome, float]:
    if move.category == "defensive":
        return TickOutcome.DODGED, 0.0

    if move.base_damage == 0.0 and move.position_change is not None:
        hit_chance = calculate_hit_chance(move, attacker, defender)
        roll = rng.random()
        if roll < hit_chance:
            return TickOutcome.HIT, 0.0
        return TickOutcome.DODGED, 0.0

    is_defending = defender_move and defender_move.id in ("block", "slip")
    is_blocking = defender_move and defender_move.id == "block"
    is_slipping = defender_move and defender_move.id == "slip"

    hit_chance = calculate_hit_chance(move, attacker, defender)
    full_damage = calculate_damage(move, attacker, defender)

    if is_slipping:
        slip_success = 0.3 + 0.4 * (defender.speed / 95.0) * (defender.stamina / defender.max_stamina)
        if rng.random() < slip_success:
            counter_chance = 0.15 + 0.15 * (defender.technique / 95.0)
            if rng.random() < counter_chance:
                return TickOutcome.COUNTER, 0.0
            return TickOutcome.DODGED, 0.0

    if is_blocking:
        block_chance = calculate_block_chance(move, defender)
        roll = rng.random()
        if roll < block_chance + hit_chance * 0.3:
            blocked_damage = calculate_block_damage(full_damage)
            return TickOutcome.BLOCKED, blocked_damage

    roll = rng.random()
    if roll < hit_chance:
        return TickOutcome.HIT, full_damage

    counter_window = 0.05 + 0.10 * (defender.technique / 95.0)
    if not is_defending and rng.random() < counter_window:
        return TickOutcome.COUNTER, 0.0

    return TickOutcome.DODGED, 0.0


def apply_damage(
    defender: FighterCombatState,
    damage: float,
    move: MoveDefinition,
    outcome: TickOutcome,
    rng: _random.Random,
):
    defender.hp -= damage
    defender.accumulated_damage += damage

    guard_drain = damage * 0.5 if outcome == TickOutcome.HIT else damage * 0.8
    defender.guard = max(0.0, defender.guard - guard_drain)

    if move.stamina_damage > 0:
        stamina_hit = move.stamina_damage
        if outcome == TickOutcome.BLOCKED:
            stamina_hit *= 0.5
        defender.stamina = max(0.0, defender.stamina - stamina_hit)

    if outcome == TickOutcome.HIT and move.stun_chance > 0:
        stun_roll = rng.random()
        hp_pct = defender.hp / defender.max_hp
        stun_bonus = 0.1 if hp_pct < 0.3 else 0.0
        if stun_roll < move.stun_chance + stun_bonus:
            defender.stun_ticks = max(defender.stun_ticks, move.stun_duration)


def apply_attacker_costs(
    attacker: FighterCombatState,
    move: MoveDefinition,
    outcome: TickOutcome,
):
    att_mods = apply_emotional_modifiers(attacker)
    stamina_cost = move.stamina_cost * att_mods["stamina_drain_mult"]

    if outcome == TickOutcome.DODGED and move.base_damage > 0:
        stamina_cost *= 1.2

    if move.stamina_cost < 0:
        attacker.stamina = min(attacker.max_stamina, attacker.stamina - move.stamina_cost)
    else:
        attacker.stamina = max(0.0, attacker.stamina - stamina_cost)

    if move.mana_cost > 0:
        attacker.mana = max(0.0, attacker.mana - move.mana_cost)
        attacker.supernatural_debt += move.mana_cost * 0.5
