import argparse
import random as _random
import sys
import os
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(__file__))

from app.config import Config
from app.engine.fighter_config import (
    generate_archetype_stats,
    ARCHETYPES_MALE,
    ARCHETYPES_FEMALE,
)
from app.engine.between_fights.retirement import RING_NAMES, PREFIXES, CORE_STATS
from app.engine.between_fights.season import TIER_SIZES, set_tier_sizes
from app.scripts.simulate_seasons import LeagueSimulator


class BalanceSimulator(LeagueSimulator):

    def __init__(self, seed=42, verbose=False):
        super().__init__(seed=seed, verbose=verbose)
        self.config = Config()

    def _make_fighter(self, counter, tier, age_range, stat_range, career_seasons_range, tier_seasons_range):
        age = self.rng.randint(*age_range)
        gender = self.rng.choice(["female", "male"])

        if gender == "male":
            archetype = self.rng.choice(ARCHETYPES_MALE)
        else:
            archetype = self.rng.choice(ARCHETYPES_FEMALE)

        has_supernatural = self.rng.random() < 0.3

        override_config = Config(
            min_total_stats=stat_range[0],
            max_total_stats=stat_range[1],
        )

        stats = generate_archetype_stats(
            archetype, gender, override_config,
            has_supernatural=has_supernatural, rng=self.rng,
        )

        career_seasons = self.rng.randint(*career_seasons_range)
        tier_seasons = self.rng.randint(*tier_seasons_range)
        total_fights = career_seasons * self.rng.randint(6, 12)

        if tier == "apex":
            win_rate = self.rng.uniform(0.55, 0.75)
        elif tier == "contender":
            win_rate = self.rng.uniform(0.45, 0.65)
        else:
            win_rate = self.rng.uniform(0.35, 0.60)

        wins = max(0, round(total_fights * win_rate))
        losses = max(0, total_fights - wins)

        for _ in range(100):
            prefix = self.rng.choice(PREFIXES) if self.rng.random() < 0.4 else ""
            name = self.rng.choice(RING_NAMES)
            ring_name = f"{prefix} {name}".strip() if prefix else name
            if ring_name not in self.used_names:
                break
        self.used_names.add(ring_name)

        peak_tier = tier
        if tier == "contender":
            peak_tier = "contender" if self.rng.random() < 0.7 else "apex"

        fighter_id = f"sim-{counter:04d}"

        return {
            "id": fighter_id,
            "ring_name": ring_name,
            "real_name": ring_name,
            "age": age,
            "gender": gender,
            "primary_archetype": archetype,
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
            "consecutive_wins": 0,
            "learning_rate": round(self.rng.uniform(0.7, 1.4), 2),
            "work_ethic": round(self.rng.uniform(0.6, 1.3), 2),
            "tier_records": {tier: {"wins": wins, "losses": losses, "draws": 0}},
            "last_fight_date": None,
            "rivalries": [],
            "storyline_log": [],
            "moves": [],
            "_entered_season": 0,
            "_entered_age": age - career_seasons,
        }


def collect_season_snapshot(sim):
    snapshot = {
        "tier_gender": {},
        "tier_archetype": {},
        "tier_stats": {},
    }
    for tier in ["apex", "contender", "underground"]:
        fighters_in_tier = [
            f for f in sim.fighters.values()
            if f.get("tier") == tier and f.get("status") == "active"
        ]
        genders = Counter(f.get("gender", "?") for f in fighters_in_tier)
        archetypes = Counter(f.get("primary_archetype", "?") for f in fighters_in_tier)
        stat_totals = defaultdict(list)
        for f in fighters_in_tier:
            for s, v in f.get("stats", {}).items():
                stat_totals[s].append(v)

        snapshot["tier_gender"][tier] = dict(genders)
        snapshot["tier_archetype"][tier] = dict(archetypes)
        snapshot["tier_stats"][tier] = {
            s: round(sum(vals) / max(1, len(vals)), 1) for s, vals in stat_totals.items()
        }
    return snapshot


