from app.engine.combat.models import FighterCombatState


def composure_dampening(state: FighterCombatState) -> float:
    return 0.3 + 0.7 * (1.0 - state.emotional_state.composure / 100.0)


def update_emotions_on_hit(
    attacker: FighterCombatState, defender: FighterCombatState, damage: float,
    attacker_guile: int = 0,
):
    dampening_a = composure_dampening(attacker)
    dampening_d = composure_dampening(defender)

    guile_psych = 1.0 + 0.25 * (attacker_guile / 100.0)

    confidence_gain = min(8.0, damage * 0.3) * dampening_a
    attacker.emotional_state.confidence += confidence_gain
    attacker.emotional_state.focus += 2.0 * dampening_a
    attacker.emotional_state.fear = max(0.0, attacker.emotional_state.fear - 3.0)

    rage_gain = min(10.0, damage * 0.4) * dampening_d * guile_psych
    defender.emotional_state.rage += rage_gain

    hp_pct = defender.hp / defender.max_hp
    if hp_pct < 0.4:
        defender.emotional_state.fear += (5.0 + damage * 0.2) * dampening_d * guile_psych
    elif hp_pct < 0.6:
        defender.emotional_state.fear += 2.0 * dampening_d * guile_psych

    if damage > 15.0:
        defender.emotional_state.fear += 3.0 * dampening_d * guile_psych
        defender.emotional_state.confidence -= 4.0 * dampening_d * guile_psych
        defender.emotional_state.focus -= 3.0 * dampening_d * guile_psych

    defender.emotional_state.confidence -= min(5.0, damage * 0.2) * dampening_d * guile_psych

    attacker.emotional_state.clamp()
    defender.emotional_state.clamp()


def update_emotions_on_miss(attacker: FighterCombatState):
    dampening = composure_dampening(attacker)
    attacker.emotional_state.confidence -= 3.0 * dampening
    attacker.emotional_state.focus -= 2.0 * dampening
    attacker.emotional_state.clamp()


def update_emotions_on_block(
    attacker: FighterCombatState, defender: FighterCombatState
):
    dampening_a = composure_dampening(attacker)
    dampening_d = composure_dampening(defender)
    attacker.emotional_state.confidence -= 1.0 * dampening_a
    defender.emotional_state.confidence += 2.0 * dampening_d
    defender.emotional_state.focus += 1.0 * dampening_d
    attacker.emotional_state.clamp()
    defender.emotional_state.clamp()


def update_emotions_on_counter(
    attacker: FighterCombatState, defender: FighterCombatState,
    counter_guile: int = 0,
):
    dampening_a = composure_dampening(attacker)
    dampening_d = composure_dampening(defender)
    guile_psych = 1.0 + 0.25 * (counter_guile / 100.0)
    attacker.emotional_state.confidence -= 5.0 * dampening_a * guile_psych
    attacker.emotional_state.fear += 3.0 * dampening_a * guile_psych
    defender.emotional_state.confidence += 6.0 * dampening_d
    defender.emotional_state.focus += 3.0 * dampening_d
    attacker.emotional_state.clamp()
    defender.emotional_state.clamp()


def update_emotions_tick_decay(state: FighterCombatState):
    emo = state.emotional_state
    emo.rage = max(0.0, emo.rage - 1.5)
    emo.fear = max(0.0, emo.fear - 1.0)

    if emo.confidence > 50.0:
        emo.confidence -= 0.5
    elif emo.confidence < 50.0:
        emo.confidence += 0.5

    base_focus = min(100.0, state.technique * 0.8)
    if emo.focus > base_focus:
        emo.focus -= 0.5
    elif emo.focus < base_focus:
        emo.focus += 0.5

    emo.clamp()


def update_mana(state: FighterCombatState):
    if state.max_mana <= 0:
        return

    gain = 1.0

    hp_pct = state.hp / state.max_hp
    if hp_pct < 0.3:
        gain += 4.0
    elif hp_pct < 0.5:
        gain += 3.0

    if state.emotional_state.rage > 50:
        gain += 2.0
    if state.emotional_state.fear > 60:
        gain += 2.0

    gain *= (0.5 + 0.5 * state.supernatural / 100.0)

    state.mana = min(state.max_mana, state.mana + gain)


def apply_emotional_modifiers(state: FighterCombatState) -> dict:
    mods = {
        "damage_mult": 1.0,
        "accuracy_mult": 1.0,
        "evasion_mult": 1.0,
        "block_mult": 1.0,
        "stamina_drain_mult": 1.0,
    }

    emo = state.emotional_state

    if emo.rage > 50:
        rage_factor = (emo.rage - 50) / 50.0
        mods["damage_mult"] += 0.15 * rage_factor
        mods["accuracy_mult"] -= 0.15 * rage_factor
        mods["block_mult"] -= 0.10 * rage_factor

    if emo.fear > 50:
        fear_factor = (emo.fear - 50) / 50.0
        mods["damage_mult"] -= 0.15 * fear_factor
        mods["evasion_mult"] += 0.15 * fear_factor
        mods["stamina_drain_mult"] += 0.20 * fear_factor

    if emo.confidence > 60:
        conf_factor = (emo.confidence - 60) / 40.0
        mods["accuracy_mult"] += 0.10 * conf_factor
        mods["damage_mult"] += 0.10 * conf_factor

    if emo.focus > 60:
        focus_factor = (emo.focus - 60) / 40.0
        mods["accuracy_mult"] += 0.15 * focus_factor
        mods["block_mult"] += 0.10 * focus_factor

    return mods


def update_emotions_between_rounds(state: FighterCombatState):
    emo = state.emotional_state
    emo.rage = max(0.0, emo.rage - 10.0)
    emo.fear = max(0.0, emo.fear - 10.0)

    if emo.confidence > 50.0:
        emo.confidence = max(50.0, emo.confidence - 5.0)
    elif emo.confidence < 50.0:
        emo.confidence = min(50.0, emo.confidence + 5.0)

    base_focus = min(100.0, state.technique * 0.8)
    diff = base_focus - emo.focus
    emo.focus += diff * 0.3

    emo.clamp()
