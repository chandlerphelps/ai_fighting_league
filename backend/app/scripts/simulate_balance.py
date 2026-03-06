import argparse
import math
import sys
import traceback
from collections import defaultdict

from app.config import load_config
from app.scripts.simulate_seasons import LeagueSimulator
from app.engine.between_fights.retirement import (
    CORE_STATS, STAT_MIN, STAT_CAP,
    GENDER_SECONDARY_RANGES,
    check_retirement, apply_aging, update_promotion_desperation,
    generate_replacement_fighter,
)
from app.engine.between_fights.league_tiers import TIER_ORDER
from app.engine.between_fights.season import (
    TIER_SIZES, season_start_date, SEASON_START_MONTH,
)
from app.engine.fighter_generator import plan_roster
from app.engine.fighter_config import generate_archetype_stats


class BalanceTracker:
    def __init__(self):
        self.fight_records: list[dict] = []
        self.season_snapshots: list[dict] = []

    def record_fight(self, winner: dict, loser: dict, method: str, tier: str, season: int):
        self.fight_records.append({
            "winner_archetype": winner.get("primary_archetype", ""),
            "winner_gender": winner.get("gender", ""),
            "loser_archetype": loser.get("primary_archetype", ""),
            "loser_gender": loser.get("gender", ""),
            "method": method,
            "tier": tier,
            "season": season,
        })

    def snapshot_tier_composition(self, fighters: dict, season: int):
        snapshot = {"season": season}
        for tier in ["apex", "contender", "underground"]:
            tier_fighters = [f for f in fighters.values() if f.get("tier") == tier and f.get("status") == "active"]
            gender_counts = defaultdict(int)
            archetype_counts = defaultdict(int)
            for f in tier_fighters:
                gender_counts[f.get("gender", "")] += 1
                archetype_counts[f.get("primary_archetype", "")] += 1
            snapshot[tier] = {
                "total": len(tier_fighters),
                "gender": dict(gender_counts),
                "archetype": dict(archetype_counts),
            }
        self.season_snapshots.append(snapshot)