def collect_fight_stats(sim):
    male_wins = 0
    female_wins = 0
    male_methods = Counter()
    female_methods = Counter()
    archetype_record = defaultdict(lambda: {"wins": 0, "losses": 0})
    cross_gender_male_wins = 0
    cross_gender_female_wins = 0

    for match in sim.season_matches:
        outcome = match.get("outcome", {})
        winner_id = outcome.get("winner_id")
        loser_id = outcome.get("loser_id")
        method = outcome.get("method", "?")

        winner = sim.fighters.get(winner_id, {})
        loser = sim.fighters.get(loser_id, {})

        w_gender = winner.get("gender", "?")
        l_gender = loser.get("gender", "?")
        w_arch = winner.get("primary_archetype", "?")
        l_arch = loser.get("primary_archetype", "?")

        if w_gender == "male":
            male_wins += 1
            male_methods[method] += 1
        else:
            female_wins += 1
            female_methods[method] += 1

        archetype_record[w_arch]["wins"] += 1
        archetype_record[l_arch]["losses"] += 1

        if w_gender != l_gender:
            if w_gender == "male":
                cross_gender_male_wins += 1
            else:
                cross_gender_female_wins += 1

    return {
        "male_wins": male_wins,
        "female_wins": female_wins,
        "male_methods": dict(male_methods),
        "female_methods": dict(female_methods),
        "archetype_record": dict(archetype_record),
        "cross_gender_male_wins": cross_gender_male_wins,
        "cross_gender_female_wins": cross_gender_female_wins,
    }


