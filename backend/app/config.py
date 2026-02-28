from dataclasses import dataclass, field
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass
class Config:
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    grok_api_key: str = ""
    grok_base_url: str = "https://api.x.ai/v1"
    # default_model: str = "minimax/minimax-m2.5"
    # narrative_model: str = "minimax/minimax-m2.5"
    default_model: str = "x-ai/grok-4.1-fast"
    narrative_model: str = "x-ai/grok-4.1-fast"

    roster_size: int = 8
    fights_per_event: int = 3
    events_per_week: int = 2
    rounds_per_fight: int = 3

    min_total_stats: int = 120
    max_total_stats: int = 340
    stat_min: int = 15
    stat_max: int = 95
    supernatural_cap: int = 50

    minor_recovery: tuple = (5, 9)
    moderate_recovery: tuple = (14, 28)
    severe_recovery: tuple = (42, 56)

    rematch_cooldown_days: int = 14
    max_idle_days: int = 14
    draw_probability: float = 0.03

    moments_per_fight: int = 4

    data_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data"
    )


def load_config() -> Config:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    return Config(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        grok_api_key=os.getenv("GROK_API_KEY", ""),
    )
