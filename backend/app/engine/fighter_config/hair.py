HAIR_COLOR_BUCKETS = [
    "Black",
    "Brown",
    "Blonde",
    "Red/Auburn",
    "White/Silver",
    "Blue",
    "Pink",
    "Green",
    "Purple",
    "Multicolor",
]

_HAIR_BUCKET_KEYWORDS = {
    "Black": ["black", "jet black", "raven", "ebony", "onyx", "dark black"],
    "Brown": [
        "brown",
        "brunette",
        "chestnut",
        "chocolate",
        "mocha",
        "mahogany",
        "walnut",
        "coffee",
        "hazel",
        "caramel",
        "tawny",
    ],
    "Blonde": [
        "blonde",
        "blond",
        "golden",
        "platinum",
        "honey",
        "sandy",
        "ash blonde",
        "strawberry blonde",
        "flaxen",
        "wheat",
        "champagne",
        "butter",
    ],
    "Red/Auburn": [
        "red",
        "auburn",
        "ginger",
        "copper",
        "crimson",
        "scarlet",
        "rust",
        "fire",
        "flame",
        "cherry",
        "ruby",
        "vermillion",
        "cinnamon",
    ],
    "White/Silver": [
        "white",
        "silver",
        "grey",
        "gray",
        "platinum white",
        "snow",
        "frost",
        "ice",
        "steel",
        "pearl",
        "ivory",
    ],
    "Blue": [
        "blue",
        "navy",
        "cerulean",
        "cobalt",
        "azure",
        "sapphire",
        "teal",
        "cyan",
        "indigo",
    ],
    "Pink": [
        "pink",
        "magenta",
        "fuchsia",
        "rose",
        "bubblegum",
        "coral",
        "salmon",
        "hot pink",
    ],
    "Green": [
        "green",
        "emerald",
        "lime",
        "olive",
        "mint",
        "jade",
        "forest",
        "sage",
        "teal green",
    ],
    "Purple": [
        "purple",
        "violet",
        "lavender",
        "lilac",
        "plum",
        "amethyst",
        "mauve",
        "orchid",
    ],
    "Multicolor": [
        "multicolor",
        "rainbow",
        "ombre",
        "gradient",
        "streaks",
        "highlights",
        "tips",
        "two-tone",
        "split",
    ],
}


def classify_hair_color(raw: str) -> str:
    if not raw:
        return ""
    lower = raw.lower().strip()
    for bucket, keywords in _HAIR_BUCKET_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                if bucket == "White/Silver" and (
                    "platinum blonde" in lower or "strawberry" in lower
                ):
                    continue
                return bucket
    return "Brown"
