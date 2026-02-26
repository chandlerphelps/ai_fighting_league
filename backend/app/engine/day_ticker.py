import uuid
from datetime import datetime, timedelta

from app.config import Config
from app.models.event import Event, EventMatch
from app.models.world_state import WorldState
from app.engine.fight_simulator import run_fight
from app.engine.post_fight import apply_fight_results
from app.engine.rankings import calculate_rankings
from app.engine.matchmaker import generate_fight_card
from app.services import data_manager


def advance_day(config: Config) -> str:
    ws_data = data_manager.load_world_state(config)
    if not ws_data:
        raise RuntimeError("No world state found. Run --init first.")

    ws = WorldState.from_dict(ws_data)
    current = datetime.strptime(ws.current_date, "%Y-%m-%d")
    next_day = current + timedelta(days=1)
    ws.current_date = next_day.strftime("%Y-%m-%d")
    ws.day_number += 1

    summary_parts = [f"Day {ws.day_number} — {ws.current_date}"]

    healed = _process_injury_recovery(ws, config)
    if healed:
        summary_parts.append(f"Healed: {', '.join(healed)}")

    event_summary = _run_todays_event(ws, config)
    if event_summary:
        summary_parts.append(event_summary)

    _ensure_upcoming_schedule(ws, config)

    ws_dict = ws.to_dict()
    data_manager.save_world_state(ws_dict, config)

    summary = " | ".join(summary_parts)
    ws_dict["last_daily_summary"] = summary
    data_manager.save_world_state(ws_dict, config)

    return summary


def _process_injury_recovery(ws: WorldState, config: Config) -> list[str]:
    healed = []
    new_injuries = {}

    for fighter_id, days_left in ws.active_injuries.items():
        remaining = days_left - 1
        if remaining <= 0:
            fighter_data = data_manager.load_fighter(fighter_id, config)
            if fighter_data:
                fighter_data["condition"]["health_status"] = "healthy"
                fighter_data["condition"]["injuries"] = []
                fighter_data["condition"]["recovery_days_remaining"] = 0
                fighter_data["condition"]["morale"] = "neutral"
                data_manager.save_fighter(fighter_data, config)
                ring_name = fighter_data.get("ring_name", fighter_id)
                healed.append(ring_name)
        else:
            new_injuries[fighter_id] = remaining

    ws.active_injuries = new_injuries
    return healed


def _run_todays_event(ws: WorldState, config: Config) -> str | None:
    today = ws.current_date
    todays_event_id = None

    for event_id in ws.upcoming_events:
        event_data = data_manager.load_event(event_id, config)
        if event_data and event_data.get("date") == today and not event_data.get("completed"):
            todays_event_id = event_id
            break

    if not todays_event_id:
        return None

    event_data = data_manager.load_event(todays_event_id, config)
    event = Event.from_dict(event_data)

    results = []
    for i, event_match in enumerate(event.matches):
        try:
            print(f"  Running fight: {event_match.fighter1_name} vs {event_match.fighter2_name}...")
            match = run_fight(
                event_match.fighter1_id, event_match.fighter2_id,
                event.id, today, config,
            )

            data_manager.save_match(match, config)

            changes = apply_fight_results(match, config)

            event.matches[i].match_id = match.id
            event.matches[i].completed = True

            outcome = match.outcome
            if outcome.is_draw:
                event.matches[i].winner_id = None
                event.matches[i].method = "draw"
                result_text = f"{event_match.fighter1_name} vs {event_match.fighter2_name}: DRAW"
            else:
                event.matches[i].winner_id = outcome.winner_id
                event.matches[i].method = outcome.method
                winner_name = event_match.fighter1_name if outcome.winner_id == event_match.fighter1_id else event_match.fighter2_name
                method_display = outcome.method.replace("_", " ").upper()
                result_text = f"{winner_name} wins by {method_display} (R{outcome.round_ended})"

            results.append(result_text)

            if outcome:
                if outcome.fighter1_injuries:
                    ws.active_injuries[event_match.fighter1_id] = max(
                        inj.get("recovery_days_remaining", 0) for inj in outcome.fighter1_injuries
                    )
                if outcome.fighter2_injuries:
                    ws.active_injuries[event_match.fighter2_id] = max(
                        inj.get("recovery_days_remaining", 0) for inj in outcome.fighter2_injuries
                    )

        except Exception as e:
            print(f"  ERROR in fight: {e}")
            results.append(f"{event_match.fighter1_name} vs {event_match.fighter2_name}: ERROR")

    event.completed = True
    event.summary = "; ".join(results)
    data_manager.save_event(event, config)

    if todays_event_id in ws.upcoming_events:
        ws.upcoming_events.remove(todays_event_id)
    ws.completed_events.append(todays_event_id)

    fighters = data_manager.load_all_fighters(config)
    matches = data_manager.load_all_matches(config)
    ws.rankings = calculate_rankings(fighters, matches)

    return f"EVENT: {event.name} — {'; '.join(results)}"


def _ensure_upcoming_schedule(ws: WorldState, config: Config):
    current = datetime.strptime(ws.current_date, "%Y-%m-%d")
    horizon = current + timedelta(days=7)

    future_events = []
    for event_id in ws.upcoming_events:
        event_data = data_manager.load_event(event_id, config)
        if event_data:
            try:
                event_date = datetime.strptime(event_data["date"], "%Y-%m-%d")
                if event_date > current:
                    future_events.append(event_date)
            except (ValueError, KeyError):
                pass

    if len(future_events) >= 2:
        return

    events_needed = 2 - len(future_events)

    if future_events:
        last_scheduled = max(future_events)
    else:
        last_scheduled = current

    for _ in range(events_needed):
        gap = 3 if not future_events else 4
        event_date = last_scheduled + timedelta(days=gap)

        if event_date <= current:
            event_date = current + timedelta(days=2)

        event = _create_event(ws, event_date, config)
        if event:
            future_events.append(event_date)
            last_scheduled = event_date


def _create_event(ws: WorldState, event_date: datetime, config: Config) -> Event | None:
    fighters = data_manager.load_all_fighters(config)
    matches = data_manager.load_all_matches(config)

    ws_dict = ws.to_dict()
    ws_dict["current_date"] = ws.current_date

    card = generate_fight_card(ws_dict, fighters, matches, config)

    if not card:
        return None

    ws.event_counter += 1
    event_id = f"e_{uuid.uuid4().hex[:8]}"
    date_str = event_date.strftime("%Y-%m-%d")

    event_matches = []
    for f1_id, f2_id in card:
        f1 = data_manager.load_fighter(f1_id, config)
        f2 = data_manager.load_fighter(f2_id, config)
        f1_name = f1.get("ring_name", f1_id) if f1 else f1_id
        f2_name = f2.get("ring_name", f2_id) if f2 else f2_id

        event_matches.append(EventMatch(
            match_id="",
            fighter1_id=f1_id,
            fighter1_name=f1_name,
            fighter2_id=f2_id,
            fighter2_name=f2_name,
        ))

    event = Event(
        id=event_id,
        date=date_str,
        name=f"AFL Fight Night {ws.event_counter}",
        matches=event_matches,
    )

    data_manager.save_event(event, config)
    ws.upcoming_events.append(event_id)

    print(f"  Scheduled: {event.name} on {date_str} ({len(card)} fights)")
    return event
