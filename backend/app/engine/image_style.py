ART_STYLE_BASE = (
    "hand-painted textures over detailed 3D forms, "
    "extremely detailed skin and fabric textures, painterly brushstroke overlay, "
    "rich moody color grading, dramatic volumetric lighting with atmospheric haze, "
    "highly detailed anatomy, professional perfect shading, "
    "absolutely no text, no words, no letters, no labels, no captions, no watermarks"
)

ART_STYLE_FEMALE = (
    ART_STYLE_BASE + ", "
    "strictly female character, feminine curves and anatomy, "
    "beautiful face with attractive features"
)

ART_STYLE_MALE = (
    ART_STYLE_BASE + ", "
    "male character, masculine build and anatomy, imposing physique, "
    "chiseled jaw, rugged handsome face"
)

ART_STYLE_TAIL_BASE = (
    "hand-painted textures, extremely detailed, "
    "moody color grading, dramatic volumetric lighting, "
    "no text, no words, no labels, no watermarks"
)

ART_STYLE_TAIL_FEMALE = ART_STYLE_TAIL_BASE + ", beautiful face, feminine"

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
