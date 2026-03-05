import random as _random
from abc import ABC, abstractmethod

from app.engine.combat.models import FighterCombatState, Position
from app.engine.combat.moves import MoveDefinition


class FightStrategy(ABC):
    @abstractmethod
    def select_move(
        self,
        own_state: FighterCombatState,
        opponent_state: FighterCombatState,
        available_moves: list[MoveDefinition],
        round_num: int,
        tick_num: int,
        rng: _random.Random,
    ) -> MoveDefinition:
        ...


class WeightedStrategy(FightStrategy):

    def select_move(
        self,
        own_state: FighterCombatState,
        opponent_state: FighterCombatState,
        available_moves: list[MoveDefinition],
        round_num: int,
        tick_num: int,
        rng: _random.Random,
    ) -> MoveDefinition:
        if not available_moves:
            raise ValueError("No available moves")

        scores = []
        for move in available_moves:
            score = self._score_move(move, own_state, opponent_state, round_num, tick_num)
            scores.append(max(0.01, score))

        total = sum(scores)
        normalized = [s / total for s in scores]

        roll = rng.random()
        cumulative = 0.0
        for i, prob in enumerate(normalized):
            cumulative += prob
            if roll <= cumulative:
                return available_moves[i]

        return available_moves[-1]

    def _score_move(
        self,
        move: MoveDefinition,
        own: FighterCombatState,
        opp: FighterCombatState,
        round_num: int,
        tick_num: int,
    ) -> float:
        score = 1.0

        score *= self._stamina_score(move, own)
        score *= self._finishing_score(move, opp)
        score *= self._defensive_score(move, own, opp)
        score *= self._supernatural_score(move, own, opp)
        score *= self._stat_affinity_score(move, own)
        score *= self._positional_score(move, own, opp)
        score *= self._combo_score(move, own)
        score *= self._fatigue_score(move, own, round_num)

        return score

    def _stamina_score(self, move: MoveDefinition, own: FighterCombatState) -> float:
        stamina_pct = own.stamina / own.max_stamina

        if move.id == "recover":
            if stamina_pct < 0.2:
                return 5.0
            elif stamina_pct < 0.4:
                return 2.5
            return 0.3

        if stamina_pct < 0.2:
            cost_ratio = move.stamina_cost / own.max_stamina
            if cost_ratio > 0.15:
                return 0.2
            return 1.5

        if stamina_pct < 0.4 and move.stamina_cost > 15:
            return 0.5

        return 1.0

    def _finishing_score(self, move: MoveDefinition, opp: FighterCombatState) -> float:
        opp_hp_pct = opp.hp / opp.max_hp

        if opp_hp_pct < 0.15 and move.is_finisher:
            return 4.0
        if opp_hp_pct < 0.25 and move.base_damage > 15:
            return 3.0
        if opp_hp_pct < 0.40 and move.base_damage > 10:
            return 1.8

        if opp.stun_ticks > 0:
            if move.base_damage > 15:
                return 3.5
            if move.base_damage > 10:
                return 2.5

        return 1.0

    def _defensive_score(
        self, move: MoveDefinition, own: FighterCombatState, opp: FighterCombatState
    ) -> float:
        own_hp_pct = own.hp / own.max_hp

        if move.category == "defensive" and move.id != "recover":
            if own.combo_counter < 0 or own_hp_pct < 0.3:
                return 2.0
            if opp.combo_counter >= 2:
                return 2.5
            if own.emotional_state.fear > 60:
                return 1.8
            return 0.8

        return 1.0

    def _supernatural_score(
        self, move: MoveDefinition, own: FighterCombatState, opp: FighterCombatState
    ) -> float:
        if move.category != "supernatural":
            return 1.0

        own_hp_pct = own.hp / own.max_hp
        opp_hp_pct = opp.hp / opp.max_hp

        if own_hp_pct < 0.3:
            return 4.0
        if opp_hp_pct < 0.25:
            return 3.5
        if own_hp_pct < 0.5 and opp_hp_pct < 0.5:
            return 2.0

        return 0.3

    def _stat_affinity_score(
        self, move: MoveDefinition, own: FighterCombatState
    ) -> float:
        if move.category == "defensive":
            return 1.0

        if own.power >= 70 and move.base_damage >= 18:
            return 1.5
        if own.power >= 70 and move.base_damage < 8:
            return 0.7

        if own.speed >= 70 and move.speed <= 3:
            return 1.4
        if own.speed >= 70 and move.speed >= 8:
            return 0.7

        if own.technique >= 70 and move.is_submission:
            return 1.6
        if own.technique >= 70 and move.accuracy >= 0.7:
            return 1.3

        if own.guile >= 30:
            if move.stamina_damage > 0:
                return 1.4
            if move.id in ("slip", "clinch_entry"):
                return 1.3
            if move.speed >= 8 and move.base_damage > 20:
                return 0.7

        return 1.0

    def _positional_score(
        self, move: MoveDefinition, own: FighterCombatState, opp: FighterCombatState
    ) -> float:
        if own.position == Position.STANDING:
            if move.id == "clinch_entry":
                if own.technique > own.power and own.technique > opp.technique:
                    return 1.5
                return 0.6

        if own.position == Position.CLINCH:
            if move.id == "throw" and own.technique > opp.technique:
                return 1.8
            if move.id == "clinch_break" and own.power > own.technique:
                return 1.5

        if own.position == Position.GROUND:
            if move.id == "sweep" and own.speed > opp.speed:
                return 2.0
            if move.is_submission:
                opp_hp_pct = opp.hp / opp.max_hp
                opp_stam_pct = opp.stamina / opp.max_stamina
                if opp_hp_pct < 0.35 and opp_stam_pct < 0.3:
                    return 3.0
                return 0.8

        return 1.0

    def _combo_score(self, move: MoveDefinition, own: FighterCombatState) -> float:
        if own.combo_counter >= 2 and move.base_damage > 15:
            return 1.8
        if own.combo_counter >= 3 and move.is_finisher:
            return 2.5
        if own.combo_counter >= 1 and move.speed <= 4:
            return 1.3
        return 1.0

    def _fatigue_score(
        self, move: MoveDefinition, own: FighterCombatState, round_num: int
    ) -> float:
        if round_num > 8:
            fatigue = (round_num - 8) * 0.1
            if move.stamina_cost > 15:
                return max(0.3, 1.0 - fatigue)
            if move.id == "recover":
                return 1.0 + fatigue

        return 1.0
