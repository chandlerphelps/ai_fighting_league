import argparse
import random
import hashlib
import sys
from collections import defaultdict

from app.engine.combat.simulator import simulate_combat
from app.engine.between_fights.training import process_daily_training, apply_fight_camp_boost
from app.engine.between_fights.retirement import generate_replacement_fighter, CORE_STATS, STAT_MIN, STAT_CAP
from app.engine.between_fights.league_tiers import (
    calculate_tier_rankings,
    get_promotion_matchups,
    apply_promotion_results,
    apply_title_fight_result,
)
from app.engine.between_fights.season import (
    process_end_of_season,
    get_tier_event_config,
    TIER_SIZES,
)


EVENT_DAYS = {
    "championship": [3, 6],
    "contender": [2, 4, 7],
    "underground": [1, 2, 3, 4, 5, 6, 7],
}

INJURY_TYPES_WINNER = ["minor bruising", "hand strain", "mild concussion"]
INJURY_TYPES_LOSER_KO = ["concussion", "orbital fracture", "broken nose"]
INJURY_TYPES_LOSER_OTHER = ["laceration", "bruised ribs", "hand fracture", "broken nose"]

MINOR_RECOVERY = (2, 4)
MODERATE_RECOVERY = (5, 10)
SEVERE_RECOVERY = (14, 21)

SEASON_ENDING_INJURY_TYPES = ["torn ACL", "fractured vertebra", "severe concussion syndrome", "shattered orbital"]
CAREER_ENDING_INJURY_TYPES = ["spinal injury", "traumatic brain injury", "shattered knee"]
SEASON_ENDING_RECOVERY = (90, 120)


