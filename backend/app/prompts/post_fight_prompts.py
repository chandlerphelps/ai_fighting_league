SYSTEM_PROMPT_STORYLINE = "Write concise, dramatic fight storyline entries."


def build_storyline_prompt(
    fighter_name: str,
    result_text: str,
    opponent_name: str,
    method: str,
    round_ended: int,
    wins: int,
    losses: int,
    draws: int,
) -> str:
    return f"""Write 2-3 sentences about what this fight meant for {fighter_name} narratively.

{fighter_name} {result_text} {opponent_name} by {method} in round {round_ended}.
Current record: {wins}-{losses}-{draws}

Capture the emotional/narrative significance — confidence building, humbling loss, rivalry intensifying, etc. Be concise and dramatic."""
