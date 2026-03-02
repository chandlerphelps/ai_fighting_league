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

### Get/save outfit options
```bash
curl "http://localhost:5001/api/outfit-options"

curl -X PUT "http://localhost:5001/api/outfit-options" \
  -H "Content-Type: application/json" \
  -d '{"sfw": {"tops": ["sports bra"], "bottoms": ["shorts"]}, "barely": {...}, "nsfw": {...}}'
```
