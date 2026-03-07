PAINTERLY_STYLE_BASE = (
    "hand-painted textures over detailed 3D forms, "
    "extremely detailed skin textures, painterly brushstroke overlay, "
    "soft even studio lighting, highly detailed anatomy, "
    "professional perfect shading"
)

PAINTERLY_STYLE_FEMALE = (
    PAINTERLY_STYLE_BASE + ", female character, beautiful and deadly"
)

PAINTERLY_STYLE_MALE = (
    PAINTERLY_STYLE_BASE + ", male character, masculine build, rugged features"
)

PAINTERLY_QUALITY = (
    "hand-painted textures, extremely detailed, anatomical precision, "
    "figure drawing study quality, "
    "each body part rendered as its own separate floating illustration, "
    "soft even lighting, clean parchment background, "
    "no text no words no labels no watermarks"
)

PAINTERLY_QUALITY_MALE = (
    "hand-painted textures, extremely detailed, anatomical precision, "
    "figure drawing study quality, "
    "each drawing rendered as its own separate floating illustration, "
    "soft even lighting, clean parchment background, "
    "masculine imposing physique, "
    "no text no words no labels no watermarks"
)


ART_STYLE_BASE = (
    "dark indie comic art, heavy black ink with minimal color, "
    "stark high-contrast shadows, noir comic style, "
    "Mike Mignola inspired bold shapes and deep blacks, "
    "limited muted color palette with one accent color, "
    "woodcut-like bold linework, atmospheric horror comic aesthetic, "
    "Hellboy art style graphic weight, "
    "absolutely no text, no words, no letters, no labels, no captions, no watermarks"
)

ART_STYLE_FEMALE = (
    ART_STYLE_BASE + ", "
    "strictly female character, feminine curves and anatomy, "
    "beautiful face with attractive features, deadly fighter"
)

ART_STYLE_MALE = (
    ART_STYLE_BASE + ", "
    "male character, masculine build and anatomy, imposing physique, "
    "chiseled jaw, rugged face"
)

ART_STYLE_TAIL_BASE = (
    "dark indie comic, heavy black ink, noir shadows, "
    "Mignola bold shapes, limited palette, atmospheric horror comic, "
    "no text, no words, no labels, no watermarks"
)

ART_STYLE_TAIL_FEMALE = ART_STYLE_TAIL_BASE + ", beautiful face, feminine, deadly"

ART_STYLE_TAIL_MALE = ART_STYLE_TAIL_BASE + ", masculine, imposing"

ART_STYLE = ART_STYLE_FEMALE
ART_STYLE_TAIL = ART_STYLE_TAIL_FEMALE


def get_art_style(gender: str = "female") -> str:
    if gender.lower() == "male":
        return ART_STYLE_MALE
    return ART_STYLE_FEMALE


def get_art_style_tail(gender: str = "female") -> str:
    if gender.lower() == "male":
        return ART_STYLE_TAIL_MALE
    return ART_STYLE_TAIL_FEMALE
