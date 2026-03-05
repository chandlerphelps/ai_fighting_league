import argparse
import random as _random
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from app.engine.combat.simulator import simulate_combat
from app.engine.between_fights.retirement import generate_replacement_fighter


def generate_roster(n_per_gender, rng, used_names):
    males = []
    females = []
    counter = 0
    for _ in range(n_per_gender):
        counter += 1
        males.append(generate_replacement_fighter(counter, 1, rng, used_names, gender_override="male"))
    for _ in range(n_per_gender):
        counter += 1
        females.append(generate_replacement_fighter(counter, 1, rng, used_names, gender_override="female"))
    return males, females


def stat_summary(fighters):
    totals = defaultdict(list)
    for f in fighters:
        for stat, val in f["stats"].items():
            totals[stat].append(val)
    return {stat: sum(vals) / len(vals) for stat, vals in totals.items()}


def run_balance_test(males, females, rng):
    results = {
        "male_wins": 0,
        "female_wins": 0,
        "draws": 0,
        "male_methods": defaultdict(int),
        "female_methods": defaultdict(int),
        "total_rounds": 0,
        "total_fights": 0,
    }

    total = len(males) * len(females)
    for i, m in enumerate(males):
        for j, f in enumerate(females):
            fight_num = i * len(females) + j + 1
            if fight_num % 500 == 0:
                print(f"  Fight {fight_num}/{total}...")

            seed = rng.randint(0, 2**31)
            result = simulate_combat(m, f, seed=seed)
            results["total_fights"] += 1
            results["total_rounds"] += result.final_round

            if result.winner_id == m["id"]:
                results["male_wins"] += 1
                results["male_methods"][result.method] += 1
            elif result.winner_id == f["id"]:
                results["female_wins"] += 1
                results["female_methods"][result.method] += 1
            else:
                results["draws"] += 1

    return results


def print_results(results, male_stats, female_stats):
    total = results["total_fights"]
    m_wins = results["male_wins"]
    f_wins = results["female_wins"]
    draws = results["draws"]

    print("\n" + "=" * 60)
    print("  BALANCE TEST RESULTS")
    print("=" * 60)
    print(f"\n  Total fights: {total}")
    print(f"  Male wins:    {m_wins} ({m_wins/total*100:.1f}%)")
    print(f"  Female wins:  {f_wins} ({f_wins/total*100:.1f}%)")
    print(f"  Draws:        {draws} ({draws/total*100:.1f}%)")
    print(f"  Avg rounds:   {results['total_rounds']/total:.1f}")

    print(f"\n  Male win methods:")
    for method, count in sorted(results["male_methods"].items()):
        print(f"    {method}: {count} ({count/max(1,m_wins)*100:.1f}%)")

    print(f"\n  Female win methods:")
    for method, count in sorted(results["female_methods"].items()):
        print(f"    {method}: {count} ({count/max(1,f_wins)*100:.1f}%)")

    print(f"\n  Average stats:")
    print(f"  {'Stat':<15} {'Male':>8} {'Female':>8} {'Diff':>8}")
    print(f"  {'-'*15} {'-'*8} {'-'*8} {'-'*8}")
    all_stats = sorted(set(list(male_stats.keys()) + list(female_stats.keys())))
    for stat in all_stats:
        m_val = male_stats.get(stat, 0)
        f_val = female_stats.get(stat, 0)
        print(f"  {stat:<15} {m_val:>8.1f} {f_val:>8.1f} {f_val-m_val:>+8.1f}")

    print("=" * 60)

    balance_pct = min(m_wins, f_wins) / max(1, max(m_wins, f_wins)) * 100
    if balance_pct >= 80:
        print("  BALANCE: GOOD (within 80-100% parity)")
    elif balance_pct >= 60:
        print("  BALANCE: MODERATE (60-80% parity)")
    else:
        print("  BALANCE: POOR (below 60% parity)")
    print()


def main():
    parser = argparse.ArgumentParser(description="Test gender balance in combat")
    parser.add_argument("--per-gender", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = _random.Random(args.seed)
    used_names = set()

    print(f"Generating {args.per_gender} fighters per gender (seed={args.seed})...")
    males, females = generate_roster(args.per_gender, rng, used_names)

    male_stats = stat_summary(males)
    female_stats = stat_summary(females)

    total_fights = args.per_gender * args.per_gender
    print(f"Running {total_fights} cross-gender fights...")
    results = run_balance_test(males, females, rng)

    print_results(results, male_stats, female_stats)


if __name__ == "__main__":
    main()
