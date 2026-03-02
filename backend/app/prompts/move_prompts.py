SYSTEM_PROMPT_MOVE_DESIGNER = (
    "You are a fighting game move designer. "
    "Create visually iconic, character-specific combat moves. "
    "Always respond with valid JSON only \u2014 an array of objects."
)


def build_move_generation_prompt(
    ring_name: str,
    build: str,
    personality: str,
    distinguishing: str,
    iconic: str,
    gender: str,
    stat_lines: str,
) -> str:
    return f"""You are designing fighting moves for "{ring_name}" in an AI fighting league.

CHARACTER:
- Build: {build}
- Personality: {personality}
- Distinguishing features: {distinguishing}
- Iconic features: {iconic}
- Gender: {gender}
- Stats: {stat_lines}

Design exactly 3 fighting moves for this character. Rules:
- Each move must feel unique to THIS character's body, personality, and strongest stats
- The moves must make sense physically - we will be generating images from them
- Moves are strikes, kicks, acrobatic attacks, or supernatural abilities — never holds or grapples
- Names: 2-4 words, evocative and memorable (fighting game style)
- stat_affinity: which stat the move leans on most (power, speed, technique, or supernatural)
- Lean into the character's highest stats and defining traits
- All three moves should feel different from each other in rhythm and visual impact

DESCRIPTION: 1-2 sentences explaining how the move works — the full choreography from start to finish. No metaphors or poetry, just plain physical action.

IMAGE_SNAPSHOT — THIS IS CRITICAL:
- This is a SINGLE FROZEN MOMENT for an artist to draw. One frame, not a sequence.
- Think through how the entire move would work step by step then pick the coolest moment to capture
- Describe the exact body position: where each limb is, weight distribution, angle of torso, head position
- End with which body parts have motion blur or speed lines (e.g. "motion blur on right leg and both fists")
- The fighter is ALONE — no opponent in the image
- BANNED: metaphors, similes, poetry, "like a ___", emotional descriptors, atmosphere words
- BANNED: any reference to an opponent, target, or impact
- BANNED: sequences or transitions — no "then", "before", "after", "lands in"
- GOOD example: "Mid-air, body horizontal, right leg fully extended forward at head height, left leg tucked under, arms swept back behind torso. Motion blur on right leg."
- GOOD example: "Deep lunge on left leg, right fist extended straight forward at shoulder height, left arm pulled back to hip, torso twisted 45 degrees. Speed lines on right fist."
- BAD example: "Leaps forward off one foot, drives both fists downward. Lands in a low crouch." (this is a sequence, not a snapshot)
- Keep it to 1-2 sentences — a single freeze-frame plus motion indicators.

Return ONLY valid JSON — an array of exactly 3 objects:
[
  {{
    "name": "<2-4 word move name>",
    "description": "<1-2 sentences: how the move works, full choreography>",
    "image_snapshot": "<1 sentence: single frozen moment, exact body position for an artist>",
    "stat_affinity": "<power|speed|technique|supernatural>"
  }}
]"""
