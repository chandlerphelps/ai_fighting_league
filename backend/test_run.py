import sys
import json
import random
from datetime import date

sys.path.insert(0, '.')

from app.config import load_config
from app.models.fighter import (
    Fighter, FightingStyle, PhysicalStats, CombatStats,
    PsychologicalStats, SupernaturalStats, Record, Condition,
)
from app.models.world_state import WorldState
from app.services import data_manager
from app.engine.day_ticker import advance_day


def create_test_fighters():
    fighters = [
        Fighter(
            id="f_iron01",
            ring_name="Iron Fist",
            real_name="Marcus Cole",
            age=29,
            origin="Detroit, Michigan, USA",
            alignment="face",
            height="6'1\"",
            weight="210 lbs",
            build="Muscular, athletic",
            distinguishing_features="Tribal tattoo sleeve on left arm, broken nose",
            ring_attire="Black shorts with gold trim, hand wraps",
            backstory="Marcus grew up in the roughest neighborhoods of Detroit. Boxing saved his life — a local gym owner took him in at age 12 and taught him discipline through the sweet science. He fought his way out of poverty, earning a reputation as one of the hardest punchers in underground circuits before going legit. He fights clean, hits hard, and never quits.",
            personality_traits=["honorable", "determined", "quiet intensity", "protective"],
            fears_quirks=["fears disappointing his mentor", "always wraps his own hands — ritual"],
            fighting_style=FightingStyle(
                primary_style="Boxing",
                secondary_style="Muay Thai",
                signature_move="The Detroit Hook — a devastating left hook to the body",
                finishing_move="Iron Curtain — an overhand right that drops opponents cold",
                known_weaknesses=["Limited ground game", "Slow against faster strikers"],
            ),
            physical_stats=PhysicalStats(strength=85, speed=60, endurance=75, durability=80, recovery=65),
            combat_stats=CombatStats(striking=90, grappling=35, defense=70, fight_iq=65, finishing_instinct=80),
            psychological_stats=PsychologicalStats(aggression=70, composure=75, confidence=80, resilience=85, killer_instinct=75),
            supernatural_stats=SupernaturalStats(),
            record=Record(),
            condition=Condition(),
        ),
        Fighter(
            id="f_viper02",
            ring_name="Viper",
            real_name="Yuki Tanaka",
            age=24,
            origin="Osaka, Japan",
            alignment="heel",
            height="5'5\"",
            weight="125 lbs",
            build="Lean, whip-fast, compact",
            distinguishing_features="Snake tattoo coiling up her spine, emerald green eyes",
            ring_attire="High-cut black leotard with green scale pattern, thigh-high boots",
            backstory="Yuki was raised in the underground fighting pits of Osaka's criminal underworld. Her father owed debts to the wrong people, and she was taken as collateral at age 14. They trained her to fight, but she trained herself to survive. She fights dirty because clean fighting gets you killed where she comes from. She escaped at 19 and now fights in the AFL — not for glory, but because violence is the only language she speaks fluently.",
            personality_traits=["cunning", "ruthless", "seductive", "distrustful"],
            fears_quirks=["never turns her back to doors", "smiles before she hurts someone"],
            fighting_style=FightingStyle(
                primary_style="Jiu-Jitsu",
                secondary_style="Dirty Boxing",
                signature_move="Serpent's Coil — a flying armbar from clinch",
                finishing_move="Venom Strike — a knee to the temple from Thai clinch",
                known_weaknesses=["Light frame, can't absorb heavy shots", "Reckless when angry"],
            ),
            physical_stats=PhysicalStats(strength=40, speed=90, endurance=70, durability=45, recovery=75),
            combat_stats=CombatStats(striking=65, grappling=85, defense=75, fight_iq=80, finishing_instinct=70),
            psychological_stats=PsychologicalStats(aggression=80, composure=55, confidence=75, resilience=70, killer_instinct=85),
            supernatural_stats=SupernaturalStats(),
            record=Record(),
            condition=Condition(),
        ),
        Fighter(
            id="f_titan03",
            ring_name="The Butcher",
            real_name="Dimitri Volkov",
            age=34,
            origin="Novosibirsk, Russia",
            alignment="heel",
            height="6'5\"",
            weight="278 lbs",
            build="Massive, barrel-chested, raw-muscled",
            distinguishing_features="Burn scars across his back, missing left earlobe",
            ring_attire="Cargo pants, bare-chested, steel-toed boots (removed for fights)",
            backstory="Dimitri was a bare-knuckle fighter in Siberian logging camps before anyone gave him a proper fight. He has no formal training — he just shows up, absorbs punishment like a glacier absorbs rain, and then breaks people. He doesn't fight for money or glory. He fights because when he's in the cage, the noise in his head goes quiet. Nobody knows what happened to him in those camps. Nobody asks twice.",
            personality_traits=["silent", "brutal", "haunted", "surprisingly gentle outside the cage"],
            fears_quirks=["doesn't speak before fights", "collects small wooden figurines"],
            fighting_style=FightingStyle(
                primary_style="Brawling",
                secondary_style="Wrestling",
                signature_move="Siberian Slam — picks opponents up and hurls them into the cage",
                finishing_move="The Cleaver — a hammerfist from mount that ends fights",
                known_weaknesses=["Slow footwork", "Gasses out in later rounds"],
            ),
            physical_stats=PhysicalStats(strength=95, speed=35, endurance=55, durability=90, recovery=50),
            combat_stats=CombatStats(striking=60, grappling=70, defense=45, fight_iq=40, finishing_instinct=85),
            psychological_stats=PsychologicalStats(aggression=90, composure=40, confidence=70, resilience=90, killer_instinct=95),
            supernatural_stats=SupernaturalStats(),
            record=Record(),
            condition=Condition(),
        ),
        Fighter(
            id="f_ghost04",
            ring_name="Whisper",
            real_name="Linh Nguyen",
            age=27,
            origin="Ho Chi Minh City, Vietnam",
            alignment="tweener",
            height="5'2\"",
            weight="112 lbs",
            build="Tiny, willowy, deceptively strong core",
            distinguishing_features="White streak in black hair, moves like she weighs nothing",
            ring_attire="White silk wrap top, flowing white pants that conceal her kicks",
            backstory="Linh trained in a remote Vietnamese monastery from age 6, learning a discipline that blends Wing Chun with chi manipulation. She is the smallest fighter in the AFL and possibly the most dangerous. She doesn't overpower opponents — she redirects their energy, finds the gaps in their defense, and dismantles them with surgical precision. She barely speaks, communicates through movement, and fights with an eerie calm that unsettles even the most composed opponents.",
            personality_traits=["serene", "observant", "enigmatic", "compassionate"],
            fears_quirks=["meditates for exactly 30 minutes before every fight", "has never raised her voice"],
            fighting_style=FightingStyle(
                primary_style="Wing Chun",
                secondary_style="Tai Chi",
                signature_move="Stillwater Counter — redirects an opponent's strike into a joint lock",
                finishing_move="Lotus Palm — a chi-enhanced palm strike to the solar plexus",
                known_weaknesses=["Fragile frame, one clean shot can end her", "Struggles against relentless pressure fighters"],
            ),
            physical_stats=PhysicalStats(strength=30, speed=85, endurance=65, durability=35, recovery=80),
            combat_stats=CombatStats(striking=75, grappling=60, defense=90, fight_iq=90, finishing_instinct=60),
            psychological_stats=PsychologicalStats(aggression=25, composure=95, confidence=70, resilience=65, killer_instinct=40),
            supernatural_stats=SupernaturalStats(chi_mastery=45),
            record=Record(),
            condition=Condition(),
        ),
        Fighter(
            id="f_blaze05",
            ring_name="Neon",
            real_name="Jaylen Washington",
            age=22,
            origin="Atlanta, Georgia, USA",
            alignment="face",
            height="5'10\"",
            weight="170 lbs",
            build="Athletic, sculpted, explosive",
            distinguishing_features="Neon green braids, always smiling, visible six-pack",
            ring_attire="Neon green shorts, matching kicks, flashy entrance jacket",
            backstory="Jaylen is the most exciting young fighter the AFL has seen in years. A former college wrestler who discovered he could strike like a middleweight and move like a flyweight. He's charismatic, fearless, and fights with a joy that's infectious. The crowd loves him. He's 22, undefeated in his mind, and convinced he's destined to be champion. Whether that confidence is warranted or just youth remains to be seen.",
            personality_traits=["charismatic", "fearless", "showman", "occasionally reckless"],
            fears_quirks=["can't resist playing to the crowd mid-fight", "superstitious about his green braids"],
            fighting_style=FightingStyle(
                primary_style="MMA Wrestling",
                secondary_style="Kickboxing",
                signature_move="The Highlight Reel — a spinning back kick to the body",
                finishing_move="Neon Lights — a flying knee that puts out the lights",
                known_weaknesses=["Showboating costs him positions", "Inexperienced against veterans"],
            ),
            physical_stats=PhysicalStats(strength=65, speed=85, endurance=70, durability=60, recovery=70),
            combat_stats=CombatStats(striking=75, grappling=75, defense=60, fight_iq=55, finishing_instinct=70),
            psychological_stats=PsychologicalStats(aggression=75, composure=50, confidence=90, resilience=60, killer_instinct=65),
            supernatural_stats=SupernaturalStats(),
            record=Record(),
            condition=Condition(),
        ),
    ]
    return fighters


