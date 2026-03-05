import argparse
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from app.scripts.simulate_seasons import LeagueSimulator


def main():
    parser = argparse.ArgumentParser(description="Simulate 30 seasons and track gender parity across all tiers")
    parser.add_argument("--seasons", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--apex", type=int, default=None)
    parser.add_argument("--contender", type=int, default=None)
    parser.add_argument("--underground", type=int, default=None)
    args = parser.parse_args()

    tier_sizes = {}
    if args.apex is not None:
        tier_sizes["apex"] = args.apex
    if args.contender is not None:
        tier_sizes["contender"] = args.contender
    if args.underground is not None:
        tier_sizes["underground"] = args.underground

    sim = LeagueSimulator(
        seed=args.seed,
        verbose=False,
        total_seasons=args.seasons,
        tier_sizes=tier_sizes or None,
    )
    sim.generate_initial_roster()

    gender_wins = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0, "fights": 0}))
    season_snapshots = []
    method_by_gender = defaultdict(lambda: defaultdict(int))
    title_holders_by_gender = defaultdict(int)
    tier_composition = defaultdict(lambda: defaultdict(lambda: {"male": 0, "female": 0}))

    print(f"Simulating {args.seasons} seasons (seed={args.seed})...\n")
    print(f"{'Season':>7} | {'M wins':>7} {'F wins':>7} {'M%':>6} | "
          f"{'Apex M/F':>10} {'Cont M/F':>10} {'UG M/F':>10} | {'Champion':>20}")
    print("-" * 105)

    for s in range(args.seasons):
        season_num = sim.world_state["season_number"]
        pre_fight_count = sim.total_fights_run

        sim.simulate_season()

        season_m_wins = 0
        season_f_wins = 0

        for match in sim.season_matches:
            outcome = match.get("outcome", {})
            winner_id = outcome.get("winner_id", "")
            loser_id = outcome.get("loser_id", "")
            method = outcome.get("method", "")

            winner = sim.fighters.get(winner_id, {})
            loser = sim.fighters.get(loser_id, {})
            w_gender = winner.get("gender", "")
            l_gender = loser.get("gender", "")
            w_tier = winner.get("tier", "underground")

            if w_gender:
                gender_wins["overall"][w_gender]["wins"] += 1
                gender_wins["overall"][w_gender]["fights"] += 1
                gender_wins[w_tier][w_gender]["wins"] += 1
                gender_wins[w_tier][w_gender]["fights"] += 1
                method_by_gender[w_gender][method] += 1
                if w_gender == "male":
                    season_m_wins += 1
                else:
                    season_f_wins += 1
            if l_gender:
                gender_wins["overall"][l_gender]["losses"] += 1
                gender_wins["overall"][l_gender]["fights"] += 1
                gender_wins[w_tier][l_gender]["losses"] += 1
                gender_wins[w_tier][l_gender]["fights"] += 1

        for tier in ["apex", "contender", "underground"]:
            active_in_tier = [f for f in sim.fighters.values() if f.get("tier") == tier and f.get("status") == "active"]
            males = sum(1 for f in active_in_tier if f.get("gender") == "male")
            females = sum(1 for f in active_in_tier if f.get("gender") == "female")
            tier_composition[season_num][tier] = {"male": males, "female": females}

        belt_holder_id = sim.world_state.get("belt_holder_id", "")
        belt_holder = sim.fighters.get(belt_holder_id, {})
        belt_gender = belt_holder.get("gender", "")
        if belt_gender:
            title_holders_by_gender[belt_gender] += 1

        champions = sim.world_state.get("season_champions", [])
        season_champ = next((c for c in champions if c["season"] == season_num), None)
        champ_name = season_champ["ring_name"] if season_champ else "N/A"

        total_s = max(1, season_m_wins + season_f_wins)
        m_pct = season_m_wins / total_s * 100

        tc = tier_composition[season_num]
        apex_str = f"{tc['apex']['male']}/{tc['apex']['female']}"
        cont_str = f"{tc['contender']['male']}/{tc['contender']['female']}"
        ug_str = f"{tc['underground']['male']}/{tc['underground']['female']}"

        print(f"{season_num:>7} | {season_m_wins:>7} {season_f_wins:>7} {m_pct:>5.1f}% | "
              f"{apex_str:>10} {cont_str:>10} {ug_str:>10} | {champ_name:>20}")

        season_snapshots.append({
            "season": season_num,
            "male_wins": season_m_wins,
            "female_wins": season_f_wins,
        })

    print("\n" + "=" * 80)
    print("  30-SEASON GENDER PARITY REPORT")
    print("=" * 80)

    total_m = gender_wins["overall"]["male"]["wins"]
    total_f = gender_wins["overall"]["female"]["wins"]
    total_fights = gender_wins["overall"]["male"]["fights"]
    print(f"\n  OVERALL WIN RATES (across {total_fights} fighter-fight slots):")
    print(f"    Male wins:    {total_m:>6} ({total_m / max(1, total_m + total_f) * 100:.1f}%)")
    print(f"    Female wins:  {total_f:>6} ({total_f / max(1, total_m + total_f) * 100:.1f}%)")

    print(f"\n  WIN RATES BY TIER:")
    for tier in ["apex", "contender", "underground"]:
        tw = gender_wins[tier]
        m_w = tw["male"]["wins"]
        f_w = tw["female"]["wins"]
        total = m_w + f_w
        if total == 0:
            continue
        print(f"    {tier.upper():>12}: Male {m_w:>5} ({m_w/total*100:.1f}%)  Female {f_w:>5} ({f_w/total*100:.1f}%)")

    print(f"\n  WIN METHODS BY GENDER:")
    for gender in ["male", "female"]:
        total_gender_wins = sum(method_by_gender[gender].values())
        print(f"    {gender.upper()}:")
        for method, count in sorted(method_by_gender[gender].items()):
            print(f"      {method:>12}: {count:>5} ({count / max(1, total_gender_wins) * 100:.1f}%)")

    print(f"\n  TITLE HOLDER SEASONS BY GENDER:")
    for gender in ["male", "female"]:
        count = title_holders_by_gender[gender]
        print(f"    {gender.upper():>8}: {count:>3} seasons ({count / max(1, args.seasons) * 100:.1f}%)")

    print(f"\n  TIER COMPOSITION (final season):")
    final_season = max(tier_composition.keys())
    for tier in ["apex", "contender", "underground"]:
        tc = tier_composition[final_season][tier]
        total = tc["male"] + tc["female"]
        if total == 0:
            continue
        print(f"    {tier.upper():>12}: {tc['male']} male / {tc['female']} female ({tc['female']/total*100:.0f}% female)")

    season_m_wins_all = [s["male_wins"] for s in season_snapshots]
    season_f_wins_all = [s["female_wins"] for s in season_snapshots]
    seasons_male_dominant = sum(1 for m, f in zip(season_m_wins_all, season_f_wins_all) if m > f)
    seasons_female_dominant = sum(1 for m, f in zip(season_m_wins_all, season_f_wins_all) if f > m)
    seasons_even = args.seasons - seasons_male_dominant - seasons_female_dominant

    print(f"\n  SEASON-LEVEL DOMINANCE:")
    print(f"    Seasons male-dominant:   {seasons_male_dominant}")
    print(f"    Seasons female-dominant: {seasons_female_dominant}")
    print(f"    Seasons even:            {seasons_even}")

    parity_ratio = min(total_m, total_f) / max(1, max(total_m, total_f)) * 100
    print(f"\n  PARITY RATIO: {parity_ratio:.1f}%")
    if parity_ratio >= 80:
        print("  VERDICT: GOOD BALANCE")
    elif parity_ratio >= 60:
        print("  VERDICT: MODERATE BALANCE")
    else:
        print("  VERDICT: POOR BALANCE — needs tuning")
    print("=" * 80)


if __name__ == "__main__":
    main()
