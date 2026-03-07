import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config import load_config
from app.services.grok_image import generate_image, edit_image, download_image

config = load_config()
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "fighters"
FEMALE_REF = Path(__file__).parent.parent / "data" / "reference_images" / "female" / "pussy_asshole_behind2.png"

NO_TEXT = "absolutely no text no words no letters no labels no captions no watermarks"

BODY_REF_LAYOUT = (
    "five separate drawings arranged with three on top and two on the bottom: "
    "face portrait in the top-left, "
    "nude rear angled view in the top-center, "
    "nude torso with breasts in the top-right, "
    "nude rear butt study in the bottom-left, "
    "nude spread-leg intimate study in the bottom-right, "
    "clear empty space between each drawing, "
    "each drawing floats independently"
)

BODY_REF_PAGE = (
    "artist anatomy study page, figure drawing body part studies, "
    "separate isolated body part drawings arranged on the page with three on top and two on the bottom, "
    "each body part cropped and drawn individually with space between them, "
    "clean off-white parchment background, organized sketchbook page layout, "
    f"{NO_TEXT}, drawing guide extremely detailed anatomy"
)

BODY_REF_SUBJECT = (
    "fair Eastern European skin, athletic 5'7\" 125 lbs frame with large heavy breasts, "
    "narrow waist, toned defined abs, large thick butt, soft round face shape, round eyes, "
    "slightly upturned nose, full pouty lips, heavy intense brows, soft subtle cheekbones, "
    "delicate tapered jawline, moderate polished makeup with foundation defined eyes lipstick, "
    "long tangled ash grey hair with white streaks often covering eyes, "
    "tribal bone jewelry across forehead, average height 5'7\", large heavy breasts, "
    "large thick butt, oracle aesthetic, sees the future, fights with foreknowledge, "
    "32 years old, from Sibiu Romania, tribal bone jewelry across forehead, "
    "long tangled ash-grey hair with white streaks, heavy intense brows, full pouty lips, scarred palms, "
    "all body parts belong to the same single character"
)

FACE_PANEL = (
    "isolated face and neck portrait drawing, foreboding unblinking stare, "
    "soft round face shape, delicate tapered jaw, soft subtle cheekbones, round eyes, "
    "heavy intense brows, slightly upturned nose, full pouty lips, polished look, "
    "foundation, defined eyes, lipstick, three-quarter angle, "
    "wearing tribal bone jewelry across forehead, "
    "long tangled ash-grey hair with white streaks, scarred palms"
)

REAR_ANGLED_PANEL = (
    "isolated nude rear view at an angle, bent forward back arched casually, "
    "large thick butt with natural curvature, hands raised above head, profile"
)

CHEST_PANEL = (
    "isolated nude female torso drawing from collarbone to thighs, "
    "large heavy breasts with large puffy nipples, natural breast shape and weight, "
    "defined collarbone, toned and defined abs/core on toned flat stomach, "
    "athletic 17-20% body fat, navel visible, narrow waist, "
    "visible labia minora peeking out fully visible and detailed, front view"
)

BUTT_PANEL = (
    "isolated nude female butt study, rear view directly behind, "
    "bent forward sensuously with back arched and butt popped out toward viewer, "
    "large thick butt with natural curvature, "
    "asshole and pussy visible from behind between spread cheeks, "
    "low rear angle looking up, explicit detail, hands spreading ass cheeks"
)

INTIMATE_PANEL = (
    "isolated nude female intimate study from navel to mid-thigh, "
    "legs up and spread apart, "
    "visible labia minora peeking out fully visible and detailed, "
    "front view, extremely detailed pussy, perfectly drawn anatomically accurate"
)

BODY_TYPE = "large heavy breasts, large puffy nipples, large thick butt, visible labia minora peeking out"

CHARSHEET_LAYOUT = (
    "character model sheet, character reference sheet, "
    "two full-body views of the exact same character side by side: "
    "front-facing view on the left, rear view on the right, "
    "consistent outfit across both views, full body head to toe visible in each panel, "
    "dark background, organized reference sheet layout"
)