class LeagueSimulator:
    def __init__(self, seed=42, verbose=False):
        self.rng = random.Random(seed)
        self.seed = seed
        self.verbose = verbose
        self.fighters = {}
        self.season_matches = []
        self.all_retired = []
        self.season_logs = []
        self.fighter_counter = 0
        self.world_state = {
            "season_number": 1,
            "season_month": 1,
            "season_day_in_month": 1,
            "tier_rankings": {"championship": [], "contender": [], "underground": []},
            "belt_holder_id": "",
            "belt_history": [],
            "retired_fighter_ids": [],
            "active_injuries": {},
            "season_champions": [],
        }
        self.total_fights_run = 0
        self.mid_season_retirements = []
        self.season_ending_injuries = []
        self.total_career_ending = 0
        self.total_season_ending = 0
        self.used_names = set()

    def generate_initial_roster(self):
        for i in range(TIER_SIZES["championship"]):
            self.fighter_counter += 1
            f = self._make_fighter(
                self.fighter_counter,
                tier="championship",
                age_range=(27, 32),
                stat_range=(260, 320),
                career_seasons_range=(5, 10),
                tier_seasons_range=(1, 4),
            )
            self.fighters[f["id"]] = f

        for i in range(TIER_SIZES["contender"]):
            self.fighter_counter += 1
            f = self._make_fighter(
                self.fighter_counter,
                tier="contender",
                age_range=(23, 28),
                stat_range=(210, 270),
                career_seasons_range=(2, 6),
                tier_seasons_range=(1, 3),
            )
            self.fighters[f["id"]] = f

        for i in range(TIER_SIZES["underground"]):
            self.fighter_counter += 1
            f = self._make_fighter(
                self.fighter_counter,
                tier="underground",
                age_range=(18, 26),
                stat_range=(150, 220),
                career_seasons_range=(0, 4),
                tier_seasons_range=(0, 2),
            )
            self.fighters[f["id"]] = f

        champ_fighters = [f for f in self.fighters.values() if f["tier"] == "championship"]
        if champ_fighters:
            belt_holder = max(champ_fighters, key=lambda f: sum(f["stats"].get(s, 0) for s in CORE_STATS))
            self.world_state["belt_holder_id"] = belt_holder["id"]
            self.world_state["belt_history"].append({
                "fighter_id": belt_holder["id"],
                "won_date": "season_0",
                "lost_date": None,
                "defenses": self.rng.randint(1, 3),
            })

        self._recalculate_all_rankings()

    def _make_fighter(self, counter, tier, age_range, stat_range, career_seasons_range, tier_seasons_range):
        age = self.rng.randint(*age_range)
        target_total = self.rng.randint(*stat_range)
        stats = self._distribute_stats(target_total)
        career_seasons = self.rng.randint(*career_seasons_range)
        tier_seasons = self.rng.randint(*tier_seasons_range)

        total_fights = career_seasons * self.rng.randint(6, 12)
        if tier == "championship":
            win_rate = self.rng.uniform(0.55, 0.75)
        elif tier == "contender":
            win_rate = self.rng.uniform(0.45, 0.65)
        else:
            win_rate = self.rng.uniform(0.35, 0.60)

        wins = max(0, round(total_fights * win_rate))
        losses = max(0, total_fights - wins)

        from app.engine.between_fights.retirement import RING_NAMES, PREFIXES
        for _ in range(100):
            prefix = self.rng.choice(PREFIXES) if self.rng.random() < 0.4 else ""
            name = self.rng.choice(RING_NAMES)
            ring_name = f"{prefix} {name}".strip() if prefix else name
            if ring_name not in self.used_names:
                break
        self.used_names.add(ring_name)

        peak_tier = tier
        if tier == "championship":
            peak_tier = "championship"
        elif tier == "contender":
            peak_tier = "contender" if self.rng.random() < 0.7 else "championship"

        fighter_id = f"sim-{counter:04d}"

        return {
            "id": fighter_id,
            "ring_name": ring_name,
            "real_name": ring_name,
            "age": age,
            "gender": self.rng.choice(["female", "male"]),
            "primary_archetype": "",
            "stats": stats,
            "record": {"wins": wins, "losses": losses, "draws": 0, "kos": self.rng.randint(0, wins // 2 + 1), "submissions": self.rng.randint(0, wins // 3 + 1)},
            "condition": {"health_status": "healthy", "injuries": [], "recovery_days_remaining": 0, "morale": "neutral", "momentum": "neutral"},
            "tier": tier,
            "status": "active",
            "training_focus": self.rng.choice(CORE_STATS),
            "training_days_accumulated": 0.0,
            "training_streak": 0,
            "seasons_in_current_tier": tier_seasons,
            "career_season_count": career_seasons,
            "peak_tier": peak_tier,
            "promotion_desperation": 0.0,
            "season_wins": 0,
            "season_losses": 0,
            "consecutive_losses": 0,
            "last_fight_date": None,
            "rivalries": [],
            "storyline_log": [],
            "moves": [],
            "_entered_season": 0,
            "_entered_age": age - career_seasons,
        }

    def _distribute_stats(self, target_total):
        raw = [self.rng.randint(25, 70) for _ in CORE_STATS]
        raw_total = sum(raw)
        scaled = [max(STAT_MIN, min(STAT_CAP, round(v * target_total / raw_total))) for v in raw]
        diff = target_total - sum(scaled)
        while diff != 0:
            idx = self.rng.randint(0, len(CORE_STATS) - 1)
            if diff > 0 and scaled[idx] < STAT_CAP:
                scaled[idx] += 1
                diff -= 1
            elif diff < 0 and scaled[idx] > STAT_MIN:
                scaled[idx] -= 1
                diff += 1
        stats = {}
        for i, s in enumerate(CORE_STATS):
            stats[s] = scaled[i]
        stats["supernatural"] = 0
        return stats

    def simulate_season(self):
        season_num = self.world_state["season_number"]
        self.season_matches = []
        self.mid_season_retirements = []
        self.season_ending_injuries = []

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"  SEASON {season_num}")
            print(f"{'='*60}")
            self._print_tier_rosters()

        for month in range(1, 9):
            self.world_state["season_month"] = month

            if month <= 6:
                self._simulate_regular_month(month)
            elif month == 7:
                self._simulate_regular_month(month)
                self._prepare_promotion_month()
            elif month == 8:
                self._simulate_promotion_month()

        season_summary = process_end_of_season(
            self.fighters,
            self.world_state,
            self.fighter_counter,
            self.rng,
            self.used_names,
        )
        self.fighter_counter = max(
            self.fighter_counter,
            max((int(fid.split("-")[1]) for fid in self.fighters if fid.startswith("sim-")), default=0),
        )

        for ret in self.mid_season_retirements:
            fid = ret["fighter_id"]
            fighter = self.fighters.get(fid, {})
            ret["_fighter_snapshot"] = dict(fighter)
            self.all_retired.append(ret)

        for ret in season_summary.get("retirements", []):
            fid = ret["fighter_id"]
            fighter = self.fighters.get(fid, {})
            ret["_fighter_snapshot"] = dict(fighter)
            self.all_retired.append(ret)

        self.total_career_ending += len(self.mid_season_retirements)
        self.total_season_ending += len(self.season_ending_injuries)

        self._recalculate_all_rankings()
        self.season_logs.append(season_summary)

        if self.verbose:
            self._print_season_summary(season_summary)

        return season_summary

    def _simulate_regular_month(self, month):
        for day in range(1, 8):
            self.world_state["season_day_in_month"] = day
            self._process_daily_recovery()
            self._process_daily_training_all()

            for tier in ["championship", "contender", "underground"]:
                if day in EVENT_DAYS[tier]:
                    self._run_tier_event(tier)

    def _process_daily_recovery(self):
        for fid, fighter in self.fighters.items():
            if fighter.get("status") != "active":
                continue
            condition = fighter.get("condition", {})
            if condition.get("health_status") == "injured":
                remaining = condition.get("recovery_days_remaining", 0) - 1
                if remaining <= 0:
                    fighter["condition"] = {
                        "health_status": "healthy",
                        "injuries": [],
                        "recovery_days_remaining": 0,
                        "morale": condition.get("morale", "neutral"),
                        "momentum": condition.get("momentum", "neutral"),
                    }
                else:
                    condition["recovery_days_remaining"] = remaining
                    for inj in condition.get("injuries", []):
                        inj["recovery_days_remaining"] = max(0, inj.get("recovery_days_remaining", 0) - 1)

    def _process_daily_training_all(self):
        for fid, fighter in self.fighters.items():
            if fighter.get("status") != "active":
                continue
            process_daily_training(fighter, self.rng)

    def _run_tier_event(self, tier):
        config = get_tier_event_config(tier)
        num_fights = self.rng.randint(config["fights_min"], config["fights_max"])

        available = [
            f for f in self.fighters.values()
            if f.get("tier") == tier
            and f.get("status") == "active"
            and f.get("condition", {}).get("health_status") == "healthy"
        ]

        if len(available) < 2:
            return

        self.rng.shuffle(available)
        fights_scheduled = []
        used = set()

        for i in range(len(available)):
            if len(fights_scheduled) >= num_fights:
                break
            for j in range(i + 1, len(available)):
                if available[i]["id"] in used or available[j]["id"] in used:
                    continue
                fights_scheduled.append((available[i]["id"], available[j]["id"]))
                used.add(available[i]["id"])
                used.add(available[j]["id"])
                break

        for f1_id, f2_id in fights_scheduled:
            self._run_single_fight(f1_id, f2_id)

    def _run_single_fight(self, f1_id, f2_id):
        f1 = self.fighters[f1_id]
        f2 = self.fighters[f2_id]

        f1_boosted_stats = apply_fight_camp_boost(f1)
        f2_boosted_stats = apply_fight_camp_boost(f2)

        f1_data = dict(f1)
        f1_data["stats"] = f1_boosted_stats
        f2_data = dict(f2)
        f2_data["stats"] = f2_boosted_stats

        season = self.world_state["season_number"]
        month = self.world_state["season_month"]
        seed_str = f"{f1_id}:{f2_id}:{season}:{month}:{self.total_fights_run}"
        seed = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)

        result = simulate_combat(f1_data, f2_data, seed=seed)
        self.total_fights_run += 1

        winner_id = result.winner_id
        loser_id = result.loser_id
        method = result.method
        final_round = result.final_round

        winner = self.fighters[winner_id]
        loser = self.fighters[loser_id]

        w_record = winner.get("record", {})
        w_record["wins"] = w_record.get("wins", 0) + 1
        if method in ("ko", "tko"):
            w_record["kos"] = w_record.get("kos", 0) + 1
        elif method == "submission":
            w_record["submissions"] = w_record.get("submissions", 0) + 1
        winner["record"] = w_record
        winner["season_wins"] = winner.get("season_wins", 0) + 1
        winner["consecutive_losses"] = 0
        winner["training_streak"] = 0

        l_record = loser.get("record", {})
        l_record["losses"] = l_record.get("losses", 0) + 1
        loser["record"] = l_record
        loser["season_losses"] = loser.get("season_losses", 0) + 1
        loser["consecutive_losses"] = loser.get("consecutive_losses", 0) + 1
        loser["training_streak"] = 0

        if loser["consecutive_losses"] >= 5:
            loser.setdefault("condition", {})["morale"] = "low"
        if winner.get("condition", {}).get("morale") == "low":
            winner["condition"]["morale"] = "neutral"

        self._apply_injury(winner, is_winner=True, method=method)
        self._apply_injury(loser, is_winner=False, method=method)

        if loser.get("status") == "retired":
            self.world_state.setdefault("retired_fighter_ids", []).append(loser_id)
            self.mid_season_retirements.append({
                "fighter_id": loser_id,
                "ring_name": loser.get("ring_name", ""),
                "reason": "career_ending_injury",
                "age": loser.get("age", 0),
                "tier": loser.get("tier", ""),
                "career_seasons": loser.get("career_season_count", 0),
                "peak_tier": loser.get("peak_tier", "underground"),
                "record": dict(loser.get("record", {})),
            })

        match_record = {
            "fighter1_id": f1_id,
            "fighter2_id": f2_id,
            "outcome": {
                "winner_id": winner_id,
                "loser_id": loser_id,
                "method": method,
                "round_ended": final_round,
            },
            "date": f"s{season}m{month}",
        }
        self.season_matches.append(match_record)

        return match_record

    def _apply_injury(self, fighter, is_winner, method):
        base_chance = 0.05 if is_winner else 0.20
        if method in ("ko", "tko") and not is_winner:
            base_chance += 0.10

        if self.rng.random() >= base_chance:
            return

        if is_winner:
            injury_type = self.rng.choice(INJURY_TYPES_WINNER)
            severity = "minor"
            recovery = self.rng.randint(*MINOR_RECOVERY)
        else:
            if method in ("ko", "tko"):
                injury_type = self.rng.choice(INJURY_TYPES_LOSER_KO)
                if injury_type == "concussion":
                    severity = self.rng.choice(["moderate", "severe"])
                    recovery = self.rng.randint(*MODERATE_RECOVERY) if severity == "moderate" else self.rng.randint(*SEVERE_RECOVERY)
                else:
                    severity = "moderate"
                    recovery = self.rng.randint(*MODERATE_RECOVERY)
            else:
                injury_type = self.rng.choice(INJURY_TYPES_LOSER_OTHER)
                severity = self.rng.choice(["minor", "moderate"])
                recovery = self.rng.randint(*MINOR_RECOVERY) if severity == "minor" else self.rng.randint(*MODERATE_RECOVERY)

        fighter["condition"] = {
            "health_status": "injured",
            "injuries": [{"type": injury_type, "severity": severity, "recovery_days_remaining": recovery}],
            "recovery_days_remaining": recovery,
            "morale": fighter.get("condition", {}).get("morale", "neutral"),
            "momentum": fighter.get("condition", {}).get("momentum", "neutral"),
        }

        if is_winner:
            return

        age = fighter.get("age", 25)
        ko_multiplier = 2.0 if method in ("ko", "tko") else 1.0

        career_end_chance = max(0, 0.005 + 0.005 * (age - 30)) * ko_multiplier
        if self.rng.random() < career_end_chance:
            injury_type = self.rng.choice(CAREER_ENDING_INJURY_TYPES)
            fighter["condition"] = {
                "health_status": "injured",
                "injuries": [{"type": injury_type, "severity": "career_ending", "recovery_days_remaining": 999}],
                "recovery_days_remaining": 999,
                "morale": fighter.get("condition", {}).get("morale", "neutral"),
                "momentum": fighter.get("condition", {}).get("momentum", "neutral"),
            }
            fighter["status"] = "retired"
            fighter["_retirement_reason"] = "career_ending_injury"
            return

        season_end_chance = max(0, 0.02 + 0.005 * (age - 28)) * ko_multiplier
        if self.rng.random() < season_end_chance:
            injury_type = self.rng.choice(SEASON_ENDING_INJURY_TYPES)
            month = self.world_state.get("season_month", 1)
            remaining_days = max(1, (8 - month) * 7)
            recovery = max(self.rng.randint(*SEASON_ENDING_RECOVERY), remaining_days)
            fighter["condition"] = {
                "health_status": "injured",
                "injuries": [{"type": injury_type, "severity": "season_ending", "recovery_days_remaining": recovery}],
                "recovery_days_remaining": recovery,
                "morale": fighter.get("condition", {}).get("morale", "neutral"),
                "momentum": fighter.get("condition", {}).get("momentum", "neutral"),
            }
            fighter["_season_record_at_injury"] = {
                "season_wins": fighter.get("season_wins", 0),
                "season_losses": fighter.get("season_losses", 0),
            }
            self.season_ending_injuries.append({
                "fighter_id": fighter["id"],
                "ring_name": fighter.get("ring_name", ""),
                "injury_type": injury_type,
                "month": month,
            })

    def _prepare_promotion_month(self):
        self._recalculate_all_rankings()
        tier_rankings = self.world_state["tier_rankings"]

        protected_fighter_ids = set()
        belt_holder = self.world_state.get("belt_holder_id", "")
        if belt_holder:
            protected_fighter_ids.add(belt_holder)

        for fid, fighter in self.fighters.items():
            if fighter.get("status") != "active":
                continue
            condition = fighter.get("condition", {})
            injuries = condition.get("injuries", [])
            has_season_ending = any(i.get("severity") == "season_ending" for i in injuries)
            if has_season_ending:
                snap = fighter.get("_season_record_at_injury", {})
                sw = snap.get("season_wins", 0)
                sl = snap.get("season_losses", 0)
                if sw > sl or sw >= 3:
                    protected_fighter_ids.add(fid)

        matchups = get_promotion_matchups(
            tier_rankings,
            champ_contender_slots=4,
            contender_underground_slots=6,
            protected_fighter_ids=protected_fighter_ids,
        )
        self.world_state["promotion_fights"] = matchups

        champ_rankings = tier_rankings.get("championship", [])
        belt_holder = self.world_state.get("belt_holder_id", "")

        if belt_holder and belt_holder in [f["id"] for f in self.fighters.values() if f.get("status") == "active" and f.get("tier") == "championship"]:
            challengers = [fid for fid in champ_rankings if fid != belt_holder]
            if challengers:
                self.world_state["title_fight"] = {
                    "champion_id": belt_holder,
                    "challenger_id": challengers[0],
                }
        elif champ_rankings and len(champ_rankings) >= 2:
            self.world_state["title_fight"] = {
                "champion_id": champ_rankings[0],
                "challenger_id": champ_rankings[1],
            }

        if self.verbose:
            print(f"\n  --- Month 7: Promotion/Relegation Announced ---")
            for m in matchups:
                upper = self.fighters.get(m["upper_fighter_id"], {}).get("ring_name", "?")
                lower = self.fighters.get(m["lower_fighter_id"], {}).get("ring_name", "?")
                print(f"    {m['tier_boundary']}: {upper} vs {lower}")
            tf = self.world_state.get("title_fight", {})
            if tf:
                champ = self.fighters.get(tf.get("champion_id", ""), {}).get("ring_name", "?")
                challenger = self.fighters.get(tf.get("challenger_id", ""), {}).get("ring_name", "?")
                print(f"    TITLE FIGHT: {champ} (C) vs {challenger}")

    def _simulate_promotion_month(self):
        for day in range(1, 8):
            self.world_state["season_day_in_month"] = day
            self._process_daily_recovery()
            self._process_daily_training_all()

        promotion_results = []
        for matchup in self.world_state.get("promotion_fights", []):
            upper_id = matchup["upper_fighter_id"]
            lower_id = matchup["lower_fighter_id"]

            upper = self.fighters.get(upper_id)
            lower = self.fighters.get(lower_id)
            if not upper or not lower:
                continue
            if upper.get("status") != "active" or lower.get("status") != "active":
                continue

            match = self._run_single_fight(upper_id, lower_id)
            winner_id = match["outcome"]["winner_id"]
            loser_id = match["outcome"]["loser_id"]

            promotion_results.append({
                "upper_fighter_id": upper_id,
                "lower_fighter_id": lower_id,
                "winner_id": winner_id,
                "loser_id": loser_id,
                "tier_boundary": matchup["tier_boundary"],
            })

        changes = apply_promotion_results(self.fighters, promotion_results)

        if self.verbose:
            print(f"\n  --- Month 8: Promotion/Relegation Results ---")
            for change in changes:
                fname = self.fighters.get(change["fighter_id"], {}).get("ring_name", "?")
                print(f"    {fname}: {change['action']} -> {change['tier']}")

        title_fight = self.world_state.get("title_fight", {})
        champ_id = title_fight.get("champion_id", "")
        challenger_id = title_fight.get("challenger_id", "")

        eligible_champs = [
            fid for fid, f in self.fighters.items()
            if f.get("status") == "active" and f.get("tier") == "championship"
        ]

        def _is_eligible(fid):
            f = self.fighters.get(fid)
            return f and f.get("status") == "active" and f.get("tier") == "championship"

        if not _is_eligible(champ_id):
            champ_id = ""
        if not _is_eligible(challenger_id) or challenger_id == champ_id:
            challenger_id = ""

        if not champ_id and eligible_champs:
            champ_id = eligible_champs[0]
        if not challenger_id:
            fallbacks = [fid for fid in eligible_champs if fid != champ_id]
            if fallbacks:
                challenger_id = fallbacks[0]

        if champ_id and challenger_id:
            match = self._run_single_fight(champ_id, challenger_id)
            winner_id = match["outcome"]["winner_id"]
            loser_id = match["outcome"]["loser_id"]
            season = self.world_state["season_number"]
            apply_title_fight_result(self.world_state, winner_id, loser_id, season)

            season_champion = {
                "season": season,
                "fighter_id": winner_id,
                "ring_name": self.fighters[winner_id]["ring_name"],
                "defeated_id": loser_id,
                "defeated_name": self.fighters[loser_id]["ring_name"],
            }
            self.world_state.setdefault("season_champions", []).append(season_champion)

            if self.verbose:
                winner_name = self.fighters[winner_id]["ring_name"]
                print(f"    TITLE FIGHT: {winner_name} wins the belt!")

        self.world_state["promotion_fights"] = []
        self.world_state["title_fight"] = {}

    def _recalculate_all_rankings(self):
        active_fighters = [f for f in self.fighters.values() if f.get("status") == "active"]
        for tier in ["championship", "contender", "underground"]:
            self.world_state["tier_rankings"][tier] = calculate_tier_rankings(
                active_fighters, tier, self.season_matches
            )

    def _print_tier_rosters(self):
        for tier in ["championship", "contender", "underground"]:
            fighters_in_tier = [f for f in self.fighters.values() if f.get("tier") == tier and f.get("status") == "active"]
            fighters_in_tier.sort(key=lambda f: sum(f["stats"].get(s, 0) for s in CORE_STATS), reverse=True)
            print(f"\n  {tier.upper()} ({len(fighters_in_tier)} fighters):")
            for f in fighters_in_tier:
                core = sum(f["stats"].get(s, 0) for s in CORE_STATS)
                rec = f.get("record", {})
                print(f"    {f['ring_name']:20s} age:{f['age']:2d}  stats:{core:3d}  "
                      f"W:{rec.get('wins',0):2d}-L:{rec.get('losses',0):2d}  "
                      f"seasons:{f.get('career_season_count',0)}")

    def _print_season_summary(self, summary):
        print(f"\n  --- End of Season {summary['season']} ---")

        if self.mid_season_retirements:
            print(f"  Mid-Season Career-Ending Injuries: {len(self.mid_season_retirements)}")
            for ret in self.mid_season_retirements:
                print(f"    {ret['ring_name']:20s} age:{ret['age']:2d}  tier:{ret['tier']}")

        if self.season_ending_injuries:
            print(f"  Season-Ending Injuries: {len(self.season_ending_injuries)}")
            for sei in self.season_ending_injuries:
                print(f"    {sei['ring_name']:20s} {sei['injury_type']} (month {sei['month']})")

        if summary.get("retirements"):
            print(f"  Retirements:")
            for ret in summary["retirements"]:
                rec = ret.get("record", {})
                print(f"    {ret['ring_name']:20s} age:{ret['age']:2d}  tier:{ret['tier']:12s}  "
                      f"reason:{ret['reason']:25s}  peak:{ret['peak_tier']}  "
                      f"W:{rec.get('wins',0)}-L:{rec.get('losses',0)}  "
                      f"career:{ret['career_seasons']} seasons")

        if summary.get("backfill_promotions"):
            print(f"  Backfill Promotions:")
            for bp in summary["backfill_promotions"]:
                print(f"    {bp['ring_name']:20s} {bp['from_tier']} -> {bp['to_tier']}")

        if summary.get("new_fighters"):
            print(f"  New Fighters:")
            for nf in summary["new_fighters"]:
                print(f"    {nf['ring_name']:20s} age:{nf['age']}")

        champions = self.world_state.get("season_champions", [])
        season_num = self.world_state["season_number"] - 1
        season_champ = next((c for c in champions if c["season"] == season_num), None)
        if season_champ:
            print(f"  Season Champion: {season_champ['ring_name']} (defeated {season_champ['defeated_name']})")
        else:
            print(f"  Season Champion: None (no title fight held)")

    def print_final_summary(self, num_seasons):
        print(f"\n{'='*70}")
        print(f"  LEAGUE SIMULATION SUMMARY — {num_seasons} SEASONS")
        print(f"{'='*70}")

        print(f"\n  Total fights simulated: {self.total_fights_run}")
        print(f"  Total retirements: {len(self.all_retired)}")
        print(f"  Total career-ending injuries: {self.total_career_ending}")
        print(f"  Total season-ending injuries: {self.total_season_ending}")
        print(f"  Fighters still active: {sum(1 for f in self.fighters.values() if f.get('status') == 'active')}")

        if self.all_retired:
            ages = [r["age"] for r in self.all_retired]
            avg_age = sum(ages) / len(ages)
            career_lengths = [r.get("career_seasons", 0) for r in self.all_retired]
            avg_career = sum(career_lengths) / len(career_lengths)
            print(f"\n  CAREER ARC STATS:")
            print(f"    Average retirement age:    {avg_age:.1f}")
            print(f"    Average career length:     {avg_career:.1f} seasons")
            print(f"    Youngest retirement:       {min(ages)}")
            print(f"    Oldest retirement:         {max(ages)}")

            print(f"\n    Retirement age distribution:")
            age_buckets = defaultdict(int)
            for a in ages:
                bucket = f"{(a // 5) * 5}-{(a // 5) * 5 + 4}"
                age_buckets[bucket] += 1
            for bucket in sorted(age_buckets.keys()):
                count = age_buckets[bucket]
                bar = "#" * count
                print(f"      {bucket:>7s}: {bar} ({count})")

            reasons = defaultdict(int)
            for r in self.all_retired:
                reasons[r.get("reason", "unknown")] += 1
            print(f"\n    Retirement reasons:")
            for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
                pct = count / len(self.all_retired) * 100
                print(f"      {reason:30s}: {count:3d} ({pct:.0f}%)")

        reached_championship = sum(1 for r in self.all_retired if r.get("peak_tier") == "championship")
        reached_contender = sum(1 for r in self.all_retired if r.get("peak_tier") in ("championship", "contender"))
        total_ret = max(1, len(self.all_retired))
        print(f"\n  TIER MOBILITY:")
        print(f"    Reached Championship:      {reached_championship}/{total_ret} ({reached_championship/total_ret*100:.0f}%)")
        print(f"    Reached Contender+:        {reached_contender}/{total_ret} ({reached_contender/total_ret*100:.0f}%)")
        print(f"    Never left Underground:    {total_ret - reached_contender}/{total_ret} ({(total_ret - reached_contender)/total_ret*100:.0f}%)")

        champ_careers = [r.get("career_seasons", 0) for r in self.all_retired if r.get("peak_tier") == "championship"]
        if champ_careers:
            print(f"    Avg career of champ-tier:  {sum(champ_careers)/len(champ_careers):.1f} seasons")

        ug_stuck = [r for r in self.all_retired if r.get("peak_tier") == "underground"]
        if ug_stuck:
            avg_ug_career = sum(r.get("career_seasons", 0) for r in ug_stuck) / len(ug_stuck)
            print(f"    Avg career stuck in UG:    {avg_ug_career:.1f} seasons")

        season_champions = self.world_state.get("season_champions", [])
        if season_champions:
            print(f"\n  SEASON CHAMPIONS:")
            for sc in season_champions:
                print(f"    Season {sc['season']:3d}: {sc['ring_name']:20s} (defeated {sc['defeated_name']})")

        belt_history = self.world_state.get("belt_history", [])
        if belt_history:
            print(f"\n  BELT HISTORY:")
            print(f"    Total title reigns: {len(belt_history)}")
            defenses = [e.get("defenses", 0) for e in belt_history]
            print(f"    Average defenses:   {sum(defenses)/len(defenses):.1f}")
            print(f"    Max defenses:       {max(defenses)}")

            print(f"\n    Champions:")
            for entry in belt_history:
                fid = entry["fighter_id"]
                fighter = self.fighters.get(fid, {})
                name = fighter.get("ring_name", fid)
                won = entry.get("won_date", "?")
                lost = entry.get("lost_date", "still champion") or "still champion"
                defs = entry.get("defenses", 0)
                print(f"      {name:20s}  won:{won:15s}  lost:{lost:20s}  defenses:{defs}")

        print(f"\n  FIGHTER ARCHETYPE ANALYSIS:")
        gatekeepers = [r for r in self.all_retired if r.get("peak_tier") == "underground" and r.get("career_seasons", 0) >= 3]
        print(f"    Gatekeepers (UG 3+ seasons):   {len(gatekeepers)}")

        iron_men = [r for r in self.all_retired if r.get("career_seasons", 0) >= 5]
        print(f"    Iron Men (5+ season careers):   {len(iron_men)}")

        late_bloomers = []
        for r in self.all_retired:
            snap = r.get("_fighter_snapshot", {})
            entered_age = snap.get("_entered_age", 18)
            if r.get("peak_tier") in ("championship", "contender") and entered_age >= 28:
                pass
            career_s = r.get("career_seasons", 0)
            if r.get("peak_tier") in ("championship", "contender") and career_s >= 5:
                late_bloomers.append(r)
        print(f"    Long-road veterans (5+ to top): {len(late_bloomers)}")

        graceful = [r for r in self.all_retired if r.get("reason") == "graceful_exit"]
        print(f"    Graceful exits (champ retire):  {len(graceful)}")

        morale_breaks = [r for r in self.all_retired if r.get("reason") == "morale_collapse"]
        print(f"    Morale collapses:              {len(morale_breaks)}")

        print(f"\n  CURRENT ROSTER:")
        self._print_tier_rosters()

        if self.verbose and len(self.all_retired) > 0:
            print(f"\n  NOTABLE CAREERS:")
            longest = sorted(self.all_retired, key=lambda r: r.get("career_seasons", 0), reverse=True)[:5]
            print(f"\n    Longest careers:")
            for r in longest:
                rec = r.get("record", {})
                print(f"      {r['ring_name']:20s} {r.get('career_seasons',0)} seasons  "
                      f"age {r.get('_fighter_snapshot', {}).get('_entered_age', '?')}-{r['age']}  "
                      f"peak:{r['peak_tier']}  W:{rec.get('wins',0)}-L:{rec.get('losses',0)}  "
                      f"reason:{r['reason']}")

            best_records = sorted(
                [r for r in self.all_retired if r.get("record", {}).get("wins", 0) + r.get("record", {}).get("losses", 0) > 5],
                key=lambda r: r.get("record", {}).get("wins", 0) / max(1, r.get("record", {}).get("wins", 0) + r.get("record", {}).get("losses", 0)),
                reverse=True,
            )[:5]
            if best_records:
                print(f"\n    Best win rates (5+ fights):")
                for r in best_records:
                    rec = r.get("record", {})
                    total = rec.get("wins", 0) + rec.get("losses", 0)
                    pct = rec.get("wins", 0) / max(1, total) * 100
                    print(f"      {r['ring_name']:20s} {pct:.0f}% ({rec.get('wins',0)}-{rec.get('losses',0)})  "
                          f"peak:{r['peak_tier']}  career:{r.get('career_seasons',0)} seasons")


def main():
    parser = argparse.ArgumentParser(description="Simulate AI Fighting League seasons")
    parser.add_argument("--seasons", type=int, default=20, help="Number of seasons to simulate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-season details")
    args = parser.parse_args()

    sim = LeagueSimulator(seed=args.seed, verbose=args.verbose)
    sim.generate_initial_roster()

    print(f"Simulating {args.seasons} seasons (seed={args.seed})...")

    for s in range(args.seasons):
        sim.simulate_season()
        if not args.verbose:
            season_num = sim.world_state["season_number"] - 1
            retirements = len(sim.season_logs[-1].get("retirements", []))
            new_fighters = len(sim.season_logs[-1].get("new_fighters", []))
            champions = sim.world_state.get("season_champions", [])
            season_champ = next((c for c in champions if c["season"] == season_num), None)
            champ_name = season_champ["ring_name"] if season_champ else "None"
            sys.stdout.write(f"\r  Season {season_num:3d} complete | "
                             f"Retirements: {retirements} | New: {new_fighters} | "
                             f"Champion: {champ_name:20s} | Fights: {sim.total_fights_run}")
            sys.stdout.flush()

    if not args.verbose:
        print()

    sim.print_final_summary(args.seasons)


if __name__ == "__main__":
    main()