def main():
    config = load_config()
    print(f"API Key loaded: {'yes' if config.openrouter_api_key else 'NO'}")
    print(f"Model: {config.default_model}")

    data_manager.ensure_data_dirs(config)

    print("\nCreating 5 test fighters...")
    fighters = create_test_fighters()
    fighter_ids = []
    for f in fighters:
        print(f"  {f.ring_name} ({f.real_name}) — Stats total: {f.total_core_stats()}")
        data_manager.save_fighter(f, config)
        fighter_ids.append(f.id)

    ws = WorldState(
        current_date=date.today().isoformat(),
        day_number=0,
        rankings=fighter_ids,
        upcoming_events=[],
        completed_events=[],
        active_injuries={},
        rivalry_graph=[],
        last_daily_summary="Test league initialized.",
        event_counter=0,
    )
    data_manager.save_world_state(ws, config)
    print(f"\nWorld state created: Day 0, {date.today().isoformat()}")

    days_to_run = 7
    print(f"\nAdvancing {days_to_run} days...\n")

    for i in range(days_to_run):
        try:
            summary = advance_day(config)
            print(summary)
            print()
        except Exception as e:
            print(f"ERROR on day {i+1}: {e}")
            import traceback
            traceback.print_exc()
            break

    ws_final = data_manager.load_world_state(config)
    if ws_final:
        print(f"\n{'='*60}")
        print(f"Final state: Day {ws_final['day_number']} — {ws_final['current_date']}")
        print(f"Rankings: {ws_final['rankings']}")
        print(f"Completed events: {len(ws_final['completed_events'])}")
        print(f"Upcoming events: {len(ws_final['upcoming_events'])}")
        print(f"Active injuries: {ws_final['active_injuries']}")


if __name__ == "__main__":
    main()