SFW_CHARACTER = (
    "fair Eastern European skin, athletic 5'7\" 125 lbs frame with large heavy breasts, "
    "narrow waist, toned defined abs, large thick butt, soft round face shape, round eyes, "
    "slightly upturned nose, full pouty lips, heavy intense brows, soft subtle cheekbones, "
    "delicate tapered jawline, long tangled ash grey hair with white streaks often covering eyes, "
    "tribal bone jewelry across forehead, average height 5'7\", "
    "large heavy breasts shape under tight fabric, partially visible large thick butt, "
    "oracle aesthetic, sees the future, fights with foreknowledge, "
    "32 years old, Midnight Black nano-weave bodysuit midriff cutout thigh windows back panels, "
    "fingerless mesh gloves, mag-locked combat boots, tribal bone forehead jewelry, "
    "glowing sigil armbands, bone-linked utility belt, "
    "tribal bone jewelry across forehead, long tangled ash-grey hair with white streaks, "
    "heavy intense brows, full pouty lips, scarred palms, "
    "from Sibiu Romania, wearing tribal bone jewelry across forehead"
)

SFW_VIEWS = (
    "front-facing slightly angled view standing tall, "
    "palms extended forward, unblinking prophetic stare, "
    "rear view standing tall"
)

SFW_EXPRESSION = "foreboding unblinking stare"


STYLES = {
    "comic_classic": {
        "body_ref_style": (
            "American comic book ink art, heavy black ink outlines, "
            "cross-hatching shading technique, pen and ink illustration, "
            "detailed comic book linework, bold graphic illustration, "
            "female character, beautiful and dangerous"
        ),
        "body_ref_quality": (
            "comic book ink art, heavy outlines, cross-hatching, "
            "detailed linework, figure drawing study quality, "
            "each body part rendered as its own separate floating illustration, "
            "clean parchment background, "
            "no text no words no labels no watermarks"
        ),
        "charsheet_style": (
            "American comic book art, heavy ink outlines, cross-hatching shading, "
            "four-color printing style, halftone dot pattern, bold graphic novel illustration, "
            "dynamic comic book panel art, Jim Lee style detailed linework, "
            "superhero comic art, pen and ink with digital coloring, "
            f"{NO_TEXT}, strictly female character, "
            "feminine curves and anatomy, beautiful face with attractive features, dangerous fighter, "
            f"character (strictly over 18 years old), character design reference sheet, {CHARSHEET_LAYOUT}"
        ),
        "charsheet_tail": (
            "comic book art, ink outlines, cross-hatching, halftone dots, "
            "graphic novel quality, dynamic illustration, "
            "beautiful face, feminine, dangerous, "
            "character reference sheet, two consistent views"
        ),
    },
    "modern_dc": {
        "body_ref_style": (
            "modern DC Comics painted art style, Alex Ross inspired painted illustration, "
            "fully painted comic book art with visible brushwork, "
            "heroic dramatic lighting, rich deep shadows, "
            "painted realism with comic book sensibility, "
            "female character, beautiful and dangerous"
        ),
        "body_ref_quality": (
            "Alex Ross painted comic art, painted illustration, "
            "heroic lighting, deep shadows, "
            "figure drawing study quality, "
            "each body part rendered as its own separate floating illustration, "
            "clean parchment background, "
            "no text no words no labels no watermarks"
        ),
        "charsheet_style": (
            "modern DC Comics cover art, Alex Ross inspired painted comic style, "
            "fully painted comic book illustration with visible brushwork, "
            "heroic dramatic lighting, rich deep shadows, "
            "painted realism with comic book sensibility, bold composition, "
            "detailed ink linework under painted color, premium cover art quality, "
            f"{NO_TEXT}, strictly female character, "
            "feminine curves and anatomy, beautiful face with attractive features, dangerous fighter, "
            f"character (strictly over 18 years old), character design reference sheet, {CHARSHEET_LAYOUT}"
        ),
        "charsheet_tail": (
            "Alex Ross painted comic art, painted comic cover, "
            "heroic lighting, deep shadows, premium comic illustration, "
            "beautiful face, feminine, dangerous, "
            "character reference sheet, two consistent views"
        ),
    },
    "indie_dark": {
        "body_ref_style": (
            "dark indie comic art, heavy black ink with minimal color, "
            "stark high-contrast shadows, noir comic style, "
            "Mike Mignola inspired bold shapes and deep blacks, "
            "limited muted color palette, woodcut-like bold linework, "
            "female character, beautiful and dangerous"
        ),
        "body_ref_quality": (
            "dark indie comic art, heavy black ink, noir shadows, "
            "Mignola bold shapes, limited palette, "
            "figure drawing study quality, "
            "each body part rendered as its own separate floating illustration, "
            "clean parchment background, "
            "no text no words no labels no watermarks"
        ),
        "charsheet_style": (
            "dark indie comic art, heavy black ink with minimal color, "
            "stark high-contrast shadows, noir comic style, "
            "Mike Mignola inspired bold shapes and deep blacks, "
            "limited muted color palette with one accent color, "
            "woodcut-like bold linework, atmospheric horror comic aesthetic, "
            "Hellboy art style graphic weight, "
            f"{NO_TEXT}, strictly female character, "
            "feminine curves and anatomy, beautiful face with attractive features, dangerous fighter, "
            f"character (strictly over 18 years old), character design reference sheet, {CHARSHEET_LAYOUT}"
        ),
        "charsheet_tail": (
            "dark indie comic, heavy black ink, noir shadows, "
            "Mignola bold shapes, limited palette, atmospheric horror comic, "
            "beautiful face, feminine, dangerous, "
            "character reference sheet, two consistent views"
        ),
    },
}