class BalanceSimulator(LeagueSimulator):
    def __init__(self, seed=42, verbose=False, total_seasons=30, tier_sizes=None, pool_size=None):
        super().__init__(seed=seed, verbose=verbose, total_seasons=total_seasons, tier_sizes=tier_sizes)

        self.balance_tracker = BalanceTracker()
        self.replacement_pool: list[dict] = []

        initial_roster = TIER_SIZES["apex"] + TIER_SIZES["contender"] + TIER_SIZES["underground"]
        computed_pool = math.ceil(total_seasons * initial_roster * 0.1) + initial_roster
        self.target_pool_size = pool_size if pool_size is not None else computed_pool

    def _generate_llm_pool(self, total_needed: int) -> list[dict]:
        config = load_config()
        config.min_total_stats = 150
        config.max_total_stats = 220

        pool = []
        existing_fighters_summaries = []
        generated = 0
        batch_num = 0

        while generated < total_needed:
            batch_size = min(8, total_needed - generated)
            gender_mix = "female" if batch_num % 2 == 0 else "male"
            batch_num += 1

            try:
                roster_entries = plan_roster(
                    config,
                    roster_size=batch_size,
                    existing_fighters=existing_fighters_summaries,
                    gender_mix=gender_mix,
                )
            except Exception as e:
                print(f"\n  WARNING: plan_roster failed (batch {batch_num}): {e}")
                traceback.print_exc()
                continue

            for entry in roster_entries:
                if generated >= total_needed:
                    break

                try:
                    self.fighter_counter += 1
                    fighter_id = f"sim-{self.fighter_counter:04d}"

                    archetype = entry.get("primary_archetype", "The Prodigy")
                    gender = entry.get("gender", "female")
                    has_supernatural = entry.get("has_supernatural", False)
                    ring_name = entry.get("ring_name", f"Fighter-{self.fighter_counter}")
                    age = self.rng.randint(18, 26)

                    stats = generate_archetype_stats(
                        archetype, gender, config,
                        has_supernatural=has_supernatural,
                    )

                    fighter_dict = {
                        "id": fighter_id,
                        "ring_name": ring_name,
                        "real_name": ring_name,
                        "age": age,
                        "gender": gender,
                        "primary_archetype": archetype,
                        "subtype": entry.get("subtype", ""),
                        "stats": stats,
                        "tier": "underground",
                        "status": "active",
                        "record": {"wins": 0, "losses": 0, "draws": 0, "kos": 0, "submissions": 0},
                        "condition": {"health_status": "healthy", "injuries": [], "recovery_days_remaining": 0, "morale": "neutral", "momentum": "neutral"},
                        "training_focus": self.rng.choice(CORE_STATS),
                        "training_days_accumulated": 0.0,
                        "training_streak": 0,
                        "seasons_in_current_tier": 0,
                        "career_season_count": 0,
                        "peak_tier": "underground",
                        "promotion_desperation": 0.0,
                        "season_wins": 0,
                        "season_losses": 0,
                        "season_tier_wins": {},
                        "consecutive_losses": 0,
                        "consecutive_wins": 0,
                        "learning_rate": round(self.rng.uniform(0.7, 1.4), 2),
                        "work_ethic": round(self.rng.uniform(0.6, 1.3), 2),
                        "tier_records": {},
                        "last_fight_date": None,
                        "rivalries": [],
                        "storyline_log": [],
                        "moves": [],
                        "_entered_season": 0,
                        "_entered_age": age,
                    }

                    pool.append(fighter_dict)

                    existing_fighters_summaries.append({
                        "ring_name": ring_name,
                        "gender": gender,
                        "primary_archetype": archetype,
                    })

                    generated += 1
                    sys.stdout.write(f"\r  Planning fighters... {generated}/{total_needed}")
                    sys.stdout.flush()

                except Exception as e:
                    print(f"\n  WARNING: fighter construction failed for {entry.get('ring_name', '?')}: {e}")
                    traceback.print_exc()
                    continue

        print()
        return pool

    def generate_initial_roster(self):
        print(f"  Generating LLM fighter pool ({self.target_pool_size} fighters)...")
        all_fighters = self._generate_llm_pool(self.target_pool_size)

        if not all_fighters:
            print("  ERROR: No fighters generated. Falling back to procedural generation.")
            super().generate_initial_roster()
            return

        initial_needed = TIER_SIZES["apex"] + TIER_SIZES["contender"] + TIER_SIZES["underground"]
        if len(all_fighters) < initial_needed:
            print(f"  WARNING: Only generated {len(all_fighters)} fighters, need {initial_needed} for roster.")
            print(f"  Supplementing with procedural fighters...")
            while len(all_fighters) < initial_needed:
                self.fighter_counter += 1
                f = generate_replacement_fighter(
                    self.fighter_counter, season=0, rng=self.rng, used_names=self.used_names,
                )
                all_fighters.append(f)

        idx = 0
        for _ in range(TIER_SIZES["underground"]):
            f = all_fighters[idx]
            f["tier"] = "underground"
            self.fighters[f["id"]] = f
            self.used_names.add(f.get("ring_name", ""))
            idx += 1

        for _ in range(TIER_SIZES["contender"]):
            f = all_fighters[idx]
            f["tier"] = "contender"
            self.fighters[f["id"]] = f
            self.used_names.add(f.get("ring_name", ""))
            idx += 1

        for _ in range(TIER_SIZES["apex"]):
            f = all_fighters[idx]
            f["tier"] = "apex"
            self.fighters[f["id"]] = f
            self.used_names.add(f.get("ring_name", ""))
            idx += 1

        self.replacement_pool = all_fighters[idx:]

        champ_fighters = [f for f in self.fighters.values() if f["tier"] == "apex"]
        if champ_fighters:
            belt_holder = max(champ_fighters, key=lambda f: sum(f.get("stats", {}).get(s, 0) for s in CORE_STATS))
            self.world_state["belt_holder_id"] = belt_holder["id"]
            self.world_state["belt_history"].append({
                "fighter_id": belt_holder["id"],
                "won_date": "season_0",
                "lost_date": None,
                "defenses": self.rng.randint(1, 3),
            })

        self._recalculate_all_rankings()

        if self.verbose:
            archetype_counts = defaultdict(int)
            gender_counts = defaultdict(int)
            for f in self.fighters.values():
                archetype_counts[f.get("primary_archetype", "")] += 1
                gender_counts[f.get("gender", "")] += 1
            print(f"\n  Initial roster generated via LLM pipeline")
            print(f"  Gender: {dict(gender_counts)}")
            print(f"  Archetypes: {dict(sorted(archetype_counts.items()))}")
            print(f"  Replacement pool remaining: {len(self.replacement_pool)}")

    def simulate_season(self):
        from datetime import timedelta
        from app.engine.between_fights.season import (
            season_start_date, season_end_date, REGULAR_MONTHS,
            is_fight_day, get_fight_start_time,
        )

        season_num = self.world_state["season_number"]
        self.season_matches = []
        self.mid_season_retirements = []
        self.season_ending_injuries = []

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"  SEASON {season_num}")
            print(f"{'='*60}")
            self._print_tier_rosters()

        start = season_start_date(season_num)
        end = season_end_date(season_num)
        self._sync_date(start)

        current = start
        while current <= end:
            self._sync_date(current)
            month = current.month

            self._process_daily_recovery()
            self._process_daily_training_all()

            if month in REGULAR_MONTHS:
                for tier in ["apex", "contender", "underground"]:
                    if is_fight_day(current, season_num, tier):
                        self._run_tier_event(tier)

            current += timedelta(days=1)

        self._prepare_promotion_month()
        self._simulate_promotion_month()

        season_summary = self._process_end_of_season_with_pool()

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

        self.balance_tracker.snapshot_tier_composition(self.fighters, season_num)

        if self.verbose:
            self._print_season_summary(season_summary)

        return season_summary

    def _process_end_of_season_with_pool(self) -> dict:
        season = self.world_state.get("season_number", 1)
        summary = {
            "season": season,
            "retirements": [],
            "aging_changes": [],
            "new_fighters": [],
            "backfill_promotions": [],
            "tier_counts_before": self._count_active_tiers(),
        }

        for fid, fighter in list(self.fighters.items()):
            if fighter.get("status") != "active":
                continue
            apply_aging(fighter, self.rng)

        for fid, fighter in list(self.fighters.items()):
            if fighter.get("status") != "active":
                continue

            is_belt_holder = self.world_state.get("belt_holder_id") == fid
            fighter["_is_belt_holder"] = is_belt_holder
            should_retire, reason = check_retirement(fighter, self.rng)
            fighter.pop("_is_belt_holder", None)

            if should_retire:
                fighter["status"] = "retired"
                summary["retirements"].append({
                    "fighter_id": fid,
                    "ring_name": fighter.get("ring_name", ""),
                    "age": fighter.get("age", 0),
                    "tier": fighter.get("tier", ""),
                    "reason": reason,
                    "career_seasons": fighter.get("career_season_count", 0),
                    "peak_tier": fighter.get("peak_tier", "underground"),
                    "record": dict(fighter.get("record", {})),
                })

                if is_belt_holder:
                    for entry in self.world_state.get("belt_history", []):
                        if entry.get("fighter_id") == fid and not entry.get("lost_date"):
                            entry["lost_date"] = f"season_{season}_retired"
                            break
                    self.world_state["belt_holder_id"] = ""

                self.world_state.setdefault("retired_fighter_ids", []).append(fid)

        for fid, fighter in self.fighters.items():
            if fighter.get("status") != "active":
                continue
            if fighter.get("tier") == "underground":
                update_promotion_desperation(fighter)

        self._backfill_from_pool(summary, season)

        for fid, fighter in self.fighters.items():
            if fighter.get("status") != "active":
                continue
            fighter["season_wins"] = 0
            fighter["season_losses"] = 0
            fighter["season_tier_wins"] = {}
            fighter["seasons_in_current_tier"] = fighter.get("seasons_in_current_tier", 0) + 1
            fighter["career_season_count"] = fighter.get("career_season_count", 0) + 1
            fighter["consecutive_losses"] = 0
            condition = fighter.get("condition", {})
            if condition.get("morale") == "low":
                condition["morale"] = "neutral"

            fighter.pop("_season_record_at_injury", None)
            injuries = condition.get("injuries", [])
            has_career_ending = any(i.get("severity") == "career_ending" for i in injuries)
            if not has_career_ending and condition.get("health_status") == "injured":
                fighter["condition"] = {
                    "health_status": "healthy",
                    "injuries": [],
                    "recovery_days_remaining": 0,
                    "morale": condition.get("morale", "neutral"),
                    "momentum": condition.get("momentum", "neutral"),
                }

        self.world_state["season_number"] = season + 1
        self.world_state["current_date"] = season_start_date(season + 1).isoformat()
        self.world_state["season_month"] = SEASON_START_MONTH
        self.world_state["season_day_in_month"] = 1

        summary["tier_counts_after"] = self._count_active_tiers()
        return summary

    def _backfill_from_pool(self, summary: dict, season: int):
        from app.engine.between_fights.league_tiers import calculate_tier_rankings

        for upper_tier, lower_tier in [("apex", "contender"), ("contender", "underground")]:
            target = TIER_SIZES[upper_tier]
            active_in_tier = [f for f in self.fighters.values() if f.get("tier") == upper_tier and f.get("status") == "active"]
            deficit = target - len(active_in_tier)

            if deficit > 0:
                lower_candidates = [
                    f for f in self.fighters.values()
                    if f.get("tier") == lower_tier and f.get("status") == "active"
                ]
                lower_candidates.sort(
                    key=lambda f: (
                        f.get("season_tier_wins", {}).get(lower_tier, 0),
                        sum(f.get("stats", {}).get(s, 0) for s in CORE_STATS),
                    ),
                    reverse=True,
                )
                for i in range(min(deficit, len(lower_candidates))):
                    promoted = lower_candidates[i]
                    promoted["tier"] = upper_tier
                    promoted["seasons_in_current_tier"] = 0
                    if TIER_ORDER.get(upper_tier, 0) > TIER_ORDER.get(promoted.get("peak_tier", "underground"), 0):
                        promoted["peak_tier"] = upper_tier
                    summary["backfill_promotions"].append({
                        "fighter_id": promoted["id"],
                        "ring_name": promoted.get("ring_name", ""),
                        "from_tier": lower_tier,
                        "to_tier": upper_tier,
                    })

        underground_target = TIER_SIZES["underground"]
        active_underground = [f for f in self.fighters.values() if f.get("tier") == "underground" and f.get("status") == "active"]
        underground_deficit = underground_target - len(active_underground)

        if underground_deficit <= 0:
            return

        for _ in range(underground_deficit):
            if self.replacement_pool:
                new_fighter = self.replacement_pool.pop(0)
            else:
                print(f"\n  WARNING: LLM pool exhausted at season {season}. Using procedural fallback.")
                self.fighter_counter += 1
                new_fighter = generate_replacement_fighter(
                    self.fighter_counter, season=season, rng=self.rng, used_names=self.used_names,
                )

            new_fighter["_entered_season"] = season
            new_fighter["_entered_age"] = new_fighter.get("age", 20)
            self.fighters[new_fighter["id"]] = new_fighter
            self.used_names.add(new_fighter.get("ring_name", ""))
            summary["new_fighters"].append({
                "fighter_id": new_fighter["id"],
                "ring_name": new_fighter.get("ring_name", ""),
                "age": new_fighter.get("age", 20),
                "archetype": new_fighter.get("primary_archetype", ""),
            })

    def _count_active_tiers(self) -> dict:
        counts = {"apex": 0, "contender": 0, "underground": 0}
        for f in self.fighters.values():
            if f.get("status") == "active":
                tier = f.get("tier", "underground")
                counts[tier] = counts.get(tier, 0) + 1
        return counts

    def _run_single_fight(self, f1_id, f2_id, start_time=""):
        match_record = super()._run_single_fight(f1_id, f2_id, start_time=start_time)

        winner_id = match_record["outcome"]["winner_id"]
        loser_id = match_record["outcome"]["loser_id"]
        method = match_record["outcome"]["method"]
        tier = self.fighters[f1_id].get("tier", "underground")
        season = self.world_state["season_number"]

        self.balance_tracker.record_fight(
            self.fighters[winner_id], self.fighters[loser_id],
            method, tier, season,
        )
        return match_record

    def print_balance_report(self):
        records = self.balance_tracker.fight_records
        snapshots = self.balance_tracker.season_snapshots

        if not records:
            print("No fight data recorded.")
            return

        print(f"\n{'='*70}")
        print(f"  BALANCE ANALYSIS REPORT — {len(records)} fights across {len(snapshots)} seasons")
        print(f"{'='*70}")

        self._print_gender_balance(records)
        self._print_archetype_balance(records)
        self._print_matchup_matrix(records)
        self._print_tier_composition_trends(snapshots)
        self._print_win_method_analysis(records)
        self._print_low_sample_flags(records)

    def _print_gender_balance(self, records):
        print(f"\n  {'─'*60}")
        print(f"  1. GENDER BALANCE")
        print(f"  {'─'*60}")

        gender_wins = defaultdict(int)
        gender_total = defaultdict(int)
        for r in records:
            gender_wins[r["winner_gender"]] += 1
            gender_total[r["winner_gender"]] += 1
            gender_total[r["loser_gender"]] += 1

        for g in sorted(gender_total.keys()):
            total = gender_total[g]
            wins = gender_wins.get(g, 0)
            pct = wins / total * 100 if total else 0
            print(f"    {g:8s}: {wins:4d} wins / {total:4d} appearances ({pct:.1f}% win rate)")

        cross_gender = [r for r in records if r["winner_gender"] != r["loser_gender"]]
        if cross_gender:
            print(f"\n    Cross-gender fights: {len(cross_gender)}")
            cg_wins = defaultdict(int)
            for r in cross_gender:
                cg_wins[r["winner_gender"]] += 1
            for g in sorted(cg_wins.keys()):
                pct = cg_wins[g] / len(cross_gender) * 100
                print(f"      {g:8s} wins: {cg_wins[g]:4d} ({pct:.1f}%)")

        champions = self.world_state.get("season_champions", [])
        if champions:
            champ_genders = defaultdict(int)
            for c in champions:
                fid = c.get("fighter_id", "")
                fighter = self.fighters.get(fid, {})
                champ_genders[fighter.get("gender", "unknown")] += 1
            print(f"\n    Championship distribution:")
            for g, cnt in sorted(champ_genders.items()):
                pct = cnt / len(champions) * 100
                print(f"      {g:8s}: {cnt:3d} titles ({pct:.1f}%)")

    def _print_archetype_balance(self, records):
        print(f"\n  {'─'*60}")
        print(f"  2. ARCHETYPE BALANCE")
        print(f"  {'─'*60}")

        arch_wins = defaultdict(int)
        arch_total = defaultdict(int)
        for r in records:
            arch_wins[r["winner_archetype"]] += 1
            arch_total[r["winner_archetype"]] += 1
            arch_total[r["loser_archetype"]] += 1

        arch_stats = []
        for arch in sorted(arch_total.keys()):
            total = arch_total[arch]
            wins = arch_wins.get(arch, 0)
            pct = wins / total * 100 if total else 0
            arch_stats.append((arch, wins, total, pct))

        arch_stats.sort(key=lambda x: x[3], reverse=True)

        max_name = max(len(a[0]) for a in arch_stats) if arch_stats else 10
        for arch, wins, total, pct in arch_stats:
            bar_len = int(pct / 2)
            bar = "#" * bar_len
            print(f"    {arch:{max_name}s}: {pct:5.1f}%  ({wins:4d}W / {total:4d}T)  {bar}")

    def _print_matchup_matrix(self, records):
        print(f"\n  {'─'*60}")
        print(f"  3. ARCHETYPE MATCHUP MATRIX")
        print(f"  {'─'*60}")

        matchup_wins = defaultdict(lambda: defaultdict(int))
        matchup_total = defaultdict(lambda: defaultdict(int))

        for r in records:
            wa = r["winner_archetype"]
            la = r["loser_archetype"]
            if wa == la:
                continue
            matchup_wins[wa][la] += 1
            matchup_total[wa][la] += 1
            matchup_total[la][wa] += 1

        all_archetypes = sorted(set(matchup_total.keys()) | set(a for d in matchup_total.values() for a in d))

        if len(all_archetypes) > 20:
            print("    (Too many archetypes for matrix, showing top matchup imbalances)")
            imbalances = []
            for a1 in all_archetypes:
                for a2 in all_archetypes:
                    if a1 >= a2:
                        continue
                    total = matchup_total[a1][a2]
                    if total < 10:
                        continue
                    a1_wins = matchup_wins[a1][a2]
                    pct = a1_wins / total * 100
                    imbalances.append((a1, a2, a1_wins, total, pct))
            imbalances.sort(key=lambda x: abs(x[4] - 50), reverse=True)
            for a1, a2, w, t, pct in imbalances[:15]:
                print(f"    {a1:15s} vs {a2:15s}: {pct:5.1f}% - {100-pct:5.1f}%  (n={t})")
            return

        abbrevs = {a: a[:4] for a in all_archetypes}
        header = "    " + " " * 12 + "".join(f"{abbrevs[a]:>6s}" for a in all_archetypes)
        print(header)

        for a1 in all_archetypes:
            row = f"    {a1:12s}"
            for a2 in all_archetypes:
                if a1 == a2:
                    row += "     -"
                else:
                    total = matchup_total[a1][a2]
                    if total < 5:
                        row += "    .."
                    else:
                        wins = matchup_wins[a1][a2]
                        pct = wins / total * 100
                        row += f"{pct:5.0f}%"
            print(row)

    def _print_tier_composition_trends(self, snapshots):
        print(f"\n  {'─'*60}")
        print(f"  4. TIER COMPOSITION TRENDS")
        print(f"  {'─'*60}")

        if not snapshots:
            print("    No snapshots recorded.")
            return

        checkpoints = []
        if len(snapshots) >= 3:
            checkpoints = [
                ("Start", snapshots[0]),
                ("Middle", snapshots[len(snapshots) // 2]),
                ("End", snapshots[-1]),
            ]
        else:
            checkpoints = [(f"Season {s['season']}", s) for s in snapshots]

        for label, snap in checkpoints:
            print(f"\n    {label} (Season {snap['season']}):")
            for tier in ["apex", "contender"]:
                tier_data = snap.get(tier, {})
                total = tier_data.get("total", 0)
                genders = tier_data.get("gender", {})
                if total > 0:
                    parts = []
                    for g in sorted(genders.keys()):
                        cnt = genders[g]
                        pct = cnt / total * 100
                        parts.append(f"{g}: {cnt} ({pct:.0f}%)")
                    print(f"      {tier:12s}: {total:3d} fighters — {', '.join(parts)}")

    def _print_win_method_analysis(self, records):
        print(f"\n  {'─'*60}")
        print(f"  5. WIN METHOD ANALYSIS")
        print(f"  {'─'*60}")

        method_by_gender = defaultdict(lambda: defaultdict(int))
        gender_fight_count = defaultdict(int)
        for r in records:
            method_by_gender[r["winner_gender"]][r["method"]] += 1
            gender_fight_count[r["winner_gender"]] += 1

        print("\n    By Gender:")
        for g in sorted(method_by_gender.keys()):
            total = gender_fight_count[g]
            print(f"      {g}:")
            for method in sorted(method_by_gender[g].keys()):
                cnt = method_by_gender[g][method]
                pct = cnt / total * 100 if total else 0
                print(f"        {method:15s}: {cnt:4d} ({pct:.1f}%)")

        method_by_arch = defaultdict(lambda: defaultdict(int))
        arch_win_count = defaultdict(int)
        for r in records:
            method_by_arch[r["winner_archetype"]][r["method"]] += 1
            arch_win_count[r["winner_archetype"]] += 1

        print("\n    By Archetype (KO/TKO rate):")
        arch_ko = []
        for arch in sorted(method_by_arch.keys()):
            total = arch_win_count[arch]
            ko_cnt = method_by_arch[arch].get("ko", 0) + method_by_arch[arch].get("tko", 0)
            sub_cnt = method_by_arch[arch].get("submission", 0)
            ko_pct = ko_cnt / total * 100 if total else 0
            sub_pct = sub_cnt / total * 100 if total else 0
            arch_ko.append((arch, ko_pct, sub_pct, total))

        arch_ko.sort(key=lambda x: x[1], reverse=True)
        max_name = max(len(a[0]) for a in arch_ko) if arch_ko else 10
        for arch, ko_pct, sub_pct, total in arch_ko:
            print(f"      {arch:{max_name}s}: KO/TKO {ko_pct:5.1f}%  Sub {sub_pct:5.1f}%  (n={total})")

    def _print_low_sample_flags(self, records):
        print(f"\n  {'─'*60}")
        print(f"  6. LOW SAMPLE SIZE FLAGS")
        print(f"  {'─'*60}")

        arch_total = defaultdict(int)
        for r in records:
            arch_total[r["winner_archetype"]] += 1
            arch_total[r["loser_archetype"]] += 1

        flagged = [(arch, cnt) for arch, cnt in arch_total.items() if cnt < 30]
        if flagged:
            flagged.sort(key=lambda x: x[1])
            for arch, cnt in flagged:
                print(f"    WARNING: {arch} has only {cnt} fight appearances (< 30)")
        else:
            print("    All archetypes have >= 30 fight appearances.")


def main():
    parser = argparse.ArgumentParser(description="Balance testing simulator with LLM-generated fighters")
    parser.add_argument("--seasons", type=int, default=50, help="Number of seasons to simulate (default: 50)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-season details")
    parser.add_argument("--pool-size", type=int, default=None, help="Override pool size (default: computed from seasons * roster * 0.1)")
    parser.add_argument("--apex", type=int, default=None, help="Apex tier size")
    parser.add_argument("--contender", type=int, default=None, help="Contender tier size")
    parser.add_argument("--underground", type=int, default=None, help="Underground tier size")
    args = parser.parse_args()

    tier_sizes = {}
    if args.apex is not None:
        tier_sizes["apex"] = args.apex
    if args.contender is not None:
        tier_sizes["contender"] = args.contender
    if args.underground is not None:
        tier_sizes["underground"] = args.underground

    sim = BalanceSimulator(
        seed=args.seed,
        verbose=args.verbose,
        total_seasons=args.seasons,
        tier_sizes=tier_sizes or None,
        pool_size=args.pool_size,
    )

    sim.generate_initial_roster()

    print(f"\n  Simulating {args.seasons} seasons (seed={args.seed})...")
    print(f"  Note: First ~5 seasons are warmup (all fighters start at underground-level stats)")

    for s in range(args.seasons):
        sim.simulate_season()
        if not args.verbose:
            season_num = sim.world_state["season_number"] - 1
            retirements = len(sim.season_logs[-1].get("retirements", []))
            new_fighters = len(sim.season_logs[-1].get("new_fighters", []))
            pool_remaining = len(sim.replacement_pool)
            champions = sim.world_state.get("season_champions", [])
            season_champ = next((c for c in champions if c["season"] == season_num), None)
            champ_name = season_champ["ring_name"] if season_champ else "None"
            sys.stdout.write(
                f"\r  Season {season_num:3d} complete | "
                f"Retirements: {retirements} | New: {new_fighters} | "
                f"Pool: {pool_remaining} | "
                f"Champion: {champ_name:20s} | Fights: {sim.total_fights_run}"
            )
            sys.stdout.flush()

    if not args.verbose:
        print()

    sim.print_final_summary(args.seasons)
    sim.print_balance_report()


if __name__ == "__main__":
    main()
