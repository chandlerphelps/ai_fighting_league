# API Usage Guide

Base URL: `http://localhost:5001`

## Fighters

### List all fighters
```bash
curl "http://localhost:5001/api/fighters"
```
Response: `[{"id": "f_abc123", "ring_name": "Venom", "_available_images": ["sfw", "barely"], ...}]`

### Get single fighter
```bash
curl "http://localhost:5001/api/fighters/f_abc123"
```

### Update fighter fields
```bash
curl -X PUT "http://localhost:5001/api/fighters/f_abc123" \
  -H "Content-Type: application/json" \
  -d '{"ring_name": "New Name", "stats": {"power": 80}}'
```

### Delete fighter
```bash
curl -X DELETE "http://localhost:5001/api/fighters/f_abc123"
```

## Generation (Async)

All generation endpoints return `{"task_id": "gen_abc123", "status": "running"}` (202). Poll `/api/tasks/<task_id>` for completion.

### Generate new fighter
```bash
curl -X POST "http://localhost:5001/api/fighters/generate" \
  -H "Content-Type: application/json" \
  -d '{"archetype": "Siren", "has_supernatural": true, "tiers": ["sfw", "barely", "nsfw"], "skimpiness_weights": [10, 30, 40, 20]}'
```

### Regenerate character (preserves record/storyline)
```bash
curl -X POST "http://localhost:5001/api/fighters/f_abc123/regenerate-character" \
  -H "Content-Type: application/json" \
  -d '{"archetype": "Witch", "has_supernatural": true}'
```

### Regenerate outfits
```bash
curl -X POST "http://localhost:5001/api/fighters/f_abc123/regenerate-outfits" \
  -H "Content-Type: application/json" \
  -d '{"tiers": ["sfw", "barely"], "skimpiness_level": 3}'
```

### Regenerate charsheet images
```bash
curl -X POST "http://localhost:5001/api/fighters/f_abc123/regenerate-images" \
  -H "Content-Type: application/json" \
  -d '{"tiers": ["sfw", "barely", "nsfw"]}'
```

### Regenerate move image
```bash
curl -X POST "http://localhost:5001/api/fighters/f_abc123/regenerate-move-image" \
  -H "Content-Type: application/json" \
  -d '{"move_index": 0, "tier": "sfw"}'
```

## Tasks

### Poll task status
```bash
curl "http://localhost:5001/api/tasks/gen_abc123"
```
Response (running): `{"task_id": "gen_abc123", "status": "running"}`
Response (done): `{"task_id": "gen_abc123", "status": "completed", "result": {...}}`
Response (failed): `{"task_id": "gen_abc123", "status": "failed", "error": "..."}`

## Config & Images

### Get archetypes
```bash
curl "http://localhost:5001/api/archetypes"
```
Response: `{"female": ["Siren", "Witch", ...], "male": ["Brute", "Veteran", ...]}`

### Get fighter image
```bash
curl "http://localhost:5001/api/fighter-images/f_abc123/sfw" --output image.png
```
Tiers: `sfw`, `barely`, `nsfw`

### Get fighter portrait
```bash
curl "http://localhost:5001/api/fighter-images/f_abc123/portrait" --output portrait.png
```

### Get/save outfit options
```bash
curl "http://localhost:5001/api/outfit-options"

curl -X PUT "http://localhost:5001/api/outfit-options" \
  -H "Content-Type: application/json" \
  -d '{"sfw": {"tops": ["sports bra"], "bottoms": ["shorts"]}, "barely": {...}, "nsfw": {...}}'
```

## Stage Advancement (Async)

### Advance single fighter to next stage
```bash
curl -X POST "http://localhost:5001/api/fighters/f_abc123/advance-stage"
```
Advances: stage 1 -> 2 (portrait), stage 2 -> 3 (full charsheets)

### Batch advance fighters
```bash
curl -X POST "http://localhost:5001/api/fighters/batch-advance" \
  -H "Content-Type: application/json" \
  -d '{"fighter_ids": ["f_abc123", "f_def456"], "target_stage": 3}'
```

## Roster Plan

### Get roster plan
```bash
curl "http://localhost:5001/api/roster-plan"
```
Response: `{"plan_id": "...", "entries": [{"ring_name": "...", "status": "pending", ...}]}`

### Create roster plan (Async)
```bash
curl -X POST "http://localhost:5001/api/roster-plan" \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "gender_mix": "mixed"}'
```

### Delete pending plan entries
```bash
curl -X DELETE "http://localhost:5001/api/roster-plan"
```

### Update plan entry
```bash
curl -X PUT "http://localhost:5001/api/roster-plan/entries/0" \
  -H "Content-Type: application/json" \
  -d '{"ring_name": "New Name", "primary_archetype": "Witch"}'
```

### Delete plan entry
```bash
curl -X DELETE "http://localhost:5001/api/roster-plan/entries/0"
```

### Regenerate plan entry (Async)
```bash
curl -X POST "http://localhost:5001/api/roster-plan/entries/0/regenerate"
```

### Add more plan entries (Async)
```bash
curl -X POST "http://localhost:5001/api/roster-plan/entries/add" \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'
```

### Generate fighters from approved plan entries (Async)
```bash
curl -X POST "http://localhost:5001/api/roster-plan/generate"
```

## World State & Simulation

### Get world state
```bash
curl "http://localhost:5001/api/world-state"
```
Response: full world_state JSON with rankings, season info, belt history, scheduled fights, next matchups

### Simulate one day
```bash
curl -X POST "http://localhost:5001/api/simulate-day"
```
Response: `{"season": 1, "date": "2024-11-02", "matches": [...], "recoveries": [...], "phase": "regular"}`

### Get pool summary
```bash
curl "http://localhost:5001/api/pool-summary"
```
Response: `{"summary": "Total: 136 fighters (80 female, 56 male)..."}`
