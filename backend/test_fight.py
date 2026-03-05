import json
import sys
import os
import glob

sys.path.insert(0, os.path.dirname(__file__))

from app.engine.combat.simulator import simulate_combat
from app.engine.combat.moves import UNIVERSAL_MOVES


def load_fighters():
    fighters = []
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "fighters")
    for path in sorted(glob.glob(os.path.join(data_dir, "f_*.json"))):
        if not path.endswith(".json"):
            continue
        with open(path) as f:
            fighters.append(json.load(f))
    return fighters


def print_header(f1, f2):
    s1, s2 = f1["stats"], f2["stats"]
    print("=" * 70)
    print(f"  {f1['ring_name']:>25}   vs   {f2['ring_name']:<25}")
    print("=" * 70)
    print(f"  {'':>25}          {'':>25}")
    for stat in ["power", "speed", "technique", "toughness", "supernatural", "guile"]:
        v1, v2 = s1.get(stat, 0), s2.get(stat, 0)
        marker1 = " <" if v1 > v2 else ""
        marker2 = "< " if v2 > v1 else ""
        print(f"  {v1:>3}{marker1:>3}  {stat:^18}  {marker2:<3}{v2:<3}")
    print()


def print_round_header(round_num):
    print(f"\n{'─' * 70}")
    print(f"  ROUND {round_num}")
    print(f"{'─' * 70}")


def format_move_name(move_key):
    move_def = UNIVERSAL_MOVES.get(move_key)
    return move_def.name if move_def else move_key


def print_tick(tick, f1_name, f2_name, f1_id):
    att_name = f1_name if tick.attacker_id == f1_id else f2_name
    def_name = f2_name if tick.attacker_id == f1_id else f1_name
    move_name = format_move_name(tick.move_used)
    def_state = tick.defender_state_after
    att_state = tick.attacker_state_after

    if tick.result == "hit":
        dmg = tick.damage_dealt
        intensity = ""
        if dmg > 20:
            intensity = " ** HUGE HIT **"
        elif dmg > 12:
            intensity = " * solid *"
        print(f"  T{tick.tick_in_round:>2} | {att_name} lands {move_name} -> {def_name} ({dmg:.0f} dmg){intensity}")
    elif tick.result == "blocked":
        print(f"  T{tick.tick_in_round:>2} | {def_name} blocks {att_name}'s {move_name}")
    elif tick.result == "dodged":
        print(f"  T{tick.tick_in_round:>2} | {def_name} dodges {att_name}'s {move_name}")
    elif tick.result == "counter":
        dmg = tick.damage_dealt
        print(f"  T{tick.tick_in_round:>2} | {def_name} COUNTERS {att_name}'s {move_name}! ({dmg:.0f} dmg)")
    elif tick.result == "slip":
        print(f"  T{tick.tick_in_round:>2} | {att_name}'s {move_name} slips past {def_name}")
    else:
        print(f"  T{tick.tick_in_round:>2} | {att_name} uses {move_name} ({tick.result})")

    if tick.finish:
        print(f"\n  *** {tick.finish.upper()} FINISH! ***\n")


def print_round_summary(rs, f1_name, f2_name):
    print(f"\n  {'':>10}  {'':>10}  {f1_name:>16}  {f2_name:>16}")
    print(f"  {'HP':>10}  {'':>10}  {rs.fighter1_hp_end:>16.1f}  {rs.fighter2_hp_end:>16.1f}")
    print(f"  {'Stamina':>10}  {'':>10}  {rs.fighter1_stamina_end:>16.1f}  {rs.fighter2_stamina_end:>16.1f}")
    print(f"  {'Mana':>10}  {'':>10}  {rs.fighter1_mana_end:>16.1f}  {rs.fighter2_mana_end:>16.1f}")
    print(f"  {'Hits':>10}  {'':>10}  {rs.fighter1_hits_landed:>13d}/{rs.fighter1_hits_attempted:<2d}  {rs.fighter2_hits_landed:>13d}/{rs.fighter2_hits_attempted:<2d}")
    print(f"  {'Dmg Dealt':>10}  {'':>10}  {rs.fighter1_damage_dealt:>16.1f}  {rs.fighter2_damage_dealt:>16.1f}")
    print(f"  {'Blocks':>10}  {'':>10}  {rs.fighter1_blocks:>16d}  {rs.fighter2_blocks:>16d}")
    print(f"  {'Dodges':>10}  {'':>10}  {rs.fighter1_dodges:>16d}  {rs.fighter2_dodges:>16d}")


def main():
    fighters = load_fighters()
    if len(fighters) < 2:
        print("Need at least 2 fighters in data/fighters/")
        return

    print("\nAvailable fighters:")
    for i, f in enumerate(fighters):
        s = f["stats"]
        print(f"  [{i}] {f['ring_name']:<20} pow={s['power']:>2} spd={s['speed']:>2} tech={s['technique']:>2} tough={s['toughness']:>2} sup={s.get('supernatural',0):>2} gui={s.get('guile',0):>2}")

    print()
    if len(sys.argv) >= 3:
        i1, i2 = int(sys.argv[1]), int(sys.argv[2])
    else:
        try:
            i1 = int(input("Pick fighter 1 (number): "))
            i2 = int(input("Pick fighter 2 (number): "))
        except (ValueError, EOFError):
            i1, i2 = 0, 1

    f1, f2 = fighters[i1], fighters[i2]

    seed = None
    if len(sys.argv) >= 4:
        seed = int(sys.argv[3])

    print_header(f1, f2)

    result = simulate_combat(f1, f2, seed=seed)

    current_round = 0
    for tick in result.tick_log:
        if tick.round_number != current_round:
            if current_round > 0:
                for rs in result.round_summaries:
                    if rs.round_number == current_round:
                        print_round_summary(rs, f1["ring_name"], f2["ring_name"])
                        break
            current_round = tick.round_number
            print_round_header(current_round)

        print_tick(tick, f1["ring_name"], f2["ring_name"], f1["id"])

    for rs in result.round_summaries:
        if rs.round_number == current_round:
            print_round_summary(rs, f1["ring_name"], f2["ring_name"])
            break

    print(f"\n{'=' * 70}")
    winner_name = f1["ring_name"] if result.winner_id == f1["id"] else f2["ring_name"]
    print(f"  WINNER: {winner_name} by {result.method.upper()} in Round {result.final_round} (tick {result.final_tick})")
    print(f"  Seed: {result.seed}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
