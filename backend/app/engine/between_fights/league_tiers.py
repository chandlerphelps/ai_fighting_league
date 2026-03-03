TIER_ORDER = {"underground": 0, "contender": 1, "championship": 2}
TIER_NAMES = ["underground", "contender", "championship"]


def calculate_tier_rankings(fighters: list[dict], tier: str, season_matches: list[dict] = None) -> list[str]:
    tier_fighters = [f for f in fighters if f.get("tier") == tier and f.get("status") == "active"]

    if season_matches is None:
        season_matches = []

    recent_match_map = {}
    for match in season_matches:
        outcome = match.get("outcome", {})
        if not outcome:
            continue
        for fid in [match.get("fighter1_id"), match.get("fighter2_id")]:
            if fid:
                if fid not in recent_match_map:
                    recent_match_map[fid] = []
                recent_match_map[fid].append(match)

    fighter_stats = []
    for fighter in tier_fighters:
        fid = fighter["id"]
        s_wins = fighter.get("season_wins", 0)
        s_losses = fighter.get("season_losses", 0)
        total = s_wins + s_losses
        win_pct = s_wins / total if total > 0 else 0.0

        recent_wins = 0
        fighter_matches = recent_match_map.get(fid, [])
        fighter_matches.sort(key=lambda m: m.get("date", ""), reverse=True)
        for m in fighter_matches[:5]:
            outcome = m.get("outcome", {})
            if outcome.get("winner_id") == fid:
                recent_wins += 1

        core_total = sum(
            fighter.get("stats", {}).get(s, 0)
            for s in ["power", "speed", "technique", "toughness"]
        )

        fighter_stats.append({
            "id": fid,
            "win_pct": win_pct,
            "season_wins": s_wins,
            "recent_wins": recent_wins,
            "total_fights": total,
            "core_total": core_total,
        })

    fighter_stats.sort(
        key=lambda f: (
            f["total_fights"] > 0,
            f["win_pct"],
            f["season_wins"],
            f["recent_wins"],
            f["core_total"],
        ),
        reverse=True,
    )

    return [f["id"] for f in fighter_stats]


def get_promotion_matchups(tier_rankings: dict, slots_per_boundary: int = 3) -> list[dict]:
    matchups = []

    champ_ranks = tier_rankings.get("championship", [])
    contender_ranks = tier_rankings.get("contender", [])
    underground_ranks = tier_rankings.get("underground", [])

    n = min(slots_per_boundary, len(champ_ranks), len(contender_ranks))
    for i in range(n):
        matchups.append({
            "upper_fighter_id": champ_ranks[-(i + 1)],
            "lower_fighter_id": contender_ranks[i],
            "tier_boundary": "champ_contender",
        })

    n = min(slots_per_boundary, len(contender_ranks), len(underground_ranks))
    for i in range(n):
        matchups.append({
            "upper_fighter_id": contender_ranks[-(i + 1)],
            "lower_fighter_id": underground_ranks[i],
            "tier_boundary": "contender_underground",
        })

    return matchups


def apply_promotion_results(fighters: dict, promotion_results: list[dict]) -> list[dict]:
    changes = []

    for result in promotion_results:
        winner_id = result["winner_id"]
        loser_id = result["loser_id"]
        boundary = result["tier_boundary"]
        upper_fighter_id = result["upper_fighter_id"]

        if boundary == "champ_contender":
            upper_tier, lower_tier = "championship", "contender"
        else:
            upper_tier, lower_tier = "contender", "underground"

        if winner_id == upper_fighter_id:
            changes.append({"fighter_id": winner_id, "action": "stayed", "tier": upper_tier})
            changes.append({"fighter_id": loser_id, "action": "stayed", "tier": lower_tier})
        else:
            promoted = fighters.get(winner_id, {})
            promoted["tier"] = upper_tier
            promoted["seasons_in_current_tier"] = 0
            if TIER_ORDER.get(upper_tier, 0) > TIER_ORDER.get(promoted.get("peak_tier", "underground"), 0):
                promoted["peak_tier"] = upper_tier
            changes.append({"fighter_id": winner_id, "action": "promoted", "tier": upper_tier})

            relegated = fighters.get(loser_id, {})
            relegated["tier"] = lower_tier
            relegated["seasons_in_current_tier"] = 0
            changes.append({"fighter_id": loser_id, "action": "relegated", "tier": lower_tier})

    return changes


def apply_title_fight_result(ws: dict, winner_id: str, loser_id: str, season: int) -> None:
    current_holder = ws.get("belt_holder_id", "")

    if current_holder and current_holder == winner_id:
        for entry in ws.get("belt_history", []):
            if entry.get("fighter_id") == winner_id and not entry.get("lost_date"):
                entry["defenses"] = entry.get("defenses", 0) + 1
                break
    else:
        for entry in ws.get("belt_history", []):
            if entry.get("fighter_id") == current_holder and not entry.get("lost_date"):
                entry["lost_date"] = f"season_{season}"
                break

        ws["belt_holder_id"] = winner_id
        ws.setdefault("belt_history", []).append({
            "fighter_id": winner_id,
            "won_date": f"season_{season}",
            "lost_date": None,
            "defenses": 0,
        })