def build_body_ref_prompt(style_data: dict) -> str:
    sections = [
        f"[STYLE] {style_data['body_ref_style']}, {BODY_REF_PAGE}",
        f"[LAYOUT] {BODY_REF_LAYOUT}",
        f"[SUBJECT] {BODY_REF_SUBJECT}",
        f"[TOP-LEFT: FACE] {FACE_PANEL}",
        f"[TOP-CENTER: REAR ANGLED VIEW] {REAR_ANGLED_PANEL}",
        f"[TOP-RIGHT: CHEST AND CROTCH STANDING] {CHEST_PANEL}",
        f"[BOTTOM-LEFT: BUTT] {BUTT_PANEL}",
        f"[BOTTOM-RIGHT: INTIMATE] {INTIMATE_PANEL}",
        f"[BODY TYPE] {BODY_TYPE}",
        f"[QUALITY] {style_data['body_ref_quality']}",
    ]
    return "\n".join(sections)


def build_sfw_prompt(style_data: dict) -> str:
    sections = [
        f"[STYLE] {style_data['charsheet_style']}",
        f"[CHARACTER] {SFW_CHARACTER}",
        f"[VIEWS] {SFW_VIEWS}",
        f"[EXPRESSION] {SFW_EXPRESSION}",
        f"[QUALITY] {style_data['charsheet_tail']}",
    ]
    return "\n".join(sections)


def main():
    for style_name, style_data in STYLES.items():
        print(f"\n{'='*60}")
        print(f"  STYLE: {style_name}")
        print(f"{'='*60}")

        body_ref_prompt = build_body_ref_prompt(style_data)
        body_ref_path = OUTPUT_DIR / f"_pipeline_{style_name}_body_ref.png"

        print(f"\n  Stage 1: Generating body_ref (using reference photo as input)...")
        try:
            urls = edit_image(
                prompt=body_ref_prompt,
                image_paths=[FEMALE_REF],
                config=config,
                aspect_ratio="1:1",
                resolution="2k",
                n=1,
                pad_to_aspect=True,
            )
            download_image(urls[0], body_ref_path)
            print(f"  Saved: {body_ref_path.name}")
        except Exception as e:
            print(f"  FAILED body_ref: {e}")
            continue

        sfw_prompt = build_sfw_prompt(style_data)
        sfw_path = OUTPUT_DIR / f"_pipeline_{style_name}_sfw.png"

        print(f"\n  Stage 2: Generating SFW charsheet (using body_ref as input)...")
        try:
            urls = edit_image(
                prompt=sfw_prompt,
                image_paths=[body_ref_path],
                config=config,
                aspect_ratio="1:1",
                resolution="2k",
                n=1,
            )
            download_image(urls[0], sfw_path)
            print(f"  Saved: {sfw_path.name}")
        except Exception as e:
            print(f"  FAILED sfw: {e}")

    print("\n\nDone! Check data/fighters/ for _pipeline_*.png files")


if __name__ == "__main__":
    main()
