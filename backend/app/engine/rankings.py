def calculate_rankings(fighters: list[dict], recent_matches: list[dict]) -> list[str]:
    fighter_stats = []

    recent_match_map = {}
    for match in recent_matches:
        outcome = match.get("outcome", {})
        if not outcome:
            continue
        for fid in [match.get("fighter1_id"), match.get("fighter2_id")]:
            if fid:
                if fid not in recent_match_map:
                    recent_match_map[fid] = []
                recent_match_map[fid].append(match)

    for fighter in fighters:
        fid = fighter["id"]
        record = fighter.get("record", {})
        wins = record.get("wins", 0)
        losses = record.get("losses", 0)
        draws = record.get("draws", 0)
        total = wins + losses + draws

        win_pct = wins / total if total > 0 else 0.0

        fighter_matches = recent_match_map.get(fid, [])
        fighter_matches.sort(key=lambda m: m.get("date", ""), reverse=True)
        recent_wins = 0
        for m in fighter_matches[:5]:
            outcome = m.get("outcome", {})
            if outcome.get("winner_id") == fid:
                recent_wins += 1

        last_fight = fighter.get("last_fight_date", "") or ""

        fighter_stats.append({
            "id": fid,
            "win_pct": win_pct,
            "total_wins": wins,
            "recent_wins": recent_wins,
            "total_fights": total,
            "last_fight": last_fight,
        })

    fighter_stats.sort(
        key=lambda f: (
            f["total_fights"] > 0,
            f["win_pct"],
            f["total_wins"],
            f["recent_wins"],
            f["last_fight"],
        ),
        reverse=True,
    )

    return [f["id"] for f in fighter_stats]