def print_report(all_fight_stats, all_snapshots, champions, num_seasons):
    total_m = sum(s["male_wins"] for s in all_fight_stats)
    total_f = sum(s["female_wins"] for s in all_fight_stats)
    total = total_m + total_f

    cross_m = sum(s["cross_gender_male_wins"] for s in all_fight_stats)
    cross_f = sum(s["cross_gender_female_wins"] for s in all_fight_stats)
    cross_total = cross_m + cross_f

    print(f"\n{'='*70}")
    print(f"  MULTI-SEASON BALANCE REPORT ({num_seasons} seasons)")
    print(f"{'='*70}")

    print(f"\n  OVERALL WIN RATES (all fights)")
    print(f"  {'Male wins:':<20} {total_m:>6} ({total_m/max(1,total)*100:.1f}%)")
    print(f"  {'Female wins:':<20} {total_f:>6} ({total_f/max(1,total)*100:.1f}%)")
    print(f"  {'Total fights:':<20} {total:>6}")

    if cross_total > 0:
        print(f"\n  CROSS-GENDER FIGHTS ONLY")
        print(f"  {'Male wins:':<20} {cross_m:>6} ({cross_m/max(1,cross_total)*100:.1f}%)")
        print(f"  {'Female wins:':<20} {cross_f:>6} ({cross_f/max(1,cross_total)*100:.1f}%)")
        print(f"  {'Total:':<20} {cross_total:>6}")

    print(f"\n  CHAMPIONS BY GENDER")
    champ_genders = Counter(c["gender"] for c in champions)
    for g in ["male", "female"]:
        count = champ_genders.get(g, 0)
        print(f"  {g.capitalize():<20} {count:>3} ({count/max(1,len(champions))*100:.1f}%)")

    print(f"\n  TIER COMPOSITION (final season snapshot)")
    final = all_snapshots[-1] if all_snapshots else {}
    for tier in ["apex", "contender", "underground"]:
        genders = final.get("tier_gender", {}).get(tier, {})
        m = genders.get("male", 0)
        f = genders.get("female", 0)
        t = m + f
        print(f"  {tier.upper():<15} M:{m:>3} ({m/max(1,t)*100:.0f}%)  F:{f:>3} ({f/max(1,t)*100:.0f}%)  Total:{t:>3}")

    print(f"\n  TIER GENDER SPLIT OVER TIME (avg across all seasons)")
    tier_m_pcts = {"apex": [], "contender": [], "underground": []}
    for snap in all_snapshots:
        for tier in ["apex", "contender", "underground"]:
            genders = snap.get("tier_gender", {}).get(tier, {})
            m = genders.get("male", 0)
            f = genders.get("female", 0)
            t = m + f
            tier_m_pcts[tier].append(m / max(1, t) * 100)
    for tier in ["apex", "contender", "underground"]:
        pcts = tier_m_pcts[tier]
        avg = sum(pcts) / max(1, len(pcts))
        print(f"  {tier.upper():<15} Avg male%: {avg:.1f}%")

    all_methods_m = Counter()
    all_methods_f = Counter()
    for s in all_fight_stats:
        all_methods_m.update(s.get("male_methods", {}))
        all_methods_f.update(s.get("female_methods", {}))

    print(f"\n  WIN METHODS")
    print(f"  {'Method':<15} {'Male':>10} {'Female':>10}")
    print(f"  {'-'*15} {'-'*10} {'-'*10}")
    all_methods = sorted(set(list(all_methods_m.keys()) + list(all_methods_f.keys())))
    for method in all_methods:
        mc = all_methods_m.get(method, 0)
        fc = all_methods_f.get(method, 0)
        mp = mc / max(1, total_m) * 100
        fp = fc / max(1, total_f) * 100
        print(f"  {method:<15} {mc:>6} ({mp:>4.1f}%) {fc:>6} ({fp:>4.1f}%)")

    combined_arch = defaultdict(lambda: {"wins": 0, "losses": 0})
    for s in all_fight_stats:
        for arch, rec in s.get("archetype_record", {}).items():
            combined_arch[arch]["wins"] += rec["wins"]
            combined_arch[arch]["losses"] += rec["losses"]

    print(f"\n  ARCHETYPE PERFORMANCE")
    print(f"  {'Archetype':<22} {'Wins':>6} {'Losses':>6} {'Win%':>7} {'Fights':>7}")
    print(f"  {'-'*22} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")
    sorted_archs = sorted(combined_arch.items(), key=lambda x: x[1]["wins"] / max(1, x[1]["wins"] + x[1]["losses"]), reverse=True)
    for arch, rec in sorted_archs:
        if not arch or arch == "?":
            continue
        total_f = rec["wins"] + rec["losses"]
        win_pct = rec["wins"] / max(1, total_f) * 100
        print(f"  {arch:<22} {rec['wins']:>6} {rec['losses']:>6} {win_pct:>6.1f}% {total_f:>7}")

    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="Multi-season gender balance simulation")
    parser.add_argument("--seasons", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    set_tier_sizes(apex=16, contender=20, underground=100)

    sim = BalanceSimulator(seed=args.seed, verbose=args.verbose)
    sim.generate_initial_roster()

    all_fight_stats = []
    all_snapshots = []
    champions = []

    print(f"Running {args.seasons} seasons (seed={args.seed})...")
    for season_num in range(args.seasons):
        sim.simulate_season()

        fight_stats = collect_fight_stats(sim)
        all_fight_stats.append(fight_stats)

        snapshot = collect_season_snapshot(sim)
        all_snapshots.append(snapshot)

        season_champs = sim.world_state.get("season_champions", [])
        if season_champs:
            latest = season_champs[-1]
            champ_fighter = sim.fighters.get(latest["fighter_id"], {})
            champions.append({
                "season": latest["season"],
                "name": latest["ring_name"],
                "gender": champ_fighter.get("gender", "?"),
                "archetype": champ_fighter.get("primary_archetype", "?"),
            })

        m = fight_stats["male_wins"]
        f = fight_stats["female_wins"]
        t = m + f
        apex_g = snapshot["tier_gender"].get("apex", {})
        am = apex_g.get("male", 0)
        af = apex_g.get("female", 0)
        print(f"  Season {season_num+1:>2}: {t:>4} fights | M:{m/max(1,t)*100:.0f}% F:{f/max(1,t)*100:.0f}% | Apex M:{am} F:{af} | Champ: {champions[-1]['name'] if champions else '?'} ({champions[-1]['gender'][0].upper() if champions else '?'})")

    print_report(all_fight_stats, all_snapshots, champions, args.seasons)


if __name__ == "__main__":
    main()
